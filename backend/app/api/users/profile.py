"""
profile.py - 个人资料接口路由（个人中心-基本资料面板数据源）

功能说明：
- GET  /api/profile   - 获取当前用户完整个人资料
- PUT  /api/profile   - 更新个人资料（昵称、签名、性别、生日、自我介绍等）
- 业务逻辑全部委托 UserProfileService
- 鉴权依赖：app.api.users.auth.get_current_user
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.users.auth import get_current_user
from app.models.database import get_db
from app.models.user import User
from app.schemas.user import ProfileUpdate, ProfileResponse
from app.services.user_profile_service import UserProfileService

router = APIRouter()


@router.get("/profile", response_model=ProfileResponse)
def get_profile(current_user: User = Depends(get_current_user)):
    """获取当前用户的完整个人资料（昵称/签名/性别/生日/简介/头像等）"""
    return UserProfileService.get_profile(None, current_user)


@router.put("/profile", response_model=ProfileResponse)
def update_profile(
    profile_data: ProfileUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """更新个人资料（昵称、签名、性别、生日、自我介绍等）"""
    return UserProfileService.update_profile(db, current_user, profile_data)
