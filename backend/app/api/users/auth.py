"""
auth.py - 鉴权依赖（公共模块）

功能说明：
- 集中管理 JWT 鉴权依赖 get_current_user
- 提供 HTTPBearer 提取 Bearer Token
- Token 续期逻辑：基于用户超时登出设置动态签发新 token
- 本文件不声明任何 @router 端点，仅作为依赖供 users 包内其他模块 import
"""
from fastapi import Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from datetime import timedelta

from app.models.database import get_db
from app.models.user import User
from app.utils.jwt import verify_token, create_access_token
import logging

logger = logging.getLogger(__name__)

security = HTTPBearer(auto_error=False)


def get_current_user(
    request: Request,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    """解析请求中的 JWT Token，注入当前登录用户对象。

    - 支持 HTTPBearer 自动注入 + 手动从 Authorization 头解析
    - 校验失败：401 Unauthorized
    - 用户不存在：404 Not Found
    - Token 临近过期：基于 user.session_timeout_minutes 动态签发新 token，
      写入 request.state.new_token，由中间件读取后下发 Set-Cookie / 响应头
    """
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
