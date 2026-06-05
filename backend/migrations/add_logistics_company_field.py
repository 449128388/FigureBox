#!/usr/bin/env python3
"""
数据库迁移脚本：为 orders 表添加 logistics_company 字段

迁移说明：
- 添加 logistics_company 字段到 orders 表
- 字段类型：VARCHAR(50)
- 允许为空

执行方式：
    cd backend
    python migrations/add_logistics_company_field.py
"""

import sys
import os

# 添加项目根目录到 Python 路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import create_engine, text
from app.core.config import settings

def upgrade():
    """执行迁移：添加 logistics_company 字段"""
    print("开始执行迁移：添加 logistics_company 字段到 orders 表...")
    
    # 创建数据库连接
    engine = create_engine(settings.DATABASE_URL)
    
    with engine.connect() as conn:
        # 检查字段是否已存在
        result = conn.execute(text("""
            SELECT COUNT(*) FROM information_schema.COLUMNS 
            WHERE TABLE_NAME = 'orders' 
            AND COLUMN_NAME = 'logistics_company'
            AND TABLE_SCHEMA = DATABASE()
        """))
        count = result.scalar()
        
        if count > 0:
            print("字段 logistics_company 已存在，跳过迁移")
            return
        
        # 添加字段
        conn.execute(text("""
            ALTER TABLE orders 
            ADD COLUMN logistics_company VARCHAR(50) NULL 
            COMMENT '物流公司：顺丰、圆通、中通、申通、韵达、EMS、其他'
        """))
        
        conn.commit()
        print("✓ 成功添加 logistics_company 字段到 orders 表")

def downgrade():
    """回滚迁移：删除 logistics_company 字段"""
    print("开始回滚：删除 logistics_company 字段...")
    
    engine = create_engine(settings.DATABASE_URL)
    
    with engine.connect() as conn:
        conn.execute(text("""
            ALTER TABLE orders 
            DROP COLUMN IF EXISTS logistics_company
        """))
        
        conn.commit()
        print("✓ 成功删除 logistics_company 字段")

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="数据库迁移脚本")
    parser.add_argument("--downgrade", action="store_true", help="执行回滚操作")
    args = parser.parse_args()
    
    if args.downgrade:
        downgrade()
    else:
        upgrade()
