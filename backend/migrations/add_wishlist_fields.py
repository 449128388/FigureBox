"""
为 figures 表添加愿望清单扩展字段

新增字段：
- wishlist_status: 愿望清单状态（wish/released/purchased/cancelled）
- source_url: 来源URL
- note: 备注
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import create_engine, text
from app.models.database import DATABASE_URL as SQLALCHEMY_DATABASE_URL


def upgrade():
    """添加愿望清单扩展字段"""
    engine = create_engine(SQLALCHEMY_DATABASE_URL)
    with engine.begin() as conn:
        # 1. wishlist_status
        try:
            conn.execute(text("""
                ALTER TABLE figures
                ADD COLUMN wishlist_status VARCHAR(20) NULL
                COMMENT '愿望清单状态：wish=愿望中, released=已发售, purchased=已购买, cancelled=已取消'
            """))
            print("✓ 添加 wishlist_status 字段")
        except Exception as e:
            if "Duplicate column name" in str(e) or "1060" in str(e):
                print("· wishlist_status 字段已存在")
            else:
                raise

        # 2. source_url
        try:
            conn.execute(text("""
                ALTER TABLE figures
                ADD COLUMN source_url VARCHAR(500) NULL
                COMMENT '愿望清单来源URL'
            """))
            print("✓ 添加 source_url 字段")
        except Exception as e:
            if "Duplicate column name" in str(e) or "1060" in str(e):
                print("· source_url 字段已存在")
            else:
                raise

        # 3. note
        try:
            conn.execute(text("""
                ALTER TABLE figures
                ADD COLUMN note TEXT NULL
                COMMENT '愿望清单备注'
            """))
            print("✓ 添加 note 字段")
        except Exception as e:
            if "Duplicate column name" in str(e) or "1060" in str(e):
                print("· note 字段已存在")
            else:
                raise

        # 4. 索引（加速 wishlist_status 过滤）
        try:
            conn.execute(text("""
                CREATE INDEX idx_figures_wishlist_status
                ON figures (purchase_type, wishlist_status, is_active)
            """))
            print("✓ 创建 idx_figures_wishlist_status 索引")
        except Exception as e:
            if "Duplicate key name" in str(e) or "1061" in str(e):
                print("· idx_figures_wishlist_status 索引已存在")
            else:
                raise

    print("\n✅ 愿望清单扩展字段迁移完成")


def downgrade():
    """回滚"""
    engine = create_engine(SQLALCHEMY_DATABASE_URL)
    with engine.begin() as conn:
        conn.execute(text("ALTER TABLE figures DROP INDEX idx_figures_wishlist_status"))
        conn.execute(text("ALTER TABLE figures DROP COLUMN note"))
        conn.execute(text("ALTER TABLE figures DROP COLUMN source_url"))
        conn.execute(text("ALTER TABLE figures DROP COLUMN wishlist_status"))
    print("✓ 愿望清单扩展字段已回滚")


if __name__ == "__main__":
    upgrade()
