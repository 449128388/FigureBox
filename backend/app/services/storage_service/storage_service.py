"""
storage_service.py - MinIO 对象存储服务

功能说明：
- 封装 MinIO SDK，提供图片上传、删除、URL 生成等操作
- 自动初始化 bucket，无需手动创建
- 图片 URL 优先使用请求的 Host 动态构造，支持多域名/NAT 部署
- 支持用户自定义 MinIO 配置（图床设置），用户配置时上传到用户指定的 MinIO
"""

import os
import logging
from uuid import uuid4
from typing import Optional, Dict, Any
from io import BytesIO
from fastapi import Request

from minio import Minio
from minio.error import S3Error

logger = logging.getLogger(__name__)


class StorageService:
    """MinIO 对象存储服务"""

    # 系统级客户端实例（单例，兜底使用）
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
        """获取系统级 MinIO 客户端（环境变量配置，延迟初始化单例）"""
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
            logger.info(f"系统 MinIO 客户端初始化完成 (endpoint={endpoint})")
        return cls._client

    @classmethod
    def _get_client_for_config(cls, config: Dict[str, Any]) -> Minio:
        """根据用户自定义配置创建 MinIO 客户端"""
        endpoint = config.get("endpoint", "").replace("http://", "").replace("https://", "")
        access_key = config.get("access_key", "")
        secret_key = config.get("secret_key", "")
        secure = config.get("secure", False)

        # localhost 替换为 host.docker.internal 以便容器内访问宿主机
        if "localhost" in endpoint:
            endpoint = endpoint.replace("localhost", "host.docker.internal")

        client = Minio(
            endpoint,
            access_key=access_key,
            secret_key=secret_key,
            secure=secure,
        )
        logger.info(f"用户自定义 MinIO 客户端创建 (endpoint={endpoint})")
        return client

    @classmethod
    def _ensure_bucket(cls) -> str:
        """确保系统级 bucket 存在"""
        bucket = os.getenv("MINIO_BUCKET", "figurebox-images")
        client = cls._get_client()
        if not client.bucket_exists(bucket):
            client.make_bucket(bucket)
            logger.info(f"系统 MinIO bucket '{bucket}' 已创建")

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
    def _ensure_bucket_for_client(cls, client: Minio, bucket: str):
        """确保用户自定义 MinIO 的 bucket 存在"""
        if not client.bucket_exists(bucket):
            client.make_bucket(bucket)
            logger.info(f"用户 MinIO bucket '{bucket}' 已创建")

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

    @classmethod
    def _build_public_url(cls, bucket: str, filename: str, request: Optional[Request] = None) -> str:
        """
        构造图片对外访问 URL

        优先使用请求的 Host 头动态构造（保留原始端口，适配 NAT/多域名/NAS 虚拟组网），
        兜底使用 MINIO_PUBLIC_URL 环境变量。
        """
        if request:
            scheme = request.headers.get("x-forwarded-proto", "http")
            host = request.headers.get("host", "localhost:28620")
            return f"{scheme}://{host}/minio/{bucket}/{filename}"
        public_url = os.getenv("MINIO_PUBLIC_URL", "http://localhost:28620/minio")
        return f"{public_url}/{bucket}/{filename}"

    @classmethod
    def _extract_user_config(cls, user) -> Optional[Dict[str, Any]]:
        """从用户对象提取 MinIO 自定义配置，若无自定义配置则返回 None"""
        if not user or not user.minio_endpoint:
            return None
        return {
            "endpoint": user.minio_endpoint,
            "access_key": user.minio_access_key,
            "secret_key": user.minio_secret_key,
            "bucket": user.minio_bucket or "figurebox-images",
            "public_url": user.minio_public_url,
            "secure": bool(user.minio_secure) if user.minio_secure is not None else False,
        }

    @classmethod
    def upload_image(cls, file_data: bytes, content_type: str, original_filename: str = "",
                     request: Optional[Request] = None,
                     minio_config: Optional[Dict[str, Any]] = None) -> str:
        """
        上传图片到 MinIO

        Args:
            file_data: 图片二进制数据
            content_type: MIME 类型 (image/jpeg, image/png 等)
            original_filename: 原始文件名（仅用于提取扩展名）
            request: FastAPI Request 对象（可选），用于动态构造图片访问 URL
            minio_config: 用户自定义 MinIO 配置字典（可选），有则使用自定义，无则用系统环境变量

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

        # 判断使用用户自定义配置还是系统默认配置
        if minio_config and minio_config.get("endpoint"):
            # 使用用户自定义 MinIO
            client = cls._get_client_for_config(minio_config)
            bucket = minio_config.get("bucket", "figurebox-images")
            cls._ensure_bucket_for_client(client, bucket)

            # 上传文件
            file_size = len(file_data)
            file_stream = BytesIO(file_data)
            client.put_object(
                bucket_name=bucket,
                object_name=filename,
                data=file_stream,
                length=file_size,
                content_type=content_type,
            )

            # 构造公开访问 URL
            custom_public_url = minio_config.get("public_url", "")
            if custom_public_url:
                url = f"{custom_public_url.rstrip('/')}/{bucket}/{filename}"
            elif request:
                scheme = request.headers.get("x-forwarded-proto", "http")
                host = request.headers.get("host", "localhost:28620")
                url = f"{scheme}://{host}/minio/{bucket}/{filename}"
            else:
                url = f"http://localhost:28620/minio/{bucket}/{filename}"

            logger.info(f"图片上传至自定义 MinIO 成功: {url}")
            return url
        else:
            # 使用系统默认 MinIO（环境变量配置）
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

            url = cls._build_public_url(bucket, filename, request)
            logger.info(f"图片上传至系统 MinIO 成功: {url}")
            return url

    @classmethod
    def delete_image(cls, url: str, minio_config: Optional[Dict[str, Any]] = None) -> bool:
        """
        从 MinIO 删除图片

        Args:
            url: 图片的完整访问 URL
            minio_config: 用户自定义 MinIO 配置（可选），用于删除用户自定义 MinIO 中的图片

        Returns:
            bool: 是否删除成功
        """
        try:
            if minio_config and minio_config.get("endpoint"):
                bucket = minio_config.get("bucket", "figurebox-images")
                client = cls._get_client_for_config(minio_config)
            else:
                bucket = os.getenv("MINIO_BUCKET", "figurebox-images")
                client = cls._get_client()

            # 从 URL 中提取 object name
            parts = url.split(f"/{bucket}/")
            if len(parts) < 2:
                logger.warning(f"无法从 URL 解析文件名: {url}")
                return False
            filename = parts[-1].split("?")[0]

            client.remove_object(bucket, filename)
            logger.info(f"图片删除成功: {bucket}/{filename}")
            return True
        except S3Error as e:
            logger.error(f"MinIO 删除失败: {e}")
            return False

    @classmethod
    def is_minio_url(cls, url: str, minio_config: Optional[Dict[str, Any]] = None) -> bool:
        """判断 URL 是否为 MinIO 存储的图片"""
        if minio_config and minio_config.get("bucket"):
            bucket = minio_config["bucket"]
        else:
            bucket = os.getenv("MINIO_BUCKET", "figurebox-images")
        return f"/{bucket}/" in url

    @classmethod
    def upload_external_images(cls, images: list, request: Optional[Request] = None) -> list:
        """
        批量处理外部图片链接：下载并上传到 MinIO 图床，返回更新后的 URL 列表

        已处于 MinIO 中的 URL 跳过；下载失败时保留原 URL 不阻断。
        """
        import requests as http_requests

        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                          "(KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
            "Referer": "https://hpoi.net/",
        }

        result = []
        for url in images:
            if not url:
                result.append(url)
                continue
            if cls.is_minio_url(url):
                result.append(url)
                continue
            try:
                resp = http_requests.get(url, headers=headers, timeout=30)
                resp.raise_for_status()
                content_type = resp.headers.get("content-type", "")
                if content_type not in cls.ALLOWED_CONTENT_TYPES:
                    content_type = "image/jpeg"
                new_url = cls.upload_image(
                    file_data=resp.content,
                    content_type=content_type,
                    request=request,
                )
                result.append(new_url)
            except Exception as e:
                logger.warning(f"外部图片下载/上传失败，保留原 URL [{url}]: {e}")
                result.append(url)
        return result
