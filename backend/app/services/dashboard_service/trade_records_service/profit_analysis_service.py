"""
盈亏分析服务
提供盈亏分析相关的核心业务逻辑
采用企业级服务层架构
"""
from typing import Dict, Any
from sqlalchemy.orm import Session

from app.models.figure import Figure
from app.models.sold_order import SoldOrder


class TradeProfitAnalysisService:
    """
    交易盈亏分析服务类

    提供以下核心功能：
    1. 年度总利润计算：统计所有已完成卖出订单的净利润
    2. 胜率计算：盈利交易占总交易的比例
    3. 最大盈利/亏损统计：找出盈利最多和亏损最多的交易
    4. 平均盈利/亏损计算：计算盈利和亏损的平均值
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
        # 获取所有卖出记录
        sold_orders = db.query(SoldOrder).filter(
            SoldOrder.user_id == user_id,
            SoldOrder.is_active == 1,
            SoldOrder.status == "已完成"
        ).all()

        # 计算年度总利润
        yearly_profit = sum(
            cls._calculate_net_profit(so) for so in sold_orders
        )

        # 统计交易数据
        stats = cls._calculate_trade_stats(db, sold_orders)

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
            float: 净利润
        """
        if sold_order.net_profit is not None:
            return sold_order.net_profit

        return (
            sold_order.sell_price
            - sold_order.cost_price
            - abs(sold_order.shipping_fee or 0)
            - abs(sold_order.platform_fee or 0)
        )

    @classmethod
    def _calculate_trade_stats(cls, db: Session, sold_orders: list) -> Dict[str, Any]:
        """
        计算交易统计数据

        Args:
            db: 数据库会话
            sold_orders: 卖出订单列表

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

        for so in sold_orders:
            profit = cls._calculate_net_profit(so)

            figure_name = ""
            if so.figure_id:
                figure = db.query(Figure).filter(Figure.id == so.figure_id).first()
                if figure:
                    figure_name = figure.name

            if profit > 0:
                win_count += 1
                total_win += profit
                if profit > max_profit:
                    max_profit = profit
                    max_profit_item = figure_name
            else:
                loss_count += 1
                total_loss += abs(profit)
                if abs(profit) > max_loss:
                    max_loss = abs(profit)
                    max_loss_item = figure_name

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
