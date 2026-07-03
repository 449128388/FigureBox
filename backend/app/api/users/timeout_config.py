"""
timeout_config.py - 超时登出配置 API 接口

功能说明：
- 提供超时登出配置的读取、更新等端点
- 遵循 RESTful 设计规范
- 所有已登录用户均可访问
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.models.database import get_db
from app.api.users import get_current_user
from app.models.user import User
from app.services.user_profile_service import TimeoutConfigService
from app.schemas.user import TimeoutConfigUpdate

router = APIRouter()


@router.get("/timeout/config", response_model=dict)
def get_timeout_config(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    获取当前用户的超时登出配置
    """
    return TimeoutConfigService.get_timeout_config(db, current_user)


@router.put("/timeout/config", response_model=dict)
def update_timeout_config(
    config_data: TimeoutConfigUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    更新当前用户的超时登出配置
    """
    return TimeoutConfigService.update_timeout_config(db, current_user, config_data)
