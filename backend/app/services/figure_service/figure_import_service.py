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
from app.models.asset import AssetTransaction, OrderTransaction
from .figure_service import FigureService
from app.services.asset_transaction_service import AssetTransactionService
from app.services.order_transaction_service import OrderTransactionService
from app.services.order_service.order_number_service import OrderNumberService
from app.services.sold_order_service.sold_order_transaction_service import SoldOrderTransactionService
from app.services.sold_order_service.sold_order_inventory_service import SoldOrderInventoryService
from app.services.sold_order_service.sold_order_figure_service import SoldOrderFigureService
from app.services.sold_order_service.sold_order_number_service import SoldOrderNumberService


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
    def get_or_create_tag(db: Session, tag_name: str) -> str:
        """
        获取或规范化标签名称（2026-07-29 重构：标签已合并到 figures.tags JSON 字段，无需再操作 Tag 表）

        Args:
            db: 数据库会话（保留以兼容旧签名）
            tag_name: 标签名称

        Returns:
            规范化后的标签名称字符串
        """
        # 去除首尾空格
        return tag_name.strip() if tag_name else tag_name
    
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
            'wishlist_status': figure_data.get('wishlist_status'),
            'source_url': figure_data.get('source_url'),
            'note': figure_data.get('note'),
            'tags': [],  # 2026-07-29 重构：标签改为 figure.tags JSON 字段，初始化为空列表
        }

        # 处理标签：合并为 JSON 字段（去重）
        tags_data = figure_data.get('tags', [])
        tag_names_list = []
        if tags_data:
            for tag_data in tags_data:
                tag_name = tag_data.get('name') if isinstance(tag_data, dict) else tag_data
                if tag_name:
                    tag_name = tag_name.strip()
                    if tag_name and tag_name not in tag_names_list:
                        tag_names_list.append(tag_name)
        processed_data['tags'] = tag_names_list

        # 使用 FigureService 创建手办（会自动创建 asset_transactions）
        figure = FigureService.create_figure(db, processed_data, user_id=user_id)

        # 2026-07-31 修复：补全库存账（asset_transactions）+ 资金账（order_transactions）导入路径
        # 解决「按 Order 重建」覆盖原始 buy/adjust 历史的问题
        FigureImportService.import_asset_transactions(
            db, figure, figure_data.get('asset_transactions', []), user_id
        )
        FigureImportService.import_order_transactions(
            db, figure, figure_data.get('order_transactions', []), user_id
        )

        # 2026-07-29 重构：标签已通过 processed_data['tags'] 传入，无需再单独处理
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
            order.payment_method = order_data.get('payment_method')
            order.payment_time = FigureImportService.parse_datetime(order_data.get('payment_time'))
            order.balance_payment_method = order_data.get('balance_payment_method')
            order.balance_payment_time = FigureImportService.parse_datetime(order_data.get('balance_payment_time'))
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
            
            # 记录动态流 BUY 事件（与订单 CRUD 保持一致的 event_type 和状态映射）
            try:
                from app.services.dashboard_service.collector_service.collector_activity_service import CollectorActivityService
                status_map = {
                    "未支付": "等待补款",
                    "已支付": "等待补款",
                    "已完成": "已付清"
                }
                feed_status = status_map.get(order.status, order.status)
                paid_type = "定金" if order.order_type == "定金预定" else "全款"
                CollectorActivityService.record_buy_event(
                    db=db,
                    user_id=user_id,
                    figure_id=figure.id,
                    figure_name=figure.name,
                    order_id=order.id,
                    order_no=order.order_number or order.display_order_number or "",
                    amount=order.deposit or 0,
                    paid_type=paid_type,
                    status=feed_status,
                    character=figure.work,
                    scale=figure.scale,
                    maker=figure.manufacturer,
                    currency=order.deposit_currency or "CNY",
                    balance=order.balance or 0,
                    balance_currency=order.balance_currency or "CNY"
                )

                # 已完成订单额外记录 IN_STOCK 到库事件
                if order.status == "已完成":
                    CollectorActivityService.record_in_stock_event(
                        db=db,
                        user_id=user_id,
                        figure_id=figure.id,
                        figure_name=figure.name,
                        in_date=datetime.now().strftime("%Y-%m-%d"),
                        order_no=order.order_number or order.display_order_number or "",
                        cost=order.balance or 0,
                        target_id=order.id,
                        target_type="order"
                    )
            except Exception as e:
                print(f"导入订单时记录动态流事件失败: {e}")
            
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
            sold_order.payment_method = sold_order_data.get('payment_method')
            sold_order.sell_date = FigureImportService.parse_date(sold_order_data.get('sell_date'))
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
            sold_order.display_order_number = sold_order_data.get('display_order_number')  # 展示订单编号
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

            # 生成展示订单编号
            SoldOrderNumberService.update_display_number(db, sold_order)

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
            
            # 记录动态流 SELL 事件（与 sold_order CRUD 保持一致）
            try:
                from app.services.dashboard_service.collector_service.collector_activity_service import CollectorActivityService
                hold_days = 0
                if figure.purchase_date and sold_order.created_at:
                    out_date = sold_order.created_at.date()
                    hold_days = max((out_date - figure.purchase_date).days, 0)
                CollectorActivityService.record_sell_event(
                    db=db,
                    user_id=user_id,
                    figure_id=figure.id,
                    figure_name=figure.name,
                    sell_price=sold_order.sell_price,
                    cost_price=sold_order.cost_price,
                    profit=sold_order.net_profit or 0,
                    buyer=sold_order.buyer_phone or "",
                    out_date=sold_order.created_at.strftime("%Y-%m-%d") if sold_order.created_at else "",
                    hold_days=hold_days,
                    order_no=sold_order.order_number or sold_order.display_order_number or "",
                    status=sold_order.status or "",
                    target_id=sold_order.id,
                    tracking_number=sold_order.tracking_number or "",
                    logistics_company=sold_order.logistics_company or "",
                    refund_amount=0
                )
            except Exception as e:
                print(f"导入已出售订单时记录动态流事件失败: {e}")

            imported_count += 1

        return imported_count

    @staticmethod
    def import_asset_transactions(db: Session, figure: Figure, asset_txs_data: List[Dict[str, Any]], user_id: int) -> int:
        """
        导入手办关联的资产交易记录（库存账）
        2026-07-31 修复：补全 buy/sell/adjust 全量历史

        流程：
        1. 删除 create_figure 自动生成的 buy 行（基于 processed_data.quantity 计算的占位行）
        2. 按 JSON 数组精确还原（含 transaction_date / notes / remaining_quantity / is_active）
        """
        if not asset_txs_data:
            return 0

        # 1. 清理 create_figure 自动生成的占位 buy 行
        db.query(AssetTransaction).filter(
            AssetTransaction.figure_id == figure.id,
            AssetTransaction.user_id == user_id
        ).delete(synchronize_session=False)
        db.flush()

        imported_count = 0
        for tx_data in asset_txs_data:
            tx = AssetTransaction(
                user_id=user_id,
                figure_id=figure.id,
                order_id=tx_data.get('order_id'),
                sold_order_id=tx_data.get('sold_order_id'),
                transaction_type=tx_data.get('transaction_type', 'buy'),
                price=tx_data.get('price', 0),
                quantity=tx_data.get('quantity', 1),
                total_amount=tx_data.get('total_amount', 0),
                remaining_quantity=tx_data.get('remaining_quantity'),
                transaction_date=FigureImportService.parse_datetime(tx_data.get('transaction_date')),
                notes=tx_data.get('notes'),
                is_active=tx_data.get('is_active', 1),
                created_at=FigureImportService.parse_datetime(tx_data.get('created_at')) or datetime.now(),
                updated_at=FigureImportService.parse_datetime(tx_data.get('updated_at')) or datetime.now()
            )
            tx.deleted_at = FigureImportService.parse_datetime(tx_data.get('deleted_at'))
            db.add(tx)
            imported_count += 1
        db.flush()
        return imported_count

    @staticmethod
    def import_order_transactions(db: Session, figure: Figure, order_txs_data: List[Dict[str, Any]], user_id: int) -> int:
        """
        导入手办关联的订单资金流水记录（资金账）
        2026-07-31 修复：补全 buy/deposit/balance/supplement/refund/fee/cancel 全量历史

        流程：
        1. 删除 import_orders 重建的资金流水（按 Order 当前状态生成的占位行）
        2. 按 JSON 数组精确还原（含 transaction_date / notes / parent_transaction_id / change_reason / previous_amount / current_amount / changed_field）
        """
        if not order_txs_data:
            return 0

        # 1. 清理 import_orders 重建的占位流水行
        db.query(OrderTransaction).filter(
            OrderTransaction.figure_id == figure.id,
            OrderTransaction.user_id == user_id
        ).delete(synchronize_session=False)
        db.flush()

        imported_count = 0
        for tx_data in order_txs_data:
            tx = OrderTransaction(
                user_id=user_id,
                figure_id=figure.id,
                order_id=tx_data.get('order_id'),
                sold_order_id=tx_data.get('sold_order_id'),
                transaction_type=tx_data.get('transaction_type', 'buy'),
                transaction_subtype=tx_data.get('transaction_subtype'),
                direction=tx_data.get('direction', 'out'),
                quantity=tx_data.get('quantity', 1),
                unit_price=tx_data.get('unit_price', 0),
                total_amount=tx_data.get('total_amount', 0),
                currency=tx_data.get('currency', 'CNY'),
                payment_method=tx_data.get('payment_method'),
                payment_time=FigureImportService.parse_datetime(tx_data.get('payment_time')),
                balance_payment_method=tx_data.get('balance_payment_method'),
                balance_payment_time=FigureImportService.parse_datetime(tx_data.get('balance_payment_time')),
                platform=tx_data.get('platform'),
                transaction_date=FigureImportService.parse_datetime(tx_data.get('transaction_date')) or datetime.now(),
                notes=tx_data.get('notes'),
                parent_transaction_id=tx_data.get('parent_transaction_id'),
                change_reason=tx_data.get('change_reason'),
                previous_amount=tx_data.get('previous_amount'),
                current_amount=tx_data.get('current_amount'),
                changed_field=tx_data.get('changed_field'),
                is_active=tx_data.get('is_active', 1),
                created_at=FigureImportService.parse_datetime(tx_data.get('created_at')) or datetime.now(),
                updated_at=FigureImportService.parse_datetime(tx_data.get('updated_at')) or datetime.now()
            )
            tx.deleted_at = FigureImportService.parse_datetime(tx_data.get('deleted_at'))
            db.add(tx)
            imported_count += 1
        db.flush()
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
