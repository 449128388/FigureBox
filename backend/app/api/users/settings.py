"""
settings.py - 隐私/推送设置接口路由（个人中心-隐私设置 + 推送设置面板数据源）

功能说明：
- PUT  /api/settings   - 更新屏蔽/隐私/推送设置
- 业务逻辑全部委托 UserProfileService
- 鉴权依赖：app.api.users.auth.get_current_user
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.users.auth import get_current_user
from app.models.database import get_db
from app.models.user import User
from app.schemas.user import SettingsUpdate
from app.services.user_profile_service import UserProfileService

router = APIRouter()


@router.put("/settings")
def update_settings(
    settings_data: SettingsUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """更新屏蔽/隐私/推送设置"""
    return UserProfileService.update_settings(db, current_user, settings_data)
