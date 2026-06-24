"""
为 activity_feed 表添加 updated_at 字段

字段用途：
- 新增记录时：updated_at = created_at
- 更新记录时：updated_at = 当前时间
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import create_engine, MetaData, Table, Column, TIMESTAMP, text
from app.models.database import DATABASE_URL


def upgrade():
    """为 activity_feed 表添加 updated_at 字段"""
    engine = create_engine(DATABASE_URL)
    metadata = MetaData()

    activity_feed = Table('activity_feed', metadata, autoload_with=engine)

    # 检查字段是否已存在
    if 'updated_at' not in activity_feed.c:
        from sqlalchemy import text as sql_text
        with engine.connect() as conn:
            conn.execute(sql_text(
                "ALTER TABLE activity_feed "
                "ADD COLUMN updated_at TIMESTAMP NULL DEFAULT CURRENT_TIMESTAMP "
                "ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间'"
            ))
            conn.commit()
        print("✅ activity_feed.updated_at 字段添加成功")
    else:
        print("⏭️  activity_feed.updated_at 字段已存在，跳过")


def downgrade():
    """删除 activity_feed 表的 updated_at 字段"""
    engine = create_engine(DATABASE_URL)
    metadata = MetaData()

    activity_feed = Table('activity_feed', metadata, autoload_with=engine)

    if 'updated_at' in activity_feed.c:
        from sqlalchemy import text as sql_text
        with engine.connect() as conn:
            conn.execute(sql_text(
                "ALTER TABLE activity_feed DROP COLUMN updated_at"
            ))
            conn.commit()
        print("✅ activity_feed.updated_at 字段删除成功")
    else:
        print("⏭️  activity_feed.updated_at 字段不存在，跳过")


if __name__ == "__main__":
    upgrade()
