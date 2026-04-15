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
from app.models.tag import Tag, figure_tag
from app.services.figure_service import FigureService
from app.services.asset_transaction_service import AssetTransactionService
from app.services.order_transaction_service import OrderTransactionService


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
            'purchase_price': figure_data.get('purchase_price', 0),
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
            # 【修复】创建订单并自动创建 asset_transactions 记录
            # 创建新订单
            order = Order()
            order.figure_id = figure.id
            order.user_id = user_id
            order.deposit = order_data.get('deposit', 0)
            order.balance = order_data.get('balance', 0)
            order.due_date = FigureImportService.parse_date(order_data.get('due_date'))
            order.status = order_data.get('status', '未支付')
            order.shop_name = order_data.get('shop_name', '')
            order.shop_contact = order_data.get('shop_contact', '')
            order.tracking_number = order_data.get('tracking_number')
            
            db.add(order)
            db.flush()  # 获取订单ID
            
            # 【修复】创建资产交易记录（库存账）和资金流水记录（资金账）
            try:
                # 1. 创建资产交易记录（库存账）- 记录数量变动
                AssetTransactionService.create_buy_transaction_from_order(
                    db=db,
                    user_id=user_id,
                    figure_id=figure.id,
                    order=order,
                    quantity=1  # 导入的订单默认数量为1
                )

                # 2. 创建资金流水记录（资金账）- 记录资金变动
                OrderTransactionService.create_transaction_from_order(
                    db=db,
                    user_id=user_id,
                    figure_id=figure.id,
                    order=order,
                    notes=f"订单导入 - {figure.name}"
                )
            except Exception as e:
                # 如果创建交易记录失败，不影响订单导入
                print(f"导入订单时创建交易记录失败: {e}")
            
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
