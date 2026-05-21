"""
operation_figure_cost.py - 手办成本查询接口

功能说明：
- 提供手办实际剩余持仓成本查询API端点
- 用于已出售订单添加时获取成本价
- 与持仓列表使用相同的计算逻辑

API端点：
- GET /figures/{figure_id}/cost: 获取手办实际剩余持仓成本

依赖：
- fastapi.APIRouter
- sqlalchemy.orm.Session
- app.services.dashboard_service.assets_service.FigureCostService

创建时间: 2026-05-20
作者: FigureBox Team
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Optional

from app.models.database import get_db
from app.models.user import User
from app.api.users import get_current_user
from app.services.dashboard_service.assets_service.figure_cost_service import (
    FigureCostService
)

router = APIRouter()


@router.get("/figures/{figure_id}/cost")
def get_figure_cost(
    figure_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    获取手办的实际剩余持仓成本价

    计算逻辑：
    - 从库存账（AssetTransaction）计算当前剩余持仓的实际平均成本
    - 只统计关联订单状态为"已完成"的买入记录
    - 基于 remaining_quantity 和 price 计算加权平均成本
    - 与持仓列表（按盈亏排序）中的成本价计算逻辑保持一致

    参数:
        figure_id: 手办ID

    返回:
        {
            "figure_id": 手办ID,
            "cost_price": 实际剩余持仓成本价,
            "stock": 当前库存数量,
            "currency": 成本价币种
        }

    异常:
        404: 手办不存在或没有库存
    """
    cost_info = FigureCostService.get_figure_cost_info(
        db=db,
        figure_id=figure_id,
        user_id=current_user.id
    )

    if cost_info is None:
        raise HTTPException(
            status_code=404,
            detail="手办不存在或没有库存"
        )

    return {
        "figure_id": figure_id,
        "cost_price": cost_info["cost_price"],
        "stock": cost_info["stock"],
        "currency": cost_info["currency"]
    }
