"""
backup.py - 系统备份/恢复 API 路由（个人中心-系统备份模块）

功能说明：
- GET  /api/backup/download - 立即备份：导出全量手办数据为 JSON
- POST /api/backup/restore  - 数据恢复：从上传的 JSON 文件恢复数据
- 业务逻辑由 BackupService 统一承载，本文件只做 HTTP 协议层
- 端点从原 figures.py 迁移过来（2026-07-31 架构升级：备份/恢复归属个人中心业务）
"""
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from fastapi.responses import Response
from sqlalchemy.orm import Session
from typing import Dict, Any

from app.models.database import get_db
from app.api.users import get_current_user
from app.models.user import User
from app.services.backup_service import BackupService

router = APIRouter()


@router.get("/backup/download")
def download_backup(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    立即备份：导出当前用户全量数据为 JSON
    """
    try:
        result = BackupService.export_backup(db)
        return Response(
            content=result["json_str"],
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
