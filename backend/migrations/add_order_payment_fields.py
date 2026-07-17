"""
Migration: 为 orders 表添加支付方式和支付时间字段

新增字段：
- payment_method: 支付方式（支付宝、微信、银行卡转账、现金）
- payment_time: 支付时间（精确到秒）
"""

import os
from sqlalchemy import create_engine, text


def migrate():
    """执行迁移"""
    database_url = os.getenv("DATABASE_URL", "mysql+pymysql://root:password@localhost:3306/figurebox")
    engine = create_engine(database_url)

    try:
        with engine.connect() as conn:
            # 检查字段是否已存在
            result = conn.execute(text("SHOW COLUMNS FROM `orders` LIKE 'payment_method'"))
            if not result.fetchone():
                conn.execute(text(
                    "ALTER TABLE `orders` ADD COLUMN `payment_method` VARCHAR(20) DEFAULT NULL COMMENT '支付方式：支付宝、微信、银行卡转账、现金' AFTER `display_order_number`"
                ))
                print("[OK] 已添加 payment_method 字段")
            else:
                print("[SKIP] payment_method 字段已存在")

            result = conn.execute(text("SHOW COLUMNS FROM `orders` LIKE 'payment_time'"))
            if not result.fetchone():
                conn.execute(text(
                    "ALTER TABLE `orders` ADD COLUMN `payment_time` DATETIME DEFAULT NULL COMMENT '支付时间' AFTER `payment_method`"
                ))
                print("[OK] 已添加 payment_time 字段")
            else:
                print("[SKIP] payment_time 字段已存在")

            conn.commit()
        print("[DONE] 迁移完成")
    except Exception as e:
        print(f"[ERROR] 迁移失败: {e}")
        raise


if __name__ == "__main__":
    migrate()
