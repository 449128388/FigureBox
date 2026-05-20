"""
数据库迁移脚本：为 order_transactions 表添加 updated_at 字段

迁移内容：
1. 添加 updated_at 字段 - 记录更新时间

执行方式：
- 开发环境：python backend/migrations/add_order_transaction_timestamps.py
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
        if 'order_transactions' not in inspector.get_table_names():
            print("order_transactions 表不存在，跳过迁移")
            return

        # 获取现有字段
        existing_columns = {col['name'] for col in inspector.get_columns('order_transactions')}
        print(f"现有字段: {existing_columns}")

        # 添加 updated_at 字段
        if 'updated_at' not in existing_columns:
            try:
                # MySQL 语法添加字段
                alter_sql = "ALTER TABLE order_transactions ADD COLUMN updated_at DATETIME"
                db.execute(text(alter_sql))
                print(f"✓ 成功添加字段: updated_at")

                # 更新现有记录的 updated_at 值为 created_at 值
                update_sql = "UPDATE order_transactions SET updated_at = created_at WHERE updated_at IS NULL"
                db.execute(text(update_sql))
                print(f"✓ 已同步现有记录的 updated_at 值")
            except Exception as e:
                print(f"✗ 添加字段 updated_at 失败: {e}")
        else:
            print(f"- 字段已存在: updated_at")

        db.commit()
        print("\n✅ 数据库迁移完成！")

    except Exception as e:
        db.rollback()
        print(f"\n❌ 迁移失败: {e}")
        raise
    finally:
        db.close()


def rollback():
    """
    回滚迁移 - 删除添加的字段
    注意：此操作会删除数据，请谨慎使用
    """
    print(f"连接到数据库...")
    engine = create_engine(DATABASE_URL)
    SessionLocal = sessionmaker(bind=engine)
    db = SessionLocal()

    try:
        # 删除 updated_at 字段
        try:
            alter_sql = "ALTER TABLE order_transactions DROP COLUMN updated_at"
            db.execute(text(alter_sql))
            print(f"✓ 成功删除字段: updated_at")
        except Exception as e:
            print(f"✗ 删除字段 updated_at 失败: {e}")

        db.commit()
        print("\n✅ 回滚完成！")

    except Exception as e:
        db.rollback()
        print(f"\n❌ 回滚失败: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "rollback":
        print("执行回滚操作...")
        rollback()
    else:
        print("执行迁移操作...")
        migrate()
