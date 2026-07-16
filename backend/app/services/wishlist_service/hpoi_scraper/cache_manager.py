"""
cache_manager.py - 多级缓存管理器（第四层防护）

使用 MySQL 持久化缓存抓取结果，避免重复请求。
同一 URL 只抓一次，数据缓存 30 天（手办信息变化很小）。
raw_html 使用 gzip 压缩后存储，节省空间。
"""
import json
import gzip
import hashlib
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import and_

from app.models.hpoi_cache import HpoiScrapeCache, _now_cst


class CacheManager:
    """缓存管理器"""

    CACHE_TTL_DAYS = 30

    @staticmethod
    def _compress(data: str) -> bytes:
        return gzip.compress(data.encode("utf-8"))

    @staticmethod
    def _decompress(data: bytes) -> str:
        return gzip.decompress(data).decode("utf-8")

    @staticmethod
    def url_to_hash(url: str) -> str:
        return hashlib.sha256(url.encode("utf-8")).hexdigest()

    @staticmethod
    def get(db: Session, url: str) -> Optional[Dict[str, Any]]:
        """获取缓存（自动判断过期）"""
        url_hash = CacheManager.url_to_hash(url)
        now = _now_cst()
        record = db.query(HpoiScrapeCache).filter(
            and_(
                HpoiScrapeCache.url_hash == url_hash,
                HpoiScrapeCache.expires_at > now,
            )
        ).first()
        if record:
            raw_html_str = None
            if record.raw_html:
                try:
                    raw_html_str = CacheManager._decompress(record.raw_html)
                except Exception:
                    pass
            return {
                "url_hash": record.url_hash,
                "source_url": record.source_url,
                "raw_html": raw_html_str,
                "parsed_data": json.loads(record.parsed_data) if record.parsed_data else None,
                "cached_at": record.created_at.isoformat() if record.created_at else None,
            }
        return None

    @staticmethod
    def set(
        db: Session,
        url: str,
        raw_html: str,
        parsed_data: Dict[str, Any],
        ttl_days: int = None,
    ) -> HpoiScrapeCache:
        """写入缓存（raw_html 自动 gzip 压缩）"""
        url_hash = CacheManager.url_to_hash(url)
        ttl = ttl_days or CacheManager.CACHE_TTL_DAYS
        expires_at = _now_cst() + timedelta(days=ttl)

        # 删除旧缓存
        db.query(HpoiScrapeCache).filter(
            HpoiScrapeCache.url_hash == url_hash
        ).delete()

        compressed_html = CacheManager._compress(raw_html)
        record = HpoiScrapeCache(
            url_hash=url_hash,
            source_url=url,
            raw_html=compressed_html,
            parsed_data=json.dumps(parsed_data, ensure_ascii=False),
            expires_at=expires_at,
        )
        db.add(record)
        db.commit()
        db.refresh(record)
        return record

    @staticmethod
    def invalidate(db: Session, url: str):
        """主动失效缓存"""
        url_hash = CacheManager.url_to_hash(url)
        db.query(HpoiScrapeCache).filter(
            HpoiScrapeCache.url_hash == url_hash
        ).delete()
        db.commit()

    @staticmethod
    def clean_expired(db: Session):
        """清理过期缓存"""
        now = _now_cst()
        deleted = db.query(HpoiScrapeCache).filter(
            HpoiScrapeCache.expires_at <= now
        ).delete()
        db.commit()
        return deleted
