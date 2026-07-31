"""
account.py - 账号基础接口路由（个人中心-账号安全面板数据源）

功能说明：
- GET  /api/me   - 获取当前登录用户基础信息
- PUT  /api/me   - 更新当前登录用户基础信息（username / email / password）
- 业务逻辑原地内联（仅字段级赋值 + password hash），未引入额外 Service
- 鉴权依赖：app.api.users.auth.get_current_user
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.users.auth import get_current_user
from app.models.database import get_db
from app.models.user import User
from app.schemas.user import User as UserSchema, UserUpdate

router = APIRouter()


@router.get("/me", response_model=UserSchema)
def get_me(current_user: User = Depends(get_current_user)):
    """获取当前登录用户基础信息（账号安全面板展示用）"""
    return current_user


@router.put("/me", response_model=UserSchema)
def update_me(
    user_update: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """更新当前登录用户基础信息：用户名 / 邮箱 / 密码

    - 仅对请求中显式传入的字段做更新，未传字段保持原值
    - 密码更新走 bcrypt 哈希
    - 写入后立即 commit + refresh，保证响应体反映最新值
    """
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
