"""
价格更新服务
提供修改现价相关的业务逻辑，包括价格更新、盈亏重算、指数重算等
"""
from datetime import datetime
from typing import Dict, Any, Optional, Tuple
from sqlalchemy.orm import Session

from app.models.figure import Figure
from app.models.asset import AssetPriceHistory
from app.services.asset_calculation_service import AssetCalculationService


class PriceUpdateService:
    """价格更新服务类"""
    
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
    def calculate_impact(
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
        # 获取所有手办
        figures = db.query(Figure).all()
        
        # 计算原总资产
        old_total_assets = AssetCalculationService.calculate_total_assets(figures)
        
        # 计算原盈亏
        old_total_cost = AssetCalculationService.calculate_total_cost(figures)
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
        old_index, _ = AssetCalculationService.calculate_plastic_index(figures, old_total_assets)
        new_index, _ = AssetCalculationService.calculate_plastic_index(figures, new_total_assets)
        
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
        impact = cls.calculate_impact(db, user_id, figure, new_price)
        
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
    
    @staticmethod
    def determine_status(profit_percentage: float) -> str:
        """
        根据盈亏比例确定状态标签
        """
        if profit_percentage >= 15:
            return "🚀 暴涨"
        elif profit_percentage >= 5:
            return "📈 上涨"
        elif profit_percentage > -5:
            return "➖ 横盘"
        elif profit_percentage > -15:
            return "📉 告警"
        elif profit_percentage > -20:
            return "🔴 破位"
        else:
            return "💀 退市"
