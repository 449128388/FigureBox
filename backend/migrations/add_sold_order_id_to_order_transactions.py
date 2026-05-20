"""
为 order_transactions 表添加 sold_order_id 字段
用于关联 sold_orders 表
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import text
from app.models.database import engine


def migrate():
    """执行迁移"""
    print("=" * 50)
    print("开始迁移：为 order_transactions 表添加 sold_order_id 字段")
    print("=" * 50)

    with engine.connect() as connection:
        # 检查字段是否已存在
        check_sql = """
            SELECT COLUMN_NAME
            FROM INFORMATION_SCHEMA.COLUMNS
            WHERE TABLE_NAME = 'order_transactions'
            AND COLUMN_NAME = 'sold_order_id'
            AND TABLE_SCHEMA = DATABASE()
        """
        result = connection.execute(text(check_sql))
        existing_columns = [row[0] for row in result]

        if 'sold_order_id' in existing_columns:
            print("✓ sold_order_id 字段已存在，跳过添加")
        else:
            try:
                # 添加 sold_order_id 字段
                alter_sql = "ALTER TABLE order_transactions ADD COLUMN sold_order_id INTEGER"
                connection.execute(text(alter_sql))
                print("✓ 成功添加字段: sold_order_id")

                # 添加外键约束（可选）
                try:
                    fk_sql = """
                        ALTER TABLE order_transactions
                        ADD CONSTRAINT fk_order_transactions_sold_order
                        FOREIGN KEY (sold_order_id) REFERENCES sold_orders(id)
                    """
                    connection.execute(text(fk_sql))
                    print("✓ 成功添加外键约束: fk_order_transactions_sold_order")
                except Exception as e:
                    print(f"⚠ 添加外键约束失败（可能已存在）: {e}")

            except Exception as e:
                print(f"✗ 添加字段 sold_order_id 失败: {e}")
                return False

        connection.commit()

    print("\n✅ 迁移完成")
    return True


if __name__ == "__main__":
    migrate()
