"""
storage_service.py - MinIO 对象存储服务

功能说明：
- 封装 MinIO SDK，提供图片上传、删除、URL 生成等操作
- 自动初始化 bucket，无需手动创建
- 配置通过环境变量注入，生产环境需修改 MINIO_PUBLIC_URL

容器间通信：
- backend → minio: 通过 Docker 内部网络访问 minio:9000
- 前端浏览器 → minio: 通过 Nginx 反向代理 /minio/ → minio:9000
"""

import os
import logging
from uuid import uuid4
from typing import Optional
from io import BytesIO

from minio import Minio
from minio.error import S3Error

logger = logging.getLogger(__name__)


class StorageService:
    """MinIO 对象存储服务"""

    # 客户端实例（单例）
    _client: Optional[Minio] = None

    # 支持的图片 MIME 类型
    ALLOWED_CONTENT_TYPES = {
        'image/jpeg': '.jpg',
        'image/png': '.png',
        'image/gif': '.gif',
        'image/webp': '.webp',
    }

    # 单张图片最大 20MB
    MAX_FILE_SIZE = 20 * 1024 * 1024

    @classmethod
    def _get_client(cls) -> Minio:
        """获取 MinIO 客户端（延迟初始化）"""
        if cls._client is None:
            endpoint = os.getenv("MINIO_ENDPOINT", "minio:9000")
            access_key = os.getenv("MINIO_ACCESS_KEY", "figurebox")
            secret_key = os.getenv("MINIO_SECRET_KEY", "FigureBox@2024!")
            secure = os.getenv("MINIO_SECURE", "false").lower() == "true"

            cls._client = Minio(
                endpoint,
                access_key=access_key,
                secret_key=secret_key,
                secure=secure,
            )
            logger.info(f"MinIO 客户端初始化完成 (endpoint={endpoint})")
        return cls._client

    @classmethod
    def _ensure_bucket(cls) -> str:
        """确保 bucket 存在，不存在则创建，并设置公开读策略"""
        bucket = os.getenv("MINIO_BUCKET", "figurebox-images")
        client = cls._get_client()
        if not client.bucket_exists(bucket):
            client.make_bucket(bucket)
            logger.info(f"MinIO bucket '{bucket}' 已创建")

        # 设置 bucket 公开读策略，允许通过 Nginx 代理直接访问图片
        # 无论 bucket 是否新创建都执行，确保已有 bucket 也应用策略
        try:
            policy = {
                "Version": "2012-10-17",
                "Statement": [
                    {
                        "Effect": "Allow",
                        "Principal": {"AWS": ["*"]},
                        "Action": ["s3:GetObject"],
                        "Resource": [f"arn:aws:s3:::{bucket}/*"],
                    }
                ],
            }
            import json
            client.set_bucket_policy(bucket, json.dumps(policy))
        except Exception as e:
            logger.warning(f"设置 bucket 公开读策略失败（非致命）: {e}")
        return bucket

    @classmethod
    def upload_image(cls, file_data: bytes, content_type: str, original_filename: str = "") -> str:
        """
        上传图片到 MinIO

        Args:
            file_data: 图片二进制数据
            content_type: MIME 类型 (image/jpeg, image/png 等)
            original_filename: 原始文件名（仅用于提取扩展名）

        Returns:
            str: 图片的公开访问 URL

        Raises:
            ValueError: 文件类型不支持或超过大小限制
            S3Error: MinIO 服务异常
        """
        # 校验文件大小
        if len(file_data) > cls.MAX_FILE_SIZE:
            raise ValueError(f"图片大小超过限制 ({cls.MAX_FILE_SIZE // 1024 // 1024}MB)")

        # 校验文件类型
        if content_type not in cls.ALLOWED_CONTENT_TYPES:
            raise ValueError(f"不支持的图片类型: {content_type}")

        # 生成唯一文件名
        ext = cls.ALLOWED_CONTENT_TYPES[content_type]
        filename = f"{uuid4().hex}{ext}"

        # 上传
        bucket = cls._ensure_bucket()
        client = cls._get_client()
        file_size = len(file_data)
        file_stream = BytesIO(file_data)

        client.put_object(
            bucket_name=bucket,
            object_name=filename,
            data=file_stream,
            length=file_size,
            content_type=content_type,
        )

        # 返回对外访问 URL（通过 Nginx 代理）
        public_url = os.getenv("MINIO_PUBLIC_URL", "http://localhost:28640")
        url = f"{public_url}/{bucket}/{filename}"
        logger.info(f"图片上传成功: {url}")
        return url

    @classmethod
    def delete_image(cls, url: str) -> bool:
        """
        从 MinIO 删除图片

        Args:
            url: 图片的完整访问 URL

        Returns:
            bool: 是否删除成功
        """
        try:
            bucket = os.getenv("MINIO_BUCKET", "figurebox-images")
            # 从 URL 中提取 object name
            # URL 格式: http://host/bucket/filename
            parts = url.split(f"/{bucket}/")
            if len(parts) < 2:
                logger.warning(f"无法从 URL 解析文件名: {url}")
                return False
            filename = parts[-1].split("?")[0]

            client = cls._get_client()
            client.remove_object(bucket, filename)
            logger.info(f"图片删除成功: {bucket}/{filename}")
            return True
        except S3Error as e:
            logger.error(f"MinIO 删除失败: {e}")
            return False

    @classmethod
    def is_minio_url(cls, url: str) -> bool:
        """判断 URL 是否为 MinIO 存储的图片"""
        public_url = os.getenv("MINIO_PUBLIC_URL", "http://localhost:28640")
        return url.startswith(public_url)
