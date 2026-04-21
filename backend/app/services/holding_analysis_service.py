"""
持仓分析服务
提供持仓相关的分析逻辑，包括风险分布、制造商分布、持仓周期、仓位分层等
"""
from datetime import date
from typing import Dict, Any, List
from sqlalchemy.orm import Session

from app.models.figure import Figure
from app.services.asset_calculation_service import AssetCalculationService


class HoldingAnalysisService:
    """持仓分析服务类"""
    
    # 预定义制造商分布颜色
    MANUFACTURER_COLORS = [
        "#5470c6", "#91cc75", "#fac858", "#ee6666", "#73c0de",
        "#3ba272", "#fc8452", "#9a60b4", "#ea7ccc", "#ff9f7f"
    ]
    
    # 风险状态配置
    RISK_CONFIG = {
        "🚀 暴涨": {"color": "#67C23A"},
        "📈 上涨": {"color": "#95D475"},
        "➖ 横盘": {"color": "#909399"},
        "📉 告警": {"color": "#E6A23C"},
        "🔴 破位": {"color": "#F56C6C"},
        "💀 退市": {"color": "#303133"}
    }
    
    # 持仓周期配置
    HOLDING_PERIOD_CONFIG = {
        "🆕 本月新入": {"color": "#67C23A", "max_days": 30},
        "📅 1年内": {"color": "#409EFF", "max_days": 365},
        "🏛️ 1-2年": {"color": "#E6A23C", "max_days": 730},
        "🦕 2年以上": {"color": "#909399", "max_days": float('inf')}
    }
    
    # 仓位分层配置
    TIER_CONFIG = {
        "🏠 海景房": {"color": "#F56C6C", "min_price": 3000},
        "💎 中端": {"color": "#409EFF", "min_price": 1000, "max_price": 3000},
        "🧩 入门": {"color": "#67C23A", "max_price": 1000}
    }
    
    @classmethod
    def build_holding_detail(
        cls,
        figure: Figure,
        total_assets: float
    ) -> Dict[str, Any]:
        """
        构建单个持仓明细
        
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
        
        # 计算市值占比
        market_value = current_price * (figure.quantity or 1)
        market_share = (
            (market_value / total_assets * 100) if total_assets > 0 else 0
        )
        
        return {
            "figure_id": figure.id,
            "figure_name": figure.name,
            "stock": figure.quantity or 1,
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
        total_assets: float
    ) -> List[Dict[str, Any]]:
        """
        构建所有持仓明细
        """
        return [
            cls.build_holding_detail(fig, total_assets) 
            for fig in figures
        ]
    
    @classmethod
    def calculate_risk_distribution(
        cls,
        holdings: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        计算风险状态分布（健康度仪表盘）
        
        统计各风险状态的手办数量和市值
        """
        # 初始化分布数据
        risk_distribution = {
            status: {"count": 0, "value": 0, "color": config["color"]}
            for status, config in cls.RISK_CONFIG.items()
        }
        
        # 统计各状态
        for holding in holdings:
            status = holding.get("status", "")
            market_value = holding.get("current_price", 0) * holding.get("stock", 1)
            if status in risk_distribution:
                risk_distribution[status]["count"] += 1
                risk_distribution[status]["value"] += market_value
        
        # 转换为饼图数据格式
        risk_pie_data = []
        for status, data in risk_distribution.items():
            if data["count"] > 0:
                risk_pie_data.append({
                    "name": status,
                    "value": round(data["value"], 2),
                    "count": data["count"],
                    "itemStyle": {"color": data["color"]}
                })
        
        return risk_pie_data
    
    @classmethod
    def calculate_manufacturer_distribution(
        cls,
        holdings: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        计算制造商分布（IP分布）
        
        统计各制造商的手办数量和市值
        """
        manufacturer_distribution: Dict[str, Dict[str, Any]] = {}
        
        for holding in holdings:
            manufacturer = holding.get("manufacturer", "未知厂商")
            if not manufacturer or manufacturer == "":
                manufacturer = "未知厂商"
            
            market_value = holding.get("current_price", 0) * holding.get("stock", 1)
            
            if manufacturer not in manufacturer_distribution:
                manufacturer_distribution[manufacturer] = {"count": 0, "value": 0}
            
            manufacturer_distribution[manufacturer]["count"] += 1
            manufacturer_distribution[manufacturer]["value"] += market_value
        
        # 转换为饼图数据格式
        manufacturer_pie_data = []
        color_idx = 0
        for manufacturer, data in manufacturer_distribution.items():
            if data["count"] > 0:
                manufacturer_pie_data.append({
                    "name": manufacturer,
                    "value": round(data["value"], 2),
                    "count": data["count"],
                    "itemStyle": {
                        "color": cls.MANUFACTURER_COLORS[
                            color_idx % len(cls.MANUFACTURER_COLORS)
                        ]
                    }
                })
                color_idx += 1
        
        # 按市值排序
        manufacturer_pie_data.sort(key=lambda x: x["value"], reverse=True)
        
        return manufacturer_pie_data
    
    @classmethod
    def calculate_holding_period_distribution(
        cls,
        holdings: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        计算持仓周期分布
        
        统计各持仓周期的手办数量和市值
        """
        # 初始化分布数据
        period_distribution = {
            period: {"count": 0, "value": 0, "color": config["color"]}
            for period, config in cls.HOLDING_PERIOD_CONFIG.items()
        }
        
        for holding in holdings:
            holding_days = holding.get("holding_days", 0)
            market_value = holding.get("current_price", 0) * holding.get("stock", 1)
            
            # 根据持有天数判断持仓周期
            if holding_days <= 30:
                period = "🆕 本月新入"
            elif holding_days <= 365:
                period = "📅 1年内"
            elif holding_days <= 730:
                period = "🏛️ 1-2年"
            else:
                period = "🦕 2年以上"
            
            period_distribution[period]["count"] += 1
            period_distribution[period]["value"] += market_value
        
        # 转换为饼图数据格式
        period_pie_data = []
        for period, data in period_distribution.items():
            if data["count"] > 0:
                period_pie_data.append({
                    "name": period,
                    "value": round(data["value"], 2),
                    "count": data["count"],
                    "itemStyle": {"color": data["color"]}
                })
        
        return period_pie_data
    
    @classmethod
    def calculate_tier_distribution(
        cls,
        holdings: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        计算仓位分层分布
        
        按单只手办市场价分层统计
        """
        # 初始化分布数据
        tier_distribution = {
            tier: {"count": 0, "value": 0, "color": config["color"]}
            for tier, config in cls.TIER_CONFIG.items()
        }
        
        for holding in holdings:
            market_price = holding.get("current_price", 0)
            market_value = market_price * holding.get("stock", 1)
            
            # 根据市场价判断分层
            if market_price > 3000:
                tier = "🏠 海景房"
            elif market_price >= 1000:
                tier = "💎 中端"
            else:
                tier = "🧩 入门"
            
            tier_distribution[tier]["count"] += 1
            tier_distribution[tier]["value"] += market_value
        
        # 转换为饼图数据格式
        tier_pie_data = []
        for tier, data in tier_distribution.items():
            if data["count"] > 0:
                tier_pie_data.append({
                    "name": tier,
                    "value": round(data["value"], 2),
                    "count": data["count"],
                    "itemStyle": {"color": data["color"]}
                })
        
        return tier_pie_data
    
    @classmethod
    def analyze_all_distributions(
        cls,
        figures: List[Figure],
        total_assets: float
    ) -> Dict[str, List[Dict[str, Any]]]:
        """
        分析所有分布数据
        
        Returns:
            Dict包含所有饼图分布数据
        """
        # 构建持仓明细
        holdings = cls.build_all_holdings(figures, total_assets)
        
        # 计算各种分布
        return {
            "risk_distribution": cls.calculate_risk_distribution(holdings),
            "manufacturer_distribution": cls.calculate_manufacturer_distribution(holdings),
            "holding_period_distribution": cls.calculate_holding_period_distribution(holdings),
            "tier_distribution": cls.calculate_tier_distribution(holdings),
            "holdings": holdings
        }
