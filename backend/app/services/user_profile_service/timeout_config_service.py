"""
timeout_config_service.py - 超时登出配置服务

功能说明：
- 提供会话超时登出配置的读取、更新等业务逻辑
- 遵循企业级服务层架构，与 API 层分离
"""

import logging
from typing import Dict, Any

from sqlalchemy.orm import Session

from app.models.user import User
from app.schemas.user import TimeoutConfigUpdate

logger = logging.getLogger(__name__)


class TimeoutConfigService:
    """超时登出配置服务类"""

    @staticmethod
    def get_timeout_config(db: Session, user: User) -> Dict[str, Any]:
        """
        获取用户的超时登出配置

        Args:
            db: 数据库会话
            user: 当前用户对象

        Returns:
            Dict: 超时登出配置数据
        """
        return {
            "timeout_minutes": user.session_timeout_minutes if user.session_timeout_minutes is not None else 30,
            "timeout_warning": bool(user.session_timeout_warning) if user.session_timeout_warning is not None else True,
        }

    @staticmethod
    def update_timeout_config(db: Session, user: User, config_data: TimeoutConfigUpdate) -> Dict[str, Any]:
        """
        更新用户的超时登出配置

        Args:
            db: 数据库会话
            user: 当前用户对象
            config_data: 更新的配置数据

        Returns:
            Dict: 更新后的超时登出配置
        """
        update_dict = config_data.model_dump(exclude_unset=True)

        field_mapping = {
            "timeout_minutes": "session_timeout_minutes",
            "timeout_warning": "session_timeout_warning",
        }

        for field, db_field in field_mapping.items():
            if field in update_dict:
                value = update_dict[field]
                if hasattr(user, db_field):
                    setattr(user, db_field, value)

        db.commit()
        db.refresh(user)
        logger.info(f"用户 {user.id} 超时登出配置已更新")

        return TimeoutConfigService.get_timeout_config(db, user)
