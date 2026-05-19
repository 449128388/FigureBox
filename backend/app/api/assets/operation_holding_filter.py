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
from typing import Optional

from app.models.database import get_db
from app.models.order import Order
from app.models.figure import Figure
from app.models.user import User
from app.api.users import get_current_user
from app.services import HoldingAnalysisService
from app.services.dashboard_service.assets_service.holding_filter_service import HoldingFilterService
from .assets_common import AssetsCommonService

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
