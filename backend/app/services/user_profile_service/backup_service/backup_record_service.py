"""
backup_record_service.py - 备份历史记录 CRUD 服务

功能说明：
- 5 个核心方法：
  * create_record     - 插一行
  * list_records      - 分页查（按 created_at desc）
  * get_record        - 单条查（带 user_id 校验防越权）
  * delete_record     - 删记录行 + 删磁盘文件
  * enforce_retain    - 保留份数清理（按 created_at desc 保留前 N 条，其余删）
"""
import logging
from typing import Dict, Any, List
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import desc

from app.models.backup_record import BackupRecord
from app.services.user_profile_service.backup_service.backup_file_service import BackupFileService

logger = logging.getLogger(__name__)


class BackupRecordService:
    """备份历史记录 CRUD 服务"""

    @staticmethod
    def create_record(
        db: Session,
        user_id: int,
        filename: str,
        file_path: str,
        size_bytes: int,
        record_count: int,
        backup_type: str
    ) -> int:
        """
        插入一条备份历史记录

        Returns:
            新插入记录的 id
        """
        record = BackupRecord(
            user_id=user_id,
            filename=filename,
            file_path=file_path,
            size_bytes=size_bytes,
            record_count=record_count,
            backup_type=backup_type
        )
        db.add(record)
        db.commit()
        db.refresh(record)
        return record.id

    @staticmethod
    def list_records(db: Session, user_id: int, page: int, page_size: int) -> Dict[str, Any]:
        """
        分页拉取当前用户的备份历史（按 created_at desc）

        Returns:
            {
                "total": N,
                "page": page,
                "page_size": page_size,
                "items": [
                    {"id": ..., "filename": ..., "size_bytes": ..., "record_count": ..., "backup_type": ..., "created_at": "..."},
                    ...
                ]
            }
        """
        base_query = db.query(BackupRecord).filter(BackupRecord.user_id == user_id)
        total = base_query.count()
        records = (
            base_query
            .order_by(desc(BackupRecord.created_at))
            .offset((page - 1) * page_size)
            .limit(page_size)
            .all()
        )
        items = [
            {
                "id": r.id,
                "filename": r.filename,
                "size_bytes": int(r.size_bytes),
                "size_kb": round(int(r.size_bytes) / 1024, 1),
                "record_count": int(r.record_count),
                "backup_type": r.backup_type,
                "created_at": r.created_at.isoformat() if r.created_at else None
            }
            for r in records
        ]
        return {
            "total": total,
            "page": page,
            "page_size": page_size,
            "items": items
        }

    @staticmethod
    def get_record(db: Session, record_id: int, user_id: int) -> BackupRecord | None:
        """
        按 ID + user_id 查询单条记录

        user_id 校验防止越权访问他人备份
        """
        return (
            db.query(BackupRecord)
            .filter(BackupRecord.id == record_id, BackupRecord.user_id == user_id)
            .first()
        )

    @staticmethod
    def delete_record(db: Session, record_id: int, user_id: int) -> Dict[str, Any]:
        """
        删除一条备份历史：先删磁盘文件，再删记录行

        Returns:
            {"success": bool, "message": str}
        """
        record = BackupRecordService.get_record(db, record_id, user_id)
        if not record:
            return {"success": False, "message": f"备份记录 {record_id} 不存在或不属于当前用户"}

        # 删磁盘文件（失败也不阻塞 DB 删）
        file_deleted = BackupFileService.delete_file(record.file_path)
        if not file_deleted:
            logger.warning(f"删除磁盘文件失败（继续删记录）: {record.file_path}")

        db.delete(record)
        db.commit()
        return {
            "success": True,
            "message": f"备份记录 {record_id} 已删除",
            "file_deleted": file_deleted
        }

    @staticmethod
    def enforce_retain(db: Session, user_id: int, retain: int) -> int:
        """
        按 retain 保留份数清理旧记录（删记录 + 删磁盘文件）

        Args:
            retain: 保留份数；0 = 不限制（直接返回 0）

        Returns:
            实际清理的条数
        """
        if retain <= 0:
            return 0

        # 查所有记录按 created_at desc
        all_records = (
            db.query(BackupRecord)
            .filter(BackupRecord.user_id == user_id)
            .order_by(desc(BackupRecord.created_at))
            .all()
        )

        if len(all_records) <= retain:
            return 0

        to_delete = all_records[retain:]   # 超出部分
        deleted_count = 0
        for record in to_delete:
            BackupFileService.delete_file(record.file_path)
            db.delete(record)
            deleted_count += 1
        db.commit()
        logger.info(f"用户 {user_id} 保留份数清理：删除 {deleted_count} 条（retain={retain}）")
        return deleted_count
