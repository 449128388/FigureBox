"""
user_profile_service.py - 用户个人资料服务

功能说明：
- 提供用户个人资料的读取、更新等业务逻辑
- 遵循企业级服务层架构，与 API 层分离
- 处理生日字符串与 Date 类型的转换
"""

import logging
from datetime import date, datetime
from typing import Optional, Dict, Any

from sqlalchemy.orm import Session

from app.models.user import User
from app.schemas.user import ProfileUpdate, SettingsUpdate

logger = logging.getLogger(__name__)


class UserProfileService:
    """用户个人资料服务类"""

    @staticmethod
    def get_profile(db: Session, user: User) -> Dict[str, Any]:
        """
        获取用户完整个人资料

        Args:
            db: 数据库会话
            user: 当前用户对象

        Returns:
            Dict: 个人资料数据
        """
        return {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "nickname": user.nickname or "",
            "signature": user.signature or "",
            "gender": user.gender or "secret",
            "birthday": user.birthday.isoformat() if user.birthday else None,
            "bio": user.bio or "",
            "avatar_url": user.avatar_url or "",
            "phone": user.phone or "",
            "wechat": user.wechat or "",
            "is_active": user.is_active,
            "is_admin": user.is_admin,
            "annual_spending_limit": user.annual_spending_limit or 0,
        }

    @staticmethod
    def update_profile(db: Session, user: User, profile_data: ProfileUpdate) -> Dict[str, Any]:
        """
        更新用户个人资料

        Args:
            db: 数据库会话
            user: 当前用户对象
            profile_data: 更新的资料数据

        Returns:
            Dict: 更新后的个人资料
        """
        update_dict = profile_data.model_dump(exclude_unset=True)

        # 处理生日字符串 → date 对象
        if "birthday" in update_dict and update_dict["birthday"]:
            try:
                update_dict["birthday"] = date.fromisoformat(update_dict["birthday"])
            except (ValueError, TypeError):
                update_dict["birthday"] = None
        elif "birthday" in update_dict:
            update_dict["birthday"] = None

        # 逐字段更新
        for field, value in update_dict.items():
            if hasattr(user, field):
                setattr(user, field, value)

        db.commit()
        db.refresh(user)
        logger.info(f"用户 {user.id} 个人资料已更新")

        return UserProfileService.get_profile(db, user)

    @staticmethod
    def update_settings(db: Session, user: User, settings_data: SettingsUpdate) -> Dict[str, Any]:
        """
        更新用户的屏蔽/隐私/推送设置

        Args:
            db: 数据库会话
            user: 当前用户对象
            settings_data: 设置数据

        Returns:
            Dict: 更新后的设置
        """
        update_dict = settings_data.model_dump(exclude_unset=True)

        for field, value in update_dict.items():
            if hasattr(user, field):
                setattr(user, field, value)

        db.commit()
        db.refresh(user)
        logger.info(f"用户 {user.id} 设置已更新")

        return {
            "block_settings": user.block_settings or "{}",
            "privacy_settings": user.privacy_settings or "{}",
            "push_settings": user.push_settings or "{}",
        }
