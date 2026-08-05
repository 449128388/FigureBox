"""
盈亏分析服务
提供盈亏分析相关的核心业务逻辑
采用企业级服务层架构
"""
from typing import Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import extract
from datetime import datetime

from app.models.figure import Figure
from app.models.sold_order import SoldOrder
from app.models.order_finance import OrderTransaction


class TradeProfitAnalysisService:
    """
    交易盈亏分析服务类

    提供以下核心功能：
    1. 年度总利润计算：统计本年度所有已完成卖出订单的净利润
    2. 胜率计算：盈利交易占总交易的比例（盈亏为0不计入）
    3. 最大盈利/亏损统计：找出盈利最多和亏损最多的交易
    4. 平均盈利/亏损计算：计算盈利和亏损的平均值
    5. 成本数据缺失处理：跳过成本缺失的交易
    6. 退货/退款处理：从本年统计中扣减退货金额
    """

    @classmethod
    def get_profit_analysis(cls, db: Session, user_id: int, current_year: int) -> Dict[str, Any]:
        """
        获取盈亏分析数据

        Args:
            db: 数据库会话
            user_id: 用户ID
            current_year: 当前年份

        Returns:
            Dict: 盈亏分析数据，包含年度利润、胜率、交易统计等
        """
        # 获取本年度的卖出记录（按created_at年份筛选）
        sold_orders = db.query(SoldOrder).filter(
            SoldOrder.user_id == user_id,
            SoldOrder.is_active == 1,
            SoldOrder.status == "已完成",
            extract('year', SoldOrder.created_at) == current_year
        ).all()

        # 获取本年度的退货/退款记录（transaction_type = 'REFUND'）
        refund_records = db.query(OrderTransaction).filter(
            OrderTransaction.user_id == user_id,
            OrderTransaction.is_active == True,
            OrderTransaction.transaction_type == "REFUND",
            extract('year', OrderTransaction.transaction_date) == current_year
        ).all()

        # 计算年度总利润（卖出 - 退货）
        yearly_profit = sum(
            cls._calculate_net_profit(so) for so in sold_orders
        )
        # 扣减退货金额
        refund_total = sum(r.total_amount or 0 for r in refund_records)
        yearly_profit -= refund_total

        # 统计交易数据
        stats = cls._calculate_trade_stats(db, sold_orders, refund_records)

        return {
            "yearly_profit": round(yearly_profit, 2),
            "win_rate": stats["win_rate"],
            "win_count": stats["win_count"],
            "loss_count": stats["loss_count"],
            "avg_profit": stats["avg_profit"],
            "avg_loss": stats["avg_loss"],
            "max_profit": stats["max_profit"],
            "max_profit_item": stats["max_profit_item"],
            "max_loss": stats["max_loss"],
            "max_loss_item": stats["max_loss_item"]
        }

    @staticmethod
    def _calculate_net_profit(sold_order: SoldOrder) -> float:
        """
        计算单笔交易的净利润

        Args:
            sold_order: 卖出订单对象

        Returns:
            float: 净利润，成本数据缺失时返回None
        """
        # 成本数据缺失检查
        if sold_order.cost_price is None or sold_order.cost_price <= 0:
            return None

        if sold_order.net_profit is not None:
            return sold_order.net_profit

        return (
            sold_order.sell_price
            - sold_order.cost_price
            - abs(sold_order.shipping_fee or 0)
            - abs(sold_order.platform_fee or 0)
        )

    @classmethod
    def _calculate_trade_stats(cls, db: Session, sold_orders: list, refund_records: list = None) -> Dict[str, Any]:
        """
        计算交易统计数据

        Args:
            db: 数据库会话
            sold_orders: 卖出订单列表
            refund_records: 退货/退款记录列表

        Returns:
            Dict: 交易统计数据
        """
        win_count = 0
        loss_count = 0
        total_win = 0.0
        total_loss = 0.0
        max_profit = 0.0
        max_loss = 0.0
        max_profit_item = ""
        max_loss_item = ""
        skipped_count = 0  # 成本缺失跳过的笔数

        for so in sold_orders:
            profit = cls._calculate_net_profit(so)

            # 成本数据缺失，跳过该笔统计
            if profit is None:
                skipped_count += 1
                continue

            figure_name = ""
            if so.figure_id:
                figure = db.query(Figure).filter(Figure.id == so.figure_id).first()
                if figure:
                    figure_name = figure.name

            # 盈亏为0不计入胜率统计（平局）
            if profit > 0:
                win_count += 1
                total_win += profit
                if profit > max_profit:
                    max_profit = profit
                    max_profit_item = figure_name
            elif profit < 0:
                loss_count += 1
                total_loss += abs(profit)
                if abs(profit) > max_loss:
                    max_loss = abs(profit)
                    max_loss_item = figure_name
            # profit == 0 时不计入任何统计

        # 处理退货/退款记录（计入亏损）
        if refund_records:
            for refund in refund_records:
                loss_count += 1
                refund_amount = refund.total_amount or 0
                total_loss += refund_amount
                if refund_amount > max_loss:
                    max_loss = refund_amount
                    max_loss_item = "退货/退款"

        total_trades = win_count + loss_count
        win_rate = round((win_count / total_trades) * 100, 1) if total_trades > 0 else 0

        return {
            "win_rate": win_rate,
            "win_count": win_count,
            "loss_count": loss_count,
            "avg_profit": round(total_win / win_count, 2) if win_count > 0 else 0,
            "avg_loss": round(total_loss / loss_count, 2) if loss_count > 0 else 0,
            "max_profit": round(max_profit, 2),
            "max_profit_item": max_profit_item,
            "max_loss": round(max_loss, 2),
            "max_loss_item": max_loss_item
        }
