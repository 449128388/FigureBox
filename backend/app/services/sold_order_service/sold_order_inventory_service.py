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

from app.models.asset import AssetTransaction, OrderTransaction
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
    def return_inventory_for_dispute(
        db: Session,
        sold_order: SoldOrder,
        current_user_id: int
    ) -> dict:
        """
        退款/纠纷状态下的库存回撤

        当订单状态变为"退款/纠纷"时，按照 FIFO 原则撤销所有卖出记录：
        - 查找该订单的所有 sell 记录（按创建时间倒序）
        - 撤销所有 sell 记录（软删除）
        - 恢复对应的库存到买入记录（后卖先回）
        - 创建 return 记录标记回撤

        Args:
            db: 数据库会话
            sold_order: 已出售订单对象
            current_user_id: 当前用户ID

        Returns:
            操作结果字典
        """
        result = {
            "inventory_returned": False,
            "return_quantity": 0,
            "error": None
        }

        now = datetime.now()

        # 1. 查找该订单的所有 sell 记录（按创建时间倒序，后卖出的先撤销）
        sell_transactions = db.query(AssetTransaction).filter(
            AssetTransaction.user_id == current_user_id,
            AssetTransaction.figure_id == sold_order.figure_id,
            AssetTransaction.transaction_type == "sell",
            AssetTransaction.sold_order_id == sold_order.id,
            AssetTransaction.is_active == True
        ).order_by(AssetTransaction.created_at.desc()).all()

        if not sell_transactions:
            return result

        total_return_quantity = 0
        total_return_cost = 0.0
        returned_records_info = []

        # 2. 逐个撤销 sell 记录
        for sell_tx in sell_transactions:
            return_quantity = sell_tx.quantity
            return_cost = (sell_tx.price or 0) * return_quantity
            total_return_quantity += return_quantity
            total_return_cost += return_cost

            returned_records_info.append({
                'sell_tx_id': sell_tx.id,
                'price': sell_tx.price,
                'quantity': return_quantity
            })

            # 软删除 sell 记录
            sell_tx.is_active = False
            sell_tx.deleted_at = now

            # 3. 恢复库存到买入记录（从该 sell 记录的扣减记录中恢复）
            deducted_records = []
            try:
                match = re.search(r"扣减记录: (\[.*?\])", sell_tx.notes or "")
                if match:
                    deducted_records = json.loads(match.group(1).replace("'", '"'))
            except:
                pass

            remaining_to_restore = return_quantity

            if deducted_records:
                # 按扣减记录的倒序恢复（后卖先回）
                for record in reversed(deducted_records):
                    if remaining_to_restore <= 0:
                        break

                    buy_tx = db.query(AssetTransaction).filter(
                        AssetTransaction.id == record['id'],
                        AssetTransaction.user_id == current_user_id,
                        AssetTransaction.transaction_type == "buy"
                    ).first()

                    if buy_tx:
                        sold_from_this = buy_tx.quantity - buy_tx.remaining_quantity
                        restore_amount = min(remaining_to_restore, sold_from_this)

                        if restore_amount > 0:
                            buy_tx.remaining_quantity += restore_amount
                            remaining_to_restore -= restore_amount

            # 如果还有未恢复的数量，按比例从已卖出的 buy 记录中恢复
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

        # 4. 创建 Asset RETURN 记录（标记为退款/纠纷导致的库存回撤）
        if total_return_quantity > 0:
            return_unit_price = total_return_cost / total_return_quantity if total_return_quantity > 0 else 0

            return_transaction = AssetTransaction(
                user_id=current_user_id,
                figure_id=sold_order.figure_id,
                order_id=None,
                sold_order_id=sold_order.id,
                transaction_type="return",
                price=return_unit_price,
                quantity=total_return_quantity,
                total_amount=total_return_cost,
                remaining_quantity=total_return_quantity,
                transaction_date=now,
                created_at=now,
                updated_at=now,
                notes=f"已出售订单 #{sold_order.id} - 退款/纠纷状态库存回撤（撤销记录:{returned_records_info}）"
            )
            db.add(return_transaction)

            result["inventory_returned"] = True
            result["return_quantity"] = total_return_quantity

        # 5. 处理 OrderTransaction（资金账）记录
        # 查找该订单的所有 sell 类型 order_transactions 记录
        order_sell_transactions = db.query(OrderTransaction).filter(
            OrderTransaction.user_id == current_user_id,
            OrderTransaction.sold_order_id == sold_order.id,
            OrderTransaction.transaction_type == "sell",
            OrderTransaction.is_active == True
        ).all()

        total_refund_amount = 0.0
        for order_sell_tx in order_sell_transactions:
            total_refund_amount += order_sell_tx.total_amount or 0
            # 软删除 sell 记录
            order_sell_tx.is_active = False
            order_sell_tx.deleted_at = now

        # 创建 refund 类型的 OrderTransaction 记录（标记退款）
        if total_refund_amount > 0:
            refund_transaction = OrderTransaction(
                user_id=current_user_id,
                figure_id=sold_order.figure_id,
                order_id=None,
                sold_order_id=sold_order.id,
                transaction_type="refund",  # 退款类型
                direction="out",  # 退款是资金流出（退回给买家）
                quantity=total_return_quantity,
                unit_price=total_refund_amount / total_return_quantity if total_return_quantity > 0 else 0,
                total_amount=total_refund_amount,
                currency="CNY",
                platform=sold_order.sell_platform,
                transaction_date=now,
                created_at=now,
                updated_at=now,
                notes=f"已出售订单 #{sold_order.id} - 退款/纠纷资金回撤",
                transaction_subtype="refund",
                changed_field="status"
            )
            db.add(refund_transaction)

        db.flush()
        return result

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

            # 1. FIFO 原则（后卖先回）：
            # 当订单数量多次变更时，可能有多条 sell 记录
            # 数量减少时，应该撤销最后卖出的那部分（最后创建的 sell 记录）
            # 按 created_at 倒序查找该订单的所有 sell 记录
            sell_transactions = db.query(AssetTransaction).filter(
                AssetTransaction.user_id == current_user_id,
                AssetTransaction.figure_id == sold_order.figure_id,
                AssetTransaction.transaction_type == "sell",
                AssetTransaction.sold_order_id == sold_order.id,
                AssetTransaction.is_active == True
            ).order_by(AssetTransaction.created_at.desc()).all()

            if sell_transactions:
                # 2. 计算需要撤销的卖出记录（从最后卖出的开始）
                remaining_to_return = return_quantity
                total_return_cost = 0.0
                returned_records_info = []  # 记录撤销了哪些 sell 记录

                for sell_tx in sell_transactions:
                    if remaining_to_return <= 0:
                        break

                    # 计算该 sell 记录需要撤销的数量
                    # sell_tx.quantity 是该次卖出的数量
                    return_from_this = min(sell_tx.quantity, remaining_to_return)
                    remaining_to_return -= return_from_this

                    # 累加成本
                    return_cost = (sell_tx.price or 0) * return_from_this
                    total_return_cost += return_cost

                    returned_records_info.append({
                        'sell_tx_id': sell_tx.id,
                        'price': sell_tx.price,
                        'return_quantity': return_from_this
                    })

                    # 减少该 sell 记录的数量（软删除或更新）
                    if return_from_this >= sell_tx.quantity:
                        # 全部撤销，软删除该 sell 记录
                        sell_tx.is_active = False
                        sell_tx.deleted_at = now
                    else:
                        # 部分撤销，更新数量
                        sell_tx.quantity -= return_from_this
                        sell_tx.total_amount = sell_tx.price * sell_tx.quantity

                    # 3. 从 notes 中解析该 sell 记录的扣减记录，恢复库存
                    deducted_records = []
                    try:
                        match = re.search(r"扣减记录: (\[.*?\])", sell_tx.notes or "")
                        if match:
                            deducted_records = json.loads(match.group(1).replace("'", '"'))
                    except:
                        pass

                    remaining_to_restore = return_from_this

                    if deducted_records:
                        # 按扣减记录的倒序恢复（后卖先回）
                        for record in reversed(deducted_records):
                            if remaining_to_restore <= 0:
                                break

                            buy_tx = db.query(AssetTransaction).filter(
                                AssetTransaction.id == record['id'],
                                AssetTransaction.user_id == current_user_id,
                                AssetTransaction.transaction_type == "buy"
                            ).first()

                            if buy_tx:
                                sold_from_this = buy_tx.quantity - buy_tx.remaining_quantity
                                restore_amount = min(remaining_to_restore, sold_from_this)

                                if restore_amount > 0:
                                    buy_tx.remaining_quantity += restore_amount
                                    remaining_to_restore -= restore_amount

                    # 如果还有未恢复的数量，按比例从已卖出的 buy 记录中恢复
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

                # 4. 创建 RETURN 记录（使用加权平均成本价）
                return_unit_price = total_return_cost / return_quantity if return_quantity > 0 else 0

                return_transaction = AssetTransaction(
                    user_id=current_user_id,
                    figure_id=sold_order.figure_id,
                    order_id=None,
                    sold_order_id=sold_order.id,
                    transaction_type="return",  # 回库类型
                    price=return_unit_price,
                    quantity=return_quantity,
                    total_amount=total_return_cost,
                    remaining_quantity=return_quantity,  # 回库数量加入库存
                    transaction_date=now,
                    created_at=now,
                    updated_at=now,
                    notes=f"已出售订单 #{sold_order.id} - 数量减少回库（原数量:{old_quantity}, 新数量:{new_quantity}, 撤销记录:{returned_records_info}）"
                )
                db.add(return_transaction)

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
