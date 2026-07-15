"""
minio_config_service.py - MinIO 配置服务

功能说明：
- 提供 MinIO 配置的读取、更新、重置为默认、测试连接等业务逻辑
- 遵循企业级服务层架构，与 API 层分离
- 支持配置验证和连接测试
"""

import os
import logging
from typing import Dict, Any
from datetime import datetime

from sqlalchemy.orm import Session

from app.models.user import User
from app.schemas.user import MinIOConfigUpdate

logger = logging.getLogger(__name__)


def _get_env_defaults() -> Dict[str, Any]:
    """读取系统环境变量中的 MinIO 默认配置"""
    return {
        "endpoint": os.getenv("MINIO_PUBLIC_ENDPOINT", "http://localhost:28640"),
        "access_key": os.getenv("MINIO_ACCESS_KEY", ""),
        "secret_key": os.getenv("MINIO_SECRET_KEY", ""),
        "bucket": os.getenv("MINIO_BUCKET", ""),
        "public_url": os.getenv("MINIO_PUBLIC_URL", ""),
        "secure": os.getenv("MINIO_SECURE", "false").lower() in ("true", "1", "yes"),
    }


class MinIOConfigService:
    """MinIO 配置服务类"""

    @staticmethod
    def get_minio_config(db: Session, user: User) -> Dict[str, Any]:
        """
        获取用户的 MinIO 配置
        """
        return {
            "endpoint": user.minio_endpoint or "",
            "access_key": user.minio_access_key or "",
            "secret_key": user.minio_secret_key or "",
            "bucket": user.minio_bucket or "",
            "public_url": user.minio_public_url or "",
            "secure": bool(user.minio_secure) if user.minio_secure is not None else False,
        }

    @staticmethod
    def update_minio_config(db: Session, user: User, config_data: MinIOConfigUpdate) -> Dict[str, Any]:
        """
        更新用户的 MinIO 配置
        """
        update_dict = config_data.model_dump(exclude_unset=True)

        field_mapping = {
            "endpoint": "minio_endpoint",
            "access_key": "minio_access_key",
            "secret_key": "minio_secret_key",
            "bucket": "minio_bucket",
            "public_url": "minio_public_url",
            "secure": "minio_secure",
        }

        for field, db_field in field_mapping.items():
            if field in update_dict:
                value = update_dict[field]
                if hasattr(user, db_field):
                    setattr(user, db_field, value)

        db.commit()
        db.refresh(user)
        logger.info(f"用户 {user.id} MinIO 配置已更新")

        return MinIOConfigService.get_minio_config(db, user)

    @staticmethod
    def reset_minio_config(db: Session, user: User) -> Dict[str, Any]:
        """
        将用户的 MinIO 配置重置为系统环境变量默认值
        """
        defaults = _get_env_defaults()

        field_mapping = {
            "endpoint": "minio_endpoint",
            "access_key": "minio_access_key",
            "secret_key": "minio_secret_key",
            "bucket": "minio_bucket",
            "public_url": "minio_public_url",
            "secure": "minio_secure",
        }

        for field, db_field in field_mapping.items():
            if hasattr(user, db_field):
                setattr(user, db_field, defaults.get(field))

        db.commit()
        db.refresh(user)
        logger.info(f"用户 {user.id} MinIO 配置已重置为默认值")

        return MinIOConfigService.get_minio_config(db, user)

    @staticmethod
    def test_connection(config_data: MinIOConfigUpdate) -> Dict[str, Any]:
        """
        测试 MinIO 连接
        """
        config = config_data.model_dump(exclude_unset=True)

        endpoint = config.get("endpoint")
        access_key = config.get("access_key")
        secret_key = config.get("secret_key")
        bucket = config.get("bucket")
        secure = config.get("secure", False)

        if not endpoint or not access_key or not secret_key:
            return {
                "success": False,
                "message": "配置不完整，请填写服务器地址、Access Key 和 Secret Key",
                "latency": 0,
            }

        try:
            from minio import Minio
            from minio.error import S3Error

            endpoint_clean = endpoint.replace("http://", "").replace("https://", "")
            if "localhost" in endpoint_clean:
                endpoint_clean = endpoint_clean.replace("localhost", "host.docker.internal")

            client = Minio(
                endpoint_clean,
                access_key=access_key,
                secret_key=secret_key,
                secure=secure,
            )

            start_time = datetime.now()
            buckets = client.list_buckets()
            latency = int((datetime.now() - start_time).total_seconds() * 1000)

            bucket_exists = any(b.name == bucket for b in buckets)

            if bucket_exists:
                return {
                    "success": True,
                    "message": "连接测试成功",
                    "latency": latency,
                }
            else:
                return {
                    "success": True,
                    "message": f"连接成功，但 Bucket '{bucket}' 不存在",
                    "latency": latency,
                }

        except S3Error as e:
            return {
                "success": False,
                "message": f"MinIO 连接失败: {str(e)}",
                "latency": 0,
            }
        except Exception as e:
            logger.error(f"MinIO 连接测试异常: {e}")
            return {
                "success": False,
                "message": f"连接测试异常: {str(e)}",
                "latency": 0,
            }