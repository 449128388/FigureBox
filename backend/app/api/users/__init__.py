"""
用户模块 - API 路由聚合

功能说明：
- 聚合 users 包内全部 Feature 子 router 与鉴权依赖
- 7 个子模块：
  * auth.py              - 公共鉴权依赖 get_current_user（不挂端点）
  * account.py           - 账号基础接口（/me）→ 账号安全面板
  * profile.py           - 个人资料接口（/profile）→ 基本资料面板
  * settings.py          - 隐私/推送设置接口（/settings）→ 隐私 + 推送面板
  * admin.py             - 管理员接口（/）→ 账号注销 / 管理员
  * minio_config.py      - MinIO 图床配置（/minio/*）→ MinIO 设置面板
  * timeout_config.py    - 超时登出配置（/timeout/*）→ 超时登出面板
  * backup.py            - 系统备份/恢复（/backup/*）→ 系统备份面板
- 顶层 router = 各子 router 顺序聚合，OpenAPI 端点列表与拆分前完全一致
- get_current_user 仍由本包 re-export，31 个下游 `from app.api.users import get_current_user` 零修改
"""

# 鉴权依赖（保持向后兼容，31 个下游文件 import 不变）
from .auth import get_current_user, security

# Feature 子 router（按现有 users/ 目录范本聚合）
from .account import router as account_router
from .profile import router as profile_router
from .settings import router as settings_router
from .admin import router as admin_router
from .minio_config import router as minio_config_router
from .timeout_config import router as timeout_config_router
from .backup import router as backup_router

# 顶层聚合 router（main.py 仍通过 app.api.users.router 注册）
from fastapi import APIRouter
router = APIRouter()
router.include_router(account_router)
router.include_router(profile_router)
router.include_router(settings_router)
router.include_router(admin_router)
router.include_router(backup_router)
router.include_router(minio_config_router)
router.include_router(timeout_config_router)

__all__ = [
    "router",
    "get_current_user",
    "security",
    "account_router",
    "profile_router",
    "settings_router",
    "admin_router",
    "minio_config_router",
    "timeout_config_router",
    "backup_router",
]
