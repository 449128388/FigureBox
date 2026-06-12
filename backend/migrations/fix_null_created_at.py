
"""
修复 user_asset_snapshots 表中 created_at 为 NULL 的记录
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.models.database import engine
from sqlalchemy import text

with engine.connect() as conn:
    result = conn.execute(text(
        "UPDATE user_asset_snapshots SET created_at = NOW() WHERE created_at IS NULL"
    ))
    conn.commit()
    print(f"已修复 {result.rowcount} 条记录")
