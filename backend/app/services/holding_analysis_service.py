"""
持仓分析服务
提供持仓相关的分析逻辑，包括持仓明细构建等
采用企业级服务层架构，分布统计逻辑拆分到 AssetDistributionService
"""
from datetime import date
from typing import Dict, Any, List
from sqlalchemy.orm import Session

from app.models.figure import Figure
from app.services.asset_calculation_service import AssetCalculationService

# 引入资产分布服务
from app.services.dashboard_service.assets_service.asset_distribution_service import (
    AssetDistributionService
)


class HoldingAnalysisService:
    """持仓分析服务类"""
    
    # 配置常量保留用于兼容性（实际逻辑已迁移到 AssetDistributionService）
    MANUFACTURER_COLORS = AssetDistributionService.MANUFACTURER_COLORS
    RISK_CONFIG = AssetDistributionService.RISK_CONFIG
    HOLDING_PERIOD_CONFIG = AssetDistributionService.HOLDING_PERIOD_CONFIG
    TIER_CONFIG = AssetDistributionService.TIER_CONFIG
    
    @classmethod
    def build_holding_detail(
        cls,
        figure: Figure,
        total_assets: float,
        order_count: int = 0
    ) -> Dict[str, Any]:
        """
        构建单个持仓明细
        
        Args:
            figure: 手办对象
            total_assets: 总资产
            order_count: 该手办的订单数量（排除已取消），默认为0
        
        Returns:
            Dict包含持仓的详细信息
        """
        cost_price = figure.average_purchase_price or 0
        current_price = figure.market_price or figure.price or 0
        profit = current_price - cost_price
        profit_percentage = (profit / cost_price * 100) if cost_price > 0 else 0
        
        # 确定状态标签
        status = AssetCalculationService.determine_status(profit_percentage)
        
        # 获取图片URL
        image_url = AssetCalculationService.get_figure_image_url(figure)
        
        # 处理入手时间和持有天数
        purchase_date_str = "未设置"
        holding_days = 0
        if figure.purchase_date:
            purchase_date_str = figure.purchase_date.strftime("%Y-%m")
            holding_days = AssetCalculationService.calculate_holding_days(
                figure.purchase_date
            )
        
        # 库存数量：以订单数量为准（排除已取消），如果没有订单则默认为1
        stock = order_count if order_count > 0 else 1
        
        # 计算市值占比
        market_value = current_price * stock
        market_share = (
            (market_value / total_assets * 100) if total_assets > 0 else 0
        )
        
        return {
            "figure_id": figure.id,
            "figure_name": figure.name,
            "stock": stock,
            "status": status,
            "cost_price": cost_price,
            "current_price": current_price,
            "profit": profit,
            "profit_percentage": profit_percentage,
            "purchase_date": purchase_date_str,
            "holding_days": holding_days,
            "market_share": round(market_share, 2),
            "image": image_url,
            "manufacturer": figure.manufacturer
        }
    
    @classmethod
    def build_all_holdings(
        cls,
        figures: List[Figure],
        total_assets: float,
        figure_order_counts: Dict[int, int] = None
    ) -> List[Dict[str, Any]]:
        """
        构建所有持仓明细
        
        Args:
            figures: 手办列表
            total_assets: 总资产
            figure_order_counts: 手办ID到订单数量的映射（排除已取消），默认为None
        
        Returns:
            List[Dict[str, Any]]: 持仓明细列表
        """
        if figure_order_counts is None:
            figure_order_counts = {}
        
        return [
            cls.build_holding_detail(
                fig, 
                total_assets,
                figure_order_counts.get(fig.id, 0)
            ) 
            for fig in figures
        ]
    
    @classmethod
    def calculate_risk_distribution(
        cls,
        holdings: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        计算风险状态分布（健康度仪表盘）
        
        委托给 AssetDistributionService 处理，保持向后兼容
        """
        return AssetDistributionService.calculate_risk_distribution(holdings)
    
    @classmethod
    def calculate_manufacturer_distribution(
        cls,
        holdings: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        计算制造商分布（IP分布）
        
        委托给 AssetDistributionService 处理，保持向后兼容
        """
        return AssetDistributionService.calculate_manufacturer_distribution(holdings)
    
    @classmethod
    def calculate_holding_period_distribution(
        cls,
        holdings: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        计算持仓周期分布
        
        委托给 AssetDistributionService 处理，保持向后兼容
        """
        return AssetDistributionService.calculate_holding_period_distribution(holdings)
    
    @classmethod
    def calculate_tier_distribution(
        cls,
        holdings: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        计算仓位分层分布
        
        委托给 AssetDistributionService 处理，保持向后兼容
        """
        return AssetDistributionService.calculate_tier_distribution(holdings)
    
    @classmethod
    def analyze_all_distributions(
        cls,
        figures: List[Figure],
        total_assets: float,
        figure_order_counts: Dict[int, int] = None
    ) -> Dict[str, List[Dict[str, Any]]]:
        """
        分析所有分布数据
        
        Args:
            figures: 手办列表
            total_assets: 总资产
            figure_order_counts: 手办ID到订单数量的映射（排除已取消），默认为None
        
        Returns:
            Dict包含所有饼图分布数据
        """
        # 构建持仓明细（传入订单数量）
        holdings = cls.build_all_holdings(figures, total_assets, figure_order_counts)
        
        # 计算各种分布
        return {
            "risk_distribution": cls.calculate_risk_distribution(holdings),
            "manufacturer_distribution": cls.calculate_manufacturer_distribution(holdings),
            "holding_period_distribution": cls.calculate_holding_period_distribution(holdings),
            "tier_distribution": cls.calculate_tier_distribution(holdings),
            "holdings": holdings
        }
