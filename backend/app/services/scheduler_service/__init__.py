"""
定时任务调度服务
提供定时任务调度和管理功能
"""
from .asset_cache_scheduler import AssetCacheScheduler, start_scheduler as start_asset_cache_scheduler, stop_scheduler as stop_asset_cache_scheduler
from .daily_snapshot_scheduler import DailySnapshotScheduler, start_daily_snapshot_scheduler, stop_daily_snapshot_scheduler
from .holding_snapshot_scheduler import HoldingSnapshotScheduler, start_holding_snapshot_scheduler, stop_holding_snapshot_scheduler
from app.services.exchange_rate_service.exchange_rate_scheduler import start_scheduler as start_exchange_rate_scheduler, stop_scheduler as stop_exchange_rate_scheduler
from app.services.dashboard_service.market_service.hpi_scheduler import start_scheduler as start_hpi_scheduler, stop_scheduler as stop_hpi_scheduler


class SchedulerManager:
    """定时任务管理器 - 统一管理所有定时任务"""

    @staticmethod
    def start_scheduler():
        """启动所有定时任务"""
        start_asset_cache_scheduler()
        start_daily_snapshot_scheduler()
        start_holding_snapshot_scheduler()
        start_exchange_rate_scheduler()
        start_hpi_scheduler()

    @staticmethod
    def stop_scheduler():
        """停止所有定时任务"""
        stop_asset_cache_scheduler()
        stop_daily_snapshot_scheduler()
        stop_holding_snapshot_scheduler()
        stop_exchange_rate_scheduler()
        stop_hpi_scheduler()


def start_scheduler():
    """启动所有定时任务（用于应用启动时调用）"""
    SchedulerManager.start_scheduler()


def stop_scheduler():
    """停止所有定时任务（用于应用关闭时调用）"""
    SchedulerManager.stop_scheduler()


__all__ = [
    'AssetCacheScheduler',
    'DailySnapshotScheduler',
    'HoldingSnapshotScheduler',
    'SchedulerManager',
    'start_scheduler',
    'stop_scheduler'
]
