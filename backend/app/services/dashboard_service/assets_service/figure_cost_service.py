"""
手办成本服务

提供获取手办实际剩余持仓成本的功能
采用企业级服务层架构，与持仓列表使用相同的计算逻辑
"""
from sqlalchemy.orm import Session
from typing import Optional

from app.models.figure import Figure
from app.services.dashboard_service.assets_service.holding_position_service import (
    HoldingPositionService
)


class FigureCostService:
    """手办成本服务类"""

    @staticmethod
    def get_figure_cost_price(
        db: Session,
        figure_id: int,
        user_id: int
    ) -> Optional[float]:
        """
        获取手办的实际剩余持仓成本价

        计算逻辑：
        - 从库存账（AssetTransaction）计算当前剩余持仓的实际平均成本
        - 只统计关联订单状态为"已完成"的买入记录
        - 基于 remaining_quantity 和 price 计算加权平均成本
        - 与持仓列表（按盈亏排序）中的成本价计算逻辑保持一致

        Args:
            db: 数据库会话
            figure_id: 手办ID
            user_id: 用户ID

        Returns:
            float: 实际剩余持仓成本价，如果没有库存则返回 None
        """
        # 首先检查手办是否存在
        figure = db.query(Figure).filter(Figure.id == figure_id).first()
        if not figure:
            return None

        # 获取库存数量
        stock = HoldingPositionService.get_figure_inventory(db, figure_id, user_id)
        if stock <= 0:
            return None

        # 计算实际剩余持仓成本
        cost_price = HoldingPositionService.calculate_remaining_cost_price(
            db, figure_id, user_id
        )

        return cost_price

    @staticmethod
    def get_figure_cost_info(
        db: Session,
        figure_id: int,
        user_id: int
    ) -> Optional[dict]:
        """
        获取手办成本相关信息

        返回信息：
        - cost_price: 实际剩余持仓成本价
        - stock: 当前库存数量
        - currency: 成本价币种（默认为 CNY）

        Args:
            db: 数据库会话
            figure_id: 手办ID
            user_id: 用户ID

        Returns:
            dict: 成本信息字典，如果没有库存则返回 None
        """
        cost_price = FigureCostService.get_figure_cost_price(db, figure_id, user_id)

        if cost_price is None:
            return None

        stock = HoldingPositionService.get_figure_inventory(db, figure_id, user_id)

        return {
            "cost_price": cost_price,
            "stock": stock,
            "currency": "CNY"
        }
