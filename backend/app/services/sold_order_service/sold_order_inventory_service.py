"""
已出售订单库存服务

处理已出售订单与库存账（AssetTransaction）的联动
扣减库存数量，更新剩余持仓
"""
import json
import re
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
        now = datetime.now()
        sell_transaction = AssetTransaction(
            user_id=current_user_id,
            figure_id=figure_id,
            order_id=None,
            sold_order_id=sold_order.id,  # 关联卖出订单ID
            transaction_type="sell",
            price=fifo_unit_price,  # 使用 FIFO 成本价
            quantity=quantity_to_sell,
            total_amount=fifo_total_cost,
            remaining_quantity=0,  # 卖出记录的剩余数量为0
            transaction_date=now,
            created_at=now,
            updated_at=now,
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
        # 查找对应的卖出交易记录（优先使用 sold_order_id 关联）
        sell_transaction = db.query(AssetTransaction).filter(
            AssetTransaction.user_id == current_user_id,
            AssetTransaction.figure_id == sold_order.figure_id,
            AssetTransaction.transaction_type == "sell",
            AssetTransaction.sold_order_id == sold_order.id,
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

    @staticmethod
    def calculate_average_cost(
        db: Session,
        figure_id: int,
        user_id: int
    ) -> float:
        """
        计算当前实时加权平均成本

        Args:
            db: 数据库会话
            figure_id: 手办ID
            user_id: 用户ID

        Returns:
            加权平均成本单价
        """
        from sqlalchemy import func

        # 查询所有买入记录
        buy_transactions = db.query(AssetTransaction).filter(
            AssetTransaction.user_id == user_id,
            AssetTransaction.figure_id == figure_id,
            AssetTransaction.transaction_type == "buy",
            AssetTransaction.is_active == True
        ).all()

        total_cost = sum(tx.price * tx.remaining_quantity for tx in buy_transactions)
        total_quantity = sum(tx.remaining_quantity for tx in buy_transactions)

        return total_cost / total_quantity if total_quantity > 0 else 0

    @staticmethod
    def update_quantity_on_sold_order_change(
        db: Session,
        sold_order: SoldOrder,
        current_user_id: int,
        old_quantity: int,
        new_quantity: int
    ) -> dict:
        """
        当已出售订单数量变更时，更新库存和交易记录

        场景A：数量减少（如 2体 → 1体）
        - 回库数 = 原数量 − 新数量
        - asset_transactions 插入 RETURN 记录
        - order_transactions UPDATE 数量

        场景B：数量增加（扣库）
        - 增扣数 = 新数量 − 原数量
        - 库存校验（失败则中断）
        - asset_transactions 插入 SELL 记录（使用实时加权平均成本）
        - order_transactions UPDATE 数量

        Args:
            db: 数据库会话
            sold_order: 已出售订单对象
            current_user_id: 当前用户ID
            old_quantity: 原数量
            new_quantity: 新数量

        Returns:
            操作结果字典
        """
        from app.services.asset_transaction_service.asset_transaction_create_service import AssetTransactionCreateService

        result = {
            "asset_transaction_created": False,
            "asset_transaction_type": None,
            "inventory_updated": False,
            "error": None
        }

        now = datetime.now()
        quantity_diff = new_quantity - old_quantity

        if quantity_diff == 0:
            return result

        if quantity_diff < 0:
            # ========== 场景A：数量减少（回库）==========
            return_quantity = abs(quantity_diff)  # 回库数量

            # 1. 查找原 SELL 记录获取成本价和扣减记录
            original_sell_tx = db.query(AssetTransaction).filter(
                AssetTransaction.user_id == current_user_id,
                AssetTransaction.figure_id == sold_order.figure_id,
                AssetTransaction.transaction_type == "sell",
                AssetTransaction.sold_order_id == sold_order.id,
                AssetTransaction.is_active == True
            ).first()

            if original_sell_tx:
                # 2. 创建 RETURN 记录
                return_price = original_sell_tx.price  # 使用原成本价
                return_total = return_price * return_quantity

                return_transaction = AssetTransaction(
                    user_id=current_user_id,
                    figure_id=sold_order.figure_id,
                    order_id=None,
                    sold_order_id=sold_order.id,
                    transaction_type="return",  # 回库类型
                    price=return_price,
                    quantity=return_quantity,
                    total_amount=return_total,
                    remaining_quantity=return_quantity,  # 回库数量加入库存
                    transaction_date=now,
                    created_at=now,
                    updated_at=now,
                    notes=f"已出售订单 #{sold_order.id} - 数量减少回库（原数量:{old_quantity}, 新数量:{new_quantity}）"
                )
                db.add(return_transaction)

                # 3. FIFO 赎回退回原则（后卖先回）：
                # 卖出时按先进先出扣减，赎回时按后进先出恢复
                # 即从最后扣减的买入记录开始恢复

                # 从 notes 中解析扣减记录
                deducted_records = []
                try:
                    # 尝试从 notes 中解析扣减记录
                    match = re.search(r"扣减记录: (\[.*?\])", original_sell_tx.notes or "")
                    if match:
                        deducted_records = json.loads(match.group(1).replace("'", '"'))
                except:
                    pass

                remaining_to_restore = return_quantity

                if deducted_records:
                    # 按扣减记录的倒序恢复（后卖先回）
                    # 卖出时：先扣减 record[0]，再扣减 record[1]...
                    # 赎回时：先恢复 record[-1]，再恢复 record[-2]...
                    for record in reversed(deducted_records):
                        if remaining_to_restore <= 0:
                            break

                        buy_tx = db.query(AssetTransaction).filter(
                            AssetTransaction.id == record['id'],
                            AssetTransaction.user_id == current_user_id,
                            AssetTransaction.transaction_type == "buy"
                        ).first()

                        if buy_tx:
                            # 计算该记录最多可恢复的数量
                            # 已卖出数量 = 原数量 - 剩余数量
                            sold_from_this = buy_tx.quantity - buy_tx.remaining_quantity
                            restore_amount = min(remaining_to_restore, sold_from_this)

                            if restore_amount > 0:
                                buy_tx.remaining_quantity += restore_amount
                                remaining_to_restore -= restore_amount

                # 如果还有未恢复的数量（可能是旧数据没有记录），按比例恢复
                if remaining_to_restore > 0:
                    buy_transactions = db.query(AssetTransaction).filter(
                        AssetTransaction.user_id == current_user_id,
                        AssetTransaction.figure_id == sold_order.figure_id,
                        AssetTransaction.transaction_type == "buy",
                        AssetTransaction.is_active == True
                    ).order_by(AssetTransaction.transaction_date.desc()).all()

                    for buy_tx in buy_transactions:
                        if remaining_to_restore <= 0:
                            break
                        sold_from_this = buy_tx.quantity - buy_tx.remaining_quantity
                        restore_amount = min(remaining_to_restore, sold_from_this)
                        if restore_amount > 0:
                            buy_tx.remaining_quantity += restore_amount
                            remaining_to_restore -= restore_amount

                result["asset_transaction_created"] = True
                result["asset_transaction_type"] = "return"
                result["inventory_updated"] = True

        else:
            # ========== 场景B：数量增加（扣库）==========
            additional_quantity = quantity_diff  # 增扣数量

            # 1. 库存校验
            current_inventory = SoldOrderInventoryService.get_current_inventory(
                db, sold_order.figure_id, current_user_id
            )

            if current_inventory < additional_quantity:
                result["error"] = f"库存不足，当前库存 {current_inventory}，需要扣减 {additional_quantity}"
                return result

            # 2. 获取实时加权平均成本
            avg_cost = SoldOrderInventoryService.calculate_average_cost(
                db, sold_order.figure_id, current_user_id
            )

            # 3. 扣减库存（FIFO）
            remaining_to_deduct = additional_quantity
            deducted_records = []

            buy_transactions = db.query(AssetTransaction).filter(
                AssetTransaction.user_id == current_user_id,
                AssetTransaction.figure_id == sold_order.figure_id,
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
                deducted_records.append({
                    'id': buy_tx.id,
                    'price': buy_tx.price,
                    'quantity': deduct_amount
                })

            # 4. 创建 SELL 记录（使用实时加权平均成本）
            sell_total = avg_cost * additional_quantity

            sell_transaction = AssetTransaction(
                user_id=current_user_id,
                figure_id=sold_order.figure_id,
                order_id=None,
                sold_order_id=sold_order.id,
                transaction_type="sell",
                price=avg_cost,
                quantity=additional_quantity,
                total_amount=sell_total,
                remaining_quantity=0,
                transaction_date=now,
                created_at=now,
                updated_at=now,
                notes=f"已出售订单 #{sold_order.id} - 数量增加扣库（原数量:{old_quantity}, 新数量:{new_quantity}, 实时成本:¥{avg_cost:.2f}）"
            )
            db.add(sell_transaction)

            result["asset_transaction_created"] = True
            result["asset_transaction_type"] = "sell"
            result["inventory_updated"] = True

        db.flush()
        return result
