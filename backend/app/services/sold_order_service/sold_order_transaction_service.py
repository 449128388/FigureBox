"""
已出售订单交易服务

处理已出售订单与尾款管理（OrderTransaction）的联动
创建卖出订单主记录，作为其他模块的外键锚点
"""
from datetime import datetime
from typing import Optional
from sqlalchemy.orm import Session

from app.models.asset import OrderTransaction
from app.models.sold_order import SoldOrder
from app.services.currency_service import CurrencyService


class SoldOrderTransactionService:
    """
    已出售订单交易服务类

    负责在创建已出售订单时，同步创建尾款管理中的卖出订单主记录
    """

    @staticmethod
    def create_sell_order_transaction(
        db: Session,
        sold_order: SoldOrder,
        current_user_id: int
    ) -> OrderTransaction:
        """
        创建卖出订单主记录（类型标记为 sell）

        作为资金流水的外键锚点，记录：
        - 买家信息、平台、卖出价、物流单号、状态
        - 生成订单 ID，供其他模块引用

        Args:
            db: 数据库会话
            sold_order: 已出售订单对象
            current_user_id: 当前用户ID

        Returns:
            创建的 OrderTransaction 对象
        """
        # 将卖出价格转换为人民币
        sell_price_cny = CurrencyService.to_cny(
            sold_order.sell_price,
            sold_order.sell_price_currency
        )

        # 构建备注信息（包含买家信息和物流单号）
        notes_parts = [f"已出售订单 #{sold_order.id}"]
        if sold_order.buyer_phone:
            notes_parts.append(f"买家电话: {sold_order.buyer_phone}")
        if sold_order.tracking_number:
            notes_parts.append(f"物流单号: {sold_order.tracking_number}")
        if sold_order.status:
            notes_parts.append(f"订单状态: {sold_order.status}")

        transaction = OrderTransaction(
            user_id=current_user_id,
            figure_id=sold_order.figure_id,
            order_id=None,  # 已出售订单不关联购买订单
            transaction_type="sell",
            direction="in",  # 卖出是资金流入
            quantity=1,  # 默认卖出1个
            unit_price=sell_price_cny,
            total_amount=sell_price_cny,
            currency="CNY",
            platform=sold_order.sell_platform,
            transaction_date=sold_order.shipping_date or datetime.now(),
            notes=" | ".join(notes_parts),
            transaction_subtype="initial",
            changed_field="sell_price"
        )

        db.add(transaction)
        db.flush()

        return transaction

    @staticmethod
    def create_shipping_fee_transaction(
        db: Session,
        sold_order: SoldOrder,
        current_user_id: int,
        parent_transaction_id: int
    ) -> OrderTransaction:
        """
        创建运费支出交易记录

        Args:
            db: 数据库会话
            sold_order: 已出售订单对象
            current_user_id: 当前用户ID
            parent_transaction_id: 关联的卖出订单交易ID

        Returns:
            创建的 OrderTransaction 对象
        """
        # 将运费转换为人民币
        shipping_fee_cny = CurrencyService.to_cny(
            sold_order.shipping_fee or 0,
            sold_order.shipping_fee_currency
        )

        if shipping_fee_cny <= 0:
            return None

        transaction = OrderTransaction(
            user_id=current_user_id,
            figure_id=sold_order.figure_id,
            order_id=None,
            transaction_type="fee",
            direction="out",  # 运费是资金流出
            quantity=0,
            unit_price=shipping_fee_cny,
            total_amount=shipping_fee_cny,
            currency="CNY",
            platform=sold_order.sell_platform,
            transaction_date=sold_order.shipping_date or datetime.now(),
            notes=f"已出售订单 #{sold_order.id} - 运费支出",
            parent_transaction_id=parent_transaction_id,
            transaction_subtype="supplement",
            changed_field="shipping_fee"
        )

        db.add(transaction)
        db.flush()

        return transaction

    @staticmethod
    def create_platform_fee_transaction(
        db: Session,
        sold_order: SoldOrder,
        current_user_id: int,
        parent_transaction_id: int
    ) -> OrderTransaction:
        """
        创建平台手续费支出交易记录

        Args:
            db: 数据库会话
            sold_order: 已出售订单对象
            current_user_id: 当前用户ID
            parent_transaction_id: 关联的卖出订单交易ID

        Returns:
            创建的 OrderTransaction 对象
        """
        # 将手续费转换为人民币
        platform_fee_cny = CurrencyService.to_cny(
            sold_order.platform_fee or 0,
            sold_order.platform_fee_currency
        )

        if platform_fee_cny <= 0:
            return None

        transaction = OrderTransaction(
            user_id=current_user_id,
            figure_id=sold_order.figure_id,
            order_id=None,
            transaction_type="fee",
            direction="out",  # 手续费是资金流出
            quantity=0,
            unit_price=platform_fee_cny,
            total_amount=platform_fee_cny,
            currency="CNY",
            platform=sold_order.sell_platform,
            transaction_date=sold_order.shipping_date or datetime.now(),
            notes=f"已出售订单 #{sold_order.id} - 平台手续费",
            parent_transaction_id=parent_transaction_id,
            transaction_subtype="supplement",
            changed_field="platform_fee"
        )

        db.add(transaction)
        db.flush()

        return transaction

    @staticmethod
    def create_all_sold_order_transactions(
        db: Session,
        sold_order: SoldOrder,
        current_user_id: int
    ) -> dict:
        """
        创建已出售订单的所有资金流水记录

        创建3笔资金流水：
        1. 收入（卖出价）- sell 类型
        2. 支出（运费）- fee 类型
        3. 支出（手续费）- fee 类型

        Args:
            db: 数据库会话
            sold_order: 已出售订单对象
            current_user_id: 当前用户ID

        Returns:
            包含所有创建的交易记录ID的字典
        """
        # 1. 创建卖出订单主记录
        sell_transaction = SoldOrderTransactionService.create_sell_order_transaction(
            db, sold_order, current_user_id
        )

        # 2. 创建运费支出记录
        shipping_transaction = SoldOrderTransactionService.create_shipping_fee_transaction(
            db, sold_order, current_user_id, sell_transaction.id
        )

        # 3. 创建手续费支出记录
        platform_fee_transaction = SoldOrderTransactionService.create_platform_fee_transaction(
            db, sold_order, current_user_id, sell_transaction.id
        )

        return {
            "sell_transaction_id": sell_transaction.id,
            "shipping_transaction_id": shipping_transaction.id if shipping_transaction else None,
            "platform_fee_transaction_id": platform_fee_transaction.id if platform_fee_transaction else None
        }
