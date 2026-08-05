"""
资产交易查询服务
提供查询资产交易记录的业务逻辑
"""
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import desc, func

from app.models.asset_transaction import AssetTransaction


class AssetTransactionQueryService:
    """资产交易查询服务类"""

    @staticmethod
    def get_transactions_by_figure(
        db: Session,
        user_id: int,
        figure_id: int
    ) -> List[AssetTransaction]:
        """
        获取指定手办的所有交易记录

        Args:
            db: 数据库会话
            user_id: 用户ID
            figure_id: 手办ID

        Returns:
            交易记录列表，按时间倒序
        """
        return db.query(AssetTransaction).filter(
            AssetTransaction.user_id == user_id,
            AssetTransaction.figure_id == figure_id
        ).order_by(desc(AssetTransaction.transaction_date)).all()

    @staticmethod
    def get_all_transactions(
        db: Session,
        user_id: int,
        transaction_type: Optional[str] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[AssetTransaction]:
        """
        获取用户的所有交易记录

        Args:
            db: 数据库会话
            user_id: 用户ID
            transaction_type: 交易类型过滤（buy/sell）
            skip: 跳过数量
            limit: 限制数量

        Returns:
            交易记录列表
        """
        query = db.query(AssetTransaction).filter(
            AssetTransaction.user_id == user_id
        )

        if transaction_type:
            query = query.filter(AssetTransaction.transaction_type == transaction_type)

        return query.order_by(desc(AssetTransaction.transaction_date)).offset(skip).limit(limit).all()

    @staticmethod
    def calculate_average_cost(
        db: Session,
        user_id: int,
        figure_id: int
    ) -> Dict[str, Any]:
        """
        计算手办的平均成本（补仓核心算法）

        Args:
            db: 数据库会话
            user_id: 用户ID
            figure_id: 手办ID

        Returns:
            包含平均成本、总持仓、总成本的字典
        """
        buy_transactions = db.query(AssetTransaction).filter(
            AssetTransaction.user_id == user_id,
            AssetTransaction.figure_id == figure_id,
            AssetTransaction.transaction_type == "buy"
        ).all()

        total_cost = sum(tx.total_amount for tx in buy_transactions)
        total_quantity = sum(tx.quantity for tx in buy_transactions)
        total_remaining = sum(tx.remaining_quantity or 0 for tx in buy_transactions)

        average_cost = total_cost / total_quantity if total_quantity > 0 else 0

        return {
            "average_cost": round(average_cost, 2),
            "total_quantity": total_quantity,
            "total_remaining": total_remaining,
            "total_cost": round(total_cost, 2)
        }

    @staticmethod
    def calculate_profit(
        db: Session,
        user_id: int,
        figure_id: int,
        current_market_price: Optional[float] = None
    ) -> Dict[str, Any]:
        """
        计算手办的盈亏情况

        Args:
            db: 数据库会话
            user_id: 用户ID
            figure_id: 手办ID
            current_market_price: 当前市场价格，可选

        Returns:
            包含盈亏数据的字典
        """
        cost_info = AssetTransactionQueryService.calculate_average_cost(db, user_id, figure_id)

        sell_transactions = db.query(AssetTransaction).filter(
            AssetTransaction.user_id == user_id,
            AssetTransaction.figure_id == figure_id,
            AssetTransaction.transaction_type == "sell"
        ).all()

        total_sell_revenue = sum(tx.total_amount for tx in sell_transactions)
        total_sell_quantity = sum(tx.quantity for tx in sell_transactions)

        result = {
            "average_cost": cost_info["average_cost"],
            "total_cost": cost_info["total_cost"],
            "total_remaining": cost_info["total_remaining"],
            "total_sell_revenue": round(total_sell_revenue, 2),
            "total_sell_quantity": total_sell_quantity,
            "realized_profit": round(total_sell_revenue - (cost_info["average_cost"] * total_sell_quantity), 2) if total_sell_quantity > 0 else 0
        }

        if current_market_price and cost_info["total_remaining"] > 0:
            unrealized_profit = (current_market_price - cost_info["average_cost"]) * cost_info["total_remaining"]
            result["current_market_price"] = current_market_price
            result["unrealized_profit"] = round(unrealized_profit, 2)
            result["total_profit"] = round(result["realized_profit"] + unrealized_profit, 2)

        return result
