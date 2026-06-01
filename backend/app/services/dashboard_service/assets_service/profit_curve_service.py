"""
收益曲线服务
提供收益曲线数据计算，采用每日收益 = 当日总市值 - 当日总成本的计算方式
采用企业级服务层架构
"""
from typing import Dict, Any, List
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, timedelta

from app.models.asset import AssetValueCache, AssetTransaction
from app.models.order import Order
from app.models.figure import Figure


class ProfitCurveService:
    """
    收益曲线服务类

    提供以下核心功能：
    1. 计算每日收益：当日总市值 - 当日总成本
    2. 生成近1月收益曲线数据
    3. 处理边界情况（空仓、全新用户等）
    """

    @staticmethod
    def calculate_daily_profit(
        db: Session,
        user_id: int,
        cache_date: datetime.date
    ) -> float:
        """
        计算指定日期的每日收益

        计算公式：
        每日收益 = 当日总市值 - 当日总成本

        当日总成本计算逻辑：
        1. 查询截至该日期所有有效的买入交易
        2. 计算累计投入成本（买入单价 × 数量）
        3. 减去已卖出部分的成本

        Args:
            db: 数据库会话
            user_id: 用户ID
            cache_date: 计算日期

        Returns:
            float: 当日收益金额（正数表示盈利，负数表示亏损）
        """
        # 获取当日总市值
        market_value_record = db.query(AssetValueCache).filter(
            AssetValueCache.user_id == user_id,
            AssetValueCache.cache_date == cache_date
        ).first()

        if not market_value_record:
            return 0.0

        total_market_value = market_value_record.total_value or 0

        # 计算截至该日期的总成本
        # 查询截至该日期所有有效的买入订单
        buy_orders = db.query(Order).filter(
            Order.user_id == user_id,
            Order.status.in_(["已完成", "已支付"]),
            Order.is_active == True,
            func.date(Order.created_at) <= cache_date
        ).all()

        total_cost = 0.0
        for order in buy_orders:
            # 计算订单实际支付金额
            deposit = order.deposit or 0
            balance = order.balance or 0
            total_cost += deposit + balance

        # 每日收益 = 总市值 - 总成本
        daily_profit = total_market_value - total_cost

        return round(daily_profit, 2)

    @staticmethod
    def get_profit_curve_data(
        db: Session,
        user_id: int,
        days: int = 30
    ) -> List[Dict[str, Any]]:
        """
        获取收益曲线数据（近N天）

        Args:
            db: 数据库会话
            user_id: 用户ID
            days: 查询天数，默认30天

        Returns:
            List[Dict]: 收益曲线数据列表，每个元素包含date和profit
        """
        # 查询近N天的市值缓存数据
        end_date = datetime.now().date()
        start_date = end_date - timedelta(days=days)

        cache_records = db.query(AssetValueCache).filter(
            AssetValueCache.user_id == user_id,
            AssetValueCache.cache_date >= start_date,
            AssetValueCache.cache_date <= end_date
        ).order_by(AssetValueCache.cache_date.asc()).all()

        if not cache_records:
            # 全新用户/无数据：返回空列表，前端显示y=0直线
            return []

        # 计算每天的收益
        profit_data = []
        for record in cache_records:
            daily_profit = ProfitCurveService.calculate_daily_profit(
                db, user_id, record.cache_date
            )
            profit_data.append({
                "date": record.cache_date.isoformat(),
                "profit": daily_profit
            })

        return profit_data

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
        # 获取最新市值记录
        latest_record = db.query(AssetValueCache).filter(
            AssetValueCache.user_id == user_id
        ).order_by(AssetValueCache.cache_date.desc()).first()

        if not latest_record:
            return {
                "profit": 0,
                "market_value": 0,
                "total_cost": 0,
                "has_data": False
            }

        # 计算当日收益
        daily_profit = ProfitCurveService.calculate_daily_profit(
            db, user_id, latest_record.cache_date
        )

        # 计算总成本
        buy_orders = db.query(Order).filter(
            Order.user_id == user_id,
            Order.status.in_(["已完成", "已支付"]),
            Order.is_active == True
        ).all()

        total_cost = sum((order.deposit or 0) + (order.balance or 0) for order in buy_orders)

        return {
            "profit": daily_profit,
            "market_value": latest_record.total_value or 0,
            "total_cost": total_cost,
            "has_data": True,
            "date": latest_record.cache_date.isoformat()
        }
