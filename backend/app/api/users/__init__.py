"""
用户模块 - API 路由

功能说明：
- 导出用户基础路由和 get_current_user 依赖，保持向后兼容
- 子模块：base.py（用户基础接口）、minio_config.py（MinIO 配置接口）
"""

from .base import router, get_current_user
from .minio_config import router as minio_config_router
from .timeout_config import router as timeout_config_router

__all__ = ["router", "get_current_user", "minio_config_router", "timeout_config_router"]
