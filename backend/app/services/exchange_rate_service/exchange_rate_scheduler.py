"""
exchange_rate_scheduler.py - 汇率定时任务调度器

功能说明：
- 定时从中国外汇交易中心获取最新汇率
- 遵循中国货币网中间价政策：
  1. 仅工作日更新（周一至周五），周末/法定节假日无新数据
  2. 每日发布时点：北京时间 09:25
  3. 09:25 更新后全天不再变动，直到下个交易日 09:25
- 无并发请求
"""

import logging
from datetime import datetime, date, time
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from pytz import timezone
from sqlalchemy.orm import Session

from app.models.database import SessionLocal
from app.services.exchange_rate_service.exchange_rate_service import ExchangeRateService

logger = logging.getLogger(__name__)

BEIJING_TZ = timezone('Asia/Shanghai')

# 2026 年中国法定节假日（仅包含占用工作日的假期）
CHINESE_HOLIDAYS_2026 = {
    date(2026, 1, 1), date(2026, 1, 2), date(2026, 1, 3),
    date(2026, 2, 16), date(2026, 2, 17), date(2026, 2, 18),
    date(2026, 2, 19), date(2026, 2, 20), date(2026, 2, 21), date(2026, 2, 22),
    date(2026, 4, 4), date(2026, 4, 5), date(2026, 4, 6),
    date(2026, 5, 1), date(2026, 5, 2), date(2026, 5, 3),
    date(2026, 6, 19), date(2026, 6, 20), date(2026, 6, 21),
    date(2026, 9, 27), date(2026, 9, 28), date(2026, 9, 29),
    date(2026, 10, 1), date(2026, 10, 2), date(2026, 10, 3),
    date(2026, 10, 4), date(2026, 10, 5), date(2026, 10, 6), date(2026, 10, 7),
}


def is_trading_day(check_date: date = None) -> bool:
    if check_date is None:
        check_date = date.today()
    if check_date.weekday() >= 5:
        return False
    if check_date in CHINESE_HOLIDAYS_2026:
        return False
    return True


class ExchangeRateScheduler:
    """汇率定时任务调度器"""

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
        """启动定时任务调度器"""
        if not self._scheduler.running:
            self._scheduler.add_job(
                func=refresh_exchange_rates,
                trigger=CronTrigger(
                    day_of_week='mon-fri',
                    hour=9,
                    minute=25,
                    timezone=BEIJING_TZ
                ),
                id="exchange_rate_refresh",
                name="汇率定时刷新（工作日 09:25）",
                replace_existing=True
            )
            self._scheduler.start()
            logger.info("汇率定时任务调度器已启动（工作日 09:25 执行）")

    def stop(self):
        if self._scheduler and self._scheduler.running:
            self._scheduler.shutdown(wait=False)
            logger.info("汇率定时任务调度器已停止")


# 全局单例
exchange_rate_scheduler = ExchangeRateScheduler()

PUBLISH_HOUR = 9
PUBLISH_MINUTE = 25


def refresh_exchange_rates():
    """执行汇率刷新任务（定时任务回调）"""
    today = date.today()
    if not is_trading_day(today):
        logger.info(f"今日({today})非交易日，跳过汇率刷新")
        return

    now = datetime.now(BEIJING_TZ)
    publish_time = time(PUBLISH_HOUR, PUBLISH_MINUTE)
    if now.time() < publish_time:
        logger.info(f"当前时间 {now.strftime('%H:%M')} 未到 09:25 发布时点，跳过汇率刷新")
        return

    logger.info("定时任务：开始刷新汇率数据...")
    db: Session = SessionLocal()
    try:
        success = ExchangeRateService.refresh_from_api(db)
        if success:
            logger.info("汇率数据刷新成功（交易日 09:25 发布）")
        else:
            logger.warning("汇率数据刷新未成功（可能当日已获取）")
    except Exception as e:
        logger.error(f"定时任务刷新汇率失败: {e}")
    finally:
        db.close()


def start_scheduler():
    """启动汇率定时任务调度器"""
    exchange_rate_scheduler.start()
    today = date.today()
    if is_trading_day(today):
        now = datetime.now(BEIJING_TZ)
        publish_time = time(PUBLISH_HOUR, PUBLISH_MINUTE)
        if now.time() >= publish_time:
            logger.info("当前为交易日且已过 09:25，立即执行首次汇率获取")
            refresh_exchange_rates()
        else:
            logger.info(f"当前为交易日但未到 09:25（当前 {now.strftime('%H:%M')}），等待定时触发")
    else:
        logger.info(f"今日({today})非交易日，跳过首次汇率获取")


def stop_scheduler():
    exchange_rate_scheduler.stop()
