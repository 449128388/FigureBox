"""
交易创建服务
提供各类资金交易记录的创建功能
"""

from sqlalchemy.orm import Session
from app.models.asset import OrderTransaction
from app.services.figure_service.figure_price_service import FigurePriceService
from datetime import datetime


class TransactionCreateService:
    """交易创建服务类"""

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
        """
        if total_amount is None:
            total_amount = unit_price * quantity

        now = datetime.now()
        transaction = OrderTransaction(
            user_id=user_id,
            figure_id=figure_id,
            order_id=order_id,
            transaction_type="buy",
            direction="out",
            quantity=quantity,
            unit_price=unit_price,
            total_amount=total_amount,
            currency="CNY",
            payment_method=payment_method,
            payment_time=None,
            balance_payment_method=None,
            balance_payment_time=None,
            platform=platform,
            transaction_date=transaction_date or now,
            created_at=now,
            updated_at=now,
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
        """
        if total_amount is None:
            total_amount = unit_price * quantity

        now = datetime.now()
        transaction = OrderTransaction(
            user_id=user_id,
            figure_id=figure_id,
            order_id=order_id,
            transaction_type="sell",
            direction="in",
            quantity=quantity,
            unit_price=unit_price,
            total_amount=total_amount,
            currency="CNY",
            payment_method=payment_method,
            payment_time=None,
            balance_payment_method=None,
            balance_payment_time=None,
            platform=platform,
            transaction_date=transaction_date or now,
            created_at=now,
            updated_at=now,
            notes=notes
        )

        db.add(transaction)
        db.flush()
        return transaction

    @staticmethod
    def create_deposit_transaction(
        db: Session,
        user_id: int,
        figure_id: int,
        order_id: int = None,
        unit_price: float = 0,
        total_amount: float = None,
        payment_method: str = None,
        platform: str = None,
        transaction_date: datetime = None,
        notes: str = None
    ) -> OrderTransaction:
        """
        创建定金交易记录（资金流出）

        使用场景：
        - 已取消订单，只记录定金支出
        """
        if total_amount is None:
            total_amount = unit_price

        now = datetime.now()
        transaction = OrderTransaction(
            user_id=user_id,
            figure_id=figure_id,
            order_id=order_id,
            transaction_type="deposit",
            direction="out",
            quantity=0,
            unit_price=unit_price,
            total_amount=total_amount,
            currency="CNY",
            payment_method=payment_method,
            payment_time=None,
            balance_payment_method=None,
            balance_payment_time=None,
            platform=platform,
            transaction_date=transaction_date or now,
            created_at=now,
            updated_at=now,
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
        """
        if total_amount is None:
            total_amount = unit_price * quantity

        now = datetime.now()
        transaction = OrderTransaction(
            user_id=user_id,
            figure_id=figure_id,
            order_id=order_id,
            transaction_type="refund",
            direction="in",
            quantity=quantity,
            unit_price=unit_price,
            total_amount=total_amount,
            currency="CNY",
            payment_method=payment_method,
            payment_time=None,
            balance_payment_method=None,
            balance_payment_time=None,
            platform=platform,
            transaction_date=transaction_date or now,
            created_at=now,
            updated_at=now,
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
        """
        now = datetime.now()
        transaction = OrderTransaction(
            user_id=user_id,
            figure_id=figure_id,
            order_id=order_id,
            transaction_type="fee",
            direction="out",
            quantity=0,
            unit_price=total_amount,
            total_amount=total_amount,
            currency="CNY",
            payment_method=payment_method,
            payment_time=None,
            balance_payment_method=None,
            balance_payment_time=None,
            platform=platform,
            transaction_date=transaction_date or now,
            created_at=now,
            updated_at=now,
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
        从订单创建买入交易记录（初始记录）

        使用场景：
        - 订单创建时记录初始资金支出
        - 标记为 transaction_subtype='initial' 以便后续变更追踪
        """
        total_amount = FigurePriceService.calculate_order_amount_cny(
            deposit=order.deposit,
            deposit_currency=order.deposit_currency,
            balance=order.balance,
            balance_currency=order.balance_currency
        )
        quantity = 1  # 订单默认对应1体手办
        unit_price = total_amount / quantity if quantity > 0 and total_amount > 0 else 0

        if total_amount <= 0:
            return None

        now = datetime.now()
        # 使用订单的创建时间作为交易记录的创建和更新时间，保持与实际业务发生时间一致
        order_created_at = order.created_at if order.created_at else now
        order_updated_at = order.updated_at if order.updated_at else now
        transaction = OrderTransaction(
            user_id=user_id,
            figure_id=figure_id,
            order_id=order.id,
            transaction_type="buy",
            direction="out",
            quantity=quantity,
            unit_price=unit_price,
            total_amount=total_amount,
            currency="CNY",
            payment_method=order.payment_method,
            payment_time=order.payment_time,
            balance_payment_method=order.balance_payment_method,
            balance_payment_time=order.balance_payment_time,
            platform=order.shop_name,
            transaction_date=transaction_date or order_created_at,
            created_at=order_created_at,
            updated_at=order_updated_at,
            notes=notes or f"订单支付 - {order.shop_name or '未知店铺'}",
            transaction_subtype="initial",  # 标记为初始交易
            changed_field="total"  # 表示整单金额
        )

        db.add(transaction)
        db.flush()
        return transaction
