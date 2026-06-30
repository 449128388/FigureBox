"""
清空所有表数据，保留表结构
使用 TRUNCATE TABLE 命令快速清空数据并重置自增ID
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import text
from app.models.database import engine, Base

# 需要清空数据的表列表（按依赖关系排序，先清空子表）
TABLES = [
    # 交易相关
    "order_transactions",      # 订单交易记录
    "asset_transactions",      # 资产交易记录
    "asset_price_history",     # 资产价格历史
    "asset_alerts",            # 资产预警
    "asset_value_cache",       # 资产价值缓存
    "stock_index_history",     # 股票指数历史
    "stock_index_cache",       # 股票指数缓存

    # 订单相关
    "sold_orders",             # 已出售订单
    "orders",                  # 订单

    # 手办相关
    "figure_tag",              # 手办标签关联表（中间表，单数命名）
    "tags",                    # 标签
    "figures",                 # 手办

    # 用户相关
    "users_info",              # 用户信息（原 users + user_settings 合并）
]


def truncate_all_tables():
    """清空所有表数据"""
    with engine.connect() as connection:
        # 禁用外键约束检查（MySQL）
        connection.execute(text("SET FOREIGN_KEY_CHECKS = 0"))

        for table_name in TABLES:
            try:
                # 使用 TRUNCATE 清空表并重置自增ID
                connection.execute(text(f"TRUNCATE TABLE {table_name}"))
                print(f"✓ 已清空表: {table_name}")
            except Exception as e:
                print(f"✗ 清空表 {table_name} 失败: {e}")

        # 重新启用外键约束检查
        connection.execute(text("SET FOREIGN_KEY_CHECKS = 1"))
        connection.commit()

    print("\n✅ 所有表数据已清空，表结构保留完整")


if __name__ == "__main__":
    print("=" * 50)
    print("开始清空数据库所有表数据")
    print("=" * 50)

    truncate_all_tables()
