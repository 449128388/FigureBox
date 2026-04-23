"""
资产分布服务
提供资产相关的分布统计逻辑，包括风险状态分布、制造商分布、持仓周期分布、仓位分层分布
采用企业级服务层架构
"""
from typing import Dict, Any, List


class AssetDistributionService:
    """资产分布服务类"""

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
    def calculate_risk_distribution(
        cls,
        holdings: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        计算风险状态分布（健康度仪表盘）

        统计各风险状态的手办数量和市值

        Args:
            holdings: 持仓明细列表

        Returns:
            List[Dict[str, Any]]: 风险状态饼图数据
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

        Args:
            holdings: 持仓明细列表

        Returns:
            List[Dict[str, Any]]: 制造商分布饼图数据
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

        Args:
            holdings: 持仓明细列表

        Returns:
            List[Dict[str, Any]]: 持仓周期分布饼图数据
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

        Args:
            holdings: 持仓明细列表

        Returns:
            List[Dict[str, Any]]: 仓位分层分布饼图数据
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
