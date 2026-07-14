"""
upload.py - 图片上传接口

功能说明：
- 提供统一的图片上传端点，将图片存储到 MinIO 对象存储
- 取代原有的 base64 编码传输方式，提升网络传输效率
- 支持多图上传，返回图片 URL 列表

使用方式：
  前端通过 FormData 格式 POST 图片文件
  后端上传至 MinIO 后返回可公开访问的 URL
"""

import logging
from typing import List

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Request
from sqlalchemy.orm import Session

from app.models.database import get_db
from app.api.users import get_current_user
from app.models.user import User
from app.services.storage_service import StorageService

logger = logging.getLogger(__name__)

router = APIRouter()

# 服务启动时确保 MinIO bucket 存在并设置公开读策略
try:
    StorageService._ensure_bucket()
    logger.info("MinIO bucket 初始化完成")
except Exception as e:
    logger.warning(f"MinIO bucket 初始化异常（首次上传时会自动处理）: {e}")


@router.post("/upload")
async def upload_image(
    file: UploadFile = File(..., description="图片文件，支持 jpg/png/gif/webp，最大 20MB"),
    current_user: User = Depends(get_current_user),
    request: Request = None,
):
    """
    上传单张图片到 MinIO 对象存储

    - 支持格式: jpeg, png, gif, webp
    - 单张限制: 20MB
    - 返回: { "url": "http://.../bucket/filename.ext" }

    前端使用方式:
        const formData = new FormData()
        formData.append('file', fileObject)
        const res = await axios.post('/api/upload', formData, {
            headers: { 'Content-Type': 'multipart/form-data' }
        })
        // res.url 即为可访问的图片 URL
    """
    if not file or not file.filename:
        raise HTTPException(status_code=400, detail="未选择文件")

    # 读取文件内容
    try:
        file_data = await file.read()
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"文件读取失败: {e}")

    if not file_data:
        raise HTTPException(status_code=400, detail="文件内容为空")

    # 上传到 MinIO
    try:
        content_type = file.content_type or "image/jpeg"
        url = StorageService.upload_image(file_data, content_type, file.filename, request)
        return {"url": url}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"图片上传失败: {e}")
        raise HTTPException(status_code=500, detail="图片上传服务异常")


@router.post("/upload/multi")
async def upload_images(
    files: List[UploadFile] = File(..., description="多张图片文件，最多 10 张，单张最大 20MB"),
    current_user: User = Depends(get_current_user),
    request: Request = None,
):
    """
    批量上传多张图片到 MinIO 对象存储

    - 最多 10 张
    - 返回: { "urls": ["url1", "url2", ...] }
    """
    if not files:
        raise HTTPException(status_code=400, detail="未选择文件")

    if len(files) > 10:
        raise HTTPException(status_code=400, detail="一次最多上传 10 张图片")

    urls = []
    errors = []

    for file in files:
        try:
            file_data = await file.read()
            if not file_data:
                errors.append({"file": file.filename, "error": "文件内容为空"})
                continue

            content_type = file.content_type or "image/jpeg"
            url = StorageService.upload_image(file_data, content_type, file.filename, request)
            urls.append(url)
        except ValueError as e:
            errors.append({"file": file.filename, "error": str(e)})
        except Exception as e:
            logger.error(f"图片上传失败 {file.filename}: {e}")
            errors.append({"file": file.filename, "error": "上传服务异常"})

    result = {"urls": urls}
    if errors:
        result["errors"] = errors

    return result
