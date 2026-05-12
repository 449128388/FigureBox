"""
已出售订单CRUD服务

提供已出售订单的创建、更新、删除功能
"""
from typing import Dict, Any
from sqlalchemy.orm import Session
from datetime import datetime

from app.models.sold_order import SoldOrder
from app.models.user import User
from app.schemas.sold_order import SoldOrderCreate, SoldOrderUpdate


class SoldOrderCrudService:
    """
    已出售订单CRUD服务类
    
    提供订单的创建、更新、删除（软删除）功能
    """

    @staticmethod
    def _calculate_profit(sell_price: float, cost_price: float, shipping_fee: float, platform_fee: float) -> Dict[str, float]:
        """
        计算净利润和利润率
        
        净利润 = 卖出价 - 成本价 + 运费 + 手续费
        利润率 = 净利润 / 成本价 * 100
        
        Args:
            sell_price: 卖出价格
            cost_price: 成本价格
            shipping_fee: 运费（负数表示支出）
            platform_fee: 平台手续费（负数表示支出）
        
        Returns:
            包含净利润和利润率的字典
        """
        net_profit = sell_price - cost_price + shipping_fee + platform_fee
        profit_rate = (net_profit / cost_price) * 100 if cost_price != 0 else 0
        
        return {
            'net_profit': round(net_profit, 2),
            'profit_rate': round(profit_rate, 2)
        }

    @staticmethod
    def create_sold_order(
        db: Session,
        order_data: SoldOrderCreate,
        current_user: User
    ) -> SoldOrder:
        """
        创建已出售订单
        
        创建时自动计算净利润和利润率
        """
        # 计算净利润和利润率
        profit_data = SoldOrderCrudService._calculate_profit(
            order_data.sell_price,
            order_data.cost_price,
            order_data.shipping_fee or 0,
            order_data.platform_fee or 0
        )

        new_order = SoldOrder(
            user_id=current_user.id,
            figure_id=order_data.figure_id,
            sell_price=order_data.sell_price,
            cost_price=order_data.cost_price,
            shipping_fee=order_data.shipping_fee or 0,
            platform_fee=order_data.platform_fee or 0,
            net_profit=profit_data['net_profit'],
            profit_rate=profit_data['profit_rate'],
            sell_platform=order_data.sell_platform,
            order_number=order_data.order_number,
            buyer_phone=order_data.buyer_phone,
            buyer_address=order_data.buyer_address,
            tracking_number=order_data.tracking_number,
            shipping_date=order_data.shipping_date,
            status=order_data.status or "待发货",
            remark=order_data.remark
        )

        db.add(new_order)
        db.commit()
        db.refresh(new_order)

        return new_order

    @staticmethod
    def update_sold_order(
        db: Session,
        order_id: int,
        order_data: SoldOrderUpdate,
        current_user: User
    ) -> SoldOrder:
        """
        更新已出售订单
        
        更新时自动重新计算净利润和利润率
        """
        order = db.query(SoldOrder).filter(
            SoldOrder.id == order_id,
            SoldOrder.user_id == current_user.id,
            SoldOrder.is_active == 1
        ).first()

        if not order:
            raise ValueError("订单不存在或已被删除")

        # 更新基本字段
        if order_data.figure_id is not None:
            order.figure_id = order_data.figure_id
        if order_data.sell_price is not None:
            order.sell_price = order_data.sell_price
        if order_data.cost_price is not None:
            order.cost_price = order_data.cost_price
        if order_data.shipping_fee is not None:
            order.shipping_fee = order_data.shipping_fee
        if order_data.platform_fee is not None:
            order.platform_fee = order_data.platform_fee
        if order_data.sell_platform is not None:
            order.sell_platform = order_data.sell_platform
        if order_data.order_number is not None:
            order.order_number = order_data.order_number
        if order_data.buyer_phone is not None:
            order.buyer_phone = order_data.buyer_phone
        if order_data.buyer_address is not None:
            order.buyer_address = order_data.buyer_address
        if order_data.tracking_number is not None:
            order.tracking_number = order_data.tracking_number
        if order_data.shipping_date is not None:
            order.shipping_date = order_data.shipping_date
        if order_data.status is not None:
            order.status = order_data.status
        if order_data.remark is not None:
            order.remark = order_data.remark

        # 如果涉及金额的字段有变化，重新计算净利润和利润率
        if (order_data.sell_price is not None or 
            order_data.cost_price is not None or 
            order_data.shipping_fee is not None or 
            order_data.platform_fee is not None):
            
            profit_data = SoldOrderCrudService._calculate_profit(
                order.sell_price,
                order.cost_price,
                order.shipping_fee,
                order.platform_fee
            )
            order.net_profit = profit_data['net_profit']
            order.profit_rate = profit_data['profit_rate']

        db.commit()
        db.refresh(order)

        return order

    @staticmethod
    def delete_sold_order(
        db: Session,
        order_id: int,
        current_user: User
    ) -> Dict[str, Any]:
        """
        软删除已出售订单
        
        不物理删除订单记录，仅标记 is_active=False 和 deleted_at
        """
        order = db.query(SoldOrder).filter(
            SoldOrder.id == order_id,
            SoldOrder.user_id == current_user.id,
            SoldOrder.is_active == 1
        ).first()

        if not order:
            raise ValueError("订单不存在或已被删除")

        order.is_active = 0
        order.deleted_at = datetime.now()

        db.commit()

        return {"message": "订单删除成功", "order_id": order_id}

    @staticmethod
    def batch_delete_sold_orders(
        db: Session,
        order_ids: list[int],
        current_user: User
    ) -> Dict[str, Any]:
        """
        批量软删除已出售订单
        
        不物理删除订单记录，仅标记 is_active=False 和 deleted_at
        """
        success_count = 0
        failed_count = 0
        errors = []

        for order_id in order_ids:
            try:
                order = db.query(SoldOrder).filter(
                    SoldOrder.id == order_id,
                    SoldOrder.user_id == current_user.id,
                    SoldOrder.is_active == 1
                ).first()

                if order:
                    order.is_active = 0
                    order.deleted_at = datetime.now()
                    success_count += 1
                else:
                    failed_count += 1
                    errors.append(f"订单ID {order_id} 不存在或已被删除")
            except Exception as e:
                failed_count += 1
                errors.append(f"订单ID {order_id} 删除失败: {str(e)}")

        db.commit()

        return {
            "success_count": success_count,
            "failed_count": failed_count,
            "errors": errors
        }