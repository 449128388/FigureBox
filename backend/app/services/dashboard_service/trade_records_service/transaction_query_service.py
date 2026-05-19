"""
交易流水查询服务
提供交易流水记录的查询和组装
采用企业级服务层架构
"""
from typing import List, Dict, Any
from sqlalchemy.orm import Session

from app.models.figure import Figure
from app.models.asset import OrderTransaction
from app.models.sold_order import SoldOrder


class TransactionQueryService:
    """
    交易流水查询服务类

    提供以下核心功能：
    1. 买入交易查询：从OrderTransaction获取资金流水
    2. 卖出交易查询：从SoldOrder获取卖出记录
    3. 交易记录组装：统一格式返回交易流水
    """

    @classmethod
    def get_transactions(cls, db: Session, user_id: int) -> List[Dict[str, Any]]:
        """
        获取交易流水记录

        从OrderTransaction和SoldOrder获取数据，统一格式返回

        Args:
            db: 数据库会话
            user_id: 用户ID

        Returns:
            List[Dict]: 交易记录列表，按时间倒序排列
        """
        records = []

        # 获取买入交易记录
        buy_records = cls._get_buy_transactions(db, user_id)
        records.extend(buy_records)

        # 获取卖出交易记录
        sell_records = cls._get_sell_transactions(db, user_id)
        records.extend(sell_records)

        # 按时间排序（倒序）
        records.sort(key=lambda x: x.get("date", ""), reverse=True)

        return records

    @staticmethod
    def _get_buy_transactions(db: Session, user_id: int) -> List[Dict[str, Any]]:
        """
        获取买入交易记录

        从OrderTransaction获取资金流水（买入）

        Args:
            db: 数据库会话
            user_id: 用户ID

        Returns:
            List[Dict]: 买入交易记录列表
        """
        records = []

        order_transactions = db.query(OrderTransaction).filter(
            OrderTransaction.user_id == user_id,
            OrderTransaction.is_active == True
        ).order_by(OrderTransaction.transaction_date.desc()).limit(50).all()

        for ot in order_transactions:
            figure_name = ""
            if ot.figure_id:
                figure = db.query(Figure).filter(Figure.id == ot.figure_id).first()
                if figure:
                    figure_name = figure.name

            direction_text = "支出" if ot.direction == "out" else "收入"

            records.append({
                "id": ot.id,
                "date": ot.transaction_date.strftime("%m-%d %H:%M") if ot.transaction_date else "",
                "amount": -ot.total_amount if ot.direction == "out" else ot.total_amount,
                "title": f"{ot.transaction_type}: {figure_name} ({direction_text})",
                "order_id": str(ot.order_id) if ot.order_id else "",
                "status": "✅ 成功",
                "payment_method": ot.payment_method or "",
                "merchant": ot.platform or "",
                "platform": ot.platform or "",
                "fee": 0,
                "net_profit": 0,
                "actions": ["查看订单"]
            })

        return records

    @staticmethod
    def _get_sell_transactions(db: Session, user_id: int) -> List[Dict[str, Any]]:
        """
        获取卖出交易记录

        从SoldOrder获取卖出记录

        Args:
            db: 数据库会话
            user_id: 用户ID

        Returns:
            List[Dict]: 卖出交易记录列表
        """
        records = []

        sold_orders = db.query(SoldOrder).filter(
            SoldOrder.user_id == user_id,
            SoldOrder.is_active == 1,
            SoldOrder.status == "已完成"
        ).order_by(SoldOrder.created_at.desc()).limit(50).all()

        for so in sold_orders:
            figure_name = ""
            if so.figure_id:
                figure = db.query(Figure).filter(Figure.id == so.figure_id).first()
                if figure:
                    figure_name = figure.name

            net_profit = so.net_profit or (
                so.sell_price - so.cost_price - abs(so.shipping_fee or 0) - abs(so.platform_fee or 0)
            )

            records.append({
                "id": so.id + 10000,
                "date": so.created_at.strftime("%m-%d %H:%M") if so.created_at else "",
                "amount": so.sell_price,
                "title": f"卖出: {figure_name}",
                "order_id": so.order_number or "",
                "status": "✅ 已到账",
                "buyer": "",
                "platform": so.sell_platform or "",
                "fee": abs(so.platform_fee or 0),
                "net_profit": round(net_profit, 2),
                "actions": ["查看买家信息", "物流信息", "评价"]
            })

        return records
