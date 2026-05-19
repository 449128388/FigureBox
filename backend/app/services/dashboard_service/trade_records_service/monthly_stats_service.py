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
        # 本月买入统计（通过OrderTransaction）
        # 统计范围：本月内所有资金流出的买入行为
        # 包含：全款购买、定金支付、尾款支付（按实际付款时间统计）
        # 退款处理：transaction_type = 'REFUND' 的反向流水从当月买入中扣减
        # 跨月订单：按实际付款时间拆分统计，上月定金计入上月，本月尾款计入本月
        # 数据源：order_transactions 表中 transaction_type = 'BUY' 且 transaction_date 在本月内的记录
        buy_amount_result = db.query(
            func.coalesce(func.sum(OrderTransaction.total_amount), 0).label('amount')
        ).filter(
            OrderTransaction.user_id == user_id,
            OrderTransaction.transaction_type == "BUY",
            OrderTransaction.is_active == True,
            func.date(OrderTransaction.transaction_date) >= month_start,
            func.date(OrderTransaction.transaction_date) <= month_end
        ).scalar() or 0

        # 买入退款扣减（REFUND类型为负向流水）
        buy_refund_result = db.query(
            func.coalesce(func.sum(OrderTransaction.total_amount), 0).label('amount')
        ).filter(
            OrderTransaction.user_id == user_id,
            OrderTransaction.transaction_type == "REFUND",
            OrderTransaction.is_active == True,
            func.date(OrderTransaction.transaction_date) >= month_start,
            func.date(OrderTransaction.transaction_date) <= month_end
        ).scalar() or 0

        # 买入笔数统计（仅统计BUY类型，不含退款）
        buy_count_result = db.query(
            func.count(OrderTransaction.id).label('count')
        ).filter(
            OrderTransaction.user_id == user_id,
            OrderTransaction.transaction_type == "BUY",
            OrderTransaction.is_active == True,
            func.date(OrderTransaction.transaction_date) >= month_start,
            func.date(OrderTransaction.transaction_date) <= month_end
        ).scalar() or 0

        # 本月卖出统计（通过OrderTransaction）
        # 统计范围：本月内所有资金流入的卖出行为
        # 包含：库存手办卖出成交
        # 退货处理：transaction_type = 'RETURN' 的反向流水从当月卖出中扣减
        # 数据源：order_transactions 表中 transaction_type = 'SELL' 且 transaction_date 在本月内的记录
        sell_amount_result = db.query(
            func.coalesce(func.sum(OrderTransaction.total_amount), 0).label('amount')
        ).filter(
            OrderTransaction.user_id == user_id,
            OrderTransaction.transaction_type == "SELL",
            OrderTransaction.is_active == True,
            func.date(OrderTransaction.transaction_date) >= month_start,
            func.date(OrderTransaction.transaction_date) <= month_end
        ).scalar() or 0

        # 卖出退货扣减（RETURN类型为负向流水）
        sell_return_result = db.query(
            func.coalesce(func.sum(OrderTransaction.total_amount), 0).label('amount')
        ).filter(
            OrderTransaction.user_id == user_id,
            OrderTransaction.transaction_type == "RETURN",
            OrderTransaction.is_active == True,
            func.date(OrderTransaction.transaction_date) >= month_start,
            func.date(OrderTransaction.transaction_date) <= month_end
        ).scalar() or 0

        # 卖出笔数统计（仅统计SELL类型，不含退货）
        sell_count_result = db.query(
            func.count(OrderTransaction.id).label('count')
        ).filter(
            OrderTransaction.user_id == user_id,
            OrderTransaction.transaction_type == "SELL",
            OrderTransaction.is_active == True,
            func.date(OrderTransaction.transaction_date) >= month_start,
            func.date(OrderTransaction.transaction_date) <= month_end
        ).scalar() or 0

        # 计算最终买入金额（扣除退款）
        buy_amount = buy_amount_result - buy_refund_result
        buy_count = buy_count_result

        # 计算最终卖出金额（扣除退货）
        sell_amount = sell_amount_result - sell_return_result
        sell_count = sell_count_result

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
