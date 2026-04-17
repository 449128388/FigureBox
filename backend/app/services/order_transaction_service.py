"""
订单资金流水服务层 - 处理手办资金变动的业务逻辑

核心原则：
- 只记录有真实资金流动的交易
- 严禁记录无资金流动的场景（库存调整、价格调整等）
- 资金账与库存账完全解耦

必须记录的场景（有真实资金流动）：
- 订单支付（买入）：trans_type='buy', direction='out'
- 订单收款（卖出）：trans_type='sell', direction='in'
- 定金支付：trans_type='buy', direction='out'
- 尾款支付：trans_type='buy', direction='out'
- 退款（退货/取消）：trans_type='refund', direction='in'
- 平台手续费：trans_type='fee', direction='out'

严禁记录的场景（无资金流动）：
- 库存调整（纠错）：不记录，或记 amount=0（占位）
- 冲正库存（数量减少）：不记录，库存账用 adjust 类型
- 价格调整（估值变化）：不记录，这是资产重估，非现金流
- 自动创建手办（无订单）：不记录，等补录订单后再记
"""

from sqlalchemy.orm import Session
from app.models.asset import OrderTransaction
from app.models.figure import Figure
from datetime import datetime


class OrderTransactionService:
    """订单资金流水服务类"""

    @staticmethod
    def create_buy_transaction(
        db: Session,
        user_id: int,
        figure_id: int,
        order_id: int = None,
        quantity: int = 1,
        unit_price: float = 0,
        total_amount: float = None,
        payment_method: str = None,
        platform: str = None,
        transaction_date: datetime = None,
        notes: str = None
    ) -> OrderTransaction:
        """
        创建买入交易记录（资金流出）

        使用场景：
        - 订单支付（全款/定金/尾款）
        - 手办购买

        Args:
            db: 数据库会话
            user_id: 用户ID
            figure_id: 手办ID
            order_id: 订单ID（可选）
            quantity: 交易数量
            unit_price: 交易单价
            total_amount: 交易总金额（默认 unit_price × quantity）
            payment_method: 支付方式（支付宝/微信/银行卡等）
            platform: 交易平台（淘宝/闲鱼/AmiAmi等）
            transaction_date: 交易发生时间（业务时间）
            notes: 交易备注

        Returns:
            OrderTransaction: 创建的资金流水记录
        """
        if total_amount is None:
            total_amount = unit_price * quantity

        transaction = OrderTransaction(
            user_id=user_id,
            figure_id=figure_id,
            order_id=order_id,
            transaction_type="buy",
            direction="out",  # 买入 = 资金流出
            quantity=quantity,
            unit_price=unit_price,
            total_amount=total_amount,
            currency="CNY",
            payment_method=payment_method,
            platform=platform,
            transaction_date=transaction_date or datetime.now(),
            notes=notes
        )

        db.add(transaction)
        db.flush()
        return transaction

    @staticmethod
    def create_sell_transaction(
        db: Session,
        user_id: int,
        figure_id: int,
        order_id: int = None,
        quantity: int = 1,
        unit_price: float = 0,
        total_amount: float = None,
        payment_method: str = None,
        platform: str = None,
        transaction_date: datetime = None,
        notes: str = None
    ) -> OrderTransaction:
        """
        创建卖出交易记录（资金流入）

        使用场景：
        - 闲鱼出售手办
        - 其他渠道卖出

        Args:
            db: 数据库会话
            user_id: 用户ID
            figure_id: 手办ID
            order_id: 订单ID（可选）
            quantity: 交易数量
            unit_price: 交易单价
            total_amount: 交易总金额（默认 unit_price × quantity）
            payment_method: 支付方式
            platform: 交易平台
            transaction_date: 交易发生时间（业务时间）
            notes: 交易备注

        Returns:
            OrderTransaction: 创建的资金流水记录
        """
        if total_amount is None:
            total_amount = unit_price * quantity

        transaction = OrderTransaction(
            user_id=user_id,
            figure_id=figure_id,
            order_id=order_id,
            transaction_type="sell",
            direction="in",  # 卖出 = 资金流入
            quantity=quantity,
            unit_price=unit_price,
            total_amount=total_amount,
            currency="CNY",
            payment_method=payment_method,
            platform=platform,
            transaction_date=transaction_date or datetime.now(),
            notes=notes
        )

        db.add(transaction)
        db.flush()
        return transaction

    @staticmethod
    def create_refund_transaction(
        db: Session,
        user_id: int,
        figure_id: int,
        order_id: int = None,
        quantity: int = 1,
        unit_price: float = 0,
        total_amount: float = None,
        payment_method: str = None,
        platform: str = None,
        transaction_date: datetime = None,
        notes: str = None
    ) -> OrderTransaction:
        """
        创建退款交易记录（资金流入）

        使用场景：
        - 订单取消退款
        - 退货退款

        Args:
            db: 数据库会话
            user_id: 用户ID
            figure_id: 手办ID
            order_id: 订单ID（可选）
            quantity: 交易数量
            unit_price: 交易单价
            total_amount: 交易总金额（默认 unit_price × quantity）
            payment_method: 支付方式
            platform: 交易平台
            transaction_date: 交易发生时间（业务时间）
            notes: 交易备注

        Returns:
            OrderTransaction: 创建的资金流水记录
        """
        if total_amount is None:
            total_amount = unit_price * quantity

        transaction = OrderTransaction(
            user_id=user_id,
            figure_id=figure_id,
            order_id=order_id,
            transaction_type="refund",
            direction="in",  # 退款 = 资金流入
            quantity=quantity,
            unit_price=unit_price,
            total_amount=total_amount,
            currency="CNY",
            payment_method=payment_method,
            platform=platform,
            transaction_date=transaction_date or datetime.now(),
            notes=notes
        )

        db.add(transaction)
        db.flush()
        return transaction

    @staticmethod
    def create_fee_transaction(
        db: Session,
        user_id: int,
        figure_id: int,
        order_id: int = None,
        total_amount: float = 0,
        payment_method: str = None,
        platform: str = None,
        transaction_date: datetime = None,
        notes: str = None
    ) -> OrderTransaction:
        """
        创建手续费交易记录（资金流出）

        使用场景：
        - 平台手续费（闲鱼扣费等）

        Args:
            db: 数据库会话
            user_id: 用户ID
            figure_id: 手办ID
            order_id: 订单ID（可选）
            total_amount: 手续费金额
            payment_method: 支付方式
            platform: 交易平台
            transaction_date: 交易发生时间（业务时间）
            notes: 交易备注

        Returns:
            OrderTransaction: 创建的资金流水记录
        """
        transaction = OrderTransaction(
            user_id=user_id,
            figure_id=figure_id,
            order_id=order_id,
            transaction_type="fee",
            direction="out",  # 手续费 = 资金流出
            quantity=0,  # 手续费没有数量概念
            unit_price=total_amount,  # 手续费金额作为单价
            total_amount=total_amount,
            currency="CNY",
            payment_method=payment_method,
            platform=platform,
            transaction_date=transaction_date or datetime.now(),
            notes=notes
        )

        db.add(transaction)
        db.flush()
        return transaction

    @staticmethod
    def create_transaction_from_order(
        db: Session,
        user_id: int,
        figure_id: int,
        order,
        transaction_date: datetime = None,
        notes: str = None
    ) -> OrderTransaction:
        """
        从订单创建买入交易记录

        使用场景：
        - 订单创建时记录资金支出

        Args:
            db: 数据库会话
            user_id: 用户ID
            figure_id: 手办ID
            order: 订单对象
            transaction_date: 交易发生时间（业务时间）
            notes: 交易备注

        Returns:
            OrderTransaction: 创建的资金流水记录
        """
        # 计算订单总金额
        total_amount = (order.deposit or 0) + (order.balance or 0)
        quantity = order.quantity or 1
        unit_price = total_amount / quantity if quantity > 0 and total_amount > 0 else 0

        # 如果订单金额为0，不创建资金流水记录（无真实资金流动）
        if total_amount <= 0:
            return None

        return OrderTransactionService.create_buy_transaction(
            db=db,
            user_id=user_id,
            figure_id=figure_id,
            order_id=order.id,
            quantity=quantity,
            unit_price=unit_price,
            total_amount=total_amount,
            platform=order.shop_name,  # 使用店铺名作为平台
            transaction_date=transaction_date or order.purchase_date or datetime.now(),
            notes=notes or f"订单支付 - {order.shop_name or '未知店铺'}"
        )

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
            OrderTransaction.direction == "out"  # 只统计资金流出
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
            OrderTransaction.direction == "in"  # 只统计资金流入
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
