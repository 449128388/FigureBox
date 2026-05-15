"""
数据库迁移脚本：为 sold_orders 表添加 quantity 字段

迁移内容：
添加 quantity 字段 - 记录卖出数量

执行方式：
- 开发环境：python backend/migrations/add_sold_order_quantity.py
- Docker 环境：自动检测并使用正确的数据库配置
"""

import sys
import os

# 添加 backend 目录到路径
backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, backend_dir)

from sqlalchemy import create_engine, text, inspect
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

# 加载环境变量
load_dotenv(os.path.join(backend_dir, '.env'))

# 数据库连接字符串
DATABASE_URL = os.getenv("DATABASE_URL", "mysql+pymysql://admin:password@localhost:3306/figurebox")


def migrate():
    """执行数据库迁移"""
    print(f"连接到数据库...")
    engine = create_engine(DATABASE_URL)
    SessionLocal = sessionmaker(bind=engine)
    db = SessionLocal()

    try:
        # 检查表是否存在
        inspector = inspect(engine)
        if 'sold_orders' not in inspector.get_table_names():
            print("sold_orders 表不存在，跳过迁移")
            return

        # 获取现有字段
        existing_columns = {col['name'] for col in inspector.get_columns('sold_orders')}
        print(f"现有字段: {existing_columns}")

        # 添加 quantity 字段（如果不存在）
        if 'quantity' not in existing_columns:
            try:
                # MySQL 语法添加字段
                alter_sql = "ALTER TABLE sold_orders ADD COLUMN quantity INTEGER DEFAULT 1"
                db.execute(text(alter_sql))
                print("✓ 成功添加字段: quantity")
            except Exception as e:
                print(f"✗ 添加字段 quantity 失败: {e}")
        else:
            print("- 字段已存在: quantity")

        db.commit()
        print("\n✅ 数据库迁移完成！")

    except Exception as e:
        db.rollback()
        print(f"\n❌ 迁移失败: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    migrate()
