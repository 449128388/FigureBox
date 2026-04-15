"""
订单资金流水服务层 - 处理手办资金变动的业务逻辑

功能说明：
- 解耦库存与资金：order_transactions 专注资金流水（资金账）
- 与 asset_transactions（库存账）配合使用，字段保持一致
- 支持手办创建、导入时的资金记录
"""

from sqlalchemy.orm import Session
from app.models.asset import OrderTransaction
from app.models.figure import Figure
from datetime import datetime


class OrderTransactionService:
    """订单资金流水服务类"""

    @staticmethod
    def create_transaction_from_figure(
        db: Session,
        user_id: int,
        figure: Figure,
        transaction_type: str = "full",
        notes: str = None
    ) -> OrderTransaction:
        """
        从手办创建资金流水记录

        使用场景：
        - 手办创建时记录资金支出
        - 手办导入时记录资金支出

        Args:
            db: 数据库会话
            user_id: 用户ID
            figure: 手办对象
            transaction_type: 交易类型 (full=全款, deposit=定金, balance=尾款)
            notes: 交易备注

        Returns:
            OrderTransaction: 创建的资金流水记录
        """
        # 计算交易金额
        purchase_price = figure.purchase_price or 0
        quantity = figure.quantity or 1
        total_amount = purchase_price * quantity

        # 【修复】无论入手价格是否为0，都创建资金流水记录，保证数据完整性
        # 价格为0的记录也是有效的交易记录，用于库存跟踪

        # 创建资金流水记录（与 asset_transactions 字段保持一致）
        transaction = OrderTransaction(
            user_id=user_id,
            figure_id=figure.id,
            order_id=None,  # 手办创建时没有关联订单
            transaction_type=transaction_type,
            quantity=quantity,  # 交易数量
            price=purchase_price,  # 交易单价
            total_amount=total_amount,  # 交易总金额（price × quantity）
            remaining_quantity=quantity,  # 初始剩余数量等于交易数量
            currency=figure.purchase_currency or "CNY",
            transaction_date=figure.purchase_date or datetime.now(),
            notes=notes or f"手办{'导入' if '导入' in (notes or '') else '创建'} - {figure.name}"
        )

        db.add(transaction)
        db.flush()  # 获取ID但不提交

        return transaction

    @staticmethod
    def create_transaction_from_order(
        db: Session,
        user_id: int,
        figure_id: int,
        order,
        transaction_type: str = None,
        notes: str = None
    ) -> OrderTransaction:
        """
        从订单创建资金流水记录

        使用场景：
        - 订单创建时记录定金/尾款支付
        - 订单状态变更时记录资金变动

        Args:
            db: Session,
            user_id: 用户ID
            figure_id: 手办ID
            order: 订单对象
            transaction_type: 交易类型 (deposit=定金, balance=尾款, full=全款)
            notes: 交易备注

        Returns:
            OrderTransaction: 创建的资金流水记录
        """
        # 根据订单状态确定交易类型和金额
        if transaction_type is None:
            # 根据订单已有金额判断
            if order.deposit > 0 and order.balance > 0:
                # 有定金和尾款，记录定金
                transaction_type = "deposit"
                price = order.deposit
            elif order.deposit > 0:
                transaction_type = "deposit"
                price = order.deposit
            elif order.balance > 0:
                transaction_type = "balance"
                price = order.balance
            else:
                # 【修复】没有金额信息时，也创建记录（价格为0）
                transaction_type = "full"
                price = 0
        else:
            # 根据指定类型获取金额
            if transaction_type == "deposit":
                price = order.deposit
            elif transaction_type == "balance":
                price = order.balance
            elif transaction_type == "full":
                price = order.deposit + order.balance
            else:
                price = 0

        # 【修复】无论价格是否为0，都创建资金流水记录，保证数据完整性
        # 价格为0的记录也是有效的交易记录

        quantity = 1  # 订单默认数量为1
        total_amount = price * quantity

        # 创建资金流水记录（与 asset_transactions 字段保持一致）
        transaction = OrderTransaction(
            user_id=user_id,
            figure_id=figure_id,
            order_id=order.id,
            transaction_type=transaction_type,
            quantity=quantity,  # 交易数量
            price=price,  # 交易单价
            total_amount=total_amount,  # 交易总金额（price × quantity）
            remaining_quantity=quantity,  # 初始剩余数量等于交易数量
            currency="CNY",  # 订单默认人民币
            transaction_date=datetime.now(),
            notes=notes or f"订单支付 - {transaction_type}"
        )

        db.add(transaction)
        db.flush()

        return transaction

    @staticmethod
    def get_figure_total_spending(
        db: Session,
        user_id: int,
        figure_id: int
    ) -> float:
        """
        获取手办的总支出金额

        Args:
            db: 数据库会话
            user_id: 用户ID
            figure_id: 手办ID

        Returns:
            float: 总支出金额
        """
        transactions = db.query(OrderTransaction).filter(
            OrderTransaction.user_id == user_id,
            OrderTransaction.figure_id == figure_id
        ).all()

        total = sum(t.total_amount for t in transactions if t.total_amount > 0)
        return total

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
            OrderTransaction.user_id == user_id
        )

        if start_date:
            query = query.filter(OrderTransaction.transaction_date >= start_date)
        if end_date:
            query = query.filter(OrderTransaction.transaction_date <= end_date)

        transactions = query.all()
        total = sum(t.total_amount for t in transactions if t.total_amount > 0)
        return total
