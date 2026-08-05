"""
资产缓存定时任务调度器

每天北京时间 23:59 主动保存所有用户的总资产到 asset_value_cache 表，
用于次日的日涨跌计算。同时在 00:10 兜底补一次昨日缺失的缓存。
"""
import logging
from datetime import datetime, date, timedelta
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from pytz import timezone
from sqlalchemy.orm import Session

from app.models.database import SessionLocal
from app.models.user import User
from app.models.order import Order
from app.models.asset_transaction import AssetValueCache
from app.services.dashboard_service.assets_service.asset_core_calculations import (
    TotalAssetsCalculator,
    DailyCacheService,
)
from app.services.dashboard_service.assets_service.index_service import IndexService

logger = logging.getLogger(__name__)
BEIJING_TZ = timezone("Asia/Shanghai")


class AssetCacheScheduler:
    """每日总资产缓存主动写入调度器"""

    def __init__(self):
        self._scheduler: BackgroundScheduler | None = None

    def start(self):
        """启动定时任务调度器"""
        if not self._scheduler or not self._scheduler.running:
            self._scheduler = BackgroundScheduler(timezone=BEIJING_TZ)
            # 主任务：每天 23:59 写入当日收盘缓存
            self._scheduler.add_job(
                func=self._daily_save_asset_cache,
                trigger=CronTrigger(hour=23, minute=59, timezone=BEIJING_TZ),
                id='daily_asset_cache_save',
                name='每日总资产缓存保存',
                replace_existing=True,
            )
            # 兜底任务：每天 00:10 补一次昨日缺失缓存（防止容器在 23:59 重启等异常）
            self._scheduler.add_job(
                func=self._backfill_yesterday_cache,
                trigger=CronTrigger(hour=0, minute=10, timezone=BEIJING_TZ),
                id='backfill_yesterday_cache',
                name='兜底补全昨日缓存',
                replace_existing=True,
            )
            # 每日 00:15 清理 stock_index_history 表，仅保留最近 2 个月（60 天）
            self._scheduler.add_job(
                func=self._cleanup_stock_index_history,
                trigger=CronTrigger(hour=0, minute=15, timezone=BEIJING_TZ),
                id='stock_index_history_cleanup',
                name='股票指数历史数据清理（每日 00:15，保留 2 个月）',
                replace_existing=True,
            )
            self._scheduler.start()
            logger.info("资产缓存定时任务调度器已启动：每日 23:59 主动写入，00:10 兜底补齐，00:15 清理指数历史")

    def stop(self):
        """停止定时任务调度器"""
        if self._scheduler and self._scheduler.running:
            self._scheduler.shutdown()
            logger.info("资产缓存定时任务调度器已停止")

    # ── 23:59 主任务 ──────────────────────────────────────────
    def _daily_save_asset_cache(self):
        """
        每日 23:59 主动保存所有用户的总资产缓存

        与"被动生成"的区别：此处由调度器主动触发，**不依赖任何用户访问**。
        写入的 total_value 即代表当日 23:59 时的真实持仓市值。
        """
        db = SessionLocal()
        try:
            logger.info(f"[主任务] 开始执行每日总资产缓存保存 - {datetime.now(BEIJING_TZ)}")
            users = db.query(User).all()
            logger.info(f"[主任务] 共找到 {len(users)} 个用户")

            success, skipped, failed = 0, 0, 0
            for user in users:
                try:
                    if self._save_user_cache_for_date(db, user.id, date.today()):
                        success += 1
                    else:
                        skipped += 1
                except Exception as e:
                    logger.error(f"[主任务] 保存用户 {user.id} 的资产缓存失败: {e}")
                    failed += 1
                    continue

            logger.info(
                f"[主任务] 完成 - 成功 {success} / 跳过 {skipped} / 失败 {failed}"
            )
        except Exception as e:
            logger.error(f"[主任务] 执行失败: {e}")
        finally:
            db.close()

    # ── 00:10 兜底任务 ──────────────────────────────────────────
    def _backfill_yesterday_cache(self):
        """
        兜底补全昨日缺失缓存

        场景：调度器在 23:59 因容器重启、crash 等原因未成功执行；
        次日 00:10 检查每个用户昨日是否已有缓存，没有则补算并写入。
        """
        db = SessionLocal()
        try:
            yesterday = date.today() - timedelta(days=1)
            logger.info(f"[兜底] 检查 {yesterday} 的资产缓存")

            users = db.query(User).all()
            backfilled = 0
            for user in users:
                exists = db.query(AssetValueCache).filter(
                    AssetValueCache.user_id == user.id,
                    AssetValueCache.cache_date == yesterday,
                ).first()
                if exists:
                    continue
                try:
                    if self._save_user_cache_for_date(db, user.id, yesterday):
                        backfilled += 1
                except Exception as e:
                    logger.error(f"[兜底] 补全用户 {user.id} 昨日缓存失败: {e}")

            if backfilled > 0:
                logger.info(f"[兜底] 已补全 {backfilled} 个用户的 {yesterday} 缓存")
            else:
                logger.info(f"[兜底] 所有用户 {yesterday} 缓存已存在，无需补全")
        except Exception as e:
            logger.error(f"[兜底] 兜底任务执行失败: {e}")
        finally:
            db.close()

    # ── 00:15 指数历史清理任务 ──────────────────────────────────────
    def _cleanup_stock_index_history(self):
        """
        每日清理 stock_index_history 表中的过期历史数据

        清理早于 60 天（2 个月）的指数历史记录，保留近期数据用于走势对比分析。
        """
        db = SessionLocal()
        try:
            logger.info("[指数清理] 开始清理 stock_index_history 表过期数据")
            deleted = IndexService.cleanup_history(db)
            logger.info(f"[指数清理] 完成，共删除 {deleted} 条 60 天前的记录")
        except Exception as e:
            logger.error(f"[指数清理] 执行失败: {e}")
        finally:
            db.close()

    # ── 通用写入逻辑 ──────────────────────────────────────────
    def _save_user_cache_for_date(self, db: Session, user_id: int, target_date: date) -> bool:
        """
        保存指定用户在指定日期的资产缓存

        Returns:
            True=成功写入, False=用户无有效订单跳过
        """
        valid_orders = db.query(Order).filter(
            Order.user_id == user_id,
            Order.is_active == 1,
            Order.status != "已取消",
        ).all()

        if not valid_orders:
            logger.debug(f"用户 {user_id} 无有效订单，跳过 {target_date} 缓存")
            return False

        total_assets = TotalAssetsCalculator.calculate_by_orders(
            db, user_id, valid_orders
        )
        DailyCacheService.save(db, user_id, total_assets)
        logger.info(
            f"用户 {user_id} 的 {target_date} 资产缓存已保存: ¥{total_assets:.2f}"
        )
        return True


# 全局调度器实例
asset_cache_scheduler = AssetCacheScheduler()


def start_scheduler():
    """启动调度器（用于应用启动时调用）"""
    asset_cache_scheduler.start()


def stop_scheduler():
    """停止调度器（用于应用关闭时调用）"""
    asset_cache_scheduler.stop()
