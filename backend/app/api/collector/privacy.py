"""
privacy.py - 收藏家隐私设置 API 接口

API端点：
- GET /collector/privacy: 获取隐私设置
- PUT /collector/privacy: 更新隐私设置
"""

from fastapi import APIRouter, Depends, Request, Response
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional

from app.models.database import get_db
from app.models.user import User
from app.api.users import get_current_user
from app.api.collector.dashboard import check_token_refresh
from app.services.dashboard_service.collector_service.collector_privacy_service import CollectorPrivacyService

router = APIRouter()


class PrivacyUpdateRequest(BaseModel):
    home_visibility: Optional[str] = None
    show_total: Optional[bool] = None
    show_figures: Optional[bool] = None
    show_asset: Optional[bool] = None
    show_tags: Optional[bool] = None
    show_feed: Optional[bool] = None
    poster_level: Optional[str] = None
    share_domain: Optional[str] = None


@router.get("/privacy")
async def get_privacy(
    request: Request,
    response: Response,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取收藏家隐私设置"""
    record = CollectorPrivacyService.get_or_create(db, current_user.id)
    check_token_refresh(request, response)
    return CollectorPrivacyService.to_dict(record)


@router.put("/privacy")
async def update_privacy(
    body: PrivacyUpdateRequest,
    request: Request,
    response: Response,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """更新收藏家隐私设置"""
    update_data = {k: v for k, v in body.dict().items() if v is not None}
    if not update_data:
        return {"success": False, "message": "没有需要更新的字段"}
    record = CollectorPrivacyService.update(db, current_user.id, update_data)
    check_token_refresh(request, response)
    return {"success": True, "settings": CollectorPrivacyService.to_dict(record)}
