"""
dashboard.py - 行情看板业务层

功能说明：
- 提供行情看板相关API端点
- 包括塑料小人指数(HPI)、成分股列表、HPI历史K线等

API端点：
- GET /dashboard: 获取行情看板数据
- GET /hpi-history: 获取 HPI 历史数据
- GET /hpi-components: 获取成分股详情
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.models.database import get_db
from app.models.user import User
from app.api.users import get_current_user
from app.services.dashboard_service.market_service.hpi_service import HPIService

router = APIRouter()


@router.get("/dashboard")
async def get_market_dashboard(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    获取行情看板 HPI 数据

    返回塑料小人指数(HPI)相关数据：
    - HPI：投资生涯全周期收益指数
    - 成分股盈亏分布
    - 卖飞/卖对统计
    """
    hpi_data = HPIService.get_hpi_dashboard(db, current_user.id)

    return {
        "index": hpi_data,
    }


@router.get("/hpi-history")
async def get_hpi_history(
    days: int = Query(365, description="查询天数"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取 HPI 历史K线数据"""
    history = HPIService.get_hpi_history(db, current_user.id, days)
    return {"history": history}


@router.get("/hpi-components")
async def get_hpi_components(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取成分股详情"""
    components = HPIService.get_components(db, current_user.id)
    return components

