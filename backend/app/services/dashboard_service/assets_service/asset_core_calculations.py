"""
资产核心计算服务
提供资产相关的核心计算逻辑，包括总资产、日涨跌、仓位等
采用企业级服务层架构，与 AssetCalculationService 分离
"""
from datetime import date, timedelta
from typing import Dict, Any, List, Tuple
from sqlalchemy.orm import Session

from app.models.asset import AssetValueCache, UserSettings
from app.models.figure import Figure
from app.models.order import Order


# 汇率配置：相对人民币的汇率
EXCHANGE_RATES = {
    'CNY': 1.0,    # 人民币
    'JPY': 1/23,   # 日元：1人民币 = 23日元
    'USD': 7.0,    # 美元：1美元 = 7人民币
    'EUR': 8.0     # 欧元：1欧元 = 8人民币
}


class TotalAssetsCalculator:
    """总资产计算服务"""
    
    @staticmethod
    def calculate_by_orders(orders: List[Order]) -> float:
        """
        计算总资产（基于已完成订单）
        
        统计规则：
        1. 统计尾款管理中状态为"已完成"的全部订单
        2. 计算手办市场总价 = 对应手办市场价（每个订单计为1个手办）
        
        计算公式：
        总资产 = Σ(手办市场价)  # 仅统计已完成订单
        
        Args:
            orders: 订单列表（仅包含已完成状态的订单）
            
        Returns:
            float: 总资产金额（人民币）
        """
        return sum(
            (order.figure.market_price or order.figure.price or 0)
            for order in orders
            if order.status == "已完成" and order.figure
        )
    
    @staticmethod
    def calculate(figures: List[Figure]) -> float:
        """
        计算总资产（向后兼容，基于手办列表）
        
        计算公式：
        总资产 = Σ(市场价 × 数量)
        
        Args:
            figures: 手办列表
            
        Returns:
            float: 总资产金额
        """
        return sum(
            (fig.market_price or fig.price or 0) * (fig.quantity or 1)
            for fig in figures
        )


class DailyChangeCalculator:
    """日涨跌计算服务"""
    
    @staticmethod
    def calculate(
        db: Session,
        user_id: int,
        total_assets: float
    ) -> Tuple[float, float, bool]:
        """
        计算日涨跌（与股票账户当日盈亏完全一致）
        
        计算逻辑：
        1. 日涨跌金额 = 今日总市值 - 昨日收盘总市值
        2. 日涨跌% = (今日总市值 - 昨日总市值) / 昨日总市值 × 100%
        3. 昨日市值取值：取昨日23:59的缓存市值作为基准
        4. 如果没有昨日市值缓存，今日不显示涨跌，明日开始正常计算
        
        Args:
            db: 数据库会话
            user_id: 用户ID
            total_assets: 今日总资产
            
        Returns:
            Tuple[float, float, bool]: (日涨跌金额, 日涨跌百分比, 是否有涨跌数据)
        """
        yesterday = date.today() - timedelta(days=1)
        yesterday_cache = db.query(AssetValueCache).filter(
            AssetValueCache.user_id == user_id,
            AssetValueCache.cache_date == yesterday
        ).first()

        if yesterday_cache:
            # 有昨日缓存，使用缓存值计算（与股票账户当日盈亏一致）
            yesterday_total_assets = yesterday_cache.total_value
            daily_change = total_assets - yesterday_total_assets
            daily_change_percentage = (
                (daily_change / yesterday_total_assets * 100)
                if yesterday_total_assets > 0 else 0
            )
            has_daily_change = True
        else:
            # 没有昨日缓存，今日不显示涨跌（与股票账户逻辑一致）
            daily_change = 0
            daily_change_percentage = 0
            has_daily_change = False

        return daily_change, daily_change_percentage, has_daily_change


class PositionCalculator:
    """仓位计算服务"""

    @staticmethod
    def _get_investment_budget(db: Session, user_id: int) -> float:
        """
        获取用户设置的投资预算上限

        Args:
            db: 数据库会话
            user_id: 用户ID

        Returns:
            float: 投资预算上限
        """
        user_settings = db.query(UserSettings).filter(
            UserSettings.user_id == user_id
        ).first()
        return user_settings.annual_spending_limit if user_settings else 0

    @staticmethod
    def _convert_to_rmb(amount: float, currency: str) -> float:
        """
        将指定币种金额转换为人民币

        Args:
            amount: 金额
            currency: 币种代码 (CNY/JPY/USD/EUR)

        Returns:
            float: 人民币金额
        """
        rate = EXCHANGE_RATES.get(currency, 1.0)
        return amount * rate

    @staticmethod
    def _calculate_invested_cost_by_orders(orders: List[Order]) -> float:
        """
        计算已投入成本（基于订单的定金+尾款，转换为人民币）

        统计规则：
        1. 统计尾款管理中所有订单的尾款+定金的总和
        2. 需要考虑定金和尾款的币种，最后以人民币进行结算

        计算公式：
        已投入成本 = Σ(定金 × 汇率 + 尾款 × 汇率)

        Args:
            orders: 订单列表

        Returns:
            float: 已投入成本（人民币）
        """
        total_cost = 0.0
        for order in orders:
            # 转换定金为人民币
            deposit_rmb = PositionCalculator._convert_to_rmb(
                order.deposit or 0,
                order.deposit_currency or 'CNY'
            )
            # 转换尾款为人民币
            balance_rmb = PositionCalculator._convert_to_rmb(
                order.balance or 0,
                order.balance_currency or 'CNY'
            )
            total_cost += deposit_rmb + balance_rmb
        return total_cost

    @staticmethod
    def _calculate_invested_cost(figures: List[Figure]) -> float:
        """
        计算已投入成本（所有持仓手办的平均买入成本价总和）
        向后兼容，基于手办列表的计算方式

        Args:
            figures: 手办列表

        Returns:
            float: 已投入成本
        """
        return sum(
            (fig.average_purchase_price or 0) * (fig.quantity or 1)
            for fig in figures
        )

    @classmethod
    def calculate_by_orders(
        cls,
        db: Session,
        user_id: int,
        orders: List[Order]
    ) -> Dict[str, Any]:
        """
        计算仓位信息（基于订单数据）

        计算公式：
        仓位 = 已投入成本 / 投资预算上限 × 100%

        已投入成本计算：
        - 基于所有订单的定金+尾款总和（已转换为人民币）

        仓位状态分级表：
        - 空仓: 0% - 灰色
        - 轻仓: 1% - 30% - 蓝色
        - 半仓: 30% - 70% - 绿色
        - 重仓: 70% - 90% - 黄色
        - 满仓: 90% - 100% - 红色
        - 超仓: >100% - 黑色

        Args:
            db: 数据库会话
            user_id: 用户ID
            orders: 订单列表

        Returns:
            Dict包含: position(仓位状态), position_percentage(仓位百分比),
                     position_color(仓位颜色), investment_budget(投资预算),
                     invested_cost(已投入成本)
        """
        investment_budget = cls._get_investment_budget(db, user_id)
        invested_cost = cls._calculate_invested_cost_by_orders(orders)

        # 计算仓位百分比
        if investment_budget > 0:
            position_percentage = (invested_cost / investment_budget) * 100
        else:
            position_percentage = 100 if invested_cost > 0 else 0

        # 根据仓位百分比确定仓位状态和颜色
        if position_percentage == 0:
            position = "空仓"
            position_color = "gray"
        elif position_percentage <= 30:
            position = "轻仓"
            position_color = "blue"
        elif position_percentage <= 70:
            position = "半仓"
            position_color = "green"
        elif position_percentage <= 90:
            position = "重仓"
            position_color = "yellow"
        elif position_percentage <= 100:
            position = "满仓"
            position_color = "red"
        else:
            position = "超仓"
            position_color = "black"

        return {
            "position": position,
            "position_percentage": round(position_percentage, 2),
            "position_color": position_color,
            "investment_budget": investment_budget,
            "invested_cost": round(invested_cost, 2)
        }

    @classmethod
    def calculate(
        cls,
        db: Session,
        user_id: int,
        figures: List[Figure]
    ) -> Dict[str, Any]:
        """
        计算仓位信息（向后兼容，基于手办列表）

        计算公式：
        仓位 = 已投入成本 / 投资预算上限 × 100%

        仓位状态分级表：
        - 空仓: 0% - 灰色
        - 轻仓: 1% - 30% - 蓝色
        - 半仓: 30% - 70% - 绿色
        - 重仓: 70% - 90% - 黄色
        - 满仓: 90% - 100% - 红色
        - 超仓: >100% - 黑色

        Args:
            db: 数据库会话
            user_id: 用户ID
            figures: 手办列表

        Returns:
            Dict包含: position(仓位状态), position_percentage(仓位百分比),
                     position_color(仓位颜色), investment_budget(投资预算),
                     invested_cost(已投入成本)
        """
        investment_budget = cls._get_investment_budget(db, user_id)
        invested_cost = cls._calculate_invested_cost(figures)

        # 计算仓位百分比
        if investment_budget > 0:
            position_percentage = (invested_cost / investment_budget) * 100
        else:
            position_percentage = 100 if invested_cost > 0 else 0

        # 根据仓位百分比确定仓位状态和颜色
        if position_percentage == 0:
            position = "空仓"
            position_color = "gray"
        elif position_percentage <= 30:
            position = "轻仓"
            position_color = "blue"
        elif position_percentage <= 70:
            position = "半仓"
            position_color = "green"
        elif position_percentage <= 90:
            position = "重仓"
            position_color = "yellow"
        elif position_percentage <= 100:
            position = "满仓"
            position_color = "red"
        else:
            position = "超仓"
            position_color = "black"

        return {
            "position": position,
            "position_percentage": round(position_percentage, 2),
            "position_color": position_color,
            "investment_budget": investment_budget,
            "invested_cost": invested_cost
        }


class DailyCacheService:
    """每日市值缓存服务"""

    @staticmethod
    def save(
        db: Session,
        user_id: int,
        total_assets: float
    ) -> None:
        """
        保存今日市值缓存（用于明日计算日涨跌）

        工作原理：
        1. 查询今日是否已有缓存记录
        2. 如果有则更新，没有则创建新记录
        3. 提交数据库事务

        Args:
            db: 数据库会话
            user_id: 用户ID
            total_assets: 今日总资产
        """
        today = date.today()
        today_cache = db.query(AssetValueCache).filter(
            AssetValueCache.user_id == user_id,
            AssetValueCache.cache_date == today
        ).first()

        if today_cache:
            # 更新今日缓存
            today_cache.total_value = total_assets
        else:
            # 创建今日缓存
            today_cache = AssetValueCache(
                user_id=user_id,
                total_value=total_assets,
                cache_date=today
            )
            db.add(today_cache)

        db.commit()
