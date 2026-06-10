"""
收益曲线服务
提供收益曲线数据计算，采用浮动盈亏计算方式
采用企业级服务层架构
"""
from typing import Dict, Any, List
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, timedelta

from app.models.asset import AssetValueCache, AssetTransaction
from app.models.holding_snapshot import HoldingSnapshotSummary
from app.models.order import Order
from app.models.figure import Figure


class ProfitCurveService:
    """
    收益曲线服务类

    提供以下核心功能：
    1. 计算每日收益：采用浮动盈亏计算方式
       浮动盈亏 = Σ[(手办当前市场价 − 加权平均成本价) × 剩余库存数量]
    2. 生成近1月收益曲线数据（基于实际持仓快照数据）
    3. 处理边界情况（空仓、全新用户等）
    """

    @staticmethod
    def calculate_daily_profit(
        db: Session,
        user_id: int,
        cache_date: datetime.date
    ) -> float:
        """
        计算指定日期的每日收益（浮动盈亏）

        计算公式：
        浮动盈亏 = Σ[(手办当前市场价 − 加权平均成本价) × 剩余库存数量]

        计算逻辑：
        1. 查询截至该日期所有有效的买入交易（AssetTransaction）
        2. 按手办ID分组计算加权平均成本
        3. 获取手办当前市场价
        4. 计算：(市场价 - 成本价) × 剩余库存

        Args:
            db: 数据库会话
            user_id: 用户ID
            cache_date: 计算日期

        Returns:
            float: 当日收益金额（正数表示盈利，负数表示亏损）
        """
        # 查询截至该日期所有有效的买入交易记录
        # 使用交易日期判断，而不是订单创建日期
        buy_transactions = db.query(
            AssetTransaction.figure_id,
            AssetTransaction.remaining_quantity,
            AssetTransaction.price
        ).filter(
            AssetTransaction.user_id == user_id,
            AssetTransaction.transaction_type == "buy",
            AssetTransaction.remaining_quantity > 0,
            AssetTransaction.is_active == True,
            func.date(AssetTransaction.transaction_date) <= cache_date
        ).all()

        if not buy_transactions:
            return 0.0

        # 按手办ID分组计算
        figure_data = {}
        for tx in buy_transactions:
            fig_id = tx.figure_id
            if fig_id not in figure_data:
                figure_data[fig_id] = {
                    "total_remaining_cost": 0.0,
                    "total_remaining": 0
                }
            figure_data[fig_id]["total_remaining_cost"] += (tx.price or 0) * (tx.remaining_quantity or 0)
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
    def get_profit_curve_data(
        db: Session,
        user_id: int,
        days: int = 30
    ) -> List[Dict[str, Any]]:
        """
        获取收益曲线数据（近N天）
        仅基于实际持仓快照数据，没有快照数据时不生成完整日期序列

        Args:
            db: 数据库会话
            user_id: 用户ID
            days: 查询天数，默认30天

        Returns:
            List[Dict]: 收益曲线数据列表，每个元素包含date和profit
        """
        end_date = datetime.now().date()
        start_date = end_date - timedelta(days=days)

        # 从持仓快照汇总表获取数据（排除今日，因为今日需要动态计算）
        snapshot_records = db.query(HoldingSnapshotSummary).filter(
            HoldingSnapshotSummary.user_id == user_id,
            HoldingSnapshotSummary.snapshot_date >= start_date,
            HoldingSnapshotSummary.snapshot_date < end_date  # 不包含今日
        ).order_by(HoldingSnapshotSummary.snapshot_date.asc()).all()

        result = []

        # 添加历史快照数据
        if snapshot_records:
            result = [
                {
                    "date": s.snapshot_date.isoformat(),
                    "profit": float(s.total_floating_pnl)
                }
                for s in snapshot_records
            ]

        # 动态计算今日收益（无论是否有历史数据，都添加今日数据）
        today_profit = ProfitCurveService.calculate_daily_profit(db, user_id, end_date)
        result.append({
            "date": end_date.isoformat(),
            "profit": today_profit
        })

        return result

    @staticmethod
    def get_latest_profit(
        db: Session,
        user_id: int
    ) -> Dict[str, Any]:
        """
        获取最新收益数据

        Args:
            db: 数据库会话
            user_id: 用户ID

        Returns:
            Dict: 包含最新收益、总市值、总成本的信息
        """
        today = datetime.now().date()

        # 首先尝试从持仓快照汇总表获取今日数据
        snapshot = db.query(HoldingSnapshotSummary).filter(
            HoldingSnapshotSummary.user_id == user_id,
            HoldingSnapshotSummary.snapshot_date == today
        ).first()

        if snapshot:
            return {
                "profit": float(snapshot.total_floating_pnl),
                "market_value": float(snapshot.total_market_value),
                "has_data": True,
                "date": snapshot.snapshot_date.isoformat()
            }

        # 如果没有今日快照，获取最新市值记录
        latest_record = db.query(AssetValueCache).filter(
            AssetValueCache.user_id == user_id
        ).order_by(AssetValueCache.cache_date.desc()).first()

        if not latest_record:
            return {
                "profit": 0,
                "market_value": 0,
                "has_data": False
            }

        # 计算当日收益
        daily_profit = ProfitCurveService.calculate_daily_profit(
            db, user_id, latest_record.cache_date
        )

        return {
            "profit": daily_profit,
            "market_value": latest_record.total_value or 0,
            "has_data": True,
            "date": latest_record.cache_date.isoformat()
        }
