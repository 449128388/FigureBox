"""
资产服务
提供资产相关的业务逻辑，是各子服务的统一入口，保持向后兼容

企业级架构说明：
本文件作为 Facade 模式实现，将业务逻辑拆分到以下子服务：
- TotalAssetsCalculator: 总资产计算（asset_core_calculations.py）
- DailyChangeCalculator: 日涨跌计算（asset_core_calculations.py）
- PositionCalculator: 仓位计算（asset_core_calculations.py）
- DailyCacheService: 每日市值缓存（asset_core_calculations.py）
- MarketBenchmarkService: 塑料指数、跑赢大盘计算（asset_market_benchmark_service.py）
- AssetDistributionService: 风险分布、制造商分布等饼图统计（asset_distribution_service.py）
- HoldingPositionService: 持仓明细构建、总成本计算、状态标签确定等（holding_position_service.py）
- IndexService: 上证指数、沪深300获取（index_service.py）

新代码应优先直接使用子服务，本文件仅用于保持向后兼容。
"""
from datetime import date
from typing import Dict, Any, List, Optional, Tuple
from sqlalchemy.orm import Session

from app.models.asset import AssetValueCache, UserSettings
from app.models.figure import Figure
from app.models.user import User

# 导入子服务
from .asset_core_calculations import (
    TotalAssetsCalculator,
    DailyChangeCalculator,
    PositionCalculator,
    DailyCacheService
)
from .asset_market_benchmark_service import MarketBenchmarkService
from .asset_distribution_service import AssetDistributionService
from .holding_position_service import HoldingPositionService
from .index_service import IndexService


class AssetCalculationService:
    """
    资产计算服务类（Facade 模式）

    作为各子服务的统一入口，所有方法委托给相应的子服务实现
    保持向后兼容，现有调用代码无需修改
    """

    # 基准日指数（保留常量用于兼容性）
    BASE_INDEX = MarketBenchmarkService.BASE_INDEX
    # 基准日上证指数（保留常量用于兼容性）
    BASE_SH_INDEX = MarketBenchmarkService.BASE_SH_INDEX

    # ==========================================================================
    # 核心计算服务（委托给 asset_core_calculations）
    # ==========================================================================
    @staticmethod
    def calculate_total_assets(figures: List[Figure]) -> float:
        """计算总资产"""
        return TotalAssetsCalculator.calculate(figures)

    @staticmethod
    def calculate_total_cost(figures: List[Figure]) -> float:
        """计算总成本"""
        return HoldingPositionService.calculate_total_cost(figures)

    @classmethod
    def calculate_daily_change(
        cls,
        db: Session,
        user_id: int,
        total_assets: float
    ) -> Tuple[float, float, bool]:
        """计算日涨跌（与股票账户当日盈亏完全一致）"""
        return DailyChangeCalculator.calculate(db, user_id, total_assets)

    @classmethod
    def save_daily_cache(
        cls,
        db: Session,
        user_id: int,
        total_assets: float
    ) -> None:
        """保存今日市值缓存（用于明日计算日涨跌）"""
        return DailyCacheService.save(db, user_id, total_assets)

    @classmethod
    def calculate_position(
        cls,
        db: Session,
        user_id: int,
        figures: List[Figure]
    ) -> Dict[str, Any]:
        """计算仓位信息"""
        return PositionCalculator.calculate(db, user_id, figures)

    # ==========================================================================
    # 市场基准服务（委托给 asset_market_benchmark_service）
    # ==========================================================================
    @classmethod
    def calculate_plastic_index(
        cls,
        figures: List[Figure],
        total_assets: float
    ) -> Tuple[float, date]:
        """计算塑料指数（市值加权复权指数）"""
        return MarketBenchmarkService.calculate_plastic_index(figures, total_assets)

    @classmethod
    def calculate_outperform_percentage(
        cls,
        plastic_index: float,
        sh_index: float
    ) -> float:
        """计算跑赢大盘百分比（成立至今）"""
        return MarketBenchmarkService.calculate_outperform_percentage(plastic_index, sh_index)

    # ==========================================================================
    # 持仓定位服务（委托给 holding_position_service）
    # ==========================================================================
    @staticmethod
    def determine_status(profit_percentage: float) -> str:
        """根据涨幅百分比确定状态标签"""
        return HoldingPositionService.determine_status(profit_percentage)

    @staticmethod
    def calculate_holding_days(purchase_date: date) -> int:
        """计算持有天数"""
        return HoldingPositionService.calculate_holding_days(purchase_date)

    @staticmethod
    def get_figure_image_url(figure: Figure) -> str:
        """获取手办图片URL"""
        return HoldingPositionService.get_figure_image_url(figure)

    @staticmethod
    def get_investment_budget(db: Session, user_id: int) -> float:
        """获取用户设置的投资预算上限"""
        user_settings = db.query(UserSettings).filter(
            UserSettings.user_id == user_id
        ).first()
        return user_settings.annual_spending_limit if user_settings else 0

    @staticmethod
    def calculate_invested_cost(figures: List[Figure]) -> float:
        """计算已投入成本（所有持仓手办的平均买入成本价总和）"""
        return sum(
            (fig.average_purchase_price or 0) * (fig.quantity or 1)
            for fig in figures
        )

    # ==========================================================================
    # 价格更新服务（委托给 holding_position_service）
    # ==========================================================================
    @staticmethod
    def get_figure_current_price(db: Session, figure_id: int) -> Optional[Figure]:
        """获取手办当前价格信息"""
        return HoldingPositionService.get_figure_current_price(db, figure_id)

    @staticmethod
    def get_price_history(db: Session, figure_id: int, limit: int = 1) -> Optional[Any]:
        """获取手办价格历史"""
        return HoldingPositionService.get_price_history(db, figure_id, limit)

    @classmethod
    def calculate_price_update_impact(
        cls,
        db: Session,
        user_id: int,
        figure: Figure,
        new_price: float
    ) -> Dict[str, Any]:
        """计算价格变更影响"""
        return HoldingPositionService.calculate_price_update_impact(db, user_id, figure, new_price)

    @classmethod
    def update_figure_price(
        cls,
        db: Session,
        figure_id: int,
        new_price: float,
        user_id: int
    ) -> Dict[str, Any]:
        """更新手办价格"""
        return HoldingPositionService.update_figure_price(db, figure_id, new_price, user_id)

    # ==========================================================================
    # 补仓服务（委托给 add_position_service）
    # ==========================================================================
    @classmethod
    def add_position(
        cls,
        db: Session,
        figure_id: int,
        user_id: int,
        quantity: int,
        price: float
    ) -> Dict[str, Any]:
        """执行补仓操作"""
        from .add_position_service import AddPositionService
        return AddPositionService.add_position(db, figure_id, user_id, quantity, price)


class HoldingAnalysisService:
    """
    持仓分析服务类（Facade 模式）

    作为各子服务的统一入口，所有方法委托给相应的子服务实现
    保持向后兼容，现有调用代码无需修改
    """

    # 配置常量保留用于兼容性
    MANUFACTURER_COLORS = AssetDistributionService.MANUFACTURER_COLORS
    RISK_CONFIG = AssetDistributionService.RISK_CONFIG
    HOLDING_PERIOD_CONFIG = AssetDistributionService.HOLDING_PERIOD_CONFIG
    TIER_CONFIG = AssetDistributionService.TIER_CONFIG

    # ==========================================================================
    # 持仓明细构建（委托给 holding_position_service）
    # ==========================================================================
    @classmethod
    def build_holding_detail(
        cls,
        figure: Figure,
        total_assets: float,
        order_count: int = 0
    ) -> Dict[str, Any]:
        """构建单个持仓明细"""
        return HoldingPositionService.build_holding_detail(figure, total_assets, order_count)

    @classmethod
    def build_all_holdings(
        cls,
        figures: List[Figure],
        total_assets: float,
        figure_order_counts: Dict[int, int] = None
    ) -> List[Dict[str, Any]]:
        """构建所有持仓明细"""
        return HoldingPositionService.build_all_holdings(figures, total_assets, figure_order_counts)

    # ==========================================================================
    # 分布统计服务（委托给 asset_distribution_service）
    # ==========================================================================
    @classmethod
    def calculate_risk_distribution(
        cls,
        holdings: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """计算风险状态分布（健康度仪表盘）"""
        return AssetDistributionService.calculate_risk_distribution(holdings)

    @classmethod
    def calculate_manufacturer_distribution(
        cls,
        holdings: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """计算制造商分布（IP分布）"""
        return AssetDistributionService.calculate_manufacturer_distribution(holdings)

    @classmethod
    def calculate_holding_period_distribution(
        cls,
        holdings: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """计算持仓周期分布"""
        return AssetDistributionService.calculate_holding_period_distribution(holdings)

    @classmethod
    def calculate_tier_distribution(
        cls,
        holdings: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """计算仓位分层分布"""
        return AssetDistributionService.calculate_tier_distribution(holdings)

    @classmethod
    def analyze_all_distributions(
        cls,
        figures: List[Figure],
        total_assets: float,
        figure_order_counts: Dict[int, int] = None
    ) -> Dict[str, List[Dict[str, Any]]]:
        """分析所有分布数据"""
        # 构建持仓明细
        holdings = cls.build_all_holdings(figures, total_assets, figure_order_counts)

        # 计算各种分布
        return {
            "risk_distribution": cls.calculate_risk_distribution(holdings),
            "manufacturer_distribution": cls.calculate_manufacturer_distribution(holdings),
            "holding_period_distribution": cls.calculate_holding_period_distribution(holdings),
            "tier_distribution": cls.calculate_tier_distribution(holdings),
            "holdings": holdings
        }


# 为了保持向后兼容，导出 IndexService 的别名
IndexService = IndexService
