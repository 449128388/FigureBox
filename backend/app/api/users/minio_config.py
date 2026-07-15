"""
minio_config.py - MinIO 配置 API 接口

功能说明：
- 提供 MinIO 配置的读取、更新、测试连接等端点
- 遵循 RESTful 设计规范
- 所有已登录用户均可访问
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.models.database import get_db
from app.api.users import get_current_user
from app.models.user import User
from app.services.user_profile_service import MinIOConfigService
from app.schemas.user import MinIOConfigUpdate

router = APIRouter()


@router.get("/minio/config", response_model=dict)
def get_minio_config(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    获取当前用户的 MinIO 配置
    """
    return MinIOConfigService.get_minio_config(db, current_user)


@router.put("/minio/config", response_model=dict)
def update_minio_config(
    config_data: MinIOConfigUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    更新当前用户的 MinIO 配置
    """
    return MinIOConfigService.update_minio_config(db, current_user, config_data)


@router.post("/minio/reset", response_model=dict)
def reset_minio_config(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    将当前用户的 MinIO 配置重置为系统默认值
    """
    return MinIOConfigService.reset_minio_config(db, current_user)


@router.post("/minio/test", response_model=dict)
def test_minio_connection(
    config_data: MinIOConfigUpdate,
    current_user: User = Depends(get_current_user)
):
    """
    测试 MinIO 连接
    """
    return MinIOConfigService.test_connection(config_data)
