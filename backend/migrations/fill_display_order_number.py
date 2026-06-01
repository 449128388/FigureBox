"""
数据库迁移脚本：为 orders 表补全 display_order_number 数据

迁移内容：
1. 为所有 display_order_number 为空的订单生成并填充展示订单编号
2. 格式：ORDER-YYYYMMDD-XXX

执行方式：
- 开发环境：python backend/migrations/fill_display_order_number.py
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


def generate_display_order_number(order_id, created_at):
    """生成展示订单编号"""
    if created_at:
        date_str = created_at.strftime('%Y%m%d')
        return f"ORDER-{date_str}-{order_id:03d}"
    else:
        return f"ORDER-{order_id:03d}"


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

        # 获取所有 display_order_number 为空的订单
        result = db.execute(text("""
            SELECT id, created_at 
            FROM orders 
            WHERE display_order_number IS NULL OR display_order_number = ''
        """))
        
        orders_to_update = result.fetchall()
        
        if not orders_to_update:
            print("没有需要补全的订单数据")
            return
        
        print(f"发现 {len(orders_to_update)} 条订单需要补全 display_order_number")
        
        # 更新每条订单的 display_order_number
        updated_count = 0
        for order_id, created_at in orders_to_update:
            display_number = generate_display_order_number(order_id, created_at)
            db.execute(text("""
                UPDATE orders 
                SET display_order_number = :display_number 
                WHERE id = :order_id
            """), {"display_number": display_number, "order_id": order_id})
            updated_count += 1
            print(f"  订单 {order_id} -> {display_number}")
        
        db.commit()
        print(f"\n✓ 成功补全 {updated_count} 条订单的 display_order_number")
        print("\n迁移完成！")

    except Exception as e:
        print(f"迁移失败: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    migrate()
