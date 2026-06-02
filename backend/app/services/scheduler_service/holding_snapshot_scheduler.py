"""
持仓快照定时任务调度器
每天北京时间23:30自动保存所有用户的持仓明细快照到holding_snapshots表
用于历史收益曲线计算
"""
import logging
from datetime import datetime, date
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from pytz import timezone
from sqlalchemy.orm import Session

from app.models.database import SessionLocal
from app.services.dashboard_service.assets_service.holding_snapshot_service import HoldingSnapshotService

logger = logging.getLogger(__name__)

# 北京时间时区
BEIJING_TZ = timezone('Asia/Shanghai')


class HoldingSnapshotScheduler:
    """持仓快照定时任务调度器"""

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
                func=self._daily_save_holding_snapshot,
                trigger=CronTrigger(hour=23, minute=30, timezone=BEIJING_TZ),
                id='daily_holding_snapshot_save',
                name='每日持仓快照保存（用于历史收益曲线计算）',
                replace_existing=True
            )
            self._scheduler.start()
            logger.info("持仓快照定时任务调度器已启动，每日北京时间23:30执行")

    def stop(self):
        """停止定时任务调度器"""
        if self._scheduler.running:
            self._scheduler.shutdown()
            logger.info("持仓快照定时任务调度器已停止")

    def _daily_save_holding_snapshot(self):
        """
        每日保存所有用户的持仓快照

        执行逻辑：
        1. 获取所有用户
        2. 对每个用户生成持仓明细快照
        3. 保存到holding_snapshots表和holding_snapshot_summaries表
        """
        db = SessionLocal()
        try:
            today = date.today()
            logger.info(f"开始执行每日持仓快照保存任务 - {datetime.now()}")

            # 使用服务类生成所有用户的持仓快照
            result = HoldingSnapshotService.generate_all_users_snapshot(db, today)

            logger.info(f"持仓快照保存完成："
                       f"总用户数={result['total_users']}, "
                       f"成功={result['success_count']}, "
                       f"失败={result['failed_count']}")

            # 记录失败的详情
            for detail in result['details']:
                if detail['status'] == 'failed':
                    logger.error(f"用户 {detail['username']}({detail['user_id']}) 快照生成失败: {detail.get('error', '未知错误')}")

        except Exception as e:
            logger.error(f"每日持仓快照保存任务执行失败: {str(e)}", exc_info=True)
        finally:
            db.close()

    def run_immediately(self):
        """
        立即执行一次持仓快照生成（用于手动触发）

        Returns:
            Dict: 执行结果
        """
        db = SessionLocal()
        try:
            today = date.today()
            logger.info(f"手动触发持仓快照保存任务 - {datetime.now()}")

            result = HoldingSnapshotService.generate_all_users_snapshot(db, today)

            logger.info(f"手动持仓快照保存完成："
                       f"总用户数={result['total_users']}, "
                       f"成功={result['success_count']}, "
                       f"失败={result['failed_count']}")

            return result

        except Exception as e:
            logger.error(f"手动持仓快照保存任务执行失败: {str(e)}", exc_info=True)
            return {
                "success": False,
                "error": str(e)
            }
        finally:
            db.close()


# 全局调度器实例
_holding_snapshot_scheduler = None


def get_holding_snapshot_scheduler():
    """获取持仓快照调度器实例（单例模式）"""
    global _holding_snapshot_scheduler
    if _holding_snapshot_scheduler is None:
        _holding_snapshot_scheduler = HoldingSnapshotScheduler()
    return _holding_snapshot_scheduler


def start_holding_snapshot_scheduler():
    """启动持仓快照定时任务调度器"""
    scheduler = get_holding_snapshot_scheduler()
    scheduler.start()
    return scheduler


def stop_holding_snapshot_scheduler():
    """停止持仓快照定时任务调度器"""
    global _holding_snapshot_scheduler
    if _holding_snapshot_scheduler is not None:
        _holding_snapshot_scheduler.stop()
        _holding_snapshot_scheduler = None
