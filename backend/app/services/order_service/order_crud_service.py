"""
订单CRUD服务
提供订单增删改查的业务逻辑，包括创建、更新、删除等
"""
from datetime import datetime
from typing import Optional
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.models.order import Order
from app.models.figure import Figure
from app.models.user import User
from app.models.asset import AssetTransaction, OrderTransaction
from app.schemas.order import OrderCreate, OrderUpdate
from app.services.asset_transaction_service import AssetTransactionService
from app.services.order_transaction_service import OrderTransactionService
from app.services.figure_service import FigureService
from app.services.figure_service.figure_price_service import FigurePriceService
from app.services.order_service.order_number_service import OrderNumberService


class OrderCrudService:
    """订单CRUD服务类"""

    @staticmethod
    def create_order(
        db: Session,
        order_data: OrderCreate,
        current_user: User
    ) -> Order:
        """
        创建订单

        创建订单时会自动关联或创建对应的资产交易记录和资金流水记录

        Args:
            db: 数据库会话
            order_data: 订单创建数据
            current_user: 当前用户

        Returns:
            Order: 创建的订单对象

        Raises:
            HTTPException: 手办不存在或订单数量超过限制时抛出
        """
        from fastapi import HTTPException, status

        # 检查手办是否存在
        db_figure = db.query(Figure).filter(Figure.id == order_data.figure_id).first()
        if not db_figure:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="手办不存在"
            )

        # 检查手办的订单数量是否超过手办的数量字段值（只计算未软删除的订单）
        order_count = db.query(func.count(Order.id)).filter(
            Order.figure_id == order_data.figure_id,
            Order.is_active == 1
        ).scalar()
        figure_quantity = db_figure.quantity or 1

        if order_count >= figure_quantity:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"该手办已达到最大订单数量限制（{figure_quantity}个）"
            )

        db_order = Order(
            user_id=current_user.id,
            created_at=datetime.now(),
            updated_at=datetime.now(),
            **order_data.dict()
        )
        db.add(db_order)
        db.commit()
        db.refresh(db_order)

        # 生成展示订单编号（格式：ORDER-YYYYMMDD-XXX）
        OrderNumberService.update_order_display_number(db, db_order)

        # 创建资金流水记录（order_transactions）和/或资产交易记录（asset_transactions）
        # 根据订单状态决定记录类型：
        # - "已完成"：同时记录资金流水+资产交易（已拿到货物，有完整资金流动）
        # - "已支付"：只记录资金流水（有资金流出但未到货）
        # - "已取消"：只记录资金流水（已支付过定金/尾款，订单已取消）
        # - "未支付"：不记录任何数据（无资金流动）
        try:
            from app.models.asset import OrderTransaction
            now = datetime.now()

            if db_order.status in ("已完成", "已支付", "已取消"):
                # 资金流水记录（资金账）- 所有已产生资金流动的状态都记录
                # 创建定金资金流水记录（独立记录，便于追踪变更）
                if db_order.deposit and db_order.deposit > 0:
                    deposit_txn = OrderTransaction(
                        user_id=current_user.id,
                        figure_id=order_data.figure_id,
                        order_id=db_order.id,
                        transaction_type="deposit",
                        direction="out",
                        quantity=1,
                        unit_price=db_order.deposit,
                        total_amount=db_order.deposit,
                        currency=db_order.deposit_currency or "CNY",
                        platform=db_order.shop_name,
                        transaction_date=now,
                        created_at=now,
                        updated_at=now,
                        notes=f"订单 #{db_order.id} 定金",
                        transaction_subtype="initial",
                        changed_field="deposit"
                    )
                    db.add(deposit_txn)

                # 创建尾款资金流水记录（独立记录，便于追踪变更）
                if db_order.balance and db_order.balance > 0:
                    balance_txn = OrderTransaction(
                        user_id=current_user.id,
                        figure_id=order_data.figure_id,
                        order_id=db_order.id,
                        transaction_type="balance",
                        direction="out",
                        quantity=1,
                        unit_price=db_order.balance,
                        total_amount=db_order.balance,
                        currency=db_order.balance_currency or "CNY",
                        platform=db_order.shop_name,
                        transaction_date=now,
                        created_at=now,
                        updated_at=now,
                        notes=f"订单 #{db_order.id} 尾款",
                        transaction_subtype="initial",
                        changed_field="balance"
                    )
                    db.add(balance_txn)

            if db_order.status == "已完成":
                # 已完成订单：额外创建资产交易记录（库存账）- 代表已入库
                total_price = FigurePriceService.calculate_order_amount_cny(
                    deposit=db_order.deposit,
                    deposit_currency=db_order.deposit_currency,
                    balance=db_order.balance,
                    balance_currency=db_order.balance_currency
                )

                AssetTransactionService.create_transaction_from_figure(
                    db=db,
                    user_id=current_user.id,
                    figure_id=order_data.figure_id,
                    price=total_price,
                    quantity=1,
                    order_id=db_order.id
                )

                # 更新手办的平均入手价格
                FigureService.update_figure_average_purchase_price(db, order_data.figure_id)

                # 更新手办持有数量（从库存账重新计算）
                current_inventory = db.query(func.sum(AssetTransaction.remaining_quantity)).filter(
                    AssetTransaction.user_id == current_user.id,
                    AssetTransaction.figure_id == order_data.figure_id,
                    AssetTransaction.transaction_type == "buy",
                    AssetTransaction.is_active == True
                ).scalar() or 0

                figure = db.query(Figure).filter(Figure.id == order_data.figure_id).first()
                if figure:
                    figure.quantity = int(current_inventory)

            db.commit()
        except Exception as e:
            # 如果创建交易记录失败，不影响订单创建
            db.rollback()
            print(f"创建交易记录失败: {e}")

        return db_order

    @staticmethod
    def update_order(
        db: Session,
        order_id: int,
        order_data: OrderUpdate,
        current_user: User
    ) -> Order:
        """
        更新订单

        Args:
            db: 数据库会话
            order_id: 订单ID
            order_data: 订单更新数据
            current_user: 当前用户

        Returns:
            Order: 更新后的订单对象

        Raises:
            HTTPException: 订单不存在或无权限时抛出
        """
        from fastapi import HTTPException, status

        db_order = db.query(Order).filter(Order.id == order_id, Order.is_active == 1).first()
        if not db_order:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="未找到该订单"
            )
        if not current_user.is_admin and db_order.user_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="权限不足"
            )

        # 记录原始 figure_id 用于后续更新平均价格
        original_figure_id = db_order.figure_id

        # 记录变更前的金额和币种（用于资金变更追踪）
        old_deposit = db_order.deposit
        old_deposit_currency = db_order.deposit_currency
        old_balance = db_order.balance
        old_balance_currency = db_order.balance_currency

        for key, value in order_data.dict(exclude_unset=True).items():
            setattr(db_order, key, value)
        db_order.updated_at = datetime.now()
        db.commit()
        db.refresh(db_order)

        # 检测并记录资金变更
        try:
            OrderTransactionService.detect_and_record_changes(
                db=db,
                order=db_order,
                old_deposit=old_deposit,
                old_deposit_currency=old_deposit_currency,
                old_balance=old_balance,
                old_balance_currency=old_balance_currency,
                current_user=current_user,
                change_reason="订单编辑"
            )
        except Exception as e:
            print(f"记录资金变更失败: {e}")

        # 创建资金流水记录（order_transactions）和/或资产交易记录（asset_transactions）
        # 处理编辑时首次创建初始记录的场景（例如从"未支付"改为"已支付"/"已取消"/"已完成"）
        # 根据订单状态决定记录类型：
        # - "已完成"：同时记录资金流水+资产交易（已拿到货物，有完整资金流动）
        # - "已支付"：只记录资金流水（有资金流出但未到货）
        # - "已取消"：只记录资金流水（已支付过定金/尾款，订单已取消）
        # - "未支付"：不记录任何数据（无资金流动）
        try:
            if db_order.status in ("已完成", "已支付", "已取消"):
                from app.models.asset import OrderTransaction as OrderTransactionModel
                # 检查是否已有初始资金流水记录
                existing_txn = db.query(OrderTransactionModel).filter(
                    OrderTransactionModel.order_id == db_order.id,
                    OrderTransactionModel.is_active == True
                ).first()

                if not existing_txn:
                    now = datetime.now()
                    # 创建定金资金流水记录
                    if db_order.deposit and db_order.deposit > 0:
                        deposit_txn = OrderTransactionModel(
                            user_id=current_user.id,
                            figure_id=db_order.figure_id,
                            order_id=db_order.id,
                            transaction_type="deposit",
                            direction="out",
                            quantity=1,
                            unit_price=db_order.deposit,
                            total_amount=db_order.deposit,
                            currency=db_order.deposit_currency or "CNY",
                            platform=db_order.shop_name,
                            transaction_date=now,
                            created_at=now,
                            updated_at=now,
                            notes=f"订单 #{db_order.id} 定金",
                            transaction_subtype="initial",
                            changed_field="deposit"
                        )
                        db.add(deposit_txn)

                    # 创建尾款资金流水记录
                    if db_order.balance and db_order.balance > 0:
                        balance_txn = OrderTransactionModel(
                            user_id=current_user.id,
                            figure_id=db_order.figure_id,
                            order_id=db_order.id,
                            transaction_type="balance",
                            direction="out",
                            quantity=1,
                            unit_price=db_order.balance,
                            total_amount=db_order.balance,
                            currency=db_order.balance_currency or "CNY",
                            platform=db_order.shop_name,
                            transaction_date=now,
                            created_at=now,
                            updated_at=now,
                            notes=f"订单 #{db_order.id} 尾款",
                            transaction_subtype="initial",
                            changed_field="balance"
                        )
                        db.add(balance_txn)

                    db.commit()

            # 编辑时由"未支付"改为"已完成"：额外创建资产交易记录（库存账）
            if db_order.status == "已完成":
                existing_asset = db.query(AssetTransaction).filter(
                    AssetTransaction.order_id == db_order.id,
                    AssetTransaction.is_active == True,
                    AssetTransaction.transaction_type == "buy"
                ).first()

                if not existing_asset:
                    total_price = FigurePriceService.calculate_order_amount_cny(
                        deposit=db_order.deposit,
                        deposit_currency=db_order.deposit_currency,
                        balance=db_order.balance,
                        balance_currency=db_order.balance_currency
                    )

                    AssetTransactionService.create_transaction_from_figure(
                        db=db,
                        user_id=current_user.id,
                        figure_id=db_order.figure_id,
                        price=total_price,
                        quantity=1,
                        order_id=db_order.id
                    )

                    db.commit()
        except Exception as e:
            print(f"创建初始交易记录失败: {e}")

        # 创建库存账调整记录（quantity=0）用于补差额
        # 仅当订单状态为"已完成"时才在 asset_transactions 中记录成本调整
        if db_order.status == "已完成":
            try:
                # 分别计算定金和尾款的人民币金额
                old_deposit_cny = FigurePriceService.convert_to_cny(old_deposit or 0, old_deposit_currency or 'CNY')
                new_deposit_cny = FigurePriceService.convert_to_cny(db_order.deposit or 0, db_order.deposit_currency or 'CNY')
                old_balance_cny = FigurePriceService.convert_to_cny(old_balance or 0, old_balance_currency or 'CNY')
                new_balance_cny = FigurePriceService.convert_to_cny(db_order.balance or 0, db_order.balance_currency or 'CNY')

                has_adjustment = False

                # 1. 处理定金变更
                deposit_diff = new_deposit_cny - old_deposit_cny
                if abs(deposit_diff) > 0.01:
                    # 判断变更类型
                    if deposit_diff > 0:
                        change_type = "追加"
                    else:
                        change_type = "减少"

                    # price 为该笔调整后的订单总成本（定金+尾款的人民币金额）
                    total_cost_after_change = new_deposit_cny + new_balance_cny
                    now = datetime.now()

                    deposit_adjust = AssetTransaction(
                        user_id=current_user.id,
                        figure_id=db_order.figure_id,
                        order_id=db_order.id,
                        transaction_type="adjust",
                        price=total_cost_after_change,
                        quantity=0,
                        total_amount=total_cost_after_change,
                        remaining_quantity=0,
                        transaction_date=now,
                        created_at=now,
                        updated_at=now,
                        notes=f"定金{change_type}导致的成本调整 ({old_deposit_cny:.2f} CNY → {new_deposit_cny:.2f} CNY)"
                    )
                    db.add(deposit_adjust)
                    has_adjustment = True

                # 2. 处理尾款变更
                balance_diff = new_balance_cny - old_balance_cny
                if abs(balance_diff) > 0.01:
                    # 判断变更类型
                    if balance_diff > 0:
                        change_type = "追加"
                    else:
                        change_type = "减少"

                    # price 为该笔调整后的订单总成本（定金+尾款的人民币金额）
                    total_cost_after_change = new_deposit_cny + new_balance_cny
                    now = datetime.now()

                    balance_adjust = AssetTransaction(
                        user_id=current_user.id,
                        figure_id=db_order.figure_id,
                        order_id=db_order.id,
                        transaction_type="adjust",
                        price=total_cost_after_change,
                        quantity=0,
                        total_amount=total_cost_after_change,
                        remaining_quantity=0,
                        transaction_date=now,
                        created_at=now,
                        updated_at=now,
                        notes=f"尾款{change_type}导致的成本调整 ({old_balance_cny:.2f} CNY → {new_balance_cny:.2f} CNY)"
                    )
                    db.add(balance_adjust)
                    has_adjustment = True

                # 如果有任何调整记录，提交事务
                if has_adjustment:
                    db.commit()
            except Exception as e:
                print(f"创建库存账调整记录失败: {e}")

        # 更新手办的平均入手价格
        try:
            FigureService.update_figure_average_purchase_price(db, db_order.figure_id)
        except Exception as e:
            print(f"更新平均入手价格失败: {e}")

        return db_order

    @staticmethod
    def delete_order(
        db: Session,
        order_id: int,
        current_user: User
    ) -> dict:
        """
        软删除订单

        不物理删除订单记录，仅标记 is_active=False 和 deleted_at
        同时软删除关联的资产交易记录和资金流水记录

        Args:
            db: 数据库会话
            order_id: 订单ID
            current_user: 当前用户

        Returns:
            dict: {"message": "Order deleted successfully"}

        Raises:
            HTTPException: 订单不存在或无权限时抛出
        """
        from fastapi import HTTPException, status

        db_order = db.query(Order).filter(Order.id == order_id).first()
        if not db_order:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="未找到该订单"
            )
        if not current_user.is_admin and db_order.user_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="权限不足"
            )

        # 记录 figure_id 用于后续更新平均价格
        figure_id = db_order.figure_id

        # 软删除关联的资产交易记录（库存账）
        db.query(AssetTransaction).filter(
            AssetTransaction.order_id == order_id
        ).update({
            'is_active': False,
            'deleted_at': datetime.now(),
            'order_id': None  # 解除外键关联，避免外键约束错误
        }, synchronize_session=False)

        # 软删除关联的资金流水记录（资金账）
        db.query(OrderTransaction).filter(
            OrderTransaction.order_id == order_id
        ).update({
            'is_active': False,
            'deleted_at': datetime.now(),
            'order_id': None  # 解除外键关联，避免外键约束错误
        }, synchronize_session=False)

        # 软删除订单本身
        db_order.is_active = 0
        db_order.deleted_at = datetime.now()

        db.commit()

        # 更新手办的平均入手价格
        try:
            FigureService.update_figure_average_purchase_price(db, figure_id)
        except Exception as e:
            print(f"更新平均入手价格失败: {e}")

        return {"message": "订单删除成功"}

    @staticmethod
    def batch_delete_orders(
        db: Session,
        order_ids: list[int],
        current_user: User
    ) -> dict:
        """
        批量软删除订单

        不物理删除订单记录，仅标记 is_active=False 和 deleted_at
        同时软删除关联的资产交易记录和资金流水记录

        Args:
            db: 数据库会话
            order_ids: 要删除的订单ID列表
            current_user: 当前用户

        Returns:
            dict: 删除结果统计
            {
                'success_count': 成功删除数量,
                'failed_count': 失败数量,
                'failed_ids': 失败的ID列表,
                'errors': 错误信息列表
            }
        """
        from fastapi import HTTPException, status

        success_count = 0
        failed_count = 0
        failed_ids = []
        errors = []

        for order_id in order_ids:
            try:
                # 检查订单是否存在
                db_order = db.query(Order).filter(
                    Order.id == order_id,
                    Order.is_active == 1
                ).first()

                if not db_order:
                    failed_count += 1
                    failed_ids.append(order_id)
                    errors.append(f"订单ID {order_id} 不存在或已被删除")
                    continue

                # 检查权限
                if not current_user.is_admin and db_order.user_id != current_user.id:
                    failed_count += 1
                    failed_ids.append(order_id)
                    errors.append(f"订单ID {order_id} 权限不足")
                    continue

                # 记录 figure_id 用于后续更新平均价格
                figure_id = db_order.figure_id

                # 软删除关联的资产交易记录（库存账）
                db.query(AssetTransaction).filter(
                    AssetTransaction.order_id == order_id
                ).update({
                    'is_active': False,
                    'deleted_at': datetime.now(),
                    'order_id': None
                }, synchronize_session=False)

                # 软删除关联的资金流水记录（资金账）
                db.query(OrderTransaction).filter(
                    OrderTransaction.order_id == order_id
                ).update({
                    'is_active': False,
                    'deleted_at': datetime.now(),
                    'order_id': None
                }, synchronize_session=False)

                # 软删除订单本身
                db_order.is_active = 0
                db_order.deleted_at = datetime.now()

                db.commit()
                success_count += 1

                # 更新手办的平均入手价格
                try:
                    FigureService.update_figure_average_purchase_price(db, figure_id)
                except Exception as e:
                    print(f"更新平均入手价格失败: {e}")

            except Exception as e:
                db.rollback()
                failed_count += 1
                failed_ids.append(order_id)
                errors.append(f"订单ID {order_id} 删除失败: {str(e)}")

        return {
            'success_count': success_count,
            'failed_count': failed_count,
            'failed_ids': failed_ids,
            'errors': errors
        }
