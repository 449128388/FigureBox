"""
已出售订单查询服务

提供已出售订单的查询和统计功能
"""
from typing import List, Optional, Dict
from sqlalchemy.orm import Session
from sqlalchemy import func, case

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
    def get_sold_orders(
        db: Session,
        current_user: User,
        figure_name: Optional[str] = None,
        order_number: Optional[str] = None,
        sell_platform: Optional[str] = None
    ) -> List[SoldOrderListItem]:
        """
        获取已出售订单列表

        Args:
            db: 数据库会话
            current_user: 当前用户
            figure_name: 手办名称模糊搜索
            order_number: 订单编号模糊搜索
            sell_platform: 卖出平台筛选

        Returns:
            List[SoldOrderListItem]: 已出售订单列表
        """
        # 构建基础查询
        query = db.query(
            SoldOrder,
            Figure.name.label('figure_name'),
            Figure.images.label('figure_images')
        ).join(
            Figure, SoldOrder.figure_id == Figure.id
        ).filter(
            SoldOrder.user_id == current_user.id,
            SoldOrder.is_active == 1
        )

        # 按手办名称模糊搜索
        if figure_name:
            query = query.filter(Figure.name.ilike(f"%{figure_name}%"))

        # 按订单编号模糊搜索
        if order_number:
            query = query.filter(SoldOrder.order_number.ilike(f"%{order_number}%"))

        # 按卖出平台筛选
        if sell_platform:
            query = query.filter(SoldOrder.sell_platform == sell_platform)

        orders = query.all()

        return [
            SoldOrderListItem(
                id=order.SoldOrder.id,
                user_id=order.SoldOrder.user_id,
                figure_id=order.SoldOrder.figure_id,
                quantity=order.SoldOrder.quantity,  # 卖出数量
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
            func.sum(case((SoldOrder.status == '待发货', 1), else_=0)).label('pending_count'),
            func.sum(case((SoldOrder.status == '已发货', 1), else_=0)).label('shipped_count'),
            func.sum(case((SoldOrder.status == '已完成', 1), else_=0)).label('completed_count'),
            func.sum(case((SoldOrder.status == '退款/纠纷', 1), else_=0)).label('dispute_count'),
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

    @staticmethod
    def get_xianyu_monthly_statistics(db: Session, current_user: User, exclude_order_id: int = None) -> Dict:
        """
        获取用户当月闲鱼订单统计信息（用于计算平台手续费）

        统计当月（自然月）的闲鱼订单数量和成交额

        Args:
            db: 数据库会话
            current_user: 当前用户
            exclude_order_id: 需要排除的订单ID（编辑时使用）

        Returns:
            Dict: 包含订单数量和成交额的字典
        """
        from datetime import datetime
        from sqlalchemy import extract

        now = datetime.now()
        current_year = now.year
        current_month = now.month

        # 查询当月闲鱼（个人卖家和鱼小铺）订单
        query = db.query(
            func.count(SoldOrder.id).label('order_count'),
            func.coalesce(func.sum(SoldOrder.sell_price), 0).label('total_amount')
        ).filter(
            SoldOrder.user_id == current_user.id,
            SoldOrder.is_active == 1,
            SoldOrder.sell_platform.in_(['闲鱼（个人卖家）', '闲鱼（鱼小铺）']),
            extract('year', SoldOrder.created_at) == current_year,
            extract('month', SoldOrder.created_at) == current_month
        )

        # 编辑时排除当前订单
        if exclude_order_id:
            query = query.filter(SoldOrder.id != exclude_order_id)

        result = query.first()

        return {
            'order_count': result.order_count or 0,
            'total_amount': float(result.total_amount or 0)
        }