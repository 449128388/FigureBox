"""
持仓定位服务
提供持仓相关的计算逻辑，包括持仓明细构建、总成本计算、状态标签确定、持有天数计算、图片URL获取、价格更新等
采用企业级服务层架构
"""
from datetime import date, datetime
from typing import Dict, Any, List, Optional, Tuple

from sqlalchemy.orm import Session

from app.models.figure import Figure
from app.models.asset import AssetPriceHistory


class HoldingPositionService:
    """持仓定位服务类"""

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
        status = cls.determine_status(profit_percentage)

        # 获取图片URL
        image_url = cls.get_figure_image_url(figure)

        # 处理入手时间和持有天数
        purchase_date_str = "未设置"
        holding_days = 0
        if figure.purchase_date:
            purchase_date_str = figure.purchase_date.strftime("%Y-%m")
            holding_days = cls.calculate_holding_days(figure.purchase_date)

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

        holdings = [
            cls.build_holding_detail(
                fig,
                total_assets,
                figure_order_counts.get(fig.id, 0)
            )
            for fig in figures
        ]

        # 按盈亏从高到低排序
        holdings.sort(key=lambda x: x.get("profit", 0), reverse=True)

        return holdings

    # ==========================================================================
    # 价格更新相关方法
    # ==========================================================================

    @staticmethod
    def get_figure_current_price(db: Session, figure_id: int) -> Optional[Figure]:
        """
        获取手办当前价格信息
        """
        return db.query(Figure).filter(Figure.id == figure_id).first()

    @staticmethod
    def get_price_history(db: Session, figure_id: int, limit: int = 1) -> Optional[AssetPriceHistory]:
        """
        获取手办价格历史
        """
        return db.query(AssetPriceHistory).filter(
            AssetPriceHistory.figure_id == figure_id
        ).order_by(AssetPriceHistory.date.desc()).first()

    @classmethod
    def calculate_price_update_impact(
        cls,
        db: Session,
        user_id: int,
        figure: Figure,
        new_price: float
    ) -> Dict[str, Any]:
        """
        计算价格变更影响

        返回:
        - old_total_assets: 原总资产
        - new_total_assets: 新总资产
        - old_profit_percentage: 原盈亏比例
        - new_profit_percentage: 新盈亏比例
        - index_change: 指数变化
        """
        from .asset_core_calculations import TotalAssetsCalculator
        from .asset_market_benchmark_service import MarketBenchmarkService

        # 获取所有手办
        figures = db.query(Figure).all()

        # 计算原总资产
        old_total_assets = TotalAssetsCalculator.calculate(figures)

        # 计算原盈亏
        old_total_cost = cls.calculate_total_cost(figures)
        old_profit = old_total_assets - old_total_cost
        old_profit_percentage = (old_profit / old_total_cost * 100) if old_total_cost > 0 else 0

        # 模拟新价格计算新总资产
        old_figure_price = figure.market_price or figure.price or 0
        price_diff = (new_price - old_figure_price) * (figure.quantity or 1)
        new_total_assets = old_total_assets + price_diff

        # 计算新盈亏
        new_profit = new_total_assets - old_total_cost
        new_profit_percentage = (new_profit / old_total_cost * 100) if old_total_cost > 0 else 0

        # 计算塑料指数（使用当前总资产）
        old_index, _ = MarketBenchmarkService.calculate_plastic_index(figures, old_total_assets)
        new_index, _ = MarketBenchmarkService.calculate_plastic_index(figures, new_total_assets)

        return {
            "old_total_assets": old_total_assets,
            "new_total_assets": new_total_assets,
            "old_profit_percentage": old_profit_percentage,
            "new_profit_percentage": new_profit_percentage,
            "index_change": new_index - old_index,
            "old_index": old_index,
            "new_index": new_index
        }

    @classmethod
    def update_figure_price(
        cls,
        db: Session,
        figure_id: int,
        new_price: float,
        user_id: int
    ) -> Dict[str, Any]:
        """
        更新手办价格

        流程:
        1. 更新手办市场价
        2. 记录价格历史
        3. 重新计算盈亏
        4. 更新状态标签

        返回:
        - 更新后的手办信息
        - 影响计算结果
        """
        # 获取手办
        figure = db.query(Figure).filter(Figure.id == figure_id).first()
        if not figure:
            raise ValueError(f"手办不存在: {figure_id}")

        # 计算影响
        impact = cls.calculate_price_update_impact(db, user_id, figure, new_price)

        # 更新手办市场价
        old_price = figure.market_price or figure.price or 0
        figure.market_price = new_price
        figure.current_value = new_price * (figure.quantity or 1)

        # 记录价格历史
        price_history = AssetPriceHistory(
            figure_id=figure_id,
            current_price=new_price
        )
        db.add(price_history)

        # 提交更改
        db.commit()
        db.refresh(figure)

        return {
            "figure": figure,
            "old_price": old_price,
            "new_price": new_price,
            "impact": impact
        }
