"""
手办导出服务
提供手办数据导出相关的业务逻辑
"""
import json
from datetime import datetime
from typing import List, Dict, Any
from sqlalchemy.orm import Session

from app.models.figure import Figure
from app.models.order import Order
from app.models.sold_order import SoldOrder


class FigureExportService:
    """手办导出服务类"""
    
    @staticmethod
    def json_serial(obj) -> str:
        """
        JSON 序列化辅助函数，处理日期类型
        
        Args:
            obj: 要序列化的对象
            
        Returns:
            序列化后的字符串
            
        Raises:
            TypeError: 类型不支持序列化时抛出
        """
        if isinstance(obj, datetime):
            return obj.isoformat()
        raise TypeError(f"类型 {type(obj)} 不可序列化")
    
    @staticmethod
    def get_figure_orders(db: Session, figure_id: int) -> List[Dict[str, Any]]:
        """
        获取手办关联的尾款订单

        Args:
            db: 数据库会话
            figure_id: 手办ID

        Returns:
            订单数据字典列表
        """
        orders = db.query(Order).filter(Order.figure_id == figure_id).all()
        orders_data = []

        for order in orders:
            order_dict = {
                "id": order.id,
                "user_id": order.user_id,
                "figure_id": order.figure_id,
                "deposit": order.deposit,
                "deposit_currency": order.deposit_currency,
                "balance": order.balance,
                "balance_currency": order.balance_currency,
                "due_date": order.due_date.isoformat() if order.due_date else None,
                "order_type": order.order_type,
                "status": order.status,
                "shop_name": order.shop_name,
                "shop_contact": order.shop_contact,
                "tracking_number": order.tracking_number,
                "logistics_company": order.logistics_company,
                "order_number": order.order_number,
                "display_order_number": order.display_order_number,
                "remarks": order.remarks,
                "created_at": order.created_at.isoformat() if order.created_at else None,
                "updated_at": order.updated_at.isoformat() if order.updated_at else None,
                "is_active": order.is_active,
                "deleted_at": order.deleted_at.isoformat() if order.deleted_at else None
            }
            orders_data.append(order_dict)

        return orders_data

    @staticmethod
    def get_figure_sold_orders(db: Session, figure_id: int) -> List[Dict[str, Any]]:
        """
        获取手办关联的已出售订单

        Args:
            db: 数据库会话
            figure_id: 手办ID

        Returns:
            已出售订单数据字典列表
        """
        sold_orders = db.query(SoldOrder).filter(SoldOrder.figure_id == figure_id).all()
        sold_orders_data = []

        for sold_order in sold_orders:
            sold_order_dict = {
                "id": sold_order.id,
                "user_id": sold_order.user_id,
                "figure_id": sold_order.figure_id,
                "quantity": sold_order.quantity,
                "sell_price": sold_order.sell_price,
                "sell_price_currency": sold_order.sell_price_currency,
                "cost_price": sold_order.cost_price,
                "cost_price_currency": sold_order.cost_price_currency,
                "shipping_fee": sold_order.shipping_fee,
                "shipping_fee_currency": sold_order.shipping_fee_currency,
                "platform_fee": sold_order.platform_fee,
                "platform_fee_currency": sold_order.platform_fee_currency,
                "net_profit": sold_order.net_profit,
                "profit_rate": sold_order.profit_rate,
                "sell_platform": sold_order.sell_platform,
                "order_number": sold_order.order_number,
                "buyer_phone": sold_order.buyer_phone,
                "buyer_address": sold_order.buyer_address,
                "tracking_number": sold_order.tracking_number,
                "logistics_company": sold_order.logistics_company,
                "shipping_date": sold_order.shipping_date.isoformat() if sold_order.shipping_date else None,
                "status": sold_order.status,
                "remark": sold_order.remark,
                "created_at": sold_order.created_at.isoformat() if sold_order.created_at else None,
                "updated_at": sold_order.updated_at.isoformat() if sold_order.updated_at else None,
                "is_active": sold_order.is_active,
                "deleted_at": sold_order.deleted_at.isoformat() if sold_order.deleted_at else None
            }
            sold_orders_data.append(sold_order_dict)

        return sold_orders_data

    @staticmethod
    def serialize_tags(figure: Figure) -> List[Dict[str, Any]]:
        """
        序列化标签对象为字典列表
        
        Args:
            figure: 手办对象
            
        Returns:
            标签数据字典列表
        """
        tags_data = []
        for tag in figure.tags:
            tag_dict = {
                "id": tag.id,
                "name": tag.name
            }
            tags_data.append(tag_dict)
        return tags_data
    
    @staticmethod
    def serialize_figure(db: Session, figure: Figure) -> Dict[str, Any]:
        """
        序列化手办对象为字典
        
        Args:
            db: 数据库会话
            figure: 手办对象
            
        Returns:
            手办数据字典
        """
        # 获取关联订单
        orders_data = FigureExportService.get_figure_orders(db, figure.id)

        # 获取关联已出售订单
        sold_orders_data = FigureExportService.get_figure_sold_orders(db, figure.id)

        # 序列化标签
        tags_data = FigureExportService.serialize_tags(figure)
        
        return {
            "id": figure.id,
            "name": figure.name,
            "japanese_name": figure.japanese_name,
            "manufacturer": figure.manufacturer,
            "price": figure.price,
            "currency": figure.currency,
            "market_price": figure.market_price,
            "market_currency": figure.market_currency,
            "quantity": figure.quantity,
            "tags": tags_data,
            "release_date": figure.release_date.isoformat() if figure.release_date else None,
            "average_purchase_price": figure.average_purchase_price,
            "purchase_currency": figure.purchase_currency,
            "purchase_date": figure.purchase_date.isoformat() if figure.purchase_date else None,
            "purchase_method": figure.purchase_method,
            "purchase_type": figure.purchase_type,
            "scale": figure.scale,
            "painting": figure.painting,
            "original_art": figure.original_art,
            "work": figure.work,
            "material": figure.material,
            "size": figure.size,
            "images": figure.images,
            "is_active": figure.is_active,
            "deleted_at": figure.deleted_at.isoformat() if figure.deleted_at else None,
            "created_at": figure.created_at.isoformat() if figure.created_at else None,
            "updated_at": figure.updated_at.isoformat() if figure.updated_at else None,
            "orders": orders_data,
            "sold_orders": sold_orders_data
        }
    
    @classmethod
    def export_all_figures(
        cls,
        db: Session
    ) -> str:
        """
        导出所有手办数据为JSON字符串
        
        Args:
            db: 数据库会话
            
        Returns:
            JSON格式的字符串
            
        Raises:
            Exception: 导出过程中发生错误时抛出
        """
        try:
            # 获取所有手办数据（不含愿望清单）
            figures = db.query(Figure).filter(
                Figure.purchase_type != 'wishlist',
            ).all()
            
            # 转换为字典列表
            figures_data = []
            for figure in figures:
                figure_dict = cls.serialize_figure(db, figure)
                figures_data.append(figure_dict)
            
            # 转换为 JSON 字符串
            json_data = json.dumps(
                figures_data,
                ensure_ascii=False,
                indent=2,
                default=cls.json_serial
            )
            
            return json_data
            
        except Exception as e:
            import traceback
            print(f"导出数据时发生错误: {str(e)}")
            print(traceback.format_exc())
            raise
    
    @staticmethod
    def get_export_filename() -> str:
        """
        获取导出文件名
        
        Returns:
            格式化的文件名
        """
        return f"figures_{datetime.utcnow().strftime('%Y-%m-%d')}.json"
