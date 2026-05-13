"""
已出售订单手办服务

处理已出售订单与手办聚合状态的联动
更新手办的当前库存数量、售罄状态
"""
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.models.figure import Figure
from app.models.asset import AssetTransaction
from app.models.sold_order import SoldOrder


class SoldOrderFigureService:
    """
    已出售订单手办服务类

    负责在创建已出售订单时，更新手办的聚合状态
    """

    @staticmethod
    def update_figure_status(
        db: Session,
        sold_order: SoldOrder,
        current_user_id: int
    ) -> Figure:
        """
        更新手办聚合状态

        当已出售订单创建时：
        - 更新当前库存数量
        - 如果库存为0，标记为售罄状态

        Args:
            db: 数据库会话
            sold_order: 已出售订单对象
            current_user_id: 当前用户ID

        Returns:
            更新后的 Figure 对象
        """
        figure = db.query(Figure).filter(
            Figure.id == sold_order.figure_id,
            Figure.is_active == True
        ).first()

        if not figure:
            return None

        # 计算当前库存数量
        current_inventory = db.query(func.sum(AssetTransaction.remaining_quantity)).filter(
            AssetTransaction.user_id == current_user_id,
            AssetTransaction.figure_id == figure.id,
            AssetTransaction.transaction_type == "buy",
            AssetTransaction.is_active == True
        ).scalar() or 0

        # 更新手办数量
        figure.quantity = int(current_inventory)

        # 如果库存为0，可以在这里添加售罄标记（如果Figure模型有该字段）
        # 目前Figure模型没有直接的售罄字段，通过quantity=0来判断

        db.flush()
        return figure

    @staticmethod
    def restore_figure_status(
        db: Session,
        sold_order: SoldOrder,
        current_user_id: int
    ) -> Figure:
        """
        恢复手办状态（用于订单删除时）

        Args:
            db: 数据库会话
            sold_order: 已出售订单对象
            current_user_id: 当前用户ID

        Returns:
            更新后的 Figure 对象
        """
        figure = db.query(Figure).filter(
            Figure.id == sold_order.figure_id,
            Figure.is_active == True
        ).first()

        if not figure:
            return None

        # 重新计算当前库存数量
        current_inventory = db.query(func.sum(AssetTransaction.remaining_quantity)).filter(
            AssetTransaction.user_id == current_user_id,
            AssetTransaction.figure_id == figure.id,
            AssetTransaction.transaction_type == "buy",
            AssetTransaction.is_active == True
        ).scalar() or 0

        # 更新手办数量
        figure.quantity = int(current_inventory)

        db.flush()
        return figure
