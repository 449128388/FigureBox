from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from datetime import timedelta
from app.models.database import get_db
from app.models.user import User
from app.schemas.user import User as UserSchema, UserUpdate, ProfileUpdate, ProfileResponse, SettingsUpdate
from app.utils.jwt import verify_token, create_access_token
from app.services.user_profile_service import UserProfileService
import logging

logger = logging.getLogger(__name__)

router = APIRouter()
security = HTTPBearer(auto_error=False)


# 获取当前用户
def get_current_user(
    request: Request,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    token = None
    if credentials:
        token = credentials.credentials
    else:
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            token = auth_header[7:]

    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user_id, should_refresh = verify_token(token)

    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    # Token 续期时使用用户的超时登出设置
    if should_refresh:
        timeout_minutes = user.session_timeout_minutes
        if timeout_minutes is None or timeout_minutes <= 0:
            expires_delta = timedelta(days=365)
        else:
            expires_delta = timedelta(minutes=timeout_minutes)
        new_token = create_access_token(data={"sub": str(user_id)}, expires_delta=expires_delta)
        request.state.new_token = new_token

    return user


# ===== 基础用户接口 =====

@router.get("/me", response_model=UserSchema)
def get_me(current_user: User = Depends(get_current_user)):
    return current_user


@router.put("/me", response_model=UserSchema)
def update_me(user_update: UserUpdate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if user_update.username:
        current_user.username = user_update.username
    if user_update.email:
        current_user.email = user_update.email
    if user_update.password:
        from app.utils.password import get_password_hash
        current_user.password_hash = get_password_hash(user_update.password)
    db.commit()
    db.refresh(current_user)
    return current_user


# ===== 个人资料接口 =====

@router.get("/profile", response_model=ProfileResponse)
def get_profile(current_user: User = Depends(get_current_user)):
    """获取当前用户的完整个人资料"""
    return UserProfileService.get_profile(None, current_user)


@router.put("/profile", response_model=ProfileResponse)
def update_profile(
    profile_data: ProfileUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """更新个人资料（昵称、签名、性别、生日、自我介绍等）"""
    return UserProfileService.update_profile(db, current_user, profile_data)


@router.put("/settings")
def update_settings(
    settings_data: SettingsUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """更新屏蔽/隐私/推送设置"""
    return UserProfileService.update_settings(db, current_user, settings_data)


# ===== 管理员路由 =====

@router.get("/", response_model=list[UserSchema])
def get_users(skip: int = 0, limit: int = 100, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    users = db.query(User).offset(skip).limit(limit).all()
    return users
