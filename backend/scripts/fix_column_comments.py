"""
修复 sold_orders 表字段注释乱码脚本

问题原因：通过 PowerShell 执行 ALTER TABLE 时，中文注释在命令行编码转换中发生乱码。
本脚本使用 Python 的 pymysql 驱动（utf8mb4 字符集）重新设置字段注释。

使用方式：
  方式一（容器内）：
    docker exec figurebox-backend-1 python scripts/fix_column_comments.py
  
  方式二（宿主机，需安装 pymysql）：
    cd backend && pip install pymysql && python scripts/fix_column_comments.py
"""

import pymysql
from pymysql.cursors import DictCursor

# 数据库连接配置（与 .env 保持一致）
DB_CONFIG = {
    "host": "db",
    "port": 3306,
    "user": "admin",
    "password": "password",
    "database": "figurebox",
    "charset": "utf8mb4",
}


def fix_comments():
    """修复字段注释"""
    connection = pymysql.connect(**DB_CONFIG)
    try:
        with connection.cursor() as cursor:
            # 1. 修复 payment_method 注释
            sql_payment = (
                "ALTER TABLE sold_orders "
                "MODIFY COLUMN payment_method VARCHAR(50) DEFAULT NULL "
                "COMMENT '支付方式：支付宝、微信、银行卡等'"
            )
            cursor.execute(sql_payment)
            print("[OK] payment_method 注释已更新")

            # 2. 修复 sell_date 注释
            sql_sell_date = (
                "ALTER TABLE sold_orders "
                "MODIFY COLUMN sell_date DATE DEFAULT NULL "
                "COMMENT '卖出日期'"
            )
            cursor.execute(sql_sell_date)
            print("[OK] sell_date 注释已更新")

        connection.commit()
        print("[DONE] 所有字段注释修复完成")
    finally:
        connection.close()


def verify_comments():
    """验证修复后的注释"""
    connection = pymysql.connect(**DB_CONFIG)
    try:
        with connection.cursor(DictCursor) as cursor:
            cursor.execute(
                "SELECT COLUMN_NAME, COLUMN_COMMENT "
                "FROM information_schema.COLUMNS "
                "WHERE TABLE_SCHEMA = %(db)s "
                "AND TABLE_NAME = 'sold_orders' "
                "AND COLUMN_NAME IN ('payment_method', 'sell_date')",
                {"db": DB_CONFIG["database"]},
            )
            rows = cursor.fetchall()
            print("\n=== 字段注释验证 ===")
            for row in rows:
                print(f"  {row['COLUMN_NAME']}: {row['COLUMN_COMMENT']}")
    finally:
        connection.close()


if __name__ == "__main__":
    fix_comments()
    verify_comments()
