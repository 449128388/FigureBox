"""
资产计算服务
提供资产相关的计算逻辑，包括总资产、日涨跌、塑料指数、仓位等
"""
from datetime import date, datetime, timedelta
from typing import Dict, Any, List, Optional, Tuple
from sqlalchemy.orm import Session

from app.models.asset import AssetValueCache, UserSettings
from app.models.figure import Figure
from app.models.user import User


class AssetCalculationService:
    """资产计算服务类"""
    
    # 基准日指数
    BASE_INDEX = 1000
    # 基准日上证指数
    BASE_SH_INDEX = 2900
    
    @staticmethod
    def calculate_total_assets(figures: List[Figure]) -> float:
        """
        计算总资产
        总资产 = Σ(市场价 × 数量)
        """
        return sum(
            (fig.market_price or fig.price or 0) * (fig.quantity or 1) 
            for fig in figures
        )
    
    @staticmethod
    def calculate_total_cost(figures: List[Figure]) -> float:
        """
        计算总成本
        总成本 = Σ(平均入手价 × 数量)
        """
        return sum(
            (fig.average_purchase_price or 0) * (fig.quantity or 1)
            for fig in figures
        )
    
    @classmethod
    def calculate_daily_change(
        cls,
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
    
    @classmethod
    def save_daily_cache(
        cls,
        db: Session,
        user_id: int,
        total_assets: float
    ) -> None:
        """
        保存今日市值缓存（用于明日计算日涨跌）
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
    
    @classmethod
    def calculate_plastic_index(
        cls,
        figures: List[Figure],
        total_assets: float
    ) -> Tuple[float, date]:
        """
        计算塑料指数（市值加权复权指数）
        
        公式：塑料指数 = 基准日指数 × (当前总市值 / 基准日总市值)
        基准日指数 = 1000
        基准日 = 最早购买手办的日期（开户首日）
        
        关键原则：
        1. 新买入手办不改变指数，只增加成分股
        2. 卖出手办不影响指数，视为成分股剔除
        3. 再版冲击（复刻）通过市场价变化自然反映在指数中
        
        Returns:
            Tuple[float, date]: (塑料指数, 基准日)
        """
        # 找到最早的购买日期作为基准日（开户首日）
        purchase_dates = [
            fig.purchase_date for fig in figures if fig.purchase_date
        ]
        
        if not purchase_dates:
            # 没有手办时，返回基准指数1000和当前日期
            return cls.BASE_INDEX, date.today()
        
        base_date = min(purchase_dates)
        
        # 基准日总市值 = 基准日当天所有持仓手办的平均入手价格总和
        # 这是用户的初始投入成本
        base_total_value = sum(
            (fig.average_purchase_price or 0) * (fig.quantity or 1)
            for fig in figures
        )
        
        # 如果没有成本数据，使用当前总资产作为基准（避免除以0）
        if base_total_value <= 0:
            base_total_value = total_assets if total_assets > 0 else cls.BASE_INDEX
        
        # 计算塑料指数
        # 公式：塑料指数 = 基准日指数 × (当前总市值 / 基准日总市值)
        plastic_index = round(
            cls.BASE_INDEX * (total_assets / base_total_value), 2
        )
        
        return plastic_index, base_date
    
    @classmethod
    def calculate_outperform_percentage(
        cls,
        plastic_index: float,
        sh_index: float
    ) -> float:
        """
        计算跑赢大盘百分比（成立至今）
        
        塑料指数涨幅 = (当前塑料指数 - 基准日指数) / 基准日指数 × 100%
        上证指数涨幅 = (当前上证指数 - 基准日上证指数) / 基准日上证指数 × 100%
        跑赢大盘 = 塑料指数涨幅 - 上证指数涨幅
        """
        plastic_change_percentage = (
            (plastic_index - cls.BASE_INDEX) / cls.BASE_INDEX
        ) * 100
        sh_change_percentage_total = (
            (sh_index - cls.BASE_SH_INDEX) / cls.BASE_SH_INDEX
        ) * 100
        outperform_percentage = round(
            plastic_change_percentage - sh_change_percentage_total, 2
        )
        
        return outperform_percentage
    
    @staticmethod
    def get_investment_budget(db: Session, user_id: int) -> float:
        """
        获取用户设置的投资预算上限
        """
        user_settings = db.query(UserSettings).filter(
            UserSettings.user_id == user_id
        ).first()
        return user_settings.annual_spending_limit if user_settings else 0
    
    @staticmethod
    def calculate_invested_cost(figures: List[Figure]) -> float:
        """
        计算已投入成本（所有持仓手办的平均买入成本价总和）
        """
        return sum(
            (fig.average_purchase_price or 0) * (fig.quantity or 1)
            for fig in figures
        )
    
    @classmethod
    def calculate_position(
        cls,
        db: Session,
        user_id: int,
        figures: List[Figure]
    ) -> Dict[str, Any]:
        """
        计算仓位信息
        
        仓位 = 已投入成本 / 投资预算上限 × 100%
        
        仓位状态分级表：
        - 空仓: 0% - 灰色
        - 轻仓: 1% - 30% - 蓝色
        - 半仓: 30% - 70% - 绿色
        - 重仓: 70% - 90% - 黄色
        - 满仓: 90% - 100% - 红色
        - 超仓: >100% - 黑色
        
        Returns:
            Dict包含: position(仓位状态), position_percentage(仓位百分比), 
                     position_color(仓位颜色), investment_budget(投资预算), 
                     invested_cost(已投入成本)
        """
        investment_budget = cls.get_investment_budget(db, user_id)
        invested_cost = cls.calculate_invested_cost(figures)
        
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
    
    @staticmethod
    def determine_status(profit_percentage: float) -> str:
        """
        根据涨幅百分比确定状态标签
        
        🚀 暴涨: 单月涨幅 ≥ +15% (绿色)
        📈 上涨: 涨幅 +5% ~ +15% (浅绿)
        ➖ 横盘: 波动 -5% ~ +5% (灰色)
        📉 告警: 跌幅 -10% ~ -20% (黄色)
        🔴 破位: 跌幅 ≥ -20% 或 破发 (红色)
        💀 退市: 跌幅 ≥ -50% 或 绝版无市 (黑色)
        """
        if profit_percentage >= 15:
            return "🚀 暴涨"
        elif profit_percentage >= 5:
            return "📈 上涨"
        elif profit_percentage >= -5:
            return "➖ 横盘"
        elif profit_percentage >= -20:
            return "📉 告警"
        elif profit_percentage >= -50:
            return "🔴 破位"
        else:
            return "💀 退市"
    
    @staticmethod
    def calculate_holding_days(purchase_date: date) -> int:
        """
        计算持有天数
        """
        import pytz
        tz = pytz.timezone('Asia/Shanghai')
        current_time = datetime.now(tz)
        
        if isinstance(purchase_date, date):
            purchase_datetime = datetime(
                purchase_date.year, purchase_date.month, purchase_date.day
            )
            purchase_time = tz.localize(purchase_datetime)
        else:
            purchase_time = tz.localize(purchase_date)
        
        return (current_time - purchase_time).days
    
    @staticmethod
    def get_figure_image_url(figure: Figure) -> str:
        """
        获取手办图片URL
        """
        if figure.images and len(figure.images) > 0:
            return figure.images[0]
        return "/imgs/no_image.png"
