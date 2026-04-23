"""
交易查询服务
提供资金交易记录的查询和统计功能
"""

from sqlalchemy.orm import Session
from app.models.asset import OrderTransaction
from datetime import datetime


class TransactionQueryService:
    """交易查询服务类"""

    @staticmethod
    def get_figure_total_spending(
        db: Session,
        user_id: int,
        figure_id: int
    ) -> float:
        """
        获取手办的总支出金额（买入 + 手续费）

        Args:
            db: 数据库会话
            user_id: 用户ID
            figure_id: 手办ID

        Returns:
            float: 总支出金额
        """
        transactions = db.query(OrderTransaction).filter(
            OrderTransaction.user_id == user_id,
            OrderTransaction.figure_id == figure_id,
            OrderTransaction.is_active == True,
            OrderTransaction.direction == "out"
        ).all()

        return sum(t.total_amount for t in transactions)

    @staticmethod
    def get_figure_total_income(
        db: Session,
        user_id: int,
        figure_id: int
    ) -> float:
        """
        获取手办的总收入金额（卖出 + 退款）

        Args:
            db: 数据库会话
            user_id: 用户ID
            figure_id: 手办ID

        Returns:
            float: 总收入金额
        """
        transactions = db.query(OrderTransaction).filter(
            OrderTransaction.user_id == user_id,
            OrderTransaction.figure_id == figure_id,
            OrderTransaction.is_active == True,
            OrderTransaction.direction == "in"
        ).all()

        return sum(t.total_amount for t in transactions)

    @staticmethod
    def get_user_total_spending(
        db: Session,
        user_id: int,
        start_date: datetime = None,
        end_date: datetime = None
    ) -> float:
        """
        获取用户总支出金额

        Args:
            db: 数据库会话
            user_id: 用户ID
            start_date: 开始日期（可选）
            end_date: 结束日期（可选）

        Returns:
            float: 总支出金额
        """
        query = db.query(OrderTransaction).filter(
            OrderTransaction.user_id == user_id,
            OrderTransaction.is_active == True,
            OrderTransaction.direction == "out"
        )

        if start_date:
            query = query.filter(OrderTransaction.transaction_date >= start_date)
        if end_date:
            query = query.filter(OrderTransaction.transaction_date <= end_date)

        transactions = query.all()
        return sum(t.total_amount for t in transactions)

    @staticmethod
    def get_user_total_income(
        db: Session,
        user_id: int,
        start_date: datetime = None,
        end_date: datetime = None
    ) -> float:
        """
        获取用户总收入金额

        Args:
            db: 数据库会话
            user_id: 用户ID
            start_date: 开始日期（可选）
            end_date: 结束日期（可选）

        Returns:
            float: 总收入金额
        """
        query = db.query(OrderTransaction).filter(
            OrderTransaction.user_id == user_id,
            OrderTransaction.is_active == True,
            OrderTransaction.direction == "in"
        )

        if start_date:
            query = query.filter(OrderTransaction.transaction_date >= start_date)
        if end_date:
            query = query.filter(OrderTransaction.transaction_date <= end_date)

        transactions = query.all()
        return sum(t.total_amount for t in transactions)

    @staticmethod
    def get_transactions_by_figure(
        db: Session,
        user_id: int,
        figure_id: int,
        transaction_type: str = None
    ):
        """
        获取手办的所有交易记录

        Args:
            db: 数据库会话
            user_id: 用户ID
            figure_id: 手办ID
            transaction_type: 交易类型过滤（可选）

        Returns:
            List[OrderTransaction]: 交易记录列表
        """
        query = db.query(OrderTransaction).filter(
            OrderTransaction.user_id == user_id,
            OrderTransaction.figure_id == figure_id,
            OrderTransaction.is_active == True
        )

        if transaction_type:
            query = query.filter(OrderTransaction.transaction_type == transaction_type)

        return query.all()

    @staticmethod
    def get_transactions_by_order(
        db: Session,
        user_id: int,
        order_id: int
    ):
        """
        获取订单的所有交易记录

        Args:
            db: 数据库会话
            user_id: 用户ID
            order_id: 订单ID

        Returns:
            List[OrderTransaction]: 交易记录列表
        """
        return db.query(OrderTransaction).filter(
            OrderTransaction.user_id == user_id,
            OrderTransaction.order_id == order_id,
            OrderTransaction.is_active == True
        ).all()
