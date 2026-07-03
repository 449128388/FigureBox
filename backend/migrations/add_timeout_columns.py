"""
为 users_info 表添加超时登出配置字段

说明：
- 检查并添加 session_timeout_minutes、session_timeout_warning 字段
- 如果字段已存在则跳过，避免重复执行报错
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import create_engine, text
from app.models.database import DATABASE_URL as SQLALCHEMY_DATABASE_URL

# 超时登出配置字段定义
TIMEOUT_COLUMNS = [
    ("session_timeout_minutes", "INT", "会话超时时间（分钟），0 表示永不超时"),
    ("session_timeout_warning", "TINYINT(1)", "超时前是否弹窗提醒"),
]


def upgrade():
    """为 users_info 表添加超时登出字段"""
    engine = create_engine(SQLALCHEMY_DATABASE_URL)

    with engine.connect() as conn:
        # 查询 users_info 表的现有字段
        result = conn.execute(text(
            "SELECT column_name FROM information_schema.columns "
            "WHERE table_schema = DATABASE() AND table_name = 'users_info'"
        ))
        existing_columns = {row[0] for row in result}
        print("✅ 已获取 users_info 表现有字段列表")

        count = 0
        for col_name, col_type, col_comment in TIMEOUT_COLUMNS:
            if col_name in existing_columns:
                print(f"  - {col_name}: 字段已存在，跳过")
                continue

            # 默认值处理
            if col_name == "session_timeout_minutes":
                default_value = "DEFAULT 30"
            elif col_name == "session_timeout_warning":
                default_value = "DEFAULT 1"
            else:
                default_value = ""

            sql = (
                f"ALTER TABLE `users_info` "
                f"ADD COLUMN `{col_name}` {col_type} "
                f"{default_value} "
                f"COMMENT '{col_comment}'"
            )
            conn.execute(text(sql))
            conn.commit()
            print(f"  ✅ {col_name}: 已添加 ({col_type})")
            count += 1

    print(f"\n🎉 共添加 {count} 个超时登出配置字段")


if __name__ == "__main__":
    upgrade()
