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

        # 创建资产交易记录（补录凭证模式）和资金流水记录
        try:
            # 1. 将订单关联到现有的库存记录（不新增记录）
            AssetTransactionService.link_order_to_existing_transaction(
                db=db,
                user_id=current_user.id,
                figure_id=order_data.figure_id,
                order=db_order
            )

            # 2. 创建资金流水记录（资金账）
            total_price = db_order.deposit + db_order.balance

            OrderTransactionService.create_buy_transaction(
                db=db,
                user_id=current_user.id,
                figure_id=order_data.figure_id,
                order_id=db_order.id,
                quantity=1,
                unit_price=total_price,
                total_amount=total_price,
                payment_method=None,
                platform=None,
                notes=f"订单 #{db_order.id} 资金流水"
            )

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

        for key, value in order_data.dict(exclude_unset=True).items():
            setattr(db_order, key, value)
        db.commit()
        db.refresh(db_order)

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
