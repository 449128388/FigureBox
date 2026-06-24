"""
动态流查询性能优化迁移脚本

功能说明：
- 为 activity_feed 表添加 user_id + created_at 复合索引
- 解决动态流查询时 MySQL 排序内存溢出问题（Error 1038: Out of sort memory）
- 优化按时间倒序查询性能

问题背景：
- 查询按 activity_feed.created_at DESC 排序
- 当数据量较大时，MySQL 的 sort_buffer_size 不足以在内存中完成排序
- 建立复合索引后，MySQL 可以直接利用索引顺序，避免 filesort

创建时间: 2026-06-23
"""

from sqlalchemy import create_engine, text
import os
import sys

# 添加项目路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def upgrade():
    """
    添加 activity_feed 表的 user_id + created_at 复合索引
    """
    from dotenv import load_dotenv
    load_dotenv()

    DATABASE_URL = os.getenv("DATABASE_URL", "mysql+pymysql://admin:password@localhost:3306/figurebox")
    engine = create_engine(DATABASE_URL)

    with engine.connect() as conn:
        try:
            conn.execute(text("""
                CREATE INDEX idx_activity_feed_user_created
                ON activity_feed(user_id, created_at DESC)
            """))
            print("✅ 创建索引: idx_activity_feed_user_created")
        except Exception as e:
            if "Duplicate key name" in str(e) or "already exists" in str(e):
                print("⚠️ 索引已存在: idx_activity_feed_user_created")
            else:
                print(f"❌ 创建索引失败: {e}")

        conn.commit()
        print("\n🎉 动态流查询性能优化完成！")


def downgrade():
    """
    回滚：删除添加的索引
    """
    from dotenv import load_dotenv
    load_dotenv()

    DATABASE_URL = os.getenv("DATABASE_URL", "mysql+pymysql://admin:password@localhost:3306/figurebox")
    engine = create_engine(DATABASE_URL)

    with engine.connect() as conn:
        try:
            conn.execute(text("DROP INDEX idx_activity_feed_user_created ON activity_feed"))
            print("✅ 删除索引: idx_activity_feed_user_created")
        except Exception as e:
            print(f"⚠️ 删除索引失败或索引不存在: {e}")

        conn.commit()
        print("\n🎉 索引回滚完成！")


if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "downgrade":
        downgrade()
    else:
        upgrade()
