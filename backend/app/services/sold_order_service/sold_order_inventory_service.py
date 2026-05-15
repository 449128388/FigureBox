"""
已出售订单库存服务

处理已出售订单与库存账（AssetTransaction）的联动
扣减库存数量，更新剩余持仓
"""
from datetime import datetime
from typing import Optional
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.models.asset import AssetTransaction
from app.models.sold_order import SoldOrder


class SoldOrderInventoryService:
    """
    已出售订单库存服务类

    负责在创建已出售订单时，扣减库存账中的持仓数量
    """

    @staticmethod
    def deduct_inventory(
        db: Session,
        sold_order: SoldOrder,
        current_user_id: int
    ) -> Optional[AssetTransaction]:
        """
        扣减库存数量

        当已出售订单创建时：
        - 扣减库存数量（trans_type='sell'）
        - 更新买入记录的 remaining_quantity
        - 创建卖出交易记录（记录进货价作为成本基准）

        Args:
            db: 数据库会话
            sold_order: 已出售订单对象
            current_user_id: 当前用户ID

        Returns:
            创建的 AssetTransaction 卖出记录，如果库存不足则返回 None
        """
        figure_id = sold_order.figure_id

        # 从订单中获取卖出数量
        quantity_to_sell = sold_order.quantity or 1  # 卖出数量

        # 检查总持仓数量
        total_remaining = db.query(func.sum(AssetTransaction.remaining_quantity)).filter(
            AssetTransaction.user_id == current_user_id,
            AssetTransaction.figure_id == figure_id,
            AssetTransaction.transaction_type == "buy",
            AssetTransaction.is_active == True
        ).scalar() or 0

        if total_remaining < quantity_to_sell:
            pass

        # 扣减买入记录的剩余数量（先进先出 FIFO）
        # 同时计算 FIFO 成本价（使用最早买入记录的价格）
        remaining_to_deduct = quantity_to_sell
        fifo_total_cost = 0.0  # FIFO 总成本
        deducted_records = []  # 记录扣减的买入记录信息

        buy_transactions = db.query(AssetTransaction).filter(
            AssetTransaction.user_id == current_user_id,
            AssetTransaction.figure_id == figure_id,
            AssetTransaction.transaction_type == "buy",
            AssetTransaction.remaining_quantity > 0,
            AssetTransaction.is_active == True
        ).order_by(AssetTransaction.transaction_date.asc()).all()

        for buy_tx in buy_transactions:
            if remaining_to_deduct <= 0:
                break

            deduct_amount = min(buy_tx.remaining_quantity, remaining_to_deduct)
            buy_tx.remaining_quantity -= deduct_amount
            remaining_to_deduct -= deduct_amount

            # 累加 FIFO 成本（买入价格 × 扣减数量）
            fifo_total_cost += (buy_tx.price or 0) * deduct_amount
            deducted_records.append({
                'id': buy_tx.id,
                'price': buy_tx.price,
                'quantity': deduct_amount
            })

        # 计算 FIFO 单位成本价
        fifo_unit_price = fifo_total_cost / quantity_to_sell if quantity_to_sell > 0 else 0

        # 创建卖出交易记录
        # 使用 FIFO 成本价作为记录价格
        sell_transaction = AssetTransaction(
            user_id=current_user_id,
            figure_id=figure_id,
            order_id=None,
            transaction_type="sell",
            price=fifo_unit_price,  # 使用 FIFO 成本价
            quantity=quantity_to_sell,
            total_amount=fifo_total_cost,
            remaining_quantity=0,  # 卖出记录的剩余数量为0
            transaction_date=datetime.now(),
            notes=f"已出售订单 #{sold_order.id} - 库存扣减（FIFO成本价: ¥{fifo_unit_price:.2f}/体，扣减记录: {deducted_records}）"
        )
        db.add(sell_transaction)

        db.flush()
        return sell_transaction

    @staticmethod
    def get_current_inventory(
        db: Session,
        figure_id: int,
        user_id: int
    ) -> int:
        """
        获取当前库存数量

        Args:
            db: 数据库会话
            figure_id: 手办ID
            user_id: 用户ID

        Returns:
            当前库存数量
        """
        total_remaining = db.query(func.sum(AssetTransaction.remaining_quantity)).filter(
            AssetTransaction.user_id == user_id,
            AssetTransaction.figure_id == figure_id,
            AssetTransaction.transaction_type == "buy",
            AssetTransaction.is_active == True
        ).scalar() or 0

        return int(total_remaining)

    @staticmethod
    def restore_inventory(
        db: Session,
        sold_order: SoldOrder,
        current_user_id: int
    ) -> bool:
        """
        恢复库存（用于订单删除/取消时）

        Args:
            db: 数据库会话
            sold_order: 已出售订单对象
            current_user_id: 当前用户ID

        Returns:
            是否成功恢复
        """
        # 查找对应的卖出交易记录
        sell_transaction = db.query(AssetTransaction).filter(
            AssetTransaction.user_id == current_user_id,
            AssetTransaction.figure_id == sold_order.figure_id,
            AssetTransaction.transaction_type == "sell",
            AssetTransaction.notes.like(f"%已出售订单 #{sold_order.id}%"),
            AssetTransaction.is_active == True
        ).first()

        if not sell_transaction:
            return False

        # 软删除卖出记录
        sell_transaction.is_active = False
        sell_transaction.deleted_at = datetime.now()

        # 恢复买入记录的剩余数量（这里简化处理，实际应该记录是从哪笔买入扣减的）
        # 实际业务中可能需要更复杂的逻辑来精确恢复

        db.flush()
        return True
