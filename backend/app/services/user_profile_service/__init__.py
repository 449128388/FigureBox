"""
用户个人资料服务模块

功能说明：
- 提供用户个人资料的读取、更新等业务逻辑
- 遵循企业级服务层架构，与 API 层分离
"""

from .user_profile_service import UserProfileService

__all__ = ["UserProfileService"]
