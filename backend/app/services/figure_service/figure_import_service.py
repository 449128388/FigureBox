"""
手办导入服务
提供手办数据导入相关的业务逻辑
"""
import json
from datetime import datetime, date
from typing import List, Dict, Any, Tuple, Optional
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.models.figure import Figure
from app.models.order import Order
from app.models.sold_order import SoldOrder
from app.models.tag import Tag, figure_tag
from .figure_service import FigureService
from app.services.asset_transaction_service import AssetTransactionService
from app.services.order_transaction_service import OrderTransactionService
from app.services.order_service.order_number_service import OrderNumberService
from app.services.sold_order_service.sold_order_transaction_service import SoldOrderTransactionService
from app.services.sold_order_service.sold_order_inventory_service import SoldOrderInventoryService
from app.services.sold_order_service.sold_order_figure_service import SoldOrderFigureService


class FigureImportService:
    """手办导入服务类"""
    
    @staticmethod
    def parse_date(date_value: Any) -> Optional[date]:
        """
        解析日期字符串为date对象
        
        Args:
            date_value: 日期字符串或None
            
        Returns:
            date对象或None
        """
        if not date_value:
            return None
        if isinstance(date_value, date):
            return date_value
        if isinstance(date_value, str):
            try:
                return datetime.strptime(date_value, '%Y-%m-%d').date()
            except ValueError:
                return None
        return None
    
    @staticmethod
    def get_or_create_tag(db: Session, tag_name: str) -> Tag:
        """
        获取或创建标签
        
        Args:
            db: 数据库会话
            tag_name: 标签名称
            
        Returns:
            Tag对象
        """
        tag = db.query(Tag).filter(Tag.name == tag_name).first()
        if not tag:
            tag = Tag(name=tag_name)
            db.add(tag)
            db.flush()
        return tag
    
    @staticmethod
    def import_figure(db: Session, figure_data: Dict[str, Any], user_id: int) -> Tuple[Figure, bool]:
        """
        导入单个手办数据
        
        Args:
            db: 数据库会话
            figure_data: 手办数据字典
            user_id: 用户ID
            
        Returns:
            (Figure对象, 是否为新创建)
        """
        # 【修复】使用 FigureService.create_figure() 创建手办
        # 这样可以自动创建对应的 asset_transactions 记录
        
        # 准备手办数据（处理日期格式）
        processed_data = {
            'name': figure_data.get('name', ''),
            'japanese_name': figure_data.get('japanese_name'),
            'manufacturer': figure_data.get('manufacturer'),
            'price': figure_data.get('price', 0),
            'currency': figure_data.get('currency', 'CNY'),
            'market_price': figure_data.get('market_price', 0),
            'market_currency': figure_data.get('market_currency', 'CNY'),
            'release_date': figure_data.get('release_date'),
            'average_purchase_price': figure_data.get('average_purchase_price', 0),
            'purchase_currency': figure_data.get('purchase_currency', 'CNY'),
            'purchase_date': figure_data.get('purchase_date'),
            'purchase_method': figure_data.get('purchase_method'),
            'purchase_type': figure_data.get('purchase_type', 'OTHER'),
            'scale': figure_data.get('scale'),
            'painting': figure_data.get('painting'),
            'original_art': figure_data.get('original_art'),
            'work': figure_data.get('work'),
            'material': figure_data.get('material'),
            'size': figure_data.get('size'),
            'images': figure_data.get('images', []),
            'quantity': figure_data.get('quantity', 1),
            'tag_ids': []  # 标签稍后单独处理
        }
        
        # 使用 FigureService 创建手办（会自动创建 asset_transactions）
        figure = FigureService.create_figure(db, processed_data, user_id=user_id)
        
        # 处理标签
        tags_data = figure_data.get('tags', [])
        if tags_data:
            for tag_data in tags_data:
                tag_name = tag_data.get('name') if isinstance(tag_data, dict) else tag_data
                if tag_name:
                    tag = FigureImportService.get_or_create_tag(db, tag_name)
                    if tag not in figure.tags:
                        figure.tags.append(tag)
            db.commit()
        
        return figure, True
    
    @staticmethod
    def parse_datetime(datetime_value: Any) -> Optional[datetime]:
        """
        解析日期时间字符串为datetime对象
        
        Args:
            datetime_value: 日期时间字符串或None
            
        Returns:
            datetime对象或None
        """
        if not datetime_value:
            return None
        if isinstance(datetime_value, datetime):
            return datetime_value
        if isinstance(datetime_value, str):
            try:
                # 处理 ISO 格式 (2026-05-25T17:51:28)
                return datetime.fromisoformat(datetime_value.replace('Z', '+00:00'))
            except ValueError:
                try:
                    return datetime.strptime(datetime_value, '%Y-%m-%d %H:%M:%S')
                except ValueError:
                    return None
        return None

    @staticmethod
    def import_orders(db: Session, figure: Figure, orders_data: List[Dict[str, Any]], user_id: int) -> int:
        """
        导入手办关联的订单
        
        Args:
            db: 数据库会话
            figure: 手办对象
            orders_data: 订单数据列表
            user_id: 用户ID
            
        Returns:
            导入的订单数量
        """
        imported_count = 0
        
        for order_data in orders_data:
            # 创建新订单
            order = Order()
            order.figure_id = figure.id
            order.user_id = user_id
            order.deposit = order_data.get('deposit', 0)
            order.deposit_currency = order_data.get('deposit_currency', 'CNY')
            order.balance = order_data.get('balance', 0)
            order.balance_currency = order_data.get('balance_currency', 'CNY')
            order.due_date = FigureImportService.parse_date(order_data.get('due_date'))
            order.order_type = order_data.get('order_type', '定金预定')
            order.status = order_data.get('status', '未支付')
            order.shop_name = order_data.get('shop_name', '')
            order.shop_contact = order_data.get('shop_contact', '')
            order.tracking_number = order_data.get('tracking_number')
            order.logistics_company = order_data.get('logistics_company')
            order.order_number = order_data.get('order_number')
            order.display_order_number = order_data.get('display_order_number')
            order.remarks = order_data.get('remarks')
            order.is_active = order_data.get('is_active', 1)
            order.created_at = FigureImportService.parse_datetime(order_data.get('created_at')) or datetime.now()
            order.updated_at = FigureImportService.parse_datetime(order_data.get('updated_at')) or datetime.now()

            db.add(order)
            db.flush()  # 获取订单ID

            # 生成展示订单编号（格式：ORDER-YYYYMMDD-XXX）
            OrderNumberService.update_order_display_number(db, order)

            # 创建资金流水记录（资金账）和/或资产交易记录（库存账）
            # 根据订单状态决定记录类型：
            # - "已完成"：同时记录资金流水+资产交易（已拿到货物，有完整资金流动）
            # - "已支付"：只记录资金流水（有资金流出但未到货）
            # - "已取消"：只记录资金流水（已支付过定金/全款，订单已取消）
            # - "未支付"：不记录任何数据（无资金流动）
            if order.status in ("已完成", "已支付", "已取消"):
                try:
                    # 资金流水记录（资金账）- 所有已产生资金流动的状态都记录
                    purchase_date = FigureImportService.parse_date(order_data.get('purchase_date'))
                    OrderTransactionService.create_transaction_from_order(
                        db=db,
                        user_id=user_id,
                        figure_id=figure.id,
                        order=order,
                        transaction_date=purchase_date,
                        notes=f"订单导入 - {figure.name}"
                    )

                    # 资产交易记录（库存账）- 只有"已完成"才记录（代表已入库）
                    if order.status == "已完成":
                        order_quantity = order_data.get('quantity', 1)
                        AssetTransactionService.create_buy_transaction_from_order(
                            db=db,
                            user_id=user_id,
                            figure_id=figure.id,
                            order=order,
                            quantity=order_quantity
                        )
                except Exception as e:
                    print(f"导入订单时创建交易记录失败: {e}")
                    import traceback
                    traceback.print_exc()
            
            imported_count += 1
        
        # 更新手办数量为实际入库数量（仅统计"已完成"订单，与asset_transactions保持一致）
        if imported_count > 0:
            completed_count = sum(1 for o in db.query(Order).filter(
                Order.figure_id == figure.id,
                Order.status == "已完成"
            ).all())
            figure.quantity = completed_count
            db.flush()

        return imported_count

    @staticmethod
    def import_sold_orders(db: Session, figure: Figure, sold_orders_data: List[Dict[str, Any]], user_id: int) -> int:
        """
        导入手办关联的已出售订单

        Args:
            db: 数据库会话
            figure: 手办对象
            sold_orders_data: 已出售订单数据列表
            user_id: 用户ID

        Returns:
            导入的已出售订单数量
        """
        imported_count = 0

        for sold_order_data in sold_orders_data:
            # 创建新已出售订单
            sold_order = SoldOrder()
            sold_order.figure_id = figure.id
            sold_order.user_id = user_id
            sold_order.quantity = sold_order_data.get('quantity', 1)
            sold_order.sell_price = sold_order_data.get('sell_price', 0)
            sold_order.sell_price_currency = sold_order_data.get('sell_price_currency', 'CNY')
            sold_order.cost_price = sold_order_data.get('cost_price', 0)
            sold_order.cost_price_currency = sold_order_data.get('cost_price_currency', 'CNY')
            sold_order.shipping_fee = sold_order_data.get('shipping_fee', 0)
            sold_order.shipping_fee_currency = sold_order_data.get('shipping_fee_currency', 'CNY')
            sold_order.platform_fee = sold_order_data.get('platform_fee', 0)
            sold_order.platform_fee_currency = sold_order_data.get('platform_fee_currency', 'CNY')
            sold_order.net_profit = sold_order_data.get('net_profit')
            sold_order.profit_rate = sold_order_data.get('profit_rate')
            sold_order.sell_platform = sold_order_data.get('sell_platform')
            sold_order.order_number = sold_order_data.get('order_number')
            sold_order.buyer_phone = sold_order_data.get('buyer_phone')
            sold_order.buyer_address = sold_order_data.get('buyer_address')
            sold_order.tracking_number = sold_order_data.get('tracking_number')
            sold_order.logistics_company = sold_order_data.get('logistics_company')
            sold_order.shipping_date = FigureImportService.parse_date(sold_order_data.get('shipping_date'))
            sold_order.status = sold_order_data.get('status', '待发货')
            sold_order.remark = sold_order_data.get('remark')
            sold_order.is_active = sold_order_data.get('is_active', 1)
            sold_order.created_at = FigureImportService.parse_datetime(sold_order_data.get('created_at')) or datetime.now()
            sold_order.updated_at = FigureImportService.parse_datetime(sold_order_data.get('updated_at')) or datetime.now()

            db.add(sold_order)
            db.flush()  # 获取订单ID

            # 设置 updated_at 等于 created_at（与创建时保持一致）
            sold_order.updated_at = sold_order.created_at

            # 创建卖出订单相关记录
            # 只处理非"退款/纠纷"状态的订单
            if sold_order.status != "退款/纠纷":
                try:
                    # 1. 尾款管理：创建卖出订单主记录和资金流水（3笔）
                    SoldOrderTransactionService.create_all_sold_order_transactions(
                        db, sold_order, user_id
                    )

                    # 2. 库存账：扣减库存数量
                    SoldOrderInventoryService.deduct_inventory(
                        db, sold_order, user_id
                    )

                    # 3. 手办聚合状态：更新库存数量和售罄状态
                    SoldOrderFigureService.update_figure_status(
                        db, sold_order, user_id
                    )
                except Exception as e:
                    print(f"导入已出售订单时创建交易记录失败: {e}")
                    import traceback
                    traceback.print_exc()

            imported_count += 1

        return imported_count

    @classmethod
    def import_figures_from_json(
        cls,
        db: Session,
        json_data: List[Dict[str, Any]],
        user_id: int
    ) -> Dict[str, Any]:
        """
        从JSON数据导入手办和订单
        
        Args:
            db: 数据库会话
            json_data: JSON数据列表
            user_id: 用户ID
            
        Returns:
            导入结果统计
        """
        result = {
            'success': True,
            'imported_figures': 0,
            'updated_figures': 0,
            'imported_orders': 0,
            'imported_sold_orders': 0,
            'errors': []
        }

        try:
            for index, figure_data in enumerate(json_data):
                try:
                    # 导入手办
                    figure, is_new = cls.import_figure(db, figure_data, user_id)

                    if is_new:
                        result['imported_figures'] += 1
                    # 不再增加 updated_figures 计数，因为我们不会更新已存在的手办

                    # 导入关联订单
                    orders_data = figure_data.get('orders', [])
                    if orders_data:
                        orders_count = cls.import_orders(db, figure, orders_data, user_id)
                        result['imported_orders'] += orders_count

                    # 导入关联已出售订单
                    sold_orders_data = figure_data.get('sold_orders', [])
                    if sold_orders_data:
                        sold_orders_count = cls.import_sold_orders(db, figure, sold_orders_data, user_id)
                        result['imported_sold_orders'] += sold_orders_count

                except Exception as e:
                    error_msg = f"第 {index + 1} 条记录导入失败: {str(e)}"
                    result['errors'].append(error_msg)

            # 提交事务
            db.commit()

        except Exception as e:
            db.rollback()
            result['success'] = False
            result['errors'].append(f"导入过程中发生错误: {str(e)}")

        return result
