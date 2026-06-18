"""
collector_transaction_service.py - 收藏家模式收藏历程服务

功能说明：
- 提供藏品收藏历程（全生命周期流水）查询服务
- 汇总某个手办下的所有资产变动记录

API端点对应：
- GET /collector/figures/{figure_id}/transactions

依赖：
- AssetTransaction 模型
- Figure 模型
"""

from sqlalchemy.orm import Session
from sqlalchemy import desc, asc
from datetime import datetime

from app.models.asset import AssetTransaction
from app.models.sold_order import SoldOrder


class CollectorTransactionService:
    """收藏家模式收藏历程服务类"""

    @staticmethod
    def get_figure_transactions(db: Session, user_id: int, figure_id: int) -> list:
        """
        获取手办全生命周期资产变动流水

        查询该 figure_id 下所有 asset_transactions 记录，
        按 transaction_date 升序排列，计算累计库存结余。

        Args:
            db: 数据库会话
            user_id: 用户ID
            figure_id: 手办ID

        Returns:
            list[dict]: 交易流水列表，按 transaction_date 倒序排列
            每项包含：
            - date: 交易日期
            - type: 交易类型（buy=买入, sell=卖出）
            - type_label: 交易类型中文标签
            - quantity: 交易数量
            - price: 单价
            - total_amount: 总金额
            - balance: 当日交易后的库存结余
        """
        # 查询所有交易记录，按日期升序
        transactions = db.query(AssetTransaction).filter(
            AssetTransaction.user_id == user_id,
            AssetTransaction.figure_id == figure_id,
            AssetTransaction.is_active == True
        ).order_by(AssetTransaction.transaction_date.asc()).all()

        if not transactions:
            return []

        # 按日期升序遍历计算库存结余
        running_balance = 0
        result = []
        for t in transactions:
            if t.transaction_type == 'buy':
                running_balance += (t.quantity or 0)
                # 通过 notes 字段判断是否为补仓（补仓买入的 notes 包含"补仓"关键词）
                is_replenish = t.notes and '补仓' in t.notes
                label = '补仓' if is_replenish else '买入'
                unit_price = t.price or 0
            elif t.transaction_type == 'sell':
                running_balance -= (t.quantity or 0)
                label = '卖出'
                # 卖出价格取 sold_orders 表的实际售价，而非成本价
                unit_price = t.price or 0  # 默认回退
                if t.sold_order_id:
                    sold_order = db.query(SoldOrder).filter(
                        SoldOrder.id == t.sold_order_id
                    ).first()
                    if sold_order and sold_order.sell_price and sold_order.quantity:
                        unit_price = sold_order.sell_price / sold_order.quantity
            else:
                # adjust → 调整，其他类型保留原值
                label = '调整' if t.transaction_type == 'adjust' else (t.transaction_type or '其他')
                unit_price = t.price or 0

            date_str = None
            if t.transaction_date:
                if isinstance(t.transaction_date, datetime):
                    date_str = t.transaction_date.strftime("%Y-%m-%d")
                else:
                    date_str = str(t.transaction_date)

            result.append({
                "date": date_str,
                "type": t.transaction_type,
                "type_label": label,
                "quantity": t.quantity or 1,
                "price": unit_price,
                "total_amount": unit_price * (t.quantity or 1),
                "balance": running_balance
            })

        # 按日期倒序返回（前端按时间线展示）
        result.reverse()
        return result
