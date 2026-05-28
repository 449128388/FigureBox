"""
定时任务调度服务
提供定时任务调度和管理功能
"""
from .asset_cache_scheduler import AssetCacheScheduler, start_scheduler as start_asset_cache_scheduler, stop_scheduler as stop_asset_cache_scheduler
from .daily_snapshot_scheduler import DailySnapshotScheduler, start_daily_snapshot_scheduler, stop_daily_snapshot_scheduler


class SchedulerManager:
    """定时任务管理器 - 统一管理所有定时任务"""
    
    @staticmethod
    def start_scheduler():
        """启动所有定时任务"""
        start_asset_cache_scheduler()
        start_daily_snapshot_scheduler()
    
    @staticmethod
    def stop_scheduler():
        """停止所有定时任务"""
        stop_asset_cache_scheduler()
        stop_daily_snapshot_scheduler()


def start_scheduler():
    """启动所有定时任务（用于应用启动时调用）"""
    SchedulerManager.start_scheduler()


def stop_scheduler():
    """停止所有定时任务（用于应用关闭时调用）"""
    SchedulerManager.stop_scheduler()


__all__ = [
    'AssetCacheScheduler', 
    'DailySnapshotScheduler',
    'SchedulerManager',
    'start_scheduler', 
    'stop_scheduler'
]
