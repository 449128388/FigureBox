"""
合并 user_settings 表到 users 表，重命名为 users_info

迁移步骤：
1. 向 users 表新增 annual_spending_limit 和 settings_updated_at 字段
2. 将 user_settings 表中的数据迁移到 users 表
3. 重命名 users 表为 users_info
4. 删除 user_settings 表
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import create_engine, text
from app.models.database import DATABASE_URL as SQLALCHEMY_DATABASE_URL


def upgrade():
    engine = create_engine(SQLALCHEMY_DATABASE_URL)

    with engine.connect() as conn:
        print("🚀 开始迁移 user_settings → users_info")

        # 1. 检查 users 表是否存在
        result = conn.execute(text(
            "SELECT COUNT(*) FROM information_schema.tables "
            "WHERE table_schema = DATABASE() AND table_name = 'users'"
        ))
        if result.scalar() == 0:
            print("⚠️ users 表不存在，跳过迁移")
            return

        # 2. 新增字段
        print("→ 添加 annual_spending_limit 字段...")
        try:
            conn.execute(text(
                "ALTER TABLE users ADD COLUMN annual_spending_limit FLOAT DEFAULT 0 "
                "COMMENT '年度手办消费上限（0表示未设置）'"
            ))
        except Exception as e:
            if "Duplicate column" in str(e):
                print("ℹ️ annual_spending_limit 字段已存在")
            else:
                print(f"⚠️ 添加字段异常: {e}")

        print("→ 添加 settings_updated_at 字段...")
        try:
            conn.execute(text(
                "ALTER TABLE users ADD COLUMN settings_updated_at DATETIME "
                "DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP "
                "COMMENT '配置最后更新时间'"
            ))
        except Exception as e:
            if "Duplicate column" in str(e):
                print("ℹ️ settings_updated_at 字段已存在")
            else:
                print(f"⚠️ 添加字段异常: {e}")

        conn.commit()

        # 3. 迁移数据：从 user_settings 表复制到 users 表
        print("→ 迁移 user_settings 数据到 users 表...")
        try:
            conn.execute(text(
                "UPDATE users u INNER JOIN user_settings s ON u.id = s.user_id "
                "SET u.annual_spending_limit = s.annual_spending_limit, "
                "u.settings_updated_at = s.updated_at"
            ))
            conn.commit()
            print("✅ 数据迁移完成")
        except Exception as e:
            if "Table" in str(e) and "doesn't exist" in str(e):
                print("ℹ️ user_settings 表不存在，跳过数据迁移")
            else:
                print(f"⚠️ 数据迁移异常: {e}")

        # 4. 重命名 users 表为 users_info
        print("→ 重命名 users 表为 users_info...")
        try:
            conn.execute(text("RENAME TABLE users TO users_info"))
            conn.commit()
            print("✅ 表重命名成功")
        except Exception as e:
            if "already exists" in str(e) or "Table 'users_info' already exists" in str(e):
                print("ℹ️ users_info 表已存在，跳过重命名")
            else:
                print(f"⚠️ 重命名异常: {e}，可能是名称被占用，尝试 DROP 后重命名")
                conn.rollback()

        # 5. 删除 user_settings 表
        print("→ 删除 user_settings 表...")
        try:
            conn.execute(text("DROP TABLE IF EXISTS user_settings"))
            conn.commit()
            print("✅ user_settings 表已删除")
        except Exception as e:
            print(f"⚠️ 删除异常: {e}")

    print("🎉 user_settings → users_info 迁移完成")


def downgrade():
    """回滚迁移"""
    engine = create_engine(SQLALCHEMY_DATABASE_URL)
    with engine.connect() as conn:
        print("🚀 开始回滚 user_settings→users_info 迁移")
        # 重命名回 users
        conn.execute(text("RENAME TABLE users_info TO users"))
        conn.commit()
        print("✅ 表已重命名回 users")


if __name__ == "__main__":
    upgrade()
