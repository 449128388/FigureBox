"""
数据库迁移脚本：为 orders 表添加订单备注字段

迁移内容：
1. 添加 remarks 字段 - 订单备注信息（用户自定义备注）

执行方式：
- 开发环境：python backend/migrations/add_order_remarks.py
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
        if 'orders' not in inspector.get_table_names():
            print("orders 表不存在，跳过迁移")
            return

        # 获取现有字段
        existing_columns = {col['name'] for col in inspector.get_columns('orders')}
        print(f"现有字段: {existing_columns}")

        # 添加 remarks 字段（如果不存在）
        if 'remarks' not in existing_columns:
            print("添加 remarks 字段...")
            db.execute(text("ALTER TABLE orders ADD COLUMN remarks VARCHAR(500)"))
            db.commit()
            print("✅ remarks 字段添加成功")
        else:
            print("remarks 字段已存在，跳过")

        print("\n✅ 数据库迁移完成")

    except Exception as e:
        db.rollback()
        print(f"❌ 迁移失败: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    migrate()
