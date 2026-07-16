"""
月度交易统计服务
提供月度买入、卖出统计及净现金流计算
采用企业级服务层架构
"""
from datetime import date
from typing import Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.models.asset import OrderTransaction
from app.models.order import Order
from app.models.sold_order import SoldOrder


class MonthlyStatsService:
    """
    月度交易统计服务类

    提供以下核心功能：
    1. 月度买入统计：统计本月买入订单数量和金额
    2. 月度卖出统计：统计本月卖出订单数量和金额
    3. 净现金流计算：卖出金额减去买入金额
    """

    @staticmethod
    def get_monthly_stats(
        db: Session,
        user_id: int,
        month_start: date,
        month_end: date
    ) -> Dict[str, Any]:
        """
        获取月度交易统计

        Args:
            db: 数据库会话
            user_id: 用户ID
            month_start: 月份开始日期
            month_end: 月份结束日期

        Returns:
            Dict: 月度统计，包含买入数量、买入金额、卖出数量、卖出金额、净现金流
        """
        # ======================== 买入统计 ========================
        # 数据源：order_transactions 表
        # 基础买入：transaction_type 为 deposit 或 buy，direction 为 out
        # 变更记录（supplement/refund/adjust/currency_change）按 transaction_subtype 分类处理

        # 1. 买入基础求和：deposit/buy + direction=out
        base_buy_amount = db.query(
            func.coalesce(func.sum(OrderTransaction.total_amount), 0).label('amount')
        ).join(
            Order, OrderTransaction.order_id == Order.id
        ).filter(
            OrderTransaction.user_id == user_id,
            OrderTransaction.transaction_type.in_(["deposit", "buy"]),
            OrderTransaction.direction == "out",
            OrderTransaction.is_active == True,
            Order.is_active == 1,
            func.date(OrderTransaction.transaction_date) >= month_start,
            func.date(OrderTransaction.transaction_date) <= month_end
        ).scalar() or 0

        # 买入笔数统计
        buy_count = db.query(
            func.count(OrderTransaction.id).label('count')
        ).join(
            Order, OrderTransaction.order_id == Order.id
        ).filter(
            OrderTransaction.user_id == user_id,
            OrderTransaction.transaction_type.in_(["deposit", "buy"]),
            OrderTransaction.direction == "out",
            OrderTransaction.is_active == True,
            Order.is_active == 1,
            func.date(OrderTransaction.transaction_date) >= month_start,
            func.date(OrderTransaction.transaction_date) <= month_end
        ).scalar() or 0

        # 2. 获取变更/调整类交易记录，按 subtype 分类处理
        change_txns = db.query(OrderTransaction).join(
            Order, OrderTransaction.order_id == Order.id
        ).filter(
            OrderTransaction.user_id == user_id,
            OrderTransaction.is_active == True,
            Order.is_active == 1,
            func.date(OrderTransaction.transaction_date) >= month_start,
            func.date(OrderTransaction.transaction_date) <= month_end,
            OrderTransaction.transaction_subtype.in_(["supplement", "refund", "adjust", "currency_change"])
        ).all()

        supplement_amount = 0      # 追加扣款
        refund_amount = 0          # 退款
        adjust_additional_amount = 0  # 调整追加
        adjust_refund_amount = 0      # 调整退款

        for tx in change_txns:
            if tx.transaction_subtype == "supplement":
                supplement_amount += tx.total_amount or 0
            elif tx.transaction_subtype == "refund":
                refund_amount += tx.total_amount or 0
            elif tx.transaction_subtype == "adjust":
                # 比较 previous_amount 与 current_amount 判断方向
                prev = tx.previous_amount or 0
                curr = tx.current_amount or 0
                if prev > curr:
                    adjust_refund_amount += tx.total_amount or 0
                else:
                    adjust_additional_amount += tx.total_amount or 0
            elif tx.transaction_subtype == "currency_change":
                if tx.direction == "in":
                    refund_amount += tx.total_amount or 0
                else:
                    supplement_amount += tx.total_amount or 0

        # 3. 计算最终买入金额（公式：base - supplement + refund - adjust_additional + adjust_refund）
        buy_amount = base_buy_amount - supplement_amount + refund_amount - adjust_additional_amount + adjust_refund_amount

        # ======================== 卖出统计（保持不变） ========================
        sell_amount_result = db.query(
            func.coalesce(func.sum(OrderTransaction.total_amount), 0).label('amount')
        ).join(
            SoldOrder, OrderTransaction.sold_order_id == SoldOrder.id
        ).filter(
            OrderTransaction.user_id == user_id,
            OrderTransaction.transaction_type == "SELL",
            OrderTransaction.is_active == True,
            SoldOrder.is_active == 1,
            func.date(OrderTransaction.transaction_date) >= month_start,
            func.date(OrderTransaction.transaction_date) <= month_end
        ).scalar() or 0

        # 卖出退货扣减（RETURN类型为负向流水）
        sell_return_result = db.query(
            func.coalesce(func.sum(OrderTransaction.total_amount), 0).label('amount')
        ).join(
            SoldOrder, OrderTransaction.sold_order_id == SoldOrder.id
        ).filter(
            OrderTransaction.user_id == user_id,
            OrderTransaction.transaction_type == "RETURN",
            OrderTransaction.is_active == True,
            SoldOrder.is_active == 1,
            func.date(OrderTransaction.transaction_date) >= month_start,
            func.date(OrderTransaction.transaction_date) <= month_end
        ).scalar() or 0

        # 卖出笔数统计（仅统计SELL类型，不含退货）
        sell_count = db.query(
            func.count(OrderTransaction.id).label('count')
        ).join(
            SoldOrder, OrderTransaction.sold_order_id == SoldOrder.id
        ).filter(
            OrderTransaction.user_id == user_id,
            OrderTransaction.transaction_type == "SELL",
            OrderTransaction.is_active == True,
            SoldOrder.is_active == 1,
            func.date(OrderTransaction.transaction_date) >= month_start,
            func.date(OrderTransaction.transaction_date) <= month_end
        ).scalar() or 0

        # 计算最终卖出金额（扣除退货）
        sell_amount = sell_amount_result - sell_return_result

        # 净现金流公式：买入总额 - 卖出总额
        # > 0 表示净流出（支出>收入），< 0 表示净流入（收入>支出）
        net_cashflow = buy_amount - sell_amount

        return {
            "buy_count": buy_count,
            "buy_amount": round(buy_amount, 2),
            "sell_count": sell_count,
            "sell_amount": round(sell_amount, 2),
            "net_cashflow": round(net_cashflow, 2)
        }
