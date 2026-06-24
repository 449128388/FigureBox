"""
timeline.py - 收藏家看板动态流接口

API端点：
- GET /collector/timeline: 获取动态流列表
- GET /collector/timeline/events: 获取按日期分组的动态流
- GET /collector/timeline/events/{id}: 获取单条事件详情

说明：
- 动态流数据从 activity_feed 表读取
- 支持按事件类型筛选
- 支持分页
"""

from fastapi import APIRouter, Depends, Request, Response, Query
from sqlalchemy.orm import Session

from app.models.database import get_db
from app.models.user import User
from app.api.users import get_current_user
from app.api.collector.dashboard import check_token_refresh
from app.services.collector_service.collector_activity_service import CollectorActivityService

router = APIRouter()


@router.get("/timeline")
async def get_collector_timeline(
    request: Request,
    response: Response,
    event_type: str = Query('all', description="事件类型筛选：all/buy/sell/order/tag/price"),
    offset: int = Query(0, description="分页偏移"),
    limit: int = Query(20, description="每页条数"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    获取收藏家看板动态流数据（按日期分组）

    返回按日期倒序分组的动态流事件列表。
    """
    groups, has_more = CollectorActivityService.get_event_groups(
        db=db,
        user_id=current_user.id,
        event_type=event_type if event_type != 'all' else None,
        offset=offset,
        limit=limit
    )

    check_token_refresh(request, response)

    return {
        "activities": groups,
        "has_more": has_more
    }


@router.get("/timeline/events")
async def get_timeline_events(
    request: Request,
    response: Response,
    event_type: str = Query('all', description="事件类型筛选"),
    offset: int = Query(0, description="分页偏移"),
    limit: int = Query(20, description="每页条数"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取动态流事件列表（平铺，不分组）"""
    events = CollectorActivityService.get_events(
        db=db,
        user_id=current_user.id,
        event_type=event_type if event_type != 'all' else None,
        offset=offset,
        limit=limit
    )

    check_token_refresh(request, response)

    return {
        "events": events,
        "total": len(events)
    }


@router.get("/timeline/events/{event_id}")
async def get_timeline_event_detail(
    event_id: int,
    request: Request,
    response: Response,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取单条事件详情"""
    detail = CollectorActivityService.get_event_detail(db, event_id)

    check_token_refresh(request, response)

    if not detail:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="事件不存在")

    return detail
