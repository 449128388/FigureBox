"""
数据库迁移脚本：添加 current_value 字段到 figures 表
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
        # 检查字段是否已存在
        result = connection.execute(text("""
            SELECT COUNT(*) 
            FROM information_schema.COLUMNS 
            WHERE TABLE_SCHEMA = DATABASE() 
            AND TABLE_NAME = 'figures' 
            AND COLUMN_NAME = 'current_value'
        """))
        
        count = result.scalar()
        
        if count == 0:
            # 添加 current_value 字段
            connection.execute(text("""
                ALTER TABLE figures 
                ADD COLUMN current_value FLOAT NULL 
                AFTER images
            """))
            connection.commit()
            print("✅ 成功添加 current_value 字段到 figures 表")
        else:
            print("⚠️ current_value 字段已存在，跳过迁移")

if __name__ == "__main__":
    migrate()
