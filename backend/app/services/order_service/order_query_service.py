"""
订单查询服务
提供订单查询相关的业务逻辑，包括列表查询、统计等
"""
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.models.order import Order
from app.models.figure import Figure
from app.models.user import User
from app.schemas.order import OrderListItem


class OrderQueryService:
    """订单查询服务类"""

    @staticmethod
    def get_unpaid_balance(db: Session, current_user: User) -> dict:
        """
        获取未支付状态的尾款总额

        Args:
            db: 数据库会话
            current_user: 当前用户

        Returns:
            dict: {"total_unpaid_balance": float}
        """
        if current_user.is_admin:
            # 管理员查看所有未支付订单的尾款总额
            total_balance = db.query(func.sum(Order.balance)).filter(
                Order.status == "未支付",
                Order.is_active == 1
            ).scalar()
        else:
            # 普通用户只查看自己的未支付订单的尾款总额
            total_balance = db.query(func.sum(Order.balance)).filter(
                Order.status == "未支付",
                Order.user_id == current_user.id,
                Order.is_active == 1
            ).scalar()

        # 如果没有未支付订单，返回0
        return {"total_unpaid_balance": float(total_balance) if total_balance else 0.0}

    @staticmethod
    def get_orders(db: Session, current_user: User) -> List[OrderListItem]:
        """
        获取订单列表

        Args:
            db: 数据库会话
            current_user: 当前用户

        Returns:
            List[OrderListItem]: 订单列表
        """
        if current_user.is_admin:
            orders = db.query(Order).join(Figure).filter(Order.is_active == 1).all()
        else:
            orders = db.query(Order).join(Figure).filter(
                Order.user_id == current_user.id,
                Order.is_active == 1
            ).all()

        return [OrderListItem(
            id=order.id,
            user_id=order.user_id,
            figure_id=order.figure_id,
            figure_name=order.figure.name,
            figure_image=order.figure.images[0] if order.figure.images else None,
            deposit=order.deposit,
            deposit_currency=order.deposit_currency,
            balance=order.balance,
            balance_currency=order.balance_currency,
            due_date=order.due_date,
            status=order.status,
            shop_name=order.shop_name,
            shop_contact=order.shop_contact,
            tracking_number=order.tracking_number
        ) for order in orders]

    @staticmethod
    def get_order_by_id(db: Session, order_id: int, current_user: User) -> Optional[Order]:
        """
        获取单个订单详情

        Args:
            db: 数据库会话
            order_id: 订单ID
            current_user: 当前用户

        Returns:
            Order对象或None

        Raises:
            HTTPException: 订单不存在或无权限时抛出
        """
        from fastapi import HTTPException, status

        order = db.query(Order).filter(Order.id == order_id, Order.is_active == 1).first()
        if not order:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="未找到该订单"
            )
        if not current_user.is_admin and order.user_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="权限不足"
            )
        return order

    @staticmethod
    def get_order_count_by_figure(db: Session, figure_id: int) -> int:
        """
        获取指定手办的订单数量（只计算未软删除的订单）

        Args:
            db: 数据库会话
            figure_id: 手办ID

        Returns:
            int: 订单数量
        """
        return db.query(func.count(Order.id)).filter(
            Order.figure_id == figure_id,
            Order.is_active == 1
        ).scalar()
