"""
资产交易创建服务
提供创建各类资产交易记录的业务逻辑
"""
from datetime import datetime
from typing import Optional
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.models.asset import AssetTransaction
from app.models.order import Order


class AssetTransactionCreateService:
    """资产交易创建服务类"""

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
        total_amount = price if quantity == 0 else price * quantity

        transaction = AssetTransaction(
            user_id=user_id,
            figure_id=figure_id,
            order_id=order_id,
            transaction_type="buy",
            price=price,
            quantity=quantity,
            total_amount=total_amount,
            remaining_quantity=quantity,
            notes="自动创建：从订单管理数据中创建"
        )

        db.add(transaction)
        db.flush()

        return transaction

    @staticmethod
    def link_order_to_existing_transaction(
        db: Session,
        user_id: int,
        figure_id: int,
        order: Order,
        quantity: int = 1
    ) -> Optional[AssetTransaction]:
        """
        将订单关联到现有的库存交易记录（补录凭证模式）

        使用场景：
        - 用户创建订单时，将订单关联到手办创建时的原始交易记录
        - 不新增交易记录，避免手办数量虚增
        - 更新原有记录的 order_id 和备注信息

        查找逻辑：
        1. 查找该手办下无订单关联的买入记录（order_id IS NULL）
        2. 如果找到，更新 order_id 并添加补录备注
        3. 如果没找到，返回 None（表示所有库存记录都已关联订单）

        Args:
            db: Session: 数据库会话
            user_id: 用户ID
            figure_id: 手办ID
            order: 订单对象
            quantity: 数量，默认为1

        Returns:
            更新的交易记录对象，如果没有可关联的记录则返回 None
        """
        existing_transaction = db.query(AssetTransaction).filter(
            AssetTransaction.user_id == user_id,
            AssetTransaction.figure_id == figure_id,
            AssetTransaction.transaction_type == "buy",
            AssetTransaction.order_id.is_(None),
            AssetTransaction.remaining_quantity > 0
        ).first()

        if existing_transaction:
            existing_transaction.order_id = order.id
            existing_transaction.notes = f"补录凭证：订单 #{order.id} 关联到原有库存记录"
            db.flush()
            return existing_transaction

        return None

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

        库存账职责：
        - price 和 total_amount 记录的是出库成本（使用FIFO算法计算），而非卖出价
        - 卖出价应记录在资金账（OrderTransaction）中

        Args:
            db: 数据库会话
            user_id: 用户ID
            figure_id: 手办ID
            price: 卖出单价（用于资金账，库存账不使用此值）
            quantity: 卖出数量
            notes: 备注

        Returns:
            创建的交易记录对象，如果持仓不足返回None
        """
        total_remaining = db.query(func.sum(AssetTransaction.remaining_quantity)).filter(
            AssetTransaction.user_id == user_id,
            AssetTransaction.figure_id == figure_id,
            AssetTransaction.transaction_type == "buy"
        ).scalar() or 0

        if total_remaining < quantity:
            raise ValueError(f"持仓不足，当前持仓：{total_remaining}，尝试卖出：{quantity}")

        # 使用FIFO算法计算出库成本
        # 遍历买入记录，按时间顺序扣减并计算总成本
        remaining_to_deduct = quantity
        total_cost = 0.0  # 出库总成本
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
            total_cost += buy_tx.price * deduct_amount  # 使用买入时的成本价计算
            buy_tx.remaining_quantity -= deduct_amount
            remaining_to_deduct -= deduct_amount

        # 计算平均出库成本单价
        cost_price = total_cost / quantity if quantity > 0 else 0

        # 创建卖出交易记录，price 和 total_amount 使用出库成本，而非卖出价
        transaction = AssetTransaction(
            user_id=user_id,
            figure_id=figure_id,
            order_id=None,
            transaction_type="sell",
            price=round(cost_price, 2),  # FIFO出库成本单价
            quantity=quantity,
            total_amount=round(total_cost, 2),  # FIFO出库总成本
            remaining_quantity=0,
            notes=notes or "卖出交易"
        )
        db.add(transaction)
        db.flush()
        return transaction

    @staticmethod
    def create_buy_transaction_from_order(
        db: Session,
        user_id: int,
        figure_id: int,
        order,
        quantity: int = 1
    ) -> AssetTransaction:
        """
        从订单创建买入交易记录（库存账）

        使用场景：
        - 手办导入时，从订单数据创建库存交易记录
        - 记录库存数量变动

        Args:
            db: 数据库会话
            user_id: 用户ID
            figure_id: 手办ID
            order: 订单对象
            quantity: 购买数量，默认为1

        Returns:
            创建的交易记录对象
        """
        from app.services.figure_service.figure_price_service import FigurePriceService
        total_amount = FigurePriceService.calculate_order_amount_cny(
            deposit=order.deposit,
            deposit_currency=order.deposit_currency,
            balance=order.balance,
            balance_currency=order.balance_currency
        )
        unit_price = total_amount / quantity if quantity > 0 and total_amount > 0 else 0

        transaction = AssetTransaction(
            user_id=user_id,
            figure_id=figure_id,
            order_id=order.id,
            transaction_type="buy",
            price=unit_price,
            quantity=quantity,
            total_amount=total_amount,
            remaining_quantity=quantity,
            notes=f"订单导入 - {order.shop_name or '未知店铺'}"
        )

        db.add(transaction)
        db.flush()
        return transaction

    @staticmethod
    def create_quantity_adjustment_transaction(
        db: Session,
        user_id: int,
        figure_id: int,
        quantity_change: int,
        price: float,
        original_quantity: int,
        new_quantity: int
    ) -> AssetTransaction:
        """
        创建数量调整冲正交易记录

        使用场景：
        - 用户在手办管理中修改手办数量时
        - 数量增加：创建买入交易（补录）
        - 数量减少：创建冲正交易（adjust类型，quantity为负数）

        Args:
            db: 数据库会话
            user_id: 用户ID
            figure_id: 手办ID
            quantity_change: 数量变化（正数表示增加，负数表示减少）
            price: 单价（使用当前手办的入手价格）
            original_quantity: 原始数量
            new_quantity: 新数量

        Returns:
            创建的交易记录对象
        """
        total_amount = price * abs(quantity_change)

        if quantity_change > 0:
            transaction = AssetTransaction(
                user_id=user_id,
                figure_id=figure_id,
                order_id=None,
                transaction_type="buy",
                price=price,
                quantity=quantity_change,
                total_amount=total_amount,
                remaining_quantity=quantity_change,
                notes=f"数量调整补录：{original_quantity} → {new_quantity}（+{quantity_change}）"
            )
        else:
            transaction = AssetTransaction(
                user_id=user_id,
                figure_id=figure_id,
                order_id=None,
                transaction_type="adjust",
                price=price,
                quantity=quantity_change,
                total_amount=-total_amount,
                remaining_quantity=0,
                notes=f"数量调整冲正：{original_quantity} → {new_quantity}（{quantity_change}）"
            )

            remaining_to_deduct = abs(quantity_change)
            buy_transactions = db.query(AssetTransaction).filter(
                AssetTransaction.user_id == user_id,
                AssetTransaction.figure_id == figure_id,
                AssetTransaction.transaction_type.in_(["buy"]),
                AssetTransaction.remaining_quantity > 0
            ).order_by(AssetTransaction.transaction_date.desc()).all()

            for buy_tx in buy_transactions:
                if remaining_to_deduct <= 0:
                    break
                deduct_amount = min(buy_tx.remaining_quantity, remaining_to_deduct)
                buy_tx.remaining_quantity -= deduct_amount
                remaining_to_deduct -= deduct_amount

        db.add(transaction)
        db.flush()
        return transaction

    @staticmethod
    def create_price_adjustment_transaction(
        db: Session,
        user_id: int,
        figure_id: int,
        old_price: float,
        new_price: float,
        quantity: int
    ) -> AssetTransaction:
        """
        创建价格调整记录

        使用场景：
        - 用户在手办管理中修改入手价格时
        - 记录价格变更历史

        Args:
            db: 数据库会话
            user_id: 用户ID
            figure_id: 手办ID
            old_price: 原价格
            new_price: 新价格
            quantity: 手办数量

        Returns:
            创建的交易记录对象
        """
        price_diff = new_price - old_price
        total_diff = price_diff * quantity

        transaction = AssetTransaction(
            user_id=user_id,
            figure_id=figure_id,
            order_id=None,
            transaction_type="adjust",
            price=price_diff,
            quantity=quantity,
            total_amount=total_diff,
            remaining_quantity=None,
            notes=f"价格调整：¥{old_price} → ¥{new_price}（差值：¥{price_diff}）"
        )

        db.add(transaction)
        db.flush()
        return transaction
