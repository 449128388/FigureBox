"""
订单CRUD服务
提供订单增删改查的业务逻辑，包括创建、更新、删除等
"""
from datetime import datetime
from typing import Optional
from sqlalchemy.orm import Session

from app.models.order import Order
from app.models.figure import Figure
from app.models.user import User
from app.models.asset import AssetTransaction, OrderTransaction
from app.schemas.order import OrderCreate, OrderUpdate
from app.services.asset_transaction_service import AssetTransactionService
from app.services.order_transaction_service import OrderTransactionService
from app.services.figure_service import FigureService
from app.services.figure_service.figure_price_service import FigurePriceService


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
        from sqlalchemy import func

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
            **order_data.dict()
        )
        db.add(db_order)
        db.commit()
        db.refresh(db_order)

        # 创建资产交易记录（库存账）和资金流水记录
        try:
            # 根据订单状态决定如何创建交易记录
            if db_order.status == "已取消":
                # 已取消订单：只记录定金，数量为0
                deposit_amount = FigurePriceService.calculate_deposit_cny(
                    deposit=db_order.deposit,
                    deposit_currency=db_order.deposit_currency
                )

                # 1. 创建资产交易记录（库存账）- 已取消订单数量为0
                AssetTransactionService.create_transaction_from_figure(
                    db=db,
                    user_id=current_user.id,
                    figure_id=order_data.figure_id,
                    price=deposit_amount,
                    quantity=0,  # 已取消订单，数量为0
                    order_id=db_order.id
                )

                # 2. 创建定金资金流水记录（资金账）- 独立记录以便追踪变更
                from app.models.asset import OrderTransaction
                deposit_txn = OrderTransaction(
                    user_id=current_user.id,
                    figure_id=order_data.figure_id,
                    order_id=db_order.id,
                    transaction_type="deposit",
                    direction="out",
                    quantity=0,
                    unit_price=db_order.deposit or 0,
                    total_amount=db_order.deposit or 0,
                    currency=db_order.deposit_currency or "CNY",
                    platform=db_order.shop_name,
                    transaction_date=datetime.now(),
                    notes=f"订单 #{db_order.id} 定金（已取消）",
                    transaction_subtype="initial",
                    changed_field="deposit"
                )
                db.add(deposit_txn)
            else:
                # 正常订单：创建完整的交易记录
                # 计算订单总金额（考虑币种转换）
                total_price = FigurePriceService.calculate_order_amount_cny(
                    deposit=db_order.deposit,
                    deposit_currency=db_order.deposit_currency,
                    balance=db_order.balance,
                    balance_currency=db_order.balance_currency
                )

                # 1. 创建资产交易记录（库存账）- 每个订单创建一条独立的库存记录
                AssetTransactionService.create_transaction_from_figure(
                    db=db,
                    user_id=current_user.id,
                    figure_id=order_data.figure_id,
                    price=total_price,
                    quantity=1,
                    order_id=db_order.id
                )

                # 2. 创建定金资金流水记录（独立记录，便于追踪变更）
                from app.models.asset import OrderTransaction
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
                        transaction_date=datetime.now(),
                        notes=f"订单 #{db_order.id} 定金",
                        transaction_subtype="initial",
                        changed_field="deposit"
                    )
                    db.add(deposit_txn)

                # 3. 创建尾款资金流水记录（独立记录，便于追踪变更）
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
                        transaction_date=datetime.now(),
                        notes=f"订单 #{db_order.id} 尾款",
                        transaction_subtype="initial",
                        changed_field="balance"
                    )
                    db.add(balance_txn)

                # 更新手办的平均入手价格
                FigureService.update_figure_average_purchase_price(db, order_data.figure_id)

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
