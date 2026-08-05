"""
dashboard.py - 行情看板业务层

功能说明：
- 提供行情看板相关API端点
- 包括塑料小人指数(HPI)、成分股列表、HPI历史K线等

API端点：
- GET /dashboard: 获取行情看板数据
- GET /hpi-history: 获取 HPI 历史数据
- GET /hpi-components: 获取成分股详情
- GET /sector-ranking: 获取用户持仓板块涨幅排行
- GET /sector-dimensions: 获取支持的板块维度列表
- GET /sector-figures: 获取板块下手办明细（用于二级展开）
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.models.database import get_db
from app.models.user import User
from app.api.users import get_current_user
from app.services.dashboard_service.market_service.hpi_service import HPIService
from app.services.dashboard_service.market_service.sector_service import SectorService

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
    - sectors：默认按作品出处的板块涨幅排行 TOP 5
    """
    hpi_data = HPIService.get_hpi_dashboard(db, current_user.id)
    sector_data = SectorService.get_user_sector_ranking(db, current_user.id, dimension="work", limit=5)

    return {
        "index": hpi_data,
        "sectors": sector_data.get("sectors", []),
        "sector_total": sector_data.get("total", 0),
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


@router.get("/sector-ranking")
async def get_sector_ranking(
    dimension: str = Query("work", description="维度：work/manufacturer/material/original_art"),
    limit: int = Query(5, description="返回板块数量上限"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取用户持仓板块涨幅排行（按指定维度聚合）"""
    data = SectorService.get_user_sector_ranking(db, current_user.id, dimension=dimension, limit=limit)
    return {
        "sectors": data.get("sectors", []),
        "total": data.get("total", 0),
        "dimension": dimension,
    }


@router.get("/sector-dimensions")
async def get_sector_dimensions():
    """获取支持的板块维度列表"""
    return {"dimensions": SectorService.get_supported_dimensions()}


@router.get("/sector-figures")
async def get_sector_figures(
    dimension: str = Query("work", description="维度：work/manufacturer/material/original_art"),
    sector_name: str = Query(..., description="板块名（与 sector-ranking 返回的 name 一致）"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取指定板块下用户持仓手办明细（用于二级展开展示）"""
    data = SectorService.get_sector_figures(db, current_user.id, dimension, sector_name)
    return data

