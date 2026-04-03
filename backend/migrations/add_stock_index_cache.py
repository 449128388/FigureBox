"""
数据库迁移脚本：添加股票指数缓存表
"""
import sys
import os

# 添加后端目录到路径
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from sqlalchemy import create_engine, text
from app.models.database import DATABASE_URL

def migrate():
    """执行迁移"""
    engine = create_engine(DATABASE_URL)

    with engine.connect() as connection:
        # 检查表是否已存在
        result = connection.execute(text("""
            SELECT COUNT(*)
            FROM information_schema.TABLES
            WHERE TABLE_SCHEMA = DATABASE()
            AND TABLE_NAME = 'stock_index_cache'
        """))

        count = result.scalar()

        if count == 0:
            # 创建stock_index_cache表
            connection.execute(text("""
                CREATE TABLE stock_index_cache (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    index_code VARCHAR(20) NOT NULL UNIQUE,
                    index_name VARCHAR(50) NOT NULL,
                    current_value FLOAT NOT NULL,
                    change_value FLOAT DEFAULT 0,
                    change_percentage FLOAT DEFAULT 0,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                    request_count INT DEFAULT 0,
                    request_date DATE NOT NULL,
                    INDEX idx_index_code (index_code)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
            """))
            connection.commit()
            print("✅ 成功创建 stock_index_cache 表")
        else:
            print("⚠️ stock_index_cache 表已存在，跳过迁移")

if __name__ == "__main__":
    migrate()
