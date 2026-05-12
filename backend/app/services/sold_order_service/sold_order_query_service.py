"""
已出售订单查询服务

提供已出售订单的查询和统计功能
"""
from typing import List, Optional, Dict
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.models.sold_order import SoldOrder
from app.models.figure import Figure
from app.models.user import User
from app.schemas.sold_order import SoldOrderListItem, SoldOrderStatistics


class SoldOrderQueryService:
    """
    已出售订单查询服务类
    
    提供订单列表查询、单个订单查询、统计信息等功能
    """

    @staticmethod
    def get_sold_orders(db: Session, current_user: User) -> List[SoldOrderListItem]:
        """
        获取已出售订单列表
        
        只返回未软删除的订单（is_active=1）
        """
        orders = db.query(
            SoldOrder,
            Figure.name.label('figure_name'),
            Figure.images.label('figure_images')
        ).join(
            Figure, SoldOrder.figure_id == Figure.id
        ).filter(
            SoldOrder.user_id == current_user.id,
            SoldOrder.is_active == 1
        ).all()

        return [
            SoldOrderListItem(
                id=order.SoldOrder.id,
                user_id=order.SoldOrder.user_id,
                figure_id=order.SoldOrder.figure_id,
                sell_price=order.SoldOrder.sell_price,
                cost_price=order.SoldOrder.cost_price,
                shipping_fee=order.SoldOrder.shipping_fee,
                platform_fee=order.SoldOrder.platform_fee,
                net_profit=order.SoldOrder.net_profit,
                profit_rate=order.SoldOrder.profit_rate,
                sell_platform=order.SoldOrder.sell_platform,
                order_number=order.SoldOrder.order_number,
                buyer_phone=order.SoldOrder.buyer_phone,
                tracking_number=order.SoldOrder.tracking_number,
                status=order.SoldOrder.status,
                figure_name=order.figure_name,
                figure_image=order.figure_images[0] if order.figure_images and len(order.figure_images) > 0 else None
            )
            for order in orders
        ]

    @staticmethod
    def get_sold_order_by_id(db: Session, order_id: int, current_user: User) -> Optional[SoldOrder]:
        """
        获取单个已出售订单详情
        
        只返回未软删除的订单（is_active=1）
        """
        order = db.query(SoldOrder).filter(
            SoldOrder.id == order_id,
            SoldOrder.user_id == current_user.id,
            SoldOrder.is_active == 1
        ).first()

        if not order:
            return None

        return order

    @staticmethod
    def get_sold_order_statistics(db: Session, current_user: User) -> SoldOrderStatistics:
        """
        获取已出售订单统计信息
        
        包括各状态订单数量和累计净利润
        """
        stats = db.query(
            func.count(SoldOrder.id).label('total_count'),
            func.sum(func.case((SoldOrder.status == '待发货', 1), else_=0)).label('pending_count'),
            func.sum(func.case((SoldOrder.status == '已发货', 1), else_=0)).label('shipped_count'),
            func.sum(func.case((SoldOrder.status == '已完成', 1), else_=0)).label('completed_count'),
            func.sum(func.case((SoldOrder.status == '退款/纠纷', 1), else_=0)).label('dispute_count'),
            func.coalesce(func.sum(SoldOrder.net_profit), 0).label('total_net_profit')
        ).filter(
            SoldOrder.user_id == current_user.id,
            SoldOrder.is_active == 1
        ).first()

        return SoldOrderStatistics(
            total_count=stats.total_count,
            pending_count=stats.pending_count or 0,
            shipped_count=stats.shipped_count or 0,
            completed_count=stats.completed_count or 0,
            dispute_count=stats.dispute_count or 0,
            total_net_profit=stats.total_net_profit or 0.0
        )