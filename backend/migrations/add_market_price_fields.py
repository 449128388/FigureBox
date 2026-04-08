"""
数据库迁移脚本：添加 market_price 和 market_currency 字段到 figures 表
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
        # 检查 market_price 字段是否已存在
        result = connection.execute(text("""
            SELECT COUNT(*) 
            FROM information_schema.COLUMNS 
            WHERE TABLE_SCHEMA = DATABASE() 
            AND TABLE_NAME = 'figures' 
            AND COLUMN_NAME = 'market_price'
        """))
        
        count = result.scalar()
        
        if count == 0:
            # 添加 market_price 字段
            connection.execute(text("""
                ALTER TABLE figures 
                ADD COLUMN market_price FLOAT NULL 
                AFTER current_value
            """))
            connection.commit()
            print("✅ 成功添加 market_price 字段到 figures 表")
        else:
            print("⚠️ market_price 字段已存在，跳过迁移")
        
        # 检查 market_currency 字段是否已存在
        result = connection.execute(text("""
            SELECT COUNT(*) 
            FROM information_schema.COLUMNS 
            WHERE TABLE_SCHEMA = DATABASE() 
            AND TABLE_NAME = 'figures' 
            AND COLUMN_NAME = 'market_currency'
        """))
        
        count = result.scalar()
        
        if count == 0:
            # 添加 market_currency 字段
            connection.execute(text("""
                ALTER TABLE figures 
                ADD COLUMN market_currency VARCHAR(10) DEFAULT 'CNY' 
                AFTER market_price
            """))
            connection.commit()
            print("✅ 成功添加 market_currency 字段到 figures 表")
        else:
            print("⚠️ market_currency 字段已存在，跳过迁移")

if __name__ == "__main__":
    migrate()
