"""
资产交易服务
提供资产交易记录相关的业务逻辑，包括创建、查询、更新交易记录
支持股票式补仓功能，记录买入卖出交易
"""
from datetime import datetime
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import desc, func

from app.models.asset import AssetTransaction
from app.models.figure import Figure
from app.models.order import Order


class AssetTransactionService:
    """资产交易服务类"""

    @staticmethod
    def create_transaction_from_figure(
        db: Session,
        user_id: int,
        figure_id: int,
        price: float,
        quantity: int = 1,
        order_id: Optional[int] = None
    ) -> AssetTransaction:
        """
        从手办数据创建资产交易记录（买入类型）

        使用场景：
        - 用户创建手办时，自动创建对应的买入交易记录
        - 用于记录资产的初始成本

        Args:
            db: 数据库会话
            user_id: 用户ID
            figure_id: 手办ID
            price: 单价
            quantity: 数量，默认为1
            order_id: 关联订单ID，可选

        Returns:
            创建的交易记录对象
        """
        total_amount = price * quantity

        transaction = AssetTransaction(
            user_id=user_id,
            figure_id=figure_id,
            order_id=order_id,
            transaction_type="buy",
            price=price,
            quantity=quantity,
            total_amount=total_amount,
            remaining_quantity=quantity,  # 初始剩余数量等于购买数量
            notes="自动创建：从手办管理数据中创建"
        )

        db.add(transaction)
        db.flush()  # 获取ID但不提交

        return transaction

    @staticmethod
    def create_buy_transaction_from_order(
        db: Session,
        user_id: int,
        figure_id: int,
        order: Order,
        quantity: int = 1
    ) -> AssetTransaction:
        """
        从订单创建资产交易记录（买入类型）

        使用场景：
        - 用户创建订单时，独立创建对应的买入交易记录
        - 不修改手办创建时的原始交易记录，保留历史数据完整性
        - 每个订单对应一条独立的交易记录

        Args:
            db: 数据库会话
            user_id: 用户ID
            figure_id: 手办ID
            order: 订单对象
            quantity: 数量，默认为1

        Returns:
            创建的交易记录对象
        """
        # 计算订单总价（定金 + 尾款）
        total_price = order.deposit + order.balance

        # 【修复】始终创建新的交易记录，不更新现有记录
        # 这样可以保留手办创建的原始记录，同时记录订单的独立信息
        transaction = AssetTransaction(
            user_id=user_id,
            figure_id=figure_id,
            order_id=order.id,
            transaction_type="buy",
            price=total_price,
            quantity=quantity,
            total_amount=total_price * quantity,
            remaining_quantity=quantity,  # 新订单的剩余数量等于订单数量
            notes=f"从订单 #{order.id} 创建"
        )
        db.add(transaction)
        db.flush()
        return transaction

    @staticmethod
    def create_sell_transaction(
        db: Session,
        user_id: int,
        figure_id: int,
        price: float,
        quantity: int,
        notes: Optional[str] = None
    ) -> Optional[AssetTransaction]:
        """
        创建卖出交易记录

        使用场景：
        - 用户卖出部分或全部手办时
        - 自动扣减剩余持仓数量

        Args:
            db: 数据库会话
            user_id: 用户ID
            figure_id: 手办ID
            price: 卖出单价
            quantity: 卖出数量
            notes: 备注

        Returns:
            创建的交易记录对象，如果持仓不足返回None
        """
        # 检查总持仓数量
        total_remaining = db.query(func.sum(AssetTransaction.remaining_quantity)).filter(
            AssetTransaction.user_id == user_id,
            AssetTransaction.figure_id == figure_id,
            AssetTransaction.transaction_type == "buy"
        ).scalar() or 0

        if total_remaining < quantity:
            raise ValueError(f"持仓不足，当前持仓：{total_remaining}，尝试卖出：{quantity}")

        # 创建卖出交易记录
        total_amount = price * quantity
        transaction = AssetTransaction(
            user_id=user_id,
            figure_id=figure_id,
            order_id=None,
            transaction_type="sell",
            price=price,
            quantity=quantity,
            total_amount=total_amount,
            remaining_quantity=0,  # 卖出记录的剩余数量为0
            notes=notes or "卖出交易"
        )
        db.add(transaction)

        # 扣减买入记录的剩余数量（先进先出）
        remaining_to_deduct = quantity
        buy_transactions = db.query(AssetTransaction).filter(
            AssetTransaction.user_id == user_id,
            AssetTransaction.figure_id == figure_id,
            AssetTransaction.transaction_type == "buy",
            AssetTransaction.remaining_quantity > 0
        ).order_by(AssetTransaction.transaction_date.asc()).all()

        for buy_tx in buy_transactions:
            if remaining_to_deduct <= 0:
                break

            deduct_amount = min(buy_tx.remaining_quantity, remaining_to_deduct)
            buy_tx.remaining_quantity -= deduct_amount
            remaining_to_deduct -= deduct_amount

        db.flush()
        return transaction

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
        # 获取所有买入记录
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
        cost_info = AssetTransactionService.calculate_average_cost(db, user_id, figure_id)

        # 获取卖出记录
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

        # 计算未实现盈亏（基于当前市场价格）
        if current_market_price and cost_info["total_remaining"] > 0:
            unrealized_profit = (current_market_price - cost_info["average_cost"]) * cost_info["total_remaining"]
            result["current_market_price"] = current_market_price
            result["unrealized_profit"] = round(unrealized_profit, 2)
            result["total_profit"] = round(result["realized_profit"] + unrealized_profit, 2)

        return result

    @staticmethod
    def delete_transaction(
        db: Session,
        transaction_id: int,
        user_id: int
    ) -> bool:
        """
        删除交易记录

        Args:
            db: 数据库会话
            transaction_id: 交易记录ID
            user_id: 用户ID

        Returns:
            是否删除成功
        """
        transaction = db.query(AssetTransaction).filter(
            AssetTransaction.id == transaction_id,
            AssetTransaction.user_id == user_id
        ).first()

        if not transaction:
            return False

        db.delete(transaction)
        db.flush()
        return True
