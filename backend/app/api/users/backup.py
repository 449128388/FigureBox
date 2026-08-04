"""
backup.py - 系统备份/恢复 API 路由（个人中心-系统备份模块）

功能说明：
- GET  /api/backup/download                - 立即备份：导出全量手办数据为 JSON（同时落盘 + 写 backup_records）
- POST /api/backup/restore                 - 数据恢复：从上传的 JSON 文件恢复数据
- GET  /api/backup/settings                - 读取当前用户自动备份配置
- PUT  /api/backup/settings                - 更新自动备份配置
- GET  /api/backup/records                 - 拉取历史记录（分页）
- DELETE /api/backup/records/{id}          - 删除某条历史（含磁盘文件）
- GET  /api/backup/records/{id}/download   - 按记录 ID 重新下载
- 业务逻辑由 BackupService / BackupRecordService / BackupFileService / BackupSettingsService 承载
- 本文件只做 HTTP 协议层
- 端点从原 figures.py 迁移过来（2026-07-31 架构升级：备份/恢复归属个人中心业务）
"""
import json
import logging
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Query
from fastapi.responses import Response
from sqlalchemy.orm import Session
from typing import Dict, Any

from app.models.database import get_db
from app.api.users import get_current_user
from app.models.user import User
from app.services.user_profile_service.backup_service import BackupService
from app.services.user_profile_service.backup_service.backup_settings_service import BackupSettingsService
from app.services.user_profile_service.backup_service.backup_record_service import BackupRecordService
from app.services.user_profile_service.backup_service.backup_file_service import BackupFileService
from app.schemas.user import BackupSettingsUpdate

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/backup/download")
def download_backup(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    立即备份：导出当前用户全量数据为 JSON

    同时：
    - 落盘到 storage/backups/{user_id}/{ts}.json
    - 写一条 backup_records 记录（type=manual）
    - 返回 Response 给浏览器触发下载
    """
    try:
        result = BackupService.export_backup(db)
        json_str = result["json_str"]

        # 落盘 + 写记录（失败不影响返回下载）
        try:
            file_path, size_bytes, record_count = BackupFileService.save_to_disk(
                user_id=current_user.id,
                json_str=json_str
            )
            filename = result["filename"]
            BackupRecordService.create_record(
                db=db,
                user_id=current_user.id,
                filename=filename,
                file_path=file_path,
                size_bytes=size_bytes,
                record_count=record_count,
                backup_type="manual"
            )
        except Exception as e:
            logger.warning(f"备份落盘/记录失败（不影响下载）: {e}")

        return Response(
            content=json_str,
            media_type="application/json",
            headers={
                "Content-Disposition": f"attachment; filename={result['filename']}"
            }
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"备份失败: {str(e)}"
        )


@router.post("/backup/restore")
async def restore_backup(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    数据恢复：从上传的 JSON 文件恢复数据
    """
    try:
        contents = await file.read()
        # UploadFile.read() 返回 bytes，先解码为 str
        if isinstance(contents, bytes):
            try:
                json_str = contents.decode('utf-8')
            except UnicodeDecodeError:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="备份文件编码不是 UTF-8，无法解析"
                )
        else:
            json_str = contents

        result = BackupService.restore_backup(db, json_str, current_user.id)
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"恢复失败: {str(e)}"
        )


# ===== 自动备份配置 =====

@router.get("/backup/settings")
def get_backup_settings(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """读取当前用户的自动备份配置"""
    return BackupSettingsService.get(db, current_user)


@router.put("/backup/settings")
def update_backup_settings(
    settings: BackupSettingsUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """更新当前用户的自动备份配置（enabled / frequency / retain）"""
    return BackupSettingsService.update(db, current_user, settings)


# ===== 备份历史 =====

@router.get("/backup/records")
def list_backup_records(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """分页拉取当前用户的备份历史"""
    return BackupRecordService.list_records(db, current_user.id, page, page_size)


@router.delete("/backup/records/{record_id}")
def delete_backup_record(
    record_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """删除某条备份历史（同时删磁盘文件）"""
    return BackupRecordService.delete_record(db, record_id, current_user.id)


@router.get("/backup/records/{record_id}/download")
def download_backup_record(
    record_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """按记录 ID 重新下载某次备份"""
    record = BackupRecordService.get_record(db, record_id, current_user.id)
    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"备份记录 {record_id} 不存在或不属于当前用户"
        )
    try:
        content = BackupFileService.read_from_disk(record.file_path)
    except FileNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"备份文件已丢失：{record.filename}"
        )
    return Response(
        content=content,
        media_type="application/json",
        headers={
            "Content-Disposition": f"attachment; filename={record.filename}"
        }
    )
