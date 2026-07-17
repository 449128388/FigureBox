"""
Migration: 为 order_transactions 表新增支付时间与尾款支付字段

新增字段：
- payment_time: 定金支付时间
- balance_payment_method: 尾款支付方式（支付宝、微信、银行卡转账、现金）
- balance_payment_time: 尾款支付时间
"""

import os
from sqlalchemy import create_engine, text


def migrate():
    """执行迁移"""
    database_url = os.getenv("DATABASE_URL", "mysql+pymysql://root:password@localhost:3306/figurebox")
    engine = create_engine(database_url)

    try:
        with engine.connect() as conn:
            result = conn.execute(text("SHOW COLUMNS FROM `order_transactions` LIKE 'payment_time'"))
            if not result.fetchone():
                conn.execute(text(
                    "ALTER TABLE `order_transactions` ADD COLUMN `payment_time` DATETIME DEFAULT NULL COMMENT '定金支付时间' AFTER `payment_method`"
                ))
                print("[OK] 已添加 payment_time 字段")
            else:
                print("[SKIP] payment_time 字段已存在")

            result = conn.execute(text("SHOW COLUMNS FROM `order_transactions` LIKE 'balance_payment_method'"))
            if not result.fetchone():
                conn.execute(text(
                    "ALTER TABLE `order_transactions` ADD COLUMN `balance_payment_method` VARCHAR(20) DEFAULT NULL COMMENT '尾款支付方式：支付宝、微信、银行卡转账、现金' AFTER `payment_time`"
                ))
                print("[OK] 已添加 balance_payment_method 字段")
            else:
                print("[SKIP] balance_payment_method 字段已存在")

            result = conn.execute(text("SHOW COLUMNS FROM `order_transactions` LIKE 'balance_payment_time'"))
            if not result.fetchone():
                conn.execute(text(
                    "ALTER TABLE `order_transactions` ADD COLUMN `balance_payment_time` DATETIME DEFAULT NULL COMMENT '尾款支付时间' AFTER `balance_payment_method`"
                ))
                print("[OK] 已添加 balance_payment_time 字段")
            else:
                print("[SKIP] balance_payment_time 字段已存在")

            conn.commit()
        print("[DONE] 迁移完成")
    except Exception as e:
        print(f"[ERROR] 迁移失败: {e}")
        raise


if __name__ == "__main__":
    migrate()
