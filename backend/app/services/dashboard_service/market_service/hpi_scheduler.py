"""
HPI 定时任务调度器 - 每日北京时间 00:30 跑批计算

功能说明：
- 遍历所有用户，为每个用户计算当日 HPI
- 写入 hpi_daily 和 hpi_components 表
"""

import logging
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from pytz import timezone
from sqlalchemy.orm import Session

from app.models.database import SessionLocal
from app.models.user import User
from app.services.dashboard_service.market_service.hpi_service import HPIService

logger = logging.getLogger(__name__)

BEIJING_TZ = timezone('Asia/Shanghai')


class HPIScheduler:
    """HPI 定时任务调度器"""

    _instance = None
    _scheduler = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if self._scheduler is None:
            self._scheduler = BackgroundScheduler(timezone=BEIJING_TZ)

    def start(self):
        if not self._scheduler.running:
            self._scheduler.add_job(
                func=run_hpi_batch,
                trigger=CronTrigger(hour=0, minute=30, timezone=BEIJING_TZ),
                id="hpi_daily_batch",
                name="HPI 每日跑批（00:30）",
                replace_existing=True
            )
            self._scheduler.start()
            logger.info("HPI 定时任务调度器已启动（每日 00:30 跑批）")
            # 启动后立即执行一次全量跑批，确保首次部署/重启后即有数据
            logger.info("HPI 定时任务：启动后立即执行首次跑批...")
            import threading
            threading.Thread(target=run_hpi_batch, daemon=True).start()

    def stop(self):
        if self._scheduler and self._scheduler.running:
            self._scheduler.shutdown(wait=False)
            logger.info("HPI 定时任务调度器已停止")


hpi_scheduler = HPIScheduler()


def run_hpi_batch():
    """执行全量 HPI 跑批"""
    logger.info("HPI 跑批任务：开始遍历所有用户...")
    db: Session = SessionLocal()
    try:
        users = db.query(User).filter(User.is_active == True).all()
        success_count = 0
        for user in users:
            try:
                if HPIService.run_daily_batch(db, user.id):
                    success_count += 1
            except Exception as e:
                logger.error(f"HPI 跑批失败 user_id={user.id}: {e}")
        logger.info(f"HPI 跑批完成：共 {len(users)} 人，成功 {success_count} 人")
    except Exception as e:
        logger.error(f"HPI 跑批任务异常: {e}")
    finally:
        db.close()


def start_scheduler():
    hpi_scheduler.start()


def stop_scheduler():
    hpi_scheduler.stop()
