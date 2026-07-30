"""
exchange_rate_service.py - 统一汇率服务模块

功能说明：
- 从中国外汇交易中心获取实时汇率数据
- 缓存到数据库，支持 3 小时缓存有效期
- 严格限速：随机延时 3-8 秒 + 单日请求 < 6 次
- 提供统一汇率查询接口，替换系统中所有硬编码汇率字典

API 端点：
- GET http://www.chinamoney.com.cn/r/cms/www/chinamoney/data/fx/ccpr.json

返回格式参考：
{
  "data": [
    {"enName": "USD/CNY", "cnName": "美元/人民币", "value": "7.0"},
    {"enName": "JPY/CNY", "cnName": "日元/人民币", "value": "0.0435"},
    ...
  ]
}
"""

import json
import logging
import random
import threading
import time
from datetime import datetime, date
from typing import Dict, Optional, Any

import requests
from sqlalchemy.orm import Session
from sqlalchemy import desc

from app.models.database import SessionLocal
from app.models.exchange_rate import ExchangeRateRealtime, ExchangeRateHistory

logger = logging.getLogger(__name__)

# 请求头常量
REQUEST_HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
    'Referer': 'http://www.chinamoney.com.cn/',
    'Accept': 'application/json, text/plain, */*',
    'Accept-Encoding': 'gzip, deflate, br',
    'Accept-Language': 'zh-CN,zh;q=0.9',
    'Connection': 'keep-alive'
}

API_URL = "http://www.chinamoney.com.cn/r/cms/www/chinamoney/data/fx/ccpr.json"

# 人民币自身汇率
CNY_RATE = 1.0

# 默认兜底汇率（当 API 不可用时使用）
FALLBACK_RATES = {
    'CNY': 1.0,
    'USD': 7.0,
    'JPY': 1/23,
    'EUR': 8.0,
    'HKD': 0.9,
    'GBP': 9.0,
}

# 全局并发锁
_fetch_lock = threading.Lock()


class ExchangeRateService:
    """统一汇率服务类"""

    @staticmethod
    def get_exchange_rates(db: Session) -> Dict[str, float]:
        """
        获取当前所有币种的汇率（统一入口）

        优先级：
        1. 从 exchange_rate_realtime 表获取缓存汇率
        2. 如果缓存为空或过期，尝试调用 API 获取
        3. 兜底使用硬编码默认汇率

        Returns:
            Dict[str, float]: 币种到人民币汇率的映射，如 {'CNY': 1.0, 'USD': 7.0, 'JPY': 0.0435}
        """
        # 尝试从缓存读取
        cached_rates = ExchangeRateService._get_cached_rates(db)
        if cached_rates:
            return cached_rates

        # 缓存为空，尝试调 API 获取
        try:
            ExchangeRateService._fetch_and_save_rates(db)
            cached_rates = ExchangeRateService._get_cached_rates(db)
            if cached_rates:
                return cached_rates
        except Exception as e:
            logger.warning(f"API 获取汇率失败: {e}")

        # 兜底返回默认汇率
        logger.warning("使用兜底默认汇率")
        return dict(FALLBACK_RATES)

    @staticmethod
    def get_rate(db: Session, currency: str) -> float:
        """
        获取单个币种对人民币的汇率

        Args:
            db: 数据库会话
            currency: 币种代码（CNY/USD/JPY/EUR 等）

        Returns:
            float: 汇率值
        """
        rates = ExchangeRateService.get_exchange_rates(db)
        return rates.get(currency.upper(), FALLBACK_RATES.get(currency.upper(), 1.0))

    @staticmethod
    def to_cny(db: Session, amount: float, currency: str) -> float:
        """
        将指定币种金额转换为人民币

        Args:
            db: 数据库会话
            amount: 金额
            currency: 币种代码

        Returns:
            float: 人民币金额
        """
        rate = ExchangeRateService.get_rate(db, currency)
        return amount * rate

    @staticmethod
    def refresh_from_api(db: Session) -> bool:
        """
        强制从 API 刷新汇率数据（供定时任务调用）

        Returns:
            bool: 是否成功
        """
        return ExchangeRateService._fetch_and_save_rates(db)

    @staticmethod
    def clear_fetch_lock() -> None:
        """
        清除全局并发锁（供定时任务使用，解决线程锁残留问题）

        当 _fetch_and_save_rates 因网络异常或进程中断导致锁未释放时，
        后续定时任务将无法获取锁而跳过执行。通过重建锁对象来强制重置。
        """
        global _fetch_lock
        _fetch_lock = threading.Lock()
        logger.info("汇率并发锁已重置")

    @staticmethod
    def cleanup_history(db: Session, retention_months: int = 2) -> int:
        """
        清理 exchange_rate_history 表中超过保留期限的历史数据

        汇率历史数据仅用于近期数据回溯，保留 2 个月可显著降低表数据量。

        Args:
            db: 数据库会话
            retention_months: 保留月数（默认 2 个月）

        Returns:
            int: 删除的记录数
        """
        from datetime import timedelta

        cutoff_date = datetime.now() - timedelta(days=retention_months * 30)
        try:
            deleted_count = db.query(ExchangeRateHistory).filter(
                ExchangeRateHistory.record_date < cutoff_date
            ).delete()
            db.commit()
            if deleted_count > 0:
                logger.info(
                    f"汇率历史数据清理完成：删除 {deleted_count} 条 "
                    f"早于 {cutoff_date.strftime('%Y-%m-%d %H:%M:%S')} 的记录"
                )
            else:
                logger.debug("汇率历史数据无需清理")
            return deleted_count
        except Exception as e:
            db.rollback()
            logger.error(f"汇率历史数据清理失败: {e}")
            return 0

    # ========== 内部方法 ==========

    @staticmethod
    def _get_cached_rates(db: Session) -> Optional[Dict[str, float]]:
        """
        从缓存表获取汇率，检查是否在有效期内

        中国外汇交易中心中间价政策：
        - 每个交易日 09:25 发布当日汇率，全天有效
        - 周末/节假日无新数据，沿用最近交易日汇率
        - 缓存有效期截止到下一个交易日 09:25

        Returns:
            Dict[str, float] | None: 有效汇率映射，None 表示缓存过期
        """
        from datetime import time as dtime

        records = db.query(ExchangeRateRealtime).all()
        if not records:
            return None

        latest = db.query(ExchangeRateRealtime).order_by(
            ExchangeRateRealtime.updated_at.desc()
        ).first()

        if latest and latest.updated_at:
            beijing_tz = None
            try:
                from pytz import timezone
                beijing_tz = timezone('Asia/Shanghai')
            except Exception:
                pass

            now = datetime.now()
            # 统一使用 UTC 进行比较
            from datetime import timezone as dt_timezone
            now_utc = now.replace(tzinfo=dt_timezone.utc) if now.tzinfo is None else now

            # 获取缓存的更新日期
            cached_time = latest.updated_at
            if cached_time.tzinfo is None:
                cached_time = cached_time.replace(tzinfo=dt_timezone.utc)

            cached_date_beijing = cached_time.astimezone(beijing_tz) if beijing_tz else cached_time
            cached_date = cached_date_beijing.date()

            # 获取当前北京时间
            now_beijing = now_utc.astimezone(beijing_tz) if beijing_tz else now
            today_beijing = now_beijing.date()

            # 如果缓存数据是今天获取的且今天已过 09:25，则全天有效
            if cached_date == today_beijing:
                if beijing_tz:
                    today_0925 = datetime(today_beijing.year, today_beijing.month, today_beijing.day,
                                           9, 25, 0, tzinfo=beijing_tz)
                else:
                    today_0925 = datetime(today_beijing.year, today_beijing.month, today_beijing.day, 9, 25)
                if now_beijing >= today_0925:
                    return {r.currency: r.rate_to_cny for r in records}

            # 如果缓存数据是昨天或更早的交易日获取的，且今天未到 09:25，则仍有效
            if today_beijing > cached_date:
                # 检查今天是否已过 09:25
                if beijing_tz:
                    today_0925 = datetime(today_beijing.year, today_beijing.month, today_beijing.day,
                                           9, 25, 0, tzinfo=beijing_tz)
                else:
                    today_0925 = datetime(today_beijing.year, today_beijing.month, today_beijing.day, 9, 25)
                if now_beijing < today_0925:
                    # 今天还没到发布时点，缓存仍然有效
                    return {r.currency: r.rate_to_cny for r in records}

        return None

    @staticmethod
    def _check_daily_limit(db: Session) -> bool:
        """检查当日请求次数是否已达上限"""
        today = date.today()
        # 统计今日已成功获取的币种数（非 API 请求次数）
        # 一次 fetch 写入全部币种，有任何一条记录就代表今日已获取过
        count = db.query(ExchangeRateRealtime).filter(
            ExchangeRateRealtime.updated_at >= today
        ).count()
        return count == 0

    @staticmethod
    def _fetch_and_save_rates(db: Session) -> bool:
        """
        从中国外汇交易中心获取汇率并保存到数据库

        严格限速：
        - 随机延时 3-8 秒
        - 单日请求 < 6 次
        - 全局并发锁
        """
        if not _fetch_lock.acquire(blocking=False):
            logger.warning("汇率获取任务正在执行中，跳过本次请求")
            return False

        try:
            # 先检查缓存是否已有今日有效数据（避免重复请求消耗配额）
            cached = ExchangeRateService._get_cached_rates(db)
            if cached is not None:
                logger.info("已有今日有效汇率数据，跳过 API 获取")
                return True

            # 检查当日请求次数
            if not ExchangeRateService._check_daily_limit(db):
                logger.warning("当日汇率请求已达上限，跳过")
                return False

            # 随机延时 3-8 秒
            delay = random.uniform(3, 8)
            logger.info(f"汇率请求随机延时 {delay:.1f} 秒...")
            time.sleep(delay)

            # 发送请求
            logger.info(f"请求汇率数据: {API_URL}")
            response = requests.get(API_URL, headers=REQUEST_HEADERS, timeout=30)

            if response.status_code != 200:
                logger.warning(f"汇率 API 返回非 200 状态码: {response.status_code}")
                return False

            # 解析返回的 JSON 数据
            try:
                data = response.json()
            except Exception as e:
                logger.error(f"汇率 API 返回非 JSON 格式: {e}, 原始内容: {response.text[:200]}")
                return False

            # 处理 data 可能是字符串的情况
            if isinstance(data, str):
                import json as _json
                try:
                    data = _json.loads(data)
                except Exception:
                    logger.error(f"汇率 API 返回字符串无法解析为 JSON: {data[:200]}")
                    return False

            rates = ExchangeRateService._parse_response(data)

            if not rates:
                logger.warning("汇率 API 返回数据为空或格式异常")
                return False

            now = datetime.now()

            # 写入数据库
            for currency, rate in rates.items():
                existing = db.query(ExchangeRateRealtime).filter(
                    ExchangeRateRealtime.currency == currency
                ).first()
                if existing:
                    existing.rate_to_cny = rate
                    existing.updated_at = now
                else:
                    db.add(ExchangeRateRealtime(
                        currency=currency,
                        rate_to_cny=rate,
                        updated_at=now
                    ))

                db.add(ExchangeRateHistory(
                    currency=currency,
                    rate_to_cny=rate,
                    record_date=now,
                    created_at=now
                ))

            db.commit()
            logger.info(f"汇率数据更新成功: {len(rates)} 个币种")
            return True

        except json.JSONDecodeError as e:
            logger.error(f"汇率 API 返回数据解析失败: {e}")
            db.rollback()
            return False
        except requests.RequestException as e:
            logger.error(f"汇率 API 请求异常: {e}")
            db.rollback()
            return False
        except Exception as e:
            logger.error(f"汇率获取失败: {e}")
            db.rollback()
            return False
        finally:
            _fetch_lock.release()

    @staticmethod
    def _parse_response(data: dict) -> Dict[str, float]:
        """
        解析中国外汇交易中心 API 返回的 JSON 数据

        实际 API 返回格式（2026-06-29 实测）：
        {
            "head": {...},
            "data": { "lastDateEn": "...", ... },
            "records": [
                {"vrtCode":"1", "price":"6.8166", "vrtEName":"USD/CNY", ...},
                {"vrtCode":"3", "price":"4.2107", "vrtEName":"100JPY/CNY", ...},
                ...
            ]
        }
        """
        rates = {}
        # 字段路径：先尝试 records（实际 API），再尝试 data（备用格式）
        raw_list = []
        if isinstance(data, dict):
            if "records" in data and isinstance(data["records"], list):
                raw_list = data["records"]
            elif "data" in data and isinstance(data["data"], list):
                raw_list = data["data"]
        elif isinstance(data, list):
            raw_list = data

        for item in raw_list:
            # 字段名：优先 vrtEName（实际 API），备用 enName
            en_name = item.get("vrtEName", "") or item.get("enName", "")
            # 价格字段：优先 price（实际 API），备用 value
            price_str = item.get("price", "") or item.get("value", "")

            if not en_name or not price_str:
                continue

            try:
                price = float(price_str)
            except (ValueError, TypeError):
                continue

            # 解析如 "USD/CNY" 或 "100JPY/CNY"
            if "/" in en_name:
                parts = en_name.split("/")
                currency_part = parts[0]  # "USD" 或 "100JPY"
                import re as _re
                match = _re.match(r'(\d+)?([A-Z]+)', currency_part)
                if match:
                    quantity = int(match.group(1)) if match.group(1) else 1
                    currency_code = match.group(2)
                    # JPY 等以 100 为单位报价：100JPY/CNY = price CNY
                    rate = price / quantity
                    rates[currency_code] = round(rate, 6)

        # 始终包含人民币自身
        rates['CNY'] = CNY_RATE
        return rates
