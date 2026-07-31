"""
admin.py - 管理员路由（账号注销-管理员相关）

功能说明：
- GET  /api/   - 列出所有用户（管理员权限）
- 仅 current_user.is_admin 可访问，否则 403
- 个人中心-账号注销面板的"请联系管理员"提示对应到本端点的权限模型
- 鉴权依赖：app.api.users.auth.get_current_user
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.users.auth import get_current_user
from app.models.database import get_db
from app.models.user import User
from app.schemas.user import User as UserSchema

router = APIRouter()


@router.get("/", response_model=list[UserSchema])
def get_users(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """管理员获取用户列表（分页）

    - 仅管理员可访问，非管理员返回 403 Forbidden
    - 默认每页 100 条，支持 skip/limit 分页参数
    """
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    users = db.query(User).offset(skip).limit(limit).all()
    return users
