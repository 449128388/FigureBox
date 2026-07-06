"""
middleware.py - FastAPI 中间件模块

功能说明：
- 提供 Token 自动续期中间件
- 遵循关注点分离原则，避免业务代码出现在主入口文件
"""

import logging
from datetime import timedelta

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware

from app.models.database import get_db
from app.models.user import User
from app.utils.jwt import verify_token, create_access_token

logger = logging.getLogger(__name__)


class TokenRefreshMiddleware(BaseHTTPMiddleware):
    """Token 自动续期中间件"""

    async def dispatch(self, request: Request, call_next):
        # 打印请求头信息用于调试
        logger.info(f"请求路径: {request.url.path}")
        logger.info(f"所有请求头: {dict(request.headers)}")
        logger.info(f"Authorization头: {request.headers.get('Authorization')}")

        response = await call_next(request)

        # 获取请求中的 token
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            token = auth_header[7:]  # 去掉 "Bearer " 前缀
            user_id, should_refresh = verify_token(token)

            # 只有当需要续期时才续期，使用用户的超时登出设置
            if user_id and should_refresh:
                db = next(get_db())
                try:
                    user = db.query(User).filter(User.id == user_id).first()
                    if user:
                        timeout_minutes = user.session_timeout_minutes
                        if timeout_minutes is None or timeout_minutes <= 0:
                            expires_delta = timedelta(days=365)
                        else:
                            expires_delta = timedelta(minutes=timeout_minutes)
                        new_token = create_access_token({"sub": user_id}, expires_delta=expires_delta)
                    else:
                        new_token = create_access_token({"sub": user_id})
                    response.headers["X-Refresh-Token"] = new_token
                finally:
                    db.close()

        return response
