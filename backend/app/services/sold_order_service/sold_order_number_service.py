
"""
已出售订单编号生成服务
提供已出售订单展示编号和订单编号的生成功能
"""
from datetime import datetime
from random import randint
from sqlalchemy.orm import Session

from app.models.sold_order import SoldOrder


class SoldOrderNumberService:
    """
    已出售订单编号服务类

    编号格式：
    - 展示编号 格式：SALE-YYYYMMDD-XXX，示例：SALE-20260612-001
    - 订单编号 格式：QS + 年月日时分秒 + 3位随机数，示例：QS20260612123456123
    """

    @staticmethod
    def generate_order_number() -> str:
        """
        生成订单编号

        用于系统自动生成的订单编号（外部平台订单号缺失时的替代方案）

        Returns:
            str: 生成的订单编号，格式 QS + 年月日时分秒 + 3位随机数
        """
        now = datetime.now()
        random_suffix = randint(100, 999)
        return f"QS{now.strftime('%Y%m%d%H%M%S')}{random_suffix}"

    @staticmethod
    def generate_display_sold_order_number(sold_order_id: int, created_at: datetime) -> str:
        """
        生成展示订单编号

        Args:
            sold_order_id: 已出售订单ID
            created_at: 订单创建时间

        Returns:
            str: 生成的订单编号，格式 SALE-YYYYMMDD-XXX
        """
        if created_at:
            date_str = created_at.strftime('%Y%m%d')
            return f"SALE-{date_str}-{sold_order_id:03d}"
        else:
            return f"SALE-{sold_order_id:03d}"

    @classmethod
    def update_display_number(cls, db: Session, sold_order: SoldOrder) -> SoldOrder:
        """
        为已出售订单生成并更新展示订单编号

        在订单创建后调用，使用订单的 id 和 created_at 生成编号
        注意：不提交事务，由调用方统一提交

        Args:
            db: 数据库会话
            sold_order: 已出售订单对象

        Returns:
            SoldOrder: 更新后的订单对象
        """
        if not sold_order.display_order_number:
            sold_order.display_order_number = cls.generate_display_sold_order_number(
                sold_order_id=sold_order.id,
                created_at=sold_order.created_at
            )
            db.flush()
        return sold_order
