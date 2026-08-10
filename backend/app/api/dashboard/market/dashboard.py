"""
dashboard.py - 行情看板业务层

功能说明：
- 提供行情看板相关API端点
- 包括塑料小人指数(HPI)、成分股列表、HPI历史K线、板块排行等

API端点：
- GET /dashboard/hpi                 行情看板 HPI 指数摘要（不含 components）
- GET /hpi-history                   获取 HPI 历史数据（K线）
- GET /hpi-components                获取成分股详情（投资复盘页）
- GET /sector-ranking                获取用户持仓板块涨幅排行（按指定维度聚合，首屏默认 dimension=work&limit=10）
- GET /sector-dimensions             获取支持的板块维度列表
- GET /sector-figures                获取板块下手办明细（用于二级展开）

"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.models.database import get_db
from app.models.user import User
from app.api.users import get_current_user
from app.services.dashboard_service.market_service.hpi_service import HPIService
from app.services.dashboard_service.market_service.sector_service import SectorService

router = APIRouter()


# ============== 内部辅助：从 HPI 字典剥离 components 数组 ==============

def _strip_components(hpi_data: dict) -> dict:
    """
    行情看板 HPI 摘要专用：从 HPIService 返回的完整数据中移除 components 数组。
    """
    if not isinstance(hpi_data, dict):
        return hpi_data
    return {k: v for k, v in hpi_data.items() if k != "components"}


# ============== 端点 1/2：行情看板 HPI 摘要 ==============

@router.get("/dashboard/hpi")
async def get_market_dashboard_hpi(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    行情看板 HPI 指数摘要（不含 components 数组）。
    返回塑料小人指数(HPI)相关数据：
    - index_value / avg_return / first_buy_date
    - total_figures / holding_figures / sold_figures
    - up_count / flat_count / down_count / sold_up_count / sold_down_count
    - in_cabinet_value / sold_value
    """
    hpi_data = HPIService.get_hpi_dashboard(db, current_user.id)
    return {"index": _strip_components(hpi_data)}


# ============== 原 /dashboard 与 /dashboard/sector-default 已删除 ==============
# 2026-08-06 拆分重构：
# - 原 GET /dashboard（单接口返回 index 含完整 components + sectors + sector_total）已替换为 /dashboard/hpi
# - 行情页首屏默认板块排行复用既有 /sector-ranking?dimension=work&limit=10 端点，
#   不再新增专用的 /dashboard/sector-default（与 /sector-ranking 重复）


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

