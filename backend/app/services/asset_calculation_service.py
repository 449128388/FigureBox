"""
资产计算服务
提供资产相关的计算逻辑，包括总资产、日涨跌、塑料指数、仓位等
采用企业级服务层架构，核心计算逻辑拆分到 dashboard_service/assets_service
"""
from datetime import date, datetime, timedelta
from typing import Dict, Any, List, Optional, Tuple
from sqlalchemy.orm import Session

from app.models.asset import AssetValueCache, UserSettings
from app.models.figure import Figure
from app.models.user import User

# 引入企业级核心计算服务
from app.services.dashboard_service.assets_service.asset_core_calculations import (
    TotalAssetsCalculator,
    DailyChangeCalculator,
    PositionCalculator,
    DailyCacheService
)

from app.services.dashboard_service.assets_service.asset_market_benchmark_service import (
    MarketBenchmarkService
)


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
        委托给 TotalAssetsCalculator 处理，保持向后兼容
        """
        return TotalAssetsCalculator.calculate(figures)
    
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
        委托给 DailyChangeCalculator 处理，保持向后兼容
        """
        return DailyChangeCalculator.calculate(db, user_id, total_assets)
    
    @classmethod
    def save_daily_cache(
        cls,
        db: Session,
        user_id: int,
        total_assets: float
    ) -> None:
        """
        保存今日市值缓存（用于明日计算日涨跌）
        
        委托给 DailyCacheService 处理，保持向后兼容
        """
        return DailyCacheService.save(db, user_id, total_assets)
    
    @classmethod
    def calculate_plastic_index(
        cls,
        figures: List[Figure],
        total_assets: float
    ) -> Tuple[float, date]:
        """
        计算塑料指数（市值加权复权指数） 
        
        委托给 MarketBenchmarkService 处理，保持向后兼容
        """
        return MarketBenchmarkService.calculate_plastic_index(figures, total_assets)
    
    @classmethod
    def calculate_outperform_percentage(
        cls,
        plastic_index: float,
        sh_index: float
    ) -> float:
        """
        计算跑赢大盘百分比（成立至今）
        
        委托给 MarketBenchmarkService 处理，保持向后兼容
        """
        return MarketBenchmarkService.calculate_outperform_percentage(plastic_index, sh_index)
    
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
        委托给 PositionCalculator 处理，保持向后兼容

        """
        return PositionCalculator.calculate(db, user_id, figures)
    
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
