"""
operation_holding_filter.py - 持仓筛选操作层

功能说明：
- 提供持仓列表筛选相关API端点
- 支持按手办名字模糊搜索和状态筛选

API端点：
- GET /holdings/filter: 筛选持仓列表

依赖：
- fastapi.APIRouter, Query
- sqlalchemy.orm.Session
- app.services.HoldingAnalysisService
- app.services.dashboard_service.assets_service.holding_filter_service.HoldingFilterService

创建时间: 2026-05-18
作者: FigureBox Team
"""

from fastapi import APIRouter, Depends, Query, Request, Response
from sqlalchemy.orm import Session
from typing import Optional, List
from pydantic import BaseModel

from app.models.database import get_db
from app.models.order import Order
from app.models.figure import Figure
from app.models.user import User
from app.api.users import get_current_user
from app.services import HoldingAnalysisService
from app.services.dashboard_service.assets_service.holding_filter_service import HoldingFilterService
from app.services.dashboard_service.assets_service.holding_position_service import HoldingPositionService
from .assets_common import AssetsCommonService


class InventoryItem(BaseModel):
    """库存手办列表项"""
    id: int
    name: str
    quantity: int
    cost_price: float
    image_url: Optional[str] = None

    class Config:
        from_attributes = True

router = APIRouter()


@router.get("/holdings/filter")
async def filter_holdings(
    request: Request,
    response: Response,
    keyword: Optional[str] = Query(None, description="手办名字搜索关键词"),
    status: Optional[str] = Query(None, description="风险状态筛选"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    筛选持仓列表

    支持按手办名字模糊搜索和风险状态筛选

    参数:
        keyword: 手办名字搜索关键词（模糊匹配）
        status: 风险状态筛选（如 '🚀 暴涨'）

    返回:
        筛选后的持仓列表
    """
    # 获取所有有效订单
    valid_orders = AssetsCommonService.get_valid_orders(db)

    # 获取有有效订单的手办列表
    figures = AssetsCommonService.get_figures_with_valid_orders(db, valid_orders)

    # 使用服务层分析持仓分布数据
    distribution_data = HoldingAnalysisService.analyze_all_distributions(
        db, figures, 0, current_user.id
    )

    # 获取原始持仓列表
    holdings = distribution_data.get("holdings", [])

    # 使用筛选服务进行筛选
    filtered_holdings = HoldingFilterService.filter_holdings(
        db=db,
        user_id=current_user.id,
        keyword=keyword,
        status=status,
        holdings=holdings
    )

    # 检查token续期
    AssetsCommonService.check_token_refresh(request, response)

    return {
        "holdings": filtered_holdings,
        "total_count": len(holdings),
        "filtered_count": len(filtered_holdings),
        "filter_options": HoldingFilterService.get_filter_options()
    }


@router.get("/holdings", response_model=List[InventoryItem])
async def get_inventory_holdings(
    has_stock: Optional[bool] = Query(None, description="只返回有库存的手办"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    获取持仓手办列表（用于卖出选择）

    返回有库存的手办列表，包含库存数量和成本价

    参数:
        has_stock: 为true时只返回库存数量>0的手办

    返回:
        手办列表，包含id、name、quantity、cost_price、image_url
    """
    # 获取所有手办
    figures = db.query(Figure).filter(Figure.user_id == current_user.id).all()

    result = []
    for figure in figures:
        # 获取库存数量
        stock = HoldingPositionService.get_figure_inventory(
            db, figure.id, current_user.id
        )

        # 如果要求有库存且库存为0，则跳过
        if has_stock and stock <= 0:
            continue

        # 获取成本价
        cost_price = HoldingPositionService.calculate_remaining_cost_price(
            db, figure.id, current_user.id
        )

        # 获取图片URL
        image_url = None
        if figure.images and len(figure.images) > 0:
            image_url = figure.images[0]

        result.append(InventoryItem(
            id=figure.id,
            name=figure.name,
            quantity=stock,
            cost_price=cost_price,
            image_url=image_url
        ))

    # 按库存数量降序排列
    result.sort(key=lambda x: x.quantity, reverse=True)

    return result
