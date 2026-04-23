"""
交易删除服务
提供资金交易记录的软删除功能
"""

from sqlalchemy.orm import Session
from app.models.asset import OrderTransaction
from datetime import datetime


class TransactionDeleteService:
    """交易删除服务类"""

    @staticmethod
    def delete_transactions_by_figure(
        db: Session,
        user_id: int,
        figure_id: int
    ) -> int:
        """
        软删除手办相关的所有资金流水记录

        Args:
            db: 数据库会话
            user_id: 用户ID
            figure_id: 手办ID

        Returns:
            int: 删除的记录数量
        """
        transactions = db.query(OrderTransaction).filter(
            OrderTransaction.user_id == user_id,
            OrderTransaction.figure_id == figure_id,
            OrderTransaction.is_active == True
        ).all()

        count = 0
        for transaction in transactions:
            transaction.is_active = False
            transaction.deleted_at = datetime.now()
            count += 1

        return count

    @staticmethod
    def delete_transactions_by_order(
        db: Session,
        user_id: int,
        order_id: int
    ) -> int:
        """
        软删除订单相关的所有资金流水记录

        Args:
            db: 数据库会话
            user_id: 用户ID
            order_id: 订单ID

        Returns:
            int: 删除的记录数量
        """
        transactions = db.query(OrderTransaction).filter(
            OrderTransaction.user_id == user_id,
            OrderTransaction.order_id == order_id,
            OrderTransaction.is_active == True
        ).all()

        count = 0
        for transaction in transactions:
            transaction.is_active = False
            transaction.deleted_at = datetime.now()
            count += 1

        return count

    @staticmethod
    def delete_transaction_by_id(
        db: Session,
        user_id: int,
        transaction_id: int
    ) -> bool:
        """
        软删除单条交易记录

        Args:
            db: 数据库会话
            user_id: 用户ID
            transaction_id: 交易记录ID

        Returns:
            bool: 是否删除成功
        """
        transaction = db.query(OrderTransaction).filter(
            OrderTransaction.id == transaction_id,
            OrderTransaction.user_id == user_id,
            OrderTransaction.is_active == True
        ).first()

        if not transaction:
            return False

        transaction.is_active = False
        transaction.deleted_at = datetime.now()
        return True
