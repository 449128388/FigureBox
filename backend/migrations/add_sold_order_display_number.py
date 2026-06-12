
"""
数据库迁移脚本：为 sold_orders 表添加 display_order_number 字段

迁移内容：
1. 添加 display_order_number 字段 - 展示订单编号（系统生成，格式：SALE-YYYYMMDD-XXX）
2. 为已有记录生成展示订单编号

执行方式：
  docker exec figurebox-backend-1 python migrations/add_sold_order_display_number.py
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import text, inspect
from app.models.database import engine


def migrate():
    """执行迁移"""
    inspector = inspect(engine)

    if 'sold_orders' not in inspector.get_table_names():
        print("sold_orders 表不存在，跳过迁移")
        return

    existing_columns = {col['name'] for col in inspector.get_columns('sold_orders')}

    with engine.connect() as connection:
        # 添加 display_order_number 字段
        if 'display_order_number' not in existing_columns:
            try:
                alter_sql = "ALTER TABLE sold_orders ADD COLUMN display_order_number VARCHAR(100) COMMENT '展示订单编号（系统生成，格式：SALE-YYYYMMDD-XXX）'"
                connection.execute(text(alter_sql))
                print("✓ 成功添加字段: display_order_number")

                # 为已有记录生成展示订单编号
                update_sql = """
                    UPDATE sold_orders
                    SET display_order_number = CONCAT('SALE-', DATE_FORMAT(COALESCE(created_at, NOW()), '%Y%m%d'), '-', LPAD(id, 3, '0'))
                    WHERE display_order_number IS NULL
                """
                result = connection.execute(text(update_sql))
                connection.commit()
                print(f"✓ 已为 {result.rowcount} 条记录生成展示订单编号")
            except Exception as e:
                print(f"✗ 添加字段失败: {e}")
        else:
            print("- 字段已存在: display_order_number")

    print("迁移完成")


if __name__ == "__main__":
    print("=" * 50)
    print("开始迁移: sold_orders 添加 display_order_number 字段")
    print("=" * 50)
    migrate()
