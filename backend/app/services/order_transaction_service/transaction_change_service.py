"""
交易变更追踪服务
提供订单资金变更检测和资金流水生成功能

核心功能：
- 检测订单定金/尾款/币种的变更
- 根据变更类型自动创建相应的资金流水记录
- 支持追加、调整、退款等多种变更场景
"""

from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session
from datetime import datetime

from app.models.order import Order
from app.models.asset import OrderTransaction
from app.models.user import User
from app.services.figure_service.figure_price_service import FigurePriceService


class OrderChangeType:
    """订单变更类型常量"""
    INITIAL = "initial"      # 初始创建
    SUPPLEMENT = "supplement"  # 追加金额
    ADJUST = "adjust"        # 调整金额
    REFUND = "refund"        # 退款
    CURRENCY_CHANGE = "currency_change"  # 币种变更


class OrderChangeField:
    """订单变更字段常量"""
    DEPOSIT = "deposit"      # 定金
    BALANCE = "balance"      # 尾款


class TransactionChangeService:
    """交易变更追踪服务类"""

    @staticmethod
    def detect_and_record_changes(
        db: Session,
        order: Order,
        old_deposit: float,
        old_deposit_currency: str,
        old_balance: float,
        old_balance_currency: str,
        current_user: User,
        change_reason: str = None
    ) -> List[OrderTransaction]:
        """
        检测订单变更并记录相应的资金流水

        Args:
            db: 数据库会话
            order: 更新后的订单对象
            old_deposit: 变更前定金金额
            old_deposit_currency: 变更前定金币种
            old_balance: 变更前尾款金额
            old_balance_currency: 变更前尾款币种
            current_user: 当前用户
            change_reason: 变更原因（可选）

        Returns:
            List[OrderTransaction]: 创建的资金流水记录列表
        """
        transactions = []

        # 1. 检测定金变更
        deposit_changes = TransactionChangeService._detect_field_change(
            field_name=OrderChangeField.DEPOSIT,
            old_amount=old_deposit,
            old_currency=old_deposit_currency,
            new_amount=order.deposit,
            new_currency=order.deposit_currency
        )

        for change in deposit_changes:
            transaction = TransactionChangeService._create_change_transaction(
                db=db,
                order=order,
                change=change,
                current_user=current_user,
                change_reason=change_reason
            )
            if transaction:
                transactions.append(transaction)

        # 2. 检测尾款变更
        balance_changes = TransactionChangeService._detect_field_change(
            field_name=OrderChangeField.BALANCE,
            old_amount=old_balance,
            old_currency=old_balance_currency,
            new_amount=order.balance,
            new_currency=order.balance_currency
        )

        for change in balance_changes:
            transaction = TransactionChangeService._create_change_transaction(
                db=db,
                order=order,
                change=change,
                current_user=current_user,
                change_reason=change_reason
            )
            if transaction:
                transactions.append(transaction)

        return transactions

    @staticmethod
    def _detect_field_change(
        field_name: str,
        old_amount: float,
        old_currency: str,
        new_amount: float,
        new_currency: str
    ) -> List[Dict[str, Any]]:
        """
        检测单个字段的变更

        Returns:
            List[Dict]: 变更列表，每个变更包含类型、金额、币种等信息
        """
        changes = []

        old_amount = old_amount or 0
        new_amount = new_amount or 0
        old_currency = old_currency or "CNY"
        new_currency = new_currency or "CNY"

        # 情况1：只有金额变化，币种不变
        if old_currency == new_currency:
            diff = new_amount - old_amount
            if diff > 0:
                # 金额增加 - 追加
                changes.append({
                    "field": field_name,
                    "change_type": OrderChangeType.SUPPLEMENT,
                    "amount": diff,
                    "currency": new_currency,
                    "previous_amount": old_amount,
                    "current_amount": new_amount,
                    "direction": "out",
                    "description": f"{field_name}_追加"
                })
            elif diff < 0:
                # 金额减少 - 退款
                changes.append({
                    "field": field_name,
                    "change_type": OrderChangeType.REFUND,
                    "amount": abs(diff),
                    "currency": new_currency,
                    "previous_amount": old_amount,
                    "current_amount": new_amount,
                    "direction": "in",
                    "description": f"{field_name}_退款"
                })
        else:
            # 情况2：币种发生变化
            # 策略：视为一次退款（原币种）+ 一次新支付（新币种）
            if old_amount > 0:
                changes.append({
                    "field": field_name,
                    "change_type": OrderChangeType.CURRENCY_CHANGE,
                    "amount": old_amount,
                    "currency": old_currency,
                    "previous_amount": old_amount,
                    "current_amount": 0,
                    "direction": "in",
                    "description": f"{field_name}_币种变更_退款（{old_currency}）"
                })

            if new_amount > 0:
                changes.append({
                    "field": field_name,
                    "change_type": OrderChangeType.CURRENCY_CHANGE,
                    "amount": new_amount,
                    "currency": new_currency,
                    "previous_amount": 0,
                    "current_amount": new_amount,
                    "direction": "out",
                    "description": f"{field_name}_币种变更_支付（{new_currency}）"
                })

        return changes

    @staticmethod
    def _create_change_transaction(
        db: Session,
        order: Order,
        change: Dict[str, Any],
        current_user: User,
        change_reason: str = None
    ) -> Optional[OrderTransaction]:
        """
        根据变更信息创建资金流水记录

        Args:
            db: 数据库会话
            order: 订单对象
            change: 变更信息
            current_user: 当前用户
            change_reason: 变更原因

        Returns:
            OrderTransaction: 创建的资金流水记录
        """
        # 查找该订单该字段的原始交易记录（用于建立关联）
        parent_transaction = db.query(OrderTransaction).filter(
            OrderTransaction.order_id == order.id,
            OrderTransaction.changed_field == change["field"],
            OrderTransaction.transaction_subtype == OrderChangeType.INITIAL,
            OrderTransaction.is_active == True
        ).first()

        # 确定交易类型
        if change["field"] == OrderChangeField.DEPOSIT:
            transaction_type = "deposit"
        else:
            transaction_type = "balance"

        # 创建变更描述
        notes = change["description"]
        if change_reason:
            notes = f"{notes} - {change_reason}"

        # 构建变更详情
        change_detail = f"{change['previous_amount']}{change.get('original_currency', change['currency'])} → {change['current_amount']}{change['currency']}"
        notes = f"{notes} ({change_detail})"

        transaction = OrderTransaction(
            user_id=current_user.id,
            figure_id=order.figure_id,
            order_id=order.id,
            transaction_type=transaction_type,
            direction=change["direction"],
            quantity=1,
            unit_price=change["amount"],
            total_amount=change["amount"],
            currency=change["currency"],
            transaction_date=datetime.now(),
            transaction_subtype=change["change_type"],
            parent_transaction_id=parent_transaction.id if parent_transaction else None,
            change_reason=change_reason,
            previous_amount=change["previous_amount"],
            current_amount=change["current_amount"],
            changed_field=change["field"],
            notes=notes
        )

        db.add(transaction)
        db.flush()
        return transaction

    @staticmethod
    def get_transaction_history(
        db: Session,
        order_id: int
    ) -> List[OrderTransaction]:
        """
        获取订单的资金流水历史（按时间排序）

        Args:
            db: 数据库会话
            order_id: 订单ID

        Returns:
            List[OrderTransaction]: 资金流水记录列表
        """
        return db.query(OrderTransaction).filter(
            OrderTransaction.order_id == order_id,
            OrderTransaction.is_active == True
        ).order_by(OrderTransaction.transaction_date.asc()).all()

    @staticmethod
    def calculate_running_total(
        db: Session,
        order_id: int
    ) -> Dict[str, float]:
        """
        计算订单的累计支付金额

        Args:
            db: 数据库会话
            order_id: 订单ID

        Returns:
            Dict: 包含各币种累计金额和人民币合计
        """
        transactions = db.query(OrderTransaction).filter(
            OrderTransaction.order_id == order_id,
            OrderTransaction.is_active == True,
            OrderTransaction.direction.in_(["out", "in"])
        ).all()

        totals = {
            "total_cny": 0.0,
            "by_currency": {}
        }

        for txn in transactions:
            # 转换为人民币
            amount_cny = FigurePriceService.convert_to_cny(
                txn.total_amount,
                txn.currency
            )

            if txn.direction == "out":
                totals["total_cny"] += amount_cny
                sign = 1
            else:  # refund
                totals["total_cny"] -= amount_cny
                sign = -1

            # 按币种统计
            currency = txn.currency
            if currency not in totals["by_currency"]:
                totals["by_currency"][currency] = 0.0
            totals["by_currency"][currency] += txn.total_amount * sign

        return totals
