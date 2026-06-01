"""
订单编号生成服务
提供订单展示编号的生成和更新功能
采用企业级服务层架构
"""
from datetime import datetime
from sqlalchemy.orm import Session

from app.models.order import Order


class OrderNumberService:
    """
    订单编号服务类

    提供以下核心功能：
    1. 生成展示订单编号（格式：ORDER-YYYYMMDD-XXX）
    2. 为订单更新展示订单编号
    3. 批量更新订单展示编号

    编号格式：
    - 格式：ORDER-YYYYMMDD-XXX
    - 示例：ORDER-20260525-001
    - YYYYMMDD：订单创建日期（来自 orders.created_at）
    - XXX：订单ID，3位数字，不足补零（来自 orders.id）
    """

    @staticmethod
    def generate_display_order_number(order_id: int, created_at: datetime) -> str:
        """
        生成展示订单编号

        Args:
            order_id: 订单ID
            created_at: 订单创建时间

        Returns:
            str: 生成的订单编号，格式 ORDER-YYYYMMDD-XXX
        """
        if created_at:
            date_str = created_at.strftime('%Y%m%d')
            return f"ORDER-{date_str}-{order_id:03d}"
        else:
            return f"ORDER-{order_id:03d}"

    @classmethod
    def update_order_display_number(cls, db: Session, order: Order) -> Order:
        """
        为订单生成并更新展示订单编号

        在订单创建后调用，使用订单的 id 和 created_at 生成编号

        Args:
            db: 数据库会话
            order: 订单对象

        Returns:
            Order: 更新后的订单对象
        """
        if not order.display_order_number:
            order.display_order_number = cls.generate_display_order_number(
                order_id=order.id,
                created_at=order.created_at
            )
            db.commit()
            db.refresh(order)
        return order

    @classmethod
    def update_order_display_number_by_id(cls, db: Session, order_id: int) -> bool:
        """
        根据订单ID更新展示订单编号

        Args:
            db: 数据库会话
            order_id: 订单ID

        Returns:
            bool: 是否成功更新
        """
        order = db.query(Order).filter(Order.id == order_id).first()
        if not order:
            return False

        if not order.display_order_number:
            order.display_order_number = cls.generate_display_order_number(
                order_id=order.id,
                created_at=order.created_at
            )
            db.commit()
            return True
        return False

    @classmethod
    def batch_update_display_numbers(cls, db: Session, user_id: int = None) -> int:
        """
        批量更新所有未设置展示订单编号的订单

        Args:
            db: 数据库会话
            user_id: 可选，指定用户ID，只更新该用户的订单

        Returns:
            int: 更新的订单数量
        """
        query = db.query(Order).filter(
            Order.display_order_number.is_(None),
            Order.is_active == 1
        )

        if user_id:
            query = query.filter(Order.user_id == user_id)

        orders = query.all()
        updated_count = 0

        for order in orders:
            order.display_order_number = cls.generate_display_order_number(
                order_id=order.id,
                created_at=order.created_at
            )
            updated_count += 1

        if updated_count > 0:
            db.commit()

        return updated_count
