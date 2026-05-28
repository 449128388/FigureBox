"""
资产日涨跌快照定时任务调度器
每天北京时间00:05自动保存所有用户的总资产快照到user_asset_snapshots表
用于明日计算日涨跌的对比基准
"""
import logging
from datetime import datetime, date
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from pytz import timezone
from sqlalchemy.orm import Session

from app.models.database import SessionLocal
from app.models.user import User
from app.services.dashboard_service.assets_service.daily_change_service import DailyChangeService

logger = logging.getLogger(__name__)

# 北京时间时区
BEIJING_TZ = timezone('Asia/Shanghai')


class DailySnapshotScheduler:
    """资产日涨跌快照定时任务调度器"""

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
            # 添加每日北京时间00:05执行的任务
            self._scheduler.add_job(
                func=self._daily_save_asset_snapshot,
                trigger=CronTrigger(hour=0, minute=5, timezone=BEIJING_TZ),
                id='daily_asset_snapshot_save',
                name='每日资产快照保存（用于日涨跌计算）',
                replace_existing=True
            )
            self._scheduler.start()
            logger.info("资产日涨跌快照定时任务调度器已启动，每日北京时间00:05执行")

    def stop(self):
        """停止定时任务调度器"""
        if self._scheduler.running:
            self._scheduler.shutdown()
            logger.info("资产日涨跌快照定时任务调度器已停止")

    def _daily_save_asset_snapshot(self):
        """
        每日保存所有用户的资产快照

        执行逻辑：
        1. 获取所有用户
        2. 对每个用户计算当前总资产
        3. 保存到user_asset_snapshots表（snapshot_date = 今天）
           这样明天计算日涨跌时，今天的数据就是"昨日总资产"
        """
        db = SessionLocal()
        try:
            today = date.today()
            logger.info(f"开始执行每日资产快照保存任务 - {datetime.now()}")

            # 获取所有用户
            users = db.query(User).all()
            logger.info(f"共找到 {len(users)} 个用户")

            for user in users:
                try:
                    self._save_user_asset_snapshot(db, user.id, today)
                except Exception as e:
                    logger.error(f"保存用户 {user.id} 的资产快照失败: {e}")
                    continue

            logger.info(f"每日资产快照保存任务完成 - {datetime.now()}")

        except Exception as e:
            logger.error(f"执行每日资产快照保存任务失败: {e}")
        finally:
            db.close()

    def _save_user_asset_snapshot(self, db: Session, user_id: int, snapshot_date: date):
        """
        保存指定用户的资产快照

        Args:
            db: 数据库会话
            user_id: 用户ID
            snapshot_date: 快照日期
        """
        try:
            # 计算当前总资产
            total_assets = DailyChangeService.calculate_total_assets_from_transactions(db, user_id)

            # 创建或更新快照
            DailyChangeService.create_snapshot(
                db=db,
                user_id=user_id,
                snapshot_date=snapshot_date,
                total_asset=total_assets,
                total_cost=0
            )

            logger.info(f"用户 {user_id} 的资产快照已保存: {total_assets}")

        except Exception as e:
            logger.error(f"保存用户 {user_id} 的资产快照时出错: {e}")
            raise


# 全局调度器实例
daily_snapshot_scheduler = DailySnapshotScheduler()


def start_daily_snapshot_scheduler():
    """启动日涨跌快照定时任务（用于应用启动时调用）"""
    daily_snapshot_scheduler.start()


def stop_daily_snapshot_scheduler():
    """停止日涨跌快照定时任务（用于应用关闭时调用）"""
    daily_snapshot_scheduler.stop()
