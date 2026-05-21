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
from .currency_service import CurrencyService


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

        unit_price 定义为净单价（每体实际到账金额）：
        unit_price = (卖出单价 × 数量 − 运费 − 手续费) / 数量

        Args:
            db: 数据库会话
            sold_order: 已出售订单对象
            current_user_id: 当前用户ID

        Returns:
            创建的 OrderTransaction 对象
        """
        # 获取数量
        quantity = sold_order.quantity or 1

        # 将卖出价格转换为人民币
        sell_price_cny = CurrencyService.to_cny(
            sold_order.sell_price,
            sold_order.sell_price_currency
        )

        # 将运费转换为人民币
        shipping_fee_cny = CurrencyService.to_cny(
            sold_order.shipping_fee or 0,
            sold_order.shipping_fee_currency
        )

        # 将手续费转换为人民币
        platform_fee_cny = CurrencyService.to_cny(
            sold_order.platform_fee or 0,
            sold_order.platform_fee_currency
        )

        # 计算净单价（每体实际到账金额）
        # unit_price = (卖出单价 × 数量 − 运费 − 手续费) / 数量
        total_sell_amount = sell_price_cny * quantity
        net_amount = total_sell_amount - shipping_fee_cny - platform_fee_cny
        unit_price = net_amount / quantity if quantity > 0 else 0

        # 构建备注信息（包含买家信息和物流单号）
        notes_parts = [f"已出售订单 #{sold_order.id}"]
        if sold_order.buyer_phone:
            notes_parts.append(f"买家电话: {sold_order.buyer_phone}")
        if sold_order.tracking_number:
            notes_parts.append(f"物流单号: {sold_order.tracking_number}")
        if sold_order.status:
            notes_parts.append(f"订单状态: {sold_order.status}")

        now = datetime.now()
        transaction = OrderTransaction(
            user_id=current_user_id,
            figure_id=sold_order.figure_id,
            order_id=None,  # 已出售订单不关联购买订单
            sold_order_id=sold_order.id,  # 关联卖出订单ID
            transaction_type="sell",
            direction="in",  # 卖出是资金流入
            quantity=quantity,
            unit_price=unit_price,
            total_amount=net_amount,
            currency="CNY",
            platform=sold_order.sell_platform,
            transaction_date=sold_order.shipping_date or now,
            created_at=now,
            updated_at=now,
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

        now = datetime.now()
        transaction = OrderTransaction(
            user_id=current_user_id,
            figure_id=sold_order.figure_id,
            order_id=None,
            sold_order_id=sold_order.id,  # 关联卖出订单ID
            transaction_type="fee",
            direction="out",  # 运费是资金流出
            quantity=0,
            unit_price=shipping_fee_cny,
            total_amount=shipping_fee_cny,
            currency="CNY",
            platform=sold_order.sell_platform,
            transaction_date=sold_order.shipping_date or now,
            created_at=now,
            updated_at=now,
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

        now = datetime.now()
        transaction = OrderTransaction(
            user_id=current_user_id,
            figure_id=sold_order.figure_id,
            order_id=None,
            sold_order_id=sold_order.id,  # 关联卖出订单ID
            transaction_type="fee",
            direction="out",  # 手续费是资金流出
            quantity=0,
            unit_price=platform_fee_cny,
            total_amount=platform_fee_cny,
            currency="CNY",
            platform=sold_order.sell_platform,
            transaction_date=sold_order.shipping_date or now,
            created_at=now,
            updated_at=now,
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

    @staticmethod
    def update_sold_order_transactions(
        db: Session,
        sold_order: SoldOrder,
        current_user_id: int
    ) -> dict:
        """
        更新已出售订单的资金流水记录

        当修改卖出价、运费、手续费时，更新对应的 order_transactions 记录：
        1. 更新卖出收入记录（sell 类型）- 修改卖出价时
        2. 更新运费支出记录（fee 类型）- 修改运费时
        3. 更新手续费支出记录（fee 类型）- 修改手续费时

        Args:
            db: 数据库会话
            sold_order: 已出售订单对象
            current_user_id: 当前用户ID

        Returns:
            包含更新的交易记录ID的字典
        """
        result = {
            "sell_transaction_updated": False,
            "shipping_transaction_updated": False,
            "platform_fee_transaction_updated": False
        }

        now = datetime.now()

        # 1. 更新卖出收入记录（sell 类型）
        sell_transaction = db.query(OrderTransaction).filter(
            OrderTransaction.sold_order_id == sold_order.id,
            OrderTransaction.transaction_type == "sell",
            OrderTransaction.is_active == True
        ).first()

        if sell_transaction:
            # 获取数量
            quantity = sold_order.quantity or 1

            # 将卖出价格转换为人民币
            sell_price_cny = CurrencyService.to_cny(
                sold_order.sell_price,
                sold_order.sell_price_currency
            )

            # 将运费转换为人民币
            shipping_fee_cny = CurrencyService.to_cny(
                sold_order.shipping_fee or 0,
                sold_order.shipping_fee_currency
            )

            # 将手续费转换为人民币
            platform_fee_cny = CurrencyService.to_cny(
                sold_order.platform_fee or 0,
                sold_order.platform_fee_currency
            )

            # 计算净单价（每体实际到账金额）
            # unit_price = (卖出单价 × 数量 − 运费 − 手续费) / 数量
            total_sell_amount = sell_price_cny * quantity
            net_amount = total_sell_amount - shipping_fee_cny - platform_fee_cny
            unit_price = net_amount / quantity if quantity > 0 else 0

            sell_transaction.quantity = quantity
            sell_transaction.unit_price = unit_price
            sell_transaction.total_amount = net_amount
            sell_transaction.updated_at = now
            result["sell_transaction_updated"] = True

        # 2. 更新运费支出记录（fee 类型）
        shipping_transaction = db.query(OrderTransaction).filter(
            OrderTransaction.sold_order_id == sold_order.id,
            OrderTransaction.transaction_type == "fee",
            OrderTransaction.changed_field == "shipping_fee",
            OrderTransaction.is_active == True
        ).first()

        if shipping_transaction:
            shipping_fee_cny = CurrencyService.to_cny(
                sold_order.shipping_fee or 0,
                sold_order.shipping_fee_currency
            )
            if shipping_fee_cny > 0:
                shipping_transaction.unit_price = shipping_fee_cny
                shipping_transaction.total_amount = shipping_fee_cny
                shipping_transaction.updated_at = now
                result["shipping_transaction_updated"] = True
            else:
                # 如果运费变为0，软删除该记录
                shipping_transaction.is_active = False
                shipping_transaction.deleted_at = now
                shipping_transaction.updated_at = now
                result["shipping_transaction_updated"] = True
        elif (sold_order.shipping_fee or 0) > 0 and sell_transaction:
            # 如果之前没有运费记录，但现在有运费了，创建新记录
            SoldOrderTransactionService.create_shipping_fee_transaction(
                db, sold_order, current_user_id, sell_transaction.id
            )
            result["shipping_transaction_updated"] = True

        # 3. 更新手续费支出记录（fee 类型）
        platform_fee_transaction = db.query(OrderTransaction).filter(
            OrderTransaction.sold_order_id == sold_order.id,
            OrderTransaction.transaction_type == "fee",
            OrderTransaction.changed_field == "platform_fee",
            OrderTransaction.is_active == True
        ).first()

        if platform_fee_transaction:
            platform_fee_cny = CurrencyService.to_cny(
                sold_order.platform_fee or 0,
                sold_order.platform_fee_currency
            )
            if platform_fee_cny > 0:
                platform_fee_transaction.unit_price = platform_fee_cny
                platform_fee_transaction.total_amount = platform_fee_cny
                platform_fee_transaction.updated_at = now
                result["platform_fee_transaction_updated"] = True
            else:
                # 如果手续费变为0，软删除该记录
                platform_fee_transaction.is_active = False
                platform_fee_transaction.deleted_at = now
                platform_fee_transaction.updated_at = now
                result["platform_fee_transaction_updated"] = True
        elif (sold_order.platform_fee or 0) > 0 and sell_transaction:
            # 如果之前没有手续费记录，但现在有手续费了，创建新记录
            SoldOrderTransactionService.create_platform_fee_transaction(
                db, sold_order, current_user_id, sell_transaction.id
            )
            result["platform_fee_transaction_updated"] = True

        db.flush()
        return result

    @staticmethod
    def update_sell_transaction_quantity(
        db: Session,
        sold_order: SoldOrder,
        current_user_id: int,
        new_quantity: int
    ) -> dict:
        """
        更新卖出交易记录的数量

        当卖出数量变更时，更新 order_transactions 中 sell 类型的记录：
        - quantity = 新数量
        - total_amount = (卖出单价 × 新数量)
        - unit_price = total_amount / 新数量

        Args:
            db: 数据库会话
            sold_order: 已出售订单对象
            current_user_id: 当前用户ID
            new_quantity: 新数量

        Returns:
            更新结果字典
        """
        result = {
            "sell_transaction_updated": False,
            "error": None
        }

        now = datetime.now()

        # 查找卖出收入记录（sell 类型）
        sell_transaction = db.query(OrderTransaction).filter(
            OrderTransaction.sold_order_id == sold_order.id,
            OrderTransaction.transaction_type == "sell",
            OrderTransaction.is_active == True
        ).first()

        if not sell_transaction:
            result["error"] = "未找到对应的卖出交易记录"
            return result

        # 将卖出价格转换为人民币
        sell_price_cny = CurrencyService.to_cny(
            sold_order.sell_price,
            sold_order.sell_price_currency
        )

        # 计算新的总金额（卖出单价 × 新数量）
        new_total_amount = sell_price_cny * new_quantity

        # 更新交易记录
        sell_transaction.quantity = new_quantity
        sell_transaction.total_amount = new_total_amount
        sell_transaction.unit_price = sell_price_cny
        sell_transaction.updated_at = now

        result["sell_transaction_updated"] = True
        db.flush()
        return result
