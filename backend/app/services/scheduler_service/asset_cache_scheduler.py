"""
资产缓存定时任务调度器
每天晚上北京时间23:30自动保存所有用户的总资产到asset_value_cache表
"""
import logging
from datetime import datetime
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from pytz import timezone
from sqlalchemy.orm import Session

from app.models.database import SessionLocal
from app.models.user import User
from app.services.dashboard_service.assets_service import (
    TotalAssetsCalculator,
    DailyCacheService
)
from app.models.order import Order

logger = logging.getLogger(__name__)

# 北京时间时区
BEIJING_TZ = timezone('Asia/Shanghai')


class AssetCacheScheduler:
    """资产缓存定时任务调度器"""

    _instance = None
    _scheduler = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if self._scheduler is None:
            # 使用北京时间时区
            self._scheduler = BackgroundScheduler(timezone=BEIJING_TZ)

    def start(self):
        """启动定时任务调度器"""
        if not self._scheduler.running:
            # 添加每日北京时间23:30执行的任务
            self._scheduler.add_job(
                func=self._daily_save_asset_cache,
                trigger=CronTrigger(hour=23, minute=30, timezone=BEIJING_TZ),
                id='daily_asset_cache_save',
                name='每日总资产缓存保存',
                replace_existing=True
            )
            self._scheduler.start()
            logger.info("资产缓存定时任务调度器已启动，每日北京时间23:30执行")

    def stop(self):
        """停止定时任务调度器"""
        if self._scheduler.running:
            self._scheduler.shutdown()
            logger.info("资产缓存定时任务调度器已停止")

    def _daily_save_asset_cache(self):
        """
        每日保存所有用户的总资产缓存

        执行逻辑：
        1. 获取所有用户
        2. 对每个用户计算当前总资产
        3. 保存到asset_value_cache表
        """
        db = SessionLocal()
        try:
            logger.info(f"开始执行每日总资产缓存保存任务 - {datetime.now()}")

            # 获取所有用户
            users = db.query(User).all()
            logger.info(f"共找到 {len(users)} 个用户")

            for user in users:
                try:
                    self._save_user_asset_cache(db, user.id)
                except Exception as e:
                    logger.error(f"保存用户 {user.id} 的资产缓存失败: {e}")
                    continue

            logger.info(f"每日总资产缓存保存任务完成 - {datetime.now()}")

        except Exception as e:
            logger.error(f"执行每日总资产缓存保存任务失败: {e}")
        finally:
            db.close()

    def _save_user_asset_cache(self, db: Session, user_id: int):
        """
        保存指定用户的总资产缓存

        Args:
            db: 数据库会话
            user_id: 用户ID
        """
        # 获取用户的所有有效订单
        valid_orders = db.query(Order).filter(
            Order.user_id == user_id,
            Order.is_active == 1,
            Order.status != "已取消"
        ).all()

        if not valid_orders:
            logger.debug(f"用户 {user_id} 没有有效订单，跳过保存")
            return

        # 计算总资产（基于已完成订单，扣除已出售数量）
        total_assets = TotalAssetsCalculator.calculate_by_orders(
            db, user_id, valid_orders
        )

        # 保存到缓存表
        DailyCacheService.save(db, user_id, total_assets)

        logger.info(f"用户 {user_id} 的资产缓存已保存: ¥{total_assets:.2f}")


# 全局调度器实例
asset_cache_scheduler = AssetCacheScheduler()


def start_scheduler():
    """启动调度器（用于应用启动时调用）"""
    asset_cache_scheduler.start()


def stop_scheduler():
    """停止调度器（用于应用关闭时调用）"""
    asset_cache_scheduler.stop()
