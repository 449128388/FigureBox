"""
hpoi_cache.py - HPOI 抓取缓存模型

存储抓取到的 HTML 和解析数据，避免重复请求。
缓存有效期默认 30 天。
"""
from sqlalchemy import Column, Integer, String, Text, LargeBinary, DateTime, Index
from datetime import datetime
from app.models.database import Base


class HpoiScrapeCache(Base):
    """HPOI 抓取缓存"""

    __tablename__ = "hpoi_scrape_cache"

    id = Column(Integer, primary_key=True, autoincrement=True)
    url_hash = Column(String(64), nullable=False, unique=True, index=True, comment="URL 的 SHA256 哈希")
    source_url = Column(String(2048), nullable=False, comment="原始 URL")
    raw_html = Column(LargeBinary, nullable=True, comment="抓取的原始 HTML（gzip 压缩后）")
    parsed_data = Column(Text, nullable=True, comment="解析后的 JSON 数据")
    created_at = Column(DateTime, default=datetime.utcnow, comment="创建时间")
    expires_at = Column(DateTime, nullable=False, comment="过期时间")

    __table_args__ = (
        Index("idx_url_hash_expires", "url_hash", "expires_at"),
    )
