"""
license_config.py - 许可管理 API 路由（个人中心-邮箱设置-许可管理面板）

功能说明：
- 端点（全部需登录）：
  - GET    /api/license/status        - 获取当前许可状态
  - GET    /api/license/machine-fingerprint - 获取本机机器指纹（用于 .req 导出）
  - POST   /api/license/activate      - 在线激活
  - POST   /api/license/import        - 离线导入 .lic 文件
  - GET    /api/license/history       - 获取许可历史记录
  - POST   /api/license/revoke        - 吊销当前许可
  - POST   /api/license/delete        - 删除许可记录
- 业务逻辑在 LicenseService 服务层
- 与 MinIO / Email / Backup 同层，全部由 main.py 单独挂载在 /api 前缀
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.models.database import get_db
from app.api.users import get_current_user
from app.models.user import User
from app.services.license_service import LicenseService
from app.schemas.license import (
    LicenseActivateRequest,
    LicenseImportRequest
)

router = APIRouter()


@router.get("/license/status", response_model=dict)
def get_license_status(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取当前用户的许可状态"""
    return LicenseService.get_license_status(db, current_user)


@router.get("/license/machine-fingerprint", response_model=dict)
def get_machine_fingerprint(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取本机机器指纹（用于导出 .req 请求文件）"""
    return LicenseService.get_machine_fingerprint(db, current_user)


@router.post("/license/activate", response_model=dict)
def activate_license(
    request: LicenseActivateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """在线激活许可"""
    try:
        return LicenseService.activate_online(db, current_user, request.license_key)
    except ValueError as e:
        return {"success": False, "message": str(e)}


@router.post("/license/import", response_model=dict)
def import_license(
    request: LicenseImportRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """离线导入 .lic 许可文件"""
    try:
        data = LicenseService.import_offline(db, current_user, request.filename, request.content)
        return {"success": True, "data": data, "message": "许可导入成功"}
    except ValueError as e:
        return {"success": False, "message": str(e)}


@router.get("/license/history", response_model=dict)
def get_license_history(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取许可历史记录"""
    return LicenseService.get_history(db, current_user)


@router.post("/license/revoke", response_model=dict)
def revoke_license(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """吊销当前许可"""
    try:
        data = LicenseService.revoke_license(db, current_user)
        return {"success": True, "data": data, "message": "许可已吊销"}
    except ValueError as e:
        return {"success": False, "message": str(e)}


@router.post("/license/delete", response_model=dict)
def delete_license(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """删除许可记录（清空状态）"""
    data = LicenseService.delete_history(db, current_user)
    return {"success": True, "data": data, "message": "许可记录已删除"}
