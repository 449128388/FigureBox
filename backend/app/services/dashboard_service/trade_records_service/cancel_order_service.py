"""
撤单服务
提供取消订单功能，支持退款和库存回滚
采用企业级服务层架构
"""
from typing import Dict, Any, Optional, List
from sqlalchemy.orm import Session
from datetime import datetime, date

from app.models.order import Order
from app.models.figure import Figure
from app.models.asset import OrderTransaction, AssetTransaction
from app.services.asset_transaction_service import AssetTransactionService
from app.services.figure_service import FigureService
from app.services.figure_service.figure_price_service import FigurePriceService


# 汇率配置：相对人民币的汇率
EXCHANGE_RATES = {
    'CNY': 1.0,    # 人民币
    'JPY': 1/23,   # 日元：1人民币 = 23日元
    'USD': 7.0,    # 美元：1美元 = 7人民币
    'EUR': 8.0     # 欧元：1欧元 = 8人民币
}


class CancelOrderService:
    """
    撤单服务类

    提供以下核心功能：
    1. 获取可取消订单列表
    2. 获取订单取消详情（用于确认弹窗）
    3. 取消订单（支持退款和库存回滚）

    取消规则：
    - 只有 status IN ('待付尾款', '已付定金', '待发货') 的订单可取消
    - 已完成的卖出/买入不可取消（需走售后/退货流程）
    - 预定单已付定金：可选退定金或不退（定金沉没）
    - 全款现货/补仓：必须全额退款
    - 已入库订单取消时必须回滚库存
    """

    # 可取消的订单状态
    CANCELABLE_STATUSES = ['已支付', '未支付', '待发货']

    @classmethod
    def get_cancelable_orders(cls, db: Session, user_id: int) -> List[Dict[str, Any]]:
        """
        获取可取消订单列表

        Args:
            db: 数据库会话
            user_id: 用户ID

        Returns:
            List[Dict]: 可取消订单列表
        """
        orders = db.query(Order).filter(
            Order.user_id == user_id,
            Order.is_active == 1,
            Order.status.in_(cls.CANCELABLE_STATUSES)
        ).order_by(Order.created_at.desc()).all()

        result = []
        for order in orders:
            figure = db.query(Figure).filter(Figure.id == order.figure_id).first()

            # 计算已支付金额
            paid_amount = cls._calculate_paid_amount(db, order)

            # 判断订单是否已入库
            is_in_stock = cls._check_order_in_stock(db, order)

            result.append({
                "order_id": order.id,
                "order_number": order.display_order_number or order.order_number or "-",
                "figure_name": figure.name if figure else "未知手办",
                "figure_image": figure.images[0] if figure and figure.images and isinstance(figure.images, list) else "",
                "order_type": order.order_type or "定金预定",
                "status": order.status,
                "paid_amount": paid_amount,
                "balance": order.balance or 0,
                "deposit": order.deposit or 0,
                "is_in_stock": is_in_stock,
                "created_at": order.created_at.strftime("%Y-%m-%d") if order.created_at else "-"
            })

        return result

    @classmethod
    def get_order_cancel_detail(cls, db: Session, user_id: int, order_id: int) -> Dict[str, Any]:
        """
        获取订单取消详情（用于确认弹窗）

        Args:
            db: 数据库会话
            user_id: 用户ID
            order_id: 订单ID

        Returns:
            Dict: 订单取消详情
        """
        order = db.query(Order).filter(
            Order.id == order_id,
            Order.user_id == user_id,
            Order.is_active == 1
        ).first()

        if not order:
            return {"error": "订单不存在"}

        # 检查订单状态是否可取消
        if order.status not in cls.CANCELABLE_STATUSES:
            return {"error": f"订单状态为'{order.status}'，不可取消"}

        figure = db.query(Figure).filter(Figure.id == order.figure_id).first()

        # 计算已支付金额
        paid_amount = cls._calculate_paid_amount(db, order)

        # 判断订单是否已入库
        is_in_stock = cls._check_order_in_stock(db, order)

        # 获取库存数量
        stock_quantity = 0
        if is_in_stock:
            asset_tx = db.query(AssetTransaction).filter(
                AssetTransaction.order_id == order.id,
                AssetTransaction.transaction_type == 'buy',
                AssetTransaction.is_active == True
            ).first()
            if asset_tx:
                stock_quantity = asset_tx.quantity or 1

        # 判断是否为预定单（有定金）
        is_preorder = order.order_type in ['定金预定', '全款预定'] or order.deposit > 0

        # 判断是否为全款现货/补仓
        is_full_payment = order.order_type in ['现货', '补仓'] or (order.deposit > 0 and order.balance == 0)

        return {
            "order_id": order.id,
            "order_number": order.display_order_number or order.order_number or "-",
            "figure_name": figure.name if figure else "未知手办",
            "figure_image": figure.images[0] if figure and figure.images and isinstance(figure.images, list) else "",
            "order_type": order.order_type or "定金预定",
            "status": order.status,
            "status_text": cls._get_status_text(order.status),
            "paid_amount": paid_amount,
            "deposit": order.deposit or 0,
            "balance": order.balance or 0,
            "is_in_stock": is_in_stock,
            "stock_quantity": stock_quantity,
            "is_preorder": is_preorder,
            "is_full_payment": is_full_payment,
            "can_refund_deposit": is_preorder,  # 预定单可以选择是否退定金
            "must_full_refund": is_full_payment,  # 全款必须全额退款
            "refund_amount": paid_amount,  # 默认可退金额为已支付金额
            "currency": order.deposit_currency or 'CNY'
        }

    @classmethod
    def cancel_order(cls, db: Session, user_id: int, order_id: int, cancel_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        取消订单

        Args:
            db: 数据库会话
            user_id: 用户ID
            order_id: 订单ID
            cancel_data: 取消参数
                - refund: 是否退款（bool）
                - refund_amount: 退款金额（可选，默认为已支付金额）
                - refund_method: 退款方式（可选）
                - reason: 取消原因（可选）

        Returns:
            Dict: 取消结果
        """
        try:
            order = db.query(Order).filter(
                Order.id == order_id,
                Order.user_id == user_id,
                Order.is_active == 1
            ).first()

            if not order:
                return {"success": False, "error": "订单不存在"}

            # 检查订单状态是否可取消
            if order.status not in cls.CANCELABLE_STATUSES:
                return {"success": False, "error": f"订单状态为'{order.status}'，不可取消"}

            figure = db.query(Figure).filter(Figure.id == order.figure_id).first()

            # 计算已支付金额
            paid_amount = cls._calculate_paid_amount(db, order)

            # 判断订单是否已入库
            is_in_stock = cls._check_order_in_stock(db, order)

            # 获取取消参数
            refund = cancel_data.get('refund', True)
            refund_amount = cancel_data.get('refund_amount', paid_amount if refund else 0)
            refund_method = cancel_data.get('refund_method', '原路退回')
            reason = cancel_data.get('reason', '')

            # 验证退款金额
            if refund and refund_amount > paid_amount:
                return {"success": False, "error": f"退款金额不能大于已支付金额 ¥{paid_amount}"}

            now = datetime.now()

            # 1. 如果已入库，回滚库存
            if is_in_stock:
                cls._rollback_stock(db, user_id, order, figure)

            # 2. 如果需要退款，创建退款交易记录
            if refund and refund_amount > 0:
                refund_tx = OrderTransaction(
                    user_id=user_id,
                    order_id=order.id,
                    transaction_type='refund',
                    total_amount=refund_amount,
                    currency=order.deposit_currency or 'CNY',
                    direction='in',
                    payment_method=refund_method,
                    transaction_date=now,
                    notes=f"订单取消退款: {reason}" if reason else "订单取消退款",
                    is_active=True,
                    created_at=now
                )
                db.add(refund_tx)

            # 3. 更新订单状态
            order.status = '已取消'
            order.updated_at = now

            # 4. 创建订单状态变更记录
            status_tx = OrderTransaction(
                user_id=user_id,
                order_id=order.id,
                transaction_type='cancel',
                total_amount=0,
                currency=order.deposit_currency or 'CNY',
                direction='out',
                payment_method='system',
                transaction_date=now,
                notes=f"订单已取消: {reason}" if reason else "订单已取消",
                is_active=True,
                created_at=now
            )
            db.add(status_tx)

            db.commit()

            return {
                "success": True,
                "order_id": order.id,
                "refund_amount": refund_amount if refund else 0,
                "is_stock_rolled_back": is_in_stock,
                "message": "订单取消成功"
            }

        except Exception as e:
            db.rollback()
            return {"success": False, "error": f"取消订单失败: {str(e)}"}

    @classmethod
    def _calculate_paid_amount(cls, db: Session, order: Order) -> float:
        """
        计算订单已支付金额

        Args:
            db: 数据库会话
            order: 订单对象

        Returns:
            float: 已支付金额（人民币）
        """
        # 查询该订单的所有支付交易记录
        transactions = db.query(OrderTransaction).filter(
            OrderTransaction.order_id == order.id,
            OrderTransaction.transaction_type.in_(['deposit', 'balance', 'full_payment']),
            OrderTransaction.direction == 'out',
            OrderTransaction.is_active == True
        ).all()

        total_paid = 0
        for tx in transactions:
            currency = tx.currency or 'CNY'
            rate = EXCHANGE_RATES.get(currency, 1.0)
            total_paid += tx.total_amount * rate

        return round(total_paid, 2)

    @classmethod
    def _check_order_in_stock(cls, db: Session, order: Order) -> bool:
        """
        检查订单是否已入库

        Args:
            db: 数据库会话
            order: 订单对象

        Returns:
            bool: 是否已入库
        """
        asset_tx = db.query(AssetTransaction).filter(
            AssetTransaction.order_id == order.id,
            AssetTransaction.transaction_type == 'buy',
            AssetTransaction.is_active == True
        ).first()

        return asset_tx is not None

    @classmethod
    def _rollback_stock(cls, db: Session, user_id: int, order: Order, figure: Figure):
        """
        回滚库存

        Args:
            db: 数据库会话
            user_id: 用户ID
            order: 订单对象
            figure: 手办对象
        """
        now = datetime.now()

        # 查找对应的资产交易记录
        asset_tx = db.query(AssetTransaction).filter(
            AssetTransaction.order_id == order.id,
            AssetTransaction.transaction_type == 'buy',
            AssetTransaction.is_active == True
        ).first()

        if asset_tx:
            # 创建退货记录（RETURN类型）
            return_tx = AssetTransaction(
                user_id=user_id,
                figure_id=order.figure_id,
                order_id=order.id,
                transaction_type='return',
                price=asset_tx.price,
                quantity=asset_tx.quantity,
                total_amount=asset_tx.total_amount,
                transaction_date=now,
                notes=f"订单取消库存回滚: 回滚{asset_tx.quantity}体",
                is_active=True,
                created_at=now
            )
            db.add(return_tx)

            # 软删除原买入记录
            asset_tx.is_active = False
            asset_tx.updated_at = now

            # 更新手办库存数量
            if figure:
                figure.stock_quantity = max(0, (figure.stock_quantity or 0) - asset_tx.quantity)
                figure.updated_at = now

    @staticmethod
    def _get_status_text(status: str) -> str:
        """获取状态显示文本"""
        status_map = {
            '未支付': '待支付',
            '已支付': '已付定金，尾款未付',
            '待发货': '待发货',
            '已完成': '已完成',
            '已取消': '已取消'
        }
        return status_map.get(status, status)
