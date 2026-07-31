"""
盈亏分析服务
提供盈亏相关的核心计算逻辑，包括浮动盈亏、实现盈亏、总收益率等
采用企业级服务层架构
"""
from typing import Dict, Any, List, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.models.figure import Figure
from app.models.order import Order
from app.models.sold_order import SoldOrder
from app.models.asset import AssetTransaction
from app.services.exchange_rate_service import ExchangeRateService


class ProfitAnalysisService:
    """
    盈亏分析服务类

    提供以下核心功能：
    1. 浮动盈亏计算：当前持仓手办按市场价全部卖出的理论收益
    2. 实现盈亏计算：已出售订单的累计净利润
    3. 总收益率计算：整体资金回报率
    4. 总投入成本计算：用于收益率分母
    """

    @staticmethod
    def calculate_floating_profit(
        db: Session,
        user_id: int
    ) -> float:
        """
        计算浮动盈亏

        含义：当前还在手里的手办，如果今天按市场价全部卖掉，理论上能赚多少钱。

        计算公式：
        浮动盈亏 = Σ[(手办当前市场价 − 加权平均成本价) × 剩余库存数量]

        计算逻辑：
        1. 查询所有有库存的手办（remaining_quantity > 0）
        2. 对每个手办计算：(市场价 - 加权平均成本) × 剩余库存
        3. 汇总所有手办的盈亏

        Args:
            db: 数据库会话
            user_id: 用户ID

        Returns:
            float: 浮动盈亏金额（正数表示盈利，负数表示亏损）
        """
        # 1. 聚合同 order 下所有 adjust 调整额（带符号：减少为负、追加为正）
        adjust_map = {}
        adjust_rows = db.query(
            AssetTransaction.order_id,
            AssetTransaction.price
        ).filter(
            AssetTransaction.user_id == user_id,
            AssetTransaction.transaction_type == "adjust",
            AssetTransaction.is_active == True
        ).all()
        for order_id, adj_price in adjust_rows:
            adjust_map[order_id] = adjust_map.get(order_id, 0.0) + (adj_price or 0.0)

        # 2. 查询所有有剩余库存的买入记录
        buy_transactions = db.query(
            AssetTransaction.figure_id,
            AssetTransaction.order_id,
            AssetTransaction.remaining_quantity,
            AssetTransaction.price
        ).filter(
            AssetTransaction.user_id == user_id,
            AssetTransaction.transaction_type == "buy",
            AssetTransaction.remaining_quantity > 0,
            AssetTransaction.is_active == True
        ).all()

        if not buy_transactions:
            return 0.0

        # 按手办ID分组计算（每行 buy 成本 = buy.price + Σadjust）
        figure_data = {}
        for tx in buy_transactions:
            fig_id = tx.figure_id
            if fig_id not in figure_data:
                figure_data[fig_id] = {
                    "total_remaining_cost": 0.0,
                    "total_remaining": 0
                }
            final_price = (tx.price or 0) + adjust_map.get(tx.order_id, 0.0)
            figure_data[fig_id]["total_remaining_cost"] += final_price * (tx.remaining_quantity or 0)
            figure_data[fig_id]["total_remaining"] += tx.remaining_quantity or 0

        # 获取手办当前市场价
        figure_ids = list(figure_data.keys())
        figures = db.query(Figure).filter(Figure.id.in_(figure_ids)).all()
        figure_prices = {fig.id: fig.market_price or fig.price or 0 for fig in figures}

        # 计算浮动盈亏
        floating_profit = 0.0
        for fig_id, data in figure_data.items():
            remaining_quantity = data["total_remaining"]
            remaining_cost = data["total_remaining_cost"]
            current_price = figure_prices.get(fig_id, 0)

            if remaining_quantity > 0:
                # 加权平均成本价
                avg_cost_price = remaining_cost / remaining_quantity
                # (市场价 - 成本价) × 数量
                floating_profit += (current_price - avg_cost_price) * remaining_quantity

        return round(floating_profit, 2)

    @staticmethod
    def calculate_realized_profit(
        db: Session,
        user_id: int
    ) -> float:
        """
        计算实现盈亏

        含义：已经卖出去的手办，扣除成本、运费、手续费后，真正到手的净利润。

        计算公式：
        实现盈亏 = 已出售订单中累计净利润

        数据来源：
        - SoldOrder.net_profit 字段（创建订单时已计算）

        Args:
            db: 数据库会话
            user_id: 用户ID

        Returns:
            float: 实现盈亏金额（正数表示盈利，负数表示亏损）
        """
        result = db.query(
            func.coalesce(func.sum(SoldOrder.net_profit), 0).label('total_net_profit')
        ).filter(
            SoldOrder.user_id == user_id,
            SoldOrder.is_active == True
        ).first()

        return round(result.total_net_profit or 0, 2)

    @staticmethod
    def calculate_total_invested_cost(
        db: Session,
        user_id: int
    ) -> float:
        """
        计算总投入成本

        含义：投资手办至今，总共投入的资金。

        计算公式：
        总投入成本 = Σ(已完成订单的定金 + 尾款)

        Args:
            db: 数据库会话
            user_id: 用户ID

        Returns:
            float: 总投入成本
        """
        # 查询已完成订单
        completed_orders = db.query(Order).filter(
            Order.user_id == user_id,
            Order.status == "已完成",
            Order.is_active == 1
        ).all()

        total_cost = 0.0
        for order in completed_orders:
            # 转换定金为人民币（使用统一汇率服务）
            deposit_rate = ExchangeRateService.get_rate(db, order.deposit_currency or 'CNY')
            deposit_rmb = (order.deposit or 0) * deposit_rate

            # 转换尾款为人民币（使用统一汇率服务）
            balance_rate = ExchangeRateService.get_rate(db, order.balance_currency or 'CNY')
            balance_rmb = (order.balance or 0) * balance_rate

            total_cost += deposit_rmb + balance_rmb

        return round(total_cost, 2)

    @classmethod
    def calculate_total_return_rate(
        cls,
        db: Session,
        user_id: int
    ) -> float:
        """
        计算总收益率

        含义：从投资手办至今，整体资金回报率是多少。

        计算公式：
        总收益率 = (浮动盈亏 + 实现盈亏) / 总投入成本 × 100%

        保留小数点后2位数。

        Args:
            db: 数据库会话
            user_id: 用户ID

        Returns:
            float: 总收益率百分比（如 24.56 表示 24.56%）
        """
        floating_profit = cls.calculate_floating_profit(db, user_id)
        realized_profit = cls.calculate_realized_profit(db, user_id)
        total_invested_cost = cls.calculate_total_invested_cost(db, user_id)

        if total_invested_cost <= 0:
            return 0.0

        total_return_rate = ((floating_profit + realized_profit) / total_invested_cost) * 100
        return round(total_return_rate, 2)

    @staticmethod
    def calculate_monthly_purchases(
        db: Session,
        user_id: int
    ) -> int:
        """
        计算本月入手数量

        统计规则：
        1. 统计本月创建的订单数量
        2. 只统计状态不为"已取消"的订单

        注意：由于 Order 模型目前没有 created_at 字段，暂时返回 0
        后续如需统计，需要：
        1. 在 Order 模型添加 created_at 字段，或
        2. 使用其他方式（如 due_date）进行估算

        Args:
            db: 数据库会话
            user_id: 用户ID

        Returns:
            int: 本月入手数量
        """
        # TODO: Order 模型缺少 created_at 字段，暂时返回 0
        # 如需实现，需要先在数据库迁移中添加 created_at 字段
        return 0

    @classmethod
    def calculate_annualized_return_rate(
        cls,
        db: Session,
        user_id: int
    ) -> float:
        """
        计算年化收益率

        公式：年化收益率 = [(1 + 总收益率)^(365/持仓天数) - 1] × 100%

        意义：消除"持有时间"差异。
        总收益率58%如果是3个月达成的，年化可能 > 200%；
        如果是3年达成的，年化只有 ~16%。

        Args:
            db: 数据库会话
            user_id: 用户ID

        Returns:
            float: 年化收益率百分比
        """
        total_return_rate = cls.calculate_total_return_rate(db, user_id)

        if total_return_rate <= 0:
            return 0.0

        # 获取用户最早入手手办的日期作为持仓起始日
        # 使用 MIN() 聚合函数直接取最早日期，避免 ORDER BY 排序导致 MySQL sort buffer 溢出
        figure_ids_subquery = db.query(Order.figure_id).filter(
            Order.user_id == user_id,
            Order.is_active == 1,
            Order.status != "已取消"
        ).subquery()

        earliest_date = db.query(func.min(Figure.purchase_date)).filter(
            Figure.id.in_(figure_ids_subquery),
            Figure.purchase_date.isnot(None)
        ).scalar()

        if not earliest_date:
            return 0.0

        # 计算持仓天数
        from datetime import datetime
        start_date = earliest_date
        end_date = datetime.now().date()
        holding_days = (end_date - start_date).days

        if holding_days <= 0:
            holding_days = 1  # 避免除以0

        # 年化收益率 = [(1 + 总收益率)^(365/持仓天数) - 1] × 100%
        total_rate_decimal = total_return_rate / 100
        annualized_rate = ((1 + total_rate_decimal) ** (365 / holding_days) - 1) * 100

        return round(annualized_rate, 2)

    @classmethod
    def calculate_realization_rate(
        cls,
        db: Session,
        user_id: int
    ) -> float:
        """
        计算变现率（落袋为安比例）

        公式：变现率 = 实现盈亏 / (实现盈亏 + 浮动盈亏) × 100%

        意义：衡量"纸面富贵"有多少已经真正变成钱。
        防止"看着赚很多，一卖就崩盘"的幻觉。

        Args:
            db: 数据库会话
            user_id: int

        Returns:
            float: 变现率百分比（0-100）
        """
        floating_profit = cls.calculate_floating_profit(db, user_id)
        realized_profit = cls.calculate_realized_profit(db, user_id)

        total_profit = realized_profit + floating_profit

        if total_profit == 0:
            return 0.0

        realization_rate = (realized_profit / total_profit) * 100
        return round(realization_rate, 2)

    @classmethod
    def calculate_max_drawdown(
        cls,
        db: Session,
        user_id: int
    ) -> float:
        """
        计算最大回撤

        公式：最大回撤 = (历史峰值总资产 - 当前总资产) / 历史峰值总资产 × 100%

        意义：衡量你曾经历过的"最惨时刻"。
        资产从最高点跌了多少，反映持仓风险。

        计算逻辑：
        1. 总资产 = 总投入成本 + 实现盈亏 + 浮动盈亏
        2. 历史峰值取当前总资产与总投入成本中的较大值
        3. 总投入成本是最保守的历史峰值估计

        Args:
            db: 数据库会话
            user_id: int

        Returns:
            float: 最大回撤百分比
        """
        # 计算当前总资产（用户定义：总投入成本 + 浮动盈亏 + 实现盈亏）
        total_invested = cls.calculate_total_invested_cost(db, user_id)
        floating_profit = cls.calculate_floating_profit(db, user_id)
        realized_profit = cls.calculate_realized_profit(db, user_id)
        current_total_assets = total_invested + floating_profit + realized_profit

        if current_total_assets <= 0:
            return 0.0

        # 历史峰值取当前总资产与总投入成本中的较大值
        # 总投入成本作为最保守的历史峰值估计
        # 当当前总资产高于总投入成本时，说明用户处于或接近历史高点
        historical_peak = max(current_total_assets, total_invested)

        if historical_peak <= 0:
            return 0.0

        # 计算回撤
        drawdown = (current_total_assets - historical_peak) / historical_peak * 100

        return round(drawdown, 2)

    @classmethod
    def get_profit_analysis(
        cls,
        db: Session,
        user_id: int
    ) -> Dict[str, Any]:
        """
        获取完整的盈亏分析数据

        返回包含：
        - floating: 浮动盈亏
        - realized: 实现盈亏
        - total_rate: 总收益率
        - total_invested_cost: 总投入成本（供参考）
        - annualized_rate: 年化收益率
        - realization_rate: 变现率
        - max_drawdown: 最大回撤

        Args:
            db: 数据库会话
            user_id: 用户ID

        Returns:
            Dict: 盈亏分析数据
        """
        floating_profit = cls.calculate_floating_profit(db, user_id)
        realized_profit = cls.calculate_realized_profit(db, user_id)
        total_return_rate = cls.calculate_total_return_rate(db, user_id)
        total_invested_cost = cls.calculate_total_invested_cost(db, user_id)
        annualized_rate = cls.calculate_annualized_return_rate(db, user_id)
        realization_rate = cls.calculate_realization_rate(db, user_id)
        max_drawdown = cls.calculate_max_drawdown(db, user_id)

        return {
            "floating": floating_profit,
            "realized": realized_profit,
            "total_rate": total_return_rate,
            "total_invested_cost": total_invested_cost,
            "annualized_rate": annualized_rate,
            "realization_rate": realization_rate,
            "max_drawdown": max_drawdown
        }
