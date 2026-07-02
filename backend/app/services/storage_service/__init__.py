"""
存储服务模块

功能说明：
- 提供 MinIO 对象存储的封装，用于手办图片的统一管理
- 支持图片上传、删除、URL 生成
- 自动创建 bucket，无需手动初始化
"""

from .storage_service import StorageService

__all__ = ["StorageService"]
