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


class TotalAssetsCalculator:
    """总资产计算服务"""
    
    @staticmethod
    def calculate(figures: List[Figure]) -> float:
        """
        计算总资产
        
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
    def _calculate_invested_cost(figures: List[Figure]) -> float:
        """
        计算已投入成本（所有持仓手办的平均买入成本价总和）

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
    def calculate(
        cls,
        db: Session,
        user_id: int,
        figures: List[Figure]
    ) -> Dict[str, Any]:
        """
        计算仓位信息

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
