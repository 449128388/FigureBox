"""
为已存在的用户填充 MinIO 配置默认值

说明：
- 仅填充当前为 NULL 或空字符串的 MinIO 字段，不覆盖用户已设置的值
- 从环境变量读取 MinIO 默认配置
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import create_engine, text
from app.models.database import DATABASE_URL as SQLALCHEMY_DATABASE_URL

# 从环境变量读取 MinIO 默认值（用户视角的 MinIO 连接信息）
MINIO_DEFAULTS = {
    "minio_endpoint": os.getenv("MINIO_PUBLIC_ENDPOINT", "http://localhost:28640"),
    "minio_access_key": os.getenv("MINIO_ACCESS_KEY", ""),
    "minio_secret_key": os.getenv("MINIO_SECRET_KEY", ""),
    "minio_bucket": os.getenv("MINIO_BUCKET", ""),
    "minio_public_url": os.getenv("MINIO_PUBLIC_URL", ""),
    "minio_secure": "1" if os.getenv("MINIO_SECURE", "false").lower() in ("true", "1", "yes") else "0",
    "minio_region": os.getenv("MINIO_REGION", "us-east-1"),
}


def upgrade():
    """为 users_info 表中 MinIO 字段为空的用户填充默认值"""
    engine = create_engine(SQLALCHEMY_DATABASE_URL)

    # 只填充有意义的默认值（非空），空字符串的字段不填充
    non_empty_defaults = {k: v for k, v in MINIO_DEFAULTS.items() if v}

    if not non_empty_defaults:
        print("⚠️  环境变量中未配置 MinIO 默认值，跳过填充")
        return

    with engine.connect() as conn:
        count = 0
        fields_filled = {}

        for col, default_val in non_empty_defaults.items():
            # 仅更新该字段为 NULL 或空字符串的行
            sql = text(
                f"UPDATE users_info SET `{col}` = :val "
                f"WHERE (`{col}` IS NULL OR `{col}` = '') AND `{col}` != :val"
            )
            result = conn.execute(sql, {"val": default_val})
            conn.commit()
            affected = result.rowcount
            if affected > 0:
                fields_filled[col] = affected
                count += affected

        if count > 0:
            print(f"✅ 已填充 {count} 个 MinIO 配置项：")
            for col, affected in fields_filled.items():
                print(f"  - {col}: 更新了 {affected} 行")
        else:
            print("ℹ️  所有用户的 MinIO 配置已是最新，无需填充")

    print(f"\n🎉 MinIO 默认值填充完成")


if __name__ == "__main__":
    upgrade()
