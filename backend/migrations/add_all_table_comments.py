"""
为所有数据库表补充或修正中文注释

说明：
- 遍历所有已知表，使用 ALTER TABLE ... COMMENT 添加备注
- 跳过已存在备注的表
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import create_engine, text
from app.models.database import Base, DATABASE_URL as SQLALCHEMY_DATABASE_URL

# 所有表的注释映射
TABLE_COMMENTS = {
    "users_info": "用户信息表 - 存储用户基本信息、认证信息及配置（含年度消费上限）",
    "users": "用户表 - 存储系统用户的基本信息和认证信息【已重命名为 users_info】",
    "figures": "手办表 - 存储手办的基本信息、市场价、成本价等核心数据",
    "orders": "订单表 - 存储手办预定/购买的订单信息（定金、尾款、状态等）",
    "sold_orders": "卖出订单表 - 存储手办卖出/转卖的记录",
    "asset_transactions": "资产交易记录表 - 记录手办的买卖交易（股票式补仓、买入卖出流水）",
    "asset_price_history": "资产价格历史表 - 记录手办价格变化历史，用于价格趋势图表",
    "asset_alerts": "资产预警设置表 - 存储用户设置的价格预警规则",
    "asset_value_cache": "资产市值缓存表 - 缓存用户每日资产总市值，用于日涨跌计算",
    "stock_index_cache": "指数缓存表 - 缓存最新上证指数/沪深300指数数据",
    "stock_index_history": "指数历史记录表 - 保存每次请求的指数详细数据，用于趋势分析",
    "order_transactions": "订单交易流水表 - 记录订单的支付流水明细（定金、尾款、费用等）",
    "plastic_index_history": "塑料手办指数(HPI)历史表 - 记录每日 HPI 指数值",
    "holding_snapshots": "持仓快照表 - 每日收盘时各手办的持仓数据快照",
    "holding_snapshot_summaries": "持仓快照汇总表 - 每日收盘时用户持仓汇总数据",
    "user_asset_snapshots": "用户资产每日快照表 - 每日记录用户资产状况用于日涨跌对比",
    "tags": "标签表 - 手办标签（作品、角色、属性等分类）",
    "figure_tag": "手办-标签关联表 - 手办和标签的多对多关联中间表",
    "activity_feed": "动态流表 - 收藏家模式的动态事件记录（入手、到库、售出等）",
    "collector_privacy": "收藏家隐私设置表 - 收藏家模式下的个人主页可见性等隐私配置",
    "favorite_manufacturers": "本命厂商表 - 用户关注/收藏的手办厂商列表",
    "cabinet_ratings": "收藏柜喜爱度评分表 - 用户在收藏柜中对手办的 1-5 星评分",
    "cabinet_figure_exclusions": "展示分类手动排除表 - 用户从展示分类中手动移出的手办记录",
    "user_settings": "用户设置表 - 存储用户的个性化配置（年度消费上限等设置）【已废弃，合并到 users_info】",
    "exchange_rate_realtime": "最新汇率缓存表 - 缓存从中国外汇交易中心获取的当前最新汇率",
    "exchange_rate_history": "汇率历史记录表 - 记录每次从中国外汇交易中心获取的汇率快照",
    "hpi_daily": "HPI每日快照表 - 投资生涯全周期收益指数每日快照",
    "hpi_components": "HPI成分明细表 - 记录每手办对指数的贡献",
}


def upgrade():
    """为所有表添加注释"""
    engine = create_engine(SQLALCHEMY_DATABASE_URL)

    # 先确保所有表已创建（ORM 模型自动建表）
    Base.metadata.create_all(bind=engine)
    print("✅ 所有 ORM 表已创建")

    with engine.connect() as conn:
        # 获取数据库中已有的所有表
        result = conn.execute(text(
            "SELECT table_name, table_comment FROM information_schema.tables "
            "WHERE table_schema = DATABASE()"
        ))
        existing_tables = {}
        for row in result:
            existing_tables[row[0]] = row[1] or ""

        count = 0
        for table_name, comment in TABLE_COMMENTS.items():
            if table_name in existing_tables:
                current_comment = existing_tables[table_name]
                # 如果注释已经是期望的值则跳过
                if current_comment == comment:
                    print(f"  - {table_name}: 注释已存在，跳过")
                    continue
                # 更新注释
                conn.execute(text(
                    f"ALTER TABLE `{table_name}` COMMENT = '{comment}'"
                ))
                conn.commit()
                print(f"  ✅ {table_name}: 注释已更新")
                count += 1
            else:
                print(f"  ⚠️ {table_name}: 表不存在，跳过")

    print(f"\n🎉 共更新 {count} 张表的注释")


if __name__ == "__main__":
    upgrade()
