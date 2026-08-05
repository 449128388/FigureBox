"""
security_service.py - 账号安全服务（登录密码修改）

功能说明：
- 提供修改登录密码的业务逻辑：当前密码校验 → 新密码强度校验 → bcrypt 哈希落库
- 遵循企业级服务层架构，与 API 层分离
- 校验规则与前端 profile_settings_v6_backup.html「修改密码」页面保持一致：
  - 当前密码必填且必须与库中 bcrypt hash 匹配
  - 新密码长度 8-20 位
  - 新密码不能与当前密码相同
"""

import logging

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.user import User
from app.schemas.user import ChangePasswordRequest
from app.utils.password import get_password_hash, verify_password

logger = logging.getLogger(__name__)


class SecurityService:
    """账号安全服务类"""

    @staticmethod
    def change_password(db: Session, user: User, request: ChangePasswordRequest) -> dict:
        """
        修改当前登录用户的登录密码

        校验顺序（任一不满足即抛 400，不落库）：
        1. 当前密码必须与库中 bcrypt hash 匹配（防止他人借已登录会话改密）
        2. 新密码长度 8-20 位（与前端输入规则一致）
        3. 新密码不能与当前密码相同（避免无意义更新）

        Args:
            db: 数据库会话
            user: 当前登录用户对象
            request: 修改密码请求体（current_password + new_password）

        Returns:
            Dict: 修改结果 {success, message}

        Raises:
            HTTPException: 400 当前密码不正确 / 新密码长度不合规 / 新密码与当前相同
        """
        # 1. 当前密码校验
        if not verify_password(request.current_password, user.password_hash):
            logger.warning(f"用户 {user.id} 修改密码失败：当前密码不正确")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="当前密码不正确",
            )

        # 2. 新密码长度校验
        new_pwd = request.new_password
        if len(new_pwd) < 8 or len(new_pwd) > 20:
            logger.warning(f"用户 {user.id} 修改密码失败：新密码长度 {len(new_pwd)} 不在 8-20 位")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="新密码长度需在 8-20 位之间",
            )

        # 3. 新旧密码不能相同
        if new_pwd == request.current_password:
            logger.warning(f"用户 {user.id} 修改密码失败：新密码与当前密码相同")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="新密码不能与当前密码相同",
            )

        # 落库：bcrypt 哈希 + commit
        user.password_hash = get_password_hash(new_pwd)
        db.commit()
        db.refresh(user)
        logger.info(f"用户 {user.id} 登录密码修改成功")

        return {"success": True, "message": "密码修改成功，请使用新密码重新登录"}
