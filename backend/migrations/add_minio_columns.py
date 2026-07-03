"""
为 users_info 表添加 MinIO 配置字段

说明：
- 检查并添加 MinIO 配置相关字段到 users_info 表
- 如果字段已存在则跳过，避免重复执行报错
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import create_engine, text
from app.models.database import DATABASE_URL as SQLALCHEMY_DATABASE_URL

# MinIO 配置字段定义
MINIO_COLUMNS = [
    ("minio_endpoint", "VARCHAR(255)", "MinIO API 端点地址"),
    ("minio_access_key", "VARCHAR(100)", "MinIO Access Key"),
    ("minio_secret_key", "VARCHAR(255)", "MinIO Secret Key"),
    ("minio_bucket", "VARCHAR(100)", "MinIO Bucket 名称"),
    ("minio_public_url", "VARCHAR(255)", "图片访问域名"),
    ("minio_secure", "TINYINT(1)", "是否使用 HTTPS"),
    ("minio_region", "VARCHAR(50)", "MinIO 区域代码"),
]


def upgrade():
    """为 users_info 表添加 MinIO 字段"""
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
        for col_name, col_type, col_comment in MINIO_COLUMNS:
            if col_name in existing_columns:
                print(f"  - {col_name}: 字段已存在，跳过")
                continue

            # 默认值处理
            default_value = "DEFAULT 'us-east-1'" if col_name == "minio_region" else "DEFAULT ''"
            if col_name == "minio_secure":
                default_value = "DEFAULT 0"

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

    print(f"\n🎉 共添加 {count} 个 MinIO 配置字段")


if __name__ == "__main__":
    upgrade()
