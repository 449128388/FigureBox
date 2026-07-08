"""
migration_add_hpoi_scrape_cache.py

创建 hpoi_scrape_cache 表，用于缓存 HPOI 抓取结果。
raw_html 使用 LargeBinary(gzip 压缩) 存储以避免 TEXT 65535 字节限制。
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from app.models.database import engine, Base
from app.models.hpoi_cache import HpoiScrapeCache

if __name__ == "__main__":
    # 删除旧表（如果列类型变更）
    try:
        HpoiScrapeCache.__table__.drop(engine)
        print("[OK] old hpoi_scrape_cache table dropped")
    except Exception:
        pass
    Base.metadata.create_all(engine)
    print("[OK] hpoi_scrape_cache table created")
