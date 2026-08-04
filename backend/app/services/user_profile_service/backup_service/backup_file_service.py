"""
backup_file_service.py - 备份文件磁盘 IO 服务

功能说明：
- 负责备份 JSON 文件的「写到磁盘 / 读回磁盘 / 删除磁盘」三件事
- 文件路径：storage/backups/{user_id}/{YYYY-MM-DD_HH-mm-ss}.json
- 通过 docker volume ./backups_data:/app/storage/backups 持久化到宿主机
- 不依赖任何业务字段，纯 IO
"""
import os
import json
from datetime import datetime
from typing import Tuple


class BackupFileService:
    """备份文件磁盘 IO 服务"""

    # 容器内根目录（与 docker-compose volume 挂载点对齐）
    STORAGE_ROOT = "/app/storage/backups"

    @staticmethod
    def _build_dir(user_id: int) -> str:
        """拼接用户目录：storage/backups/{user_id}/"""
        return os.path.join(BackupFileService.STORAGE_ROOT, str(user_id))

    @staticmethod
    def _build_filename() -> str:
        """生成文件名：YYYY-MM-DD_HH-mm-ss.json"""
        return f"figurebox_backup_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.json"

    @staticmethod
    def save_to_disk(user_id: int, json_str: str) -> Tuple[str, int, int]:
        """
        写入备份 JSON 到磁盘

        Args:
            user_id: 所属用户 ID
            json_str: 完整 JSON 字符串

        Returns:
            (file_path, size_bytes, record_count)
            - file_path: 容器内绝对路径
            - size_bytes: 写入字节数
            - record_count: 解析 figures 数组长度
        """
        dir_path = BackupFileService._build_dir(user_id)
        os.makedirs(dir_path, exist_ok=True)

        filename = BackupFileService._build_filename()
        file_path = os.path.join(dir_path, filename)

        # 写文件
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(json_str)

        size_bytes = os.path.getsize(file_path)

        # 解析 figures 数量（兼容裸数组 / {figures: [...]} 两种格式）
        try:
            parsed = json.loads(json_str)
            if isinstance(parsed, dict):
                record_count = len(parsed.get("figures", []))
            elif isinstance(parsed, list):
                record_count = len(parsed)
            else:
                record_count = 0
        except Exception:
            record_count = 0

        return file_path, size_bytes, record_count

    @staticmethod
    def read_from_disk(file_path: str) -> bytes:
        """
        读取磁盘上的备份文件

        Args:
            file_path: 文件绝对路径

        Returns:
            文件内容（bytes）

        Raises:
            FileNotFoundError: 文件不存在
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"备份文件不存在: {file_path}")
        with open(file_path, "rb") as f:
            return f.read()

    @staticmethod
    def delete_file(file_path: str) -> bool:
        """
        删除磁盘上的备份文件

        Args:
            file_path: 文件绝对路径

        Returns:
            True=删除成功（或文件已不存在），False=删除失败
        """
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
            return True
        except Exception:
            return False
