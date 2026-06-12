"""
补款服务
提供尾款支付相关的业务逻辑
采用企业级服务层架构
"""
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, date, timedelta

from app.models.order import Order
from app.models.figure import Figure
from app.models.asset import OrderTransaction, AssetTransaction
from app.services.asset_transaction_service import AssetTransactionService
from app.services.figure_service import FigureService
from app.services.figure_service.figure_price_service import FigurePriceService


class PayBalanceService:
    """
    补款服务类

    提供以下核心功能：
    1. 获取待补款订单列表
    2. 支付尾款
    3. 创建尾款交易记录
    4. 更新订单状态并入库
    """

    @classmethod
    def get_pending_balance_orders(cls, db: Session, user_id: int) -> List[Dict[str, Any]]:
        """
        获取待补款订单列表

        过滤条件：
        - 订单状态为"未支付"（待付尾款）
        - 尾款金额 > 0
        - 展示全部需要支付尾款的数据，不限制时间范围

        排序规则：
        - 逾期订单置顶（标红）
        - 按到期日升序排列

        Args:
            db: 数据库会话
            user_id: 用户ID

        Returns:
            List[Dict]: 待补款订单列表
        """
        today = date.today()

        # 查询待补款订单
        orders = db.query(Order).filter(
            Order.user_id == user_id,
            Order.is_active == 1,
            Order.status == '未支付',  # 待支付尾款
            Order.balance > 0  # 有尾款需要支付
        ).order_by(Order.due_date.asc()).all()

        result = []
        for order in orders:
            # 获取手办信息
            figure = db.query(Figure).filter(Figure.id == order.figure_id).first()
            figure_name = figure.name if figure else "未知手办"
            figure_image = ""
            if figure and figure.images and isinstance(figure.images, list) and len(figure.images) > 0:
                figure_image = figure.images[0]

            # 计算逾期状态
            days_until_due = (order.due_date - today).days if order.due_date else 0
            is_overdue = days_until_due < 0

            # 计算逾期/到期描述
            if is_overdue:
                due_text = f"已逾期{abs(days_until_due)}天"
            elif days_until_due == 0:
                due_text = "今天到期"
            else:
                due_text = f"到期: {days_until_due}天后"

            result.append({
                "order_id": order.id,
                "order_number": order.display_order_number or f"ORDER-{order.id}",
                "figure_id": order.figure_id,
                "figure_name": figure_name,
                "figure_image": figure_image,
                "deposit": order.deposit or 0,
                "deposit_currency": order.deposit_currency or "CNY",
                "balance": order.balance or 0,
                "balance_currency": order.balance_currency or "CNY",
                "due_date": order.due_date.isoformat() if order.due_date else None,
                "days_until_due": days_until_due,
                "is_overdue": is_overdue,
                "due_text": due_text
            })

        # 排序：逾期置顶，然后按到期日升序
        result.sort(key=lambda x: (not x["is_overdue"], x["days_until_due"]))

        return result

    @classmethod
    def pay_balance(cls, db: Session, user_id: int, order_id: int, payment_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        支付尾款

        业务流程：
        1. 验证订单状态（必须为"未支付"）
        2. 创建尾款交易记录
        3. 更新订单状态为"已完成"
        4. 创建资产交易记录（入库）
        5. 更新手办平均入手价格

        Args:
            db: 数据库会话
            user_id: 用户ID
            order_id: 订单ID
            payment_data: 支付数据
                - payment_method: 支付方式
                - payment_date: 支付时间
                - amount: 本次支付金额（可选，默认为剩余尾款）

        Returns:
            Dict: 支付结果
        """
        try:
            # 查询订单
            order = db.query(Order).filter(
                Order.id == order_id,
                Order.user_id == user_id,
                Order.is_active == 1
            ).first()

            if not order:
                return {"success": False, "error": "订单不存在"}

            if order.status != "未支付":
                return {"success": False, "error": f"订单状态为{order.status}，无法支付尾款"}

            if order.balance <= 0:
                return {"success": False, "error": "该订单没有尾款需要支付"}

            # 提取支付数据
            payment_method = payment_data.get('payment_method', '支付宝')
            payment_date_str = payment_data.get('payment_date')
            payment_amount = payment_data.get('amount', order.balance)

            # 解析支付时间
            if payment_date_str:
                try:
                    payment_date = datetime.strptime(payment_date_str, '%Y-%m-%d %H:%M')
                except ValueError:
                    payment_date = datetime.now()
            else:
                payment_date = datetime.now()

            # 验证支付金额
            if payment_amount <= 0:
                return {"success": False, "error": "支付金额必须大于0"}

            if payment_amount > order.balance:
                return {"success": False, "error": f"支付金额不能超过尾款金额{order.balance}"}

            # 1. 创建尾款交易记录
            balance_tx = OrderTransaction(
                user_id=user_id,
                order_id=order.id,
                transaction_type='balance',
                total_amount=payment_amount,
                currency=order.balance_currency or 'CNY',
                direction='out',
                payment_method=payment_method,
                transaction_date=payment_date,
                is_active=True,
                created_at=datetime.now()
            )
            db.add(balance_tx)

            # 2. 更新订单状态
            order.status = '已完成'
            order.updated_at = datetime.now()

            # 如果部分支付，更新尾款金额
            if payment_amount < order.balance:
                order.balance = order.balance - payment_amount
            else:
                order.balance = 0

            # 3. 创建资产交易记录（入库）
            try:
                # 计算订单总金额
                total_price = FigurePriceService.calculate_order_amount_cny(
                    deposit=order.deposit,
                    deposit_currency=order.deposit_currency,
                    balance=order.balance + payment_amount,  # 加上本次支付的尾款
                    balance_currency=order.balance_currency
                )

                AssetTransactionService.create_transaction_from_figure(
                    db=db,
                    user_id=user_id,
                    figure_id=order.figure_id,
                    price=total_price,
                    quantity=1,
                    order_id=order.id
                )

                # 4. 更新手办平均入手价格
                FigureService.update_figure_average_purchase_price(db, order.figure_id)

                # 5. 更新手办持有数量（从库存账重新计算）
                current_inventory = db.query(func.sum(AssetTransaction.remaining_quantity)).filter(
                    AssetTransaction.user_id == user_id,
                    AssetTransaction.figure_id == order.figure_id,
                    AssetTransaction.transaction_type == "buy",
                    AssetTransaction.is_active == True
                ).scalar() or 0

                figure = db.query(Figure).filter(Figure.id == order.figure_id).first()
                if figure:
                    figure.quantity = int(current_inventory)

            except Exception as e:
                print(f"创建资产交易记录失败: {e}")
                # 不影响支付流程，继续提交

            db.commit()

            return {
                "success": True,
                "order_id": order.id,
                "payment_amount": payment_amount,
                "message": "尾款支付成功，订单已入库"
            }

        except Exception as e:
            db.rollback()
            return {"success": False, "error": f"支付尾款失败: {str(e)}"}

    @classmethod
    def get_order_payment_detail(cls, db: Session, user_id: int, order_id: int) -> Dict[str, Any]:
        """
        获取订单支付详情

        Args:
            db: 数据库会话
            user_id: 用户ID
            order_id: 订单ID

        Returns:
            Dict: 订单支付详情
        """
        order = db.query(Order).filter(
            Order.id == order_id,
            Order.user_id == user_id,
            Order.is_active == 1
        ).first()

        if not order:
            return {"error": "订单不存在"}

        # 获取手办信息
        figure = db.query(Figure).filter(Figure.id == order.figure_id).first()
        figure_name = figure.name if figure else "未知手办"

        return {
            "order_id": order.id,
            "order_number": order.display_order_number or f"ORDER-{order.id}",
            "figure_name": figure_name,
            "balance": order.balance or 0,
            "balance_currency": order.balance_currency or "CNY",
            "due_date": order.due_date.isoformat() if order.due_date else None
        }
