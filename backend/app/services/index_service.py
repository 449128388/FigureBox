"""
指数服务模块
提供股票指数相关的业务逻辑
"""
from datetime import datetime, date
from typing import Dict, Optional, Any
import requests
import random
import time
import re
import threading
from sqlalchemy.orm import Session
from sqlalchemy import desc

from app.models.asset import StockIndexCache, StockIndexHistory


# 全局锁，用于防止同一秒内重复获取同一指数数据
_index_fetch_locks: Dict[str, bool] = {}
_index_fetch_locks_lock = threading.Lock()

# 请求头常量
REQUEST_HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36 QQBrowser/12.0',
    'Referer': 'https://stock.finance.qq.com/',
    'Accept': '*/*',
    'Accept-Encoding': 'gzip, deflate, br',
    'Accept-Language': 'zh-CN,zh;q=0.9',
    'Connection': 'keep-alive'
}

# 指数配置
INDEX_CONFIG = {
    "sh000001": {"name": "上证指数", "default_value": 3200},
    "sh000300": {"name": "沪深300", "default_value": 4000}
}


class IndexService:
    """指数服务类"""
    
    DAILY_REQUEST_LIMIT = 6
    CACHE_DURATION_HOURS = 3
    
    @staticmethod
    def _fetch_index_from_qq(index_code: str) -> Optional[Dict[str, Any]]:
        """从腾讯财经获取指数数据"""
        url = f"https://qt.gtimg.cn/q={index_code}"
        config = INDEX_CONFIG[index_code]
        
        try:
            time.sleep(random.uniform(3, 8))
            response = requests.get(url, headers=REQUEST_HEADERS, timeout=30)
            response.encoding = 'gbk'
            
            if response.status_code == 200:
                match = re.search(rf'v_{index_code}="([^"]+)"', response.text)
                if match:
                    parts = match.group(1).split('~')
                    if len(parts) >= 6:
                        current, prev = float(parts[3]), float(parts[4])
                        change = current - prev
                        return {
                            "index_code": index_code,
                            "index_name": config["name"],
                            "current_value": current,
                            "change_value": round(change, 2),
                            "change_percentage": round((change / prev * 100) if prev > 0 else 0, 2),
                            "prev_close": prev,
                            "open_value": float(parts[5]) if len(parts) > 5 else None
                        }
        except Exception as e:
            print(f"获取{config['name']}失败: {e}")
        return None
    
    @classmethod
    def _check_need_fetch(cls, cache: Optional[StockIndexCache], today: date) -> bool:
        """检查是否需要获取新数据"""
        if not cache or cache.request_date != today:
            return True
        if cache.request_count >= cls.DAILY_REQUEST_LIMIT:
            return False
        return (datetime.now() - cache.updated_at).total_seconds() > cls.CACHE_DURATION_HOURS * 3600
    
    @classmethod
    def _get_cached_response(cls, cache: StockIndexCache) -> Dict[str, Any]:
        """从缓存构建响应"""
        return {
            "index_code": cache.index_code,
            "index_name": cache.index_name,
            "current_value": cache.current_value,
            "change_value": cache.change_value,
            "change_percentage": cache.change_percentage
        }
    
    @classmethod
    def _save_index_data(cls, db: Session, data: Dict, cache: Optional[StockIndexCache], today: date) -> None:
        """保存指数数据"""
        now = datetime.now()
        db.add(StockIndexHistory(
            index_code=data["index_code"], index_name=data["index_name"],
            current_value=data["current_value"], change_value=data["change_value"],
            change_percentage=data["change_percentage"], prev_close=data.get("prev_close"),
            open_value=data.get("open_value"), request_time=now, request_date=today
        ))
        
        if cache:
            cache.current_value, cache.change_value = data["current_value"], data["change_value"]
            cache.change_percentage, cache.updated_at = data["change_percentage"], now
            cache.request_count, cache.request_date = cache.request_count + 1, today
        else:
            db.add(StockIndexCache(
                index_code=data["index_code"], index_name=data["index_name"],
                current_value=data["current_value"], change_value=data["change_value"],
                change_percentage=data["change_percentage"], request_count=1, request_date=today
            ))
        db.commit()
    
    @classmethod
    def _get_cached_index(cls, db: Session, index_code: str) -> Dict[str, Any]:
        """获取缓存的指数数据"""
        today = date.today()
        config = INDEX_CONFIG[index_code]
        cache = db.query(StockIndexCache).filter(StockIndexCache.index_code == index_code).first()
        
        if cls._check_need_fetch(cache, today) and (not cache or cache.request_count < cls.DAILY_REQUEST_LIMIT):
            lock_key = f"{index_code}_{datetime.now().strftime('%Y%m%d%H%M%S')}"
            
            with _index_fetch_locks_lock:
                if lock_key in _index_fetch_locks:
                    time.sleep(0.5)
                    db.refresh(cache)
                    return cls._get_cached_response(cache) if cache else cls._default_response(index_code)
                _index_fetch_locks[lock_key] = True
            
            try:
                data = cls._fetch_index_from_qq(index_code)
                if data:
                    cls._save_index_data(db, data, cache, today)
                    return data
            finally:
                with _index_fetch_locks_lock:
                    _index_fetch_locks.pop(lock_key, None)
        
        if cache:
            return cls._get_cached_response(cache)
        return cls._default_response(index_code)
    
    @staticmethod
    def _default_response(index_code: str) -> Dict[str, Any]:
        """获取默认响应"""
        config = INDEX_CONFIG[index_code]
        return {
            "index_code": index_code, "index_name": config["name"],
            "current_value": config["default_value"], "change_value": 0, "change_percentage": 0
        }
    
    @classmethod
    def get_cached_sh_index(cls, db: Session) -> Dict[str, Any]:
        """获取上证指数"""
        return cls._get_cached_index(db, "sh000001")
    
    @classmethod
    def get_cached_hs300_index(cls, db: Session) -> Dict[str, Any]:
        """获取沪深300指数"""
        return cls._get_cached_index(db, "sh000300")
    
    @classmethod
    def get_index_comparison_data(cls, db: Session, index_code: str) -> Optional[Dict[str, Any]]:
        """获取指数对比数据"""
        records = db.query(StockIndexHistory).filter(
            StockIndexHistory.index_code == index_code
        ).order_by(desc(StockIndexHistory.request_time)).limit(2).all()
        
        if not records:
            return None
        if len(records) == 1:
            return {"current_value": records[0].current_value, "change_value": 0, 
                    "change_percentage": 0, "has_history": False, "trend": "flat"}
        
        latest, prev = records[0], records[1]
        change = latest.current_value - prev.current_value
        pct = (change / prev.current_value * 100) if prev.current_value > 0 else 0
        trend = "up" if change > 0 else ("down" if change < 0 else "flat")
        
        return {
            "current_value": latest.current_value, "change_value": round(change, 2),
            "change_percentage": round(pct, 2), "has_history": True, "trend": trend
        }
