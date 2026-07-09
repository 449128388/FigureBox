"""
migration_add_hpoi_scrape_cache.py

创建或更新 hpoi_scrape_cache 表，用于缓存 HPOI 抓取结果。
- 首次运行：直接创建表
- 升级运行：如果 raw_html 仍为 text 类型，ALTER 为 blob（gzip 压缩兼容）
- 幂等：不会 DROP 已有数据
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from sqlalchemy import inspect, text as sa_text
from app.models.database import engine, Base
from app.models.hpoi_cache import HpoiScrapeCache

if __name__ == "__main__":
    inspector = inspect(engine)
    table_name = HpoiScrapeCache.__tablename__

    if not inspector.has_table(table_name):
        # 首次创建
        Base.metadata.create_all(engine)
        print(f"[OK] {table_name} table created")
    else:
        # 检查 raw_html 列类型
        columns = {c["name"]: c for c in inspector.get_columns(table_name)}
        raw_col = columns.get("raw_html")
        if raw_col:
            col_type = str(raw_col.get("type", ""))
            # 如果旧类型是 TEXT，改为 LargeBinary（兼容 gzip）
            if "TEXT" in col_type.upper():
                with engine.connect() as conn:
                    conn.execute(sa_text(
                        "ALTER TABLE hpoi_scrape_cache MODIFY raw_html blob "
                        "COMMENT '抓取的原始 HTML（gzip 压缩后）'"
                    ))
                    conn.commit()
                print(f"[OK] {table_name}.raw_html upgraded: TEXT -> blob")
            else:
                print(f"[OK] {table_name}.raw_html already blob, skipped")
        else:
            print(f"[WARN] {table_name} has no raw_html column, skipping")

        # 确保其余列存在（新加的列）
        Base.metadata.create_all(engine)
        print(f"[OK] {table_name} table synced (existing data preserved)")
