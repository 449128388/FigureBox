"""
manufacturers.py - 本命厂商 API 接口

API端点：
- GET /collector/manufacturers: 获取所有本命厂商列表
- POST /collector/manufacturers: 新增本命厂商
- GET /collector/manufacturers/{id}: 获取单个厂商详情（含手办列表）
- PUT /collector/manufacturers/{id}: 更新本命厂商
- DELETE /collector/manufacturers/{id}: 删除本命厂商

职责：
- 管理用户在收藏家模式中的本命厂商数据
- 提供厂商维度的手办统计信息
"""

import logging
import requests
from fastapi import APIRouter, Depends, Request, Response, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional

from app.models.database import get_db
from app.models.user import User
from app.api.users import get_current_user
from app.services.collector_service.collector_manufacturer_service import CollectorManufacturerService
from app.services.storage_service.storage_service import StorageService

logger = logging.getLogger(__name__)

router = APIRouter()


def _upload_external_logo(logo_url: str, request: Request) -> str:
    """
    下载外部图片链接并上传到 MinIO 图床，返回 MinIO URL

    如果 logo_url 为空或已是 MinIO 内部 URL，直接返回原值。
    下载失败时保留原 URL 不阻断流程。
    """
    if not logo_url:
        return logo_url
    
    # 已是 MinIO 内部 URL，无需处理
    if StorageService.is_minio_url(logo_url):
        return logo_url

    try:
        # 模拟浏览器请求头，绕过 CDN 防盗链
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                          "(KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
            "Referer": "https://hpoi.net/",
        }
        resp = requests.get(logo_url, headers=headers, timeout=30)
        resp.raise_for_status()

        content_type = resp.headers.get("content-type", "")
        if content_type not in StorageService.ALLOWED_CONTENT_TYPES:
            content_type = "image/jpeg"  # 兜底

        new_url = StorageService.upload_image(
            file_data=resp.content,
            content_type=content_type,
            request=request,
        )
        logger.info(f"外部 Logo 已上传至 MinIO: {logo_url} -> {new_url}")
        return new_url
    except Exception as e:
        logger.warning(f"外部 Logo 下载/上传失败，保留原 URL: {e}")
        return logo_url


class CreateManufacturerRequest(BaseModel):
    """新增本命厂商请求参数"""
    name: str
    name_jp: Optional[str] = ""
    description: Optional[str] = ""
    logo_url: Optional[str] = ""
    website_url: Optional[str] = ""
    twitter_url: Optional[str] = ""
    sort_order: Optional[int] = 0


class UpdateManufacturerRequest(BaseModel):
    """更新本命厂商请求参数"""
    name: Optional[str] = None
    name_jp: Optional[str] = None
    description: Optional[str] = None
    logo_url: Optional[str] = None
    website_url: Optional[str] = None
    twitter_url: Optional[str] = None
    sort_order: Optional[int] = None


@router.get("/manufacturers")
async def get_manufacturers(
    request: Request,
    response: Response,
    keyword: str = "",
    filter_type: str = "",
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取所有本命厂商列表（支持按关键词搜索和状态筛选）

    Query Params:
        keyword: 搜索关键词（厂商名称 / 日文名 / 描述 模糊匹配）
        filter_type: 筛选类型
            - "in"  : 有在柜藏品
            - "out" : 无在柜藏品
            - ""    : 全部

    Response:
        {
            "manufacturers": [...],   # 按 filter_type 过滤后的列表
            "total": int,             # 当前列表数量
            "stats": {                # 独立于 filter_type 的统计（仅受 keyword 影响）
                "all": int, "in": int, "out": int
            }
        }
    """
    data = CollectorManufacturerService.get_all(
        db, current_user.id, keyword=keyword, filter_type=filter_type
    )
    return data


@router.get("/manufacturers/{manufacturer_id}")
async def get_manufacturer_detail(
    manufacturer_id: int,
    request: Request,
    response: Response,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取单个本命厂商详情含手办列表"""
    detail = CollectorManufacturerService.get_by_id(db, current_user.id, manufacturer_id)
    if not detail:
        raise HTTPException(status_code=404, detail="本命厂商不存在")
    return detail


@router.post("/manufacturers")
async def create_manufacturer(
    body: CreateManufacturerRequest,
    request: Request,
    response: Response,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """新增本命厂商"""
    if not body.name or not body.name.strip():
        raise HTTPException(status_code=400, detail="厂商名称不能为空")

    data = body.dict()
    # 外部 Logo 自动下载并上传到 MinIO
    if data.get("logo_url"):
        data["logo_url"] = _upload_external_logo(data["logo_url"], request)

    manufacturer = CollectorManufacturerService.create(db, current_user.id, data)
    return {
        "id": manufacturer.id,
        "name": manufacturer.name,
        "message": "本命厂商已添加"
    }


@router.put("/manufacturers/{manufacturer_id}")
async def update_manufacturer(
    manufacturer_id: int,
    body: UpdateManufacturerRequest,
    request: Request,
    response: Response,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """更新本命厂商"""
    update_data = {k: v for k, v in body.dict().items() if v is not None}
    if not update_data:
        raise HTTPException(status_code=400, detail="没有需要更新的字段")

    # 外部 Logo 自动下载并上传到 MinIO
    if "logo_url" in update_data and update_data["logo_url"]:
        update_data["logo_url"] = _upload_external_logo(update_data["logo_url"], request)

    manufacturer = CollectorManufacturerService.update(db, current_user.id, manufacturer_id, update_data)
    if not manufacturer:
        raise HTTPException(status_code=404, detail="本命厂商不存在")

    return {
        "id": manufacturer.id,
        "name": manufacturer.name,
        "message": "厂商信息已更新"
    }


@router.delete("/manufacturers/{manufacturer_id}")
async def delete_manufacturer(
    manufacturer_id: int,
    request: Request,
    response: Response,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """删除本命厂商（软删除）"""
    success = CollectorManufacturerService.delete(db, current_user.id, manufacturer_id)
    if not success:
        raise HTTPException(status_code=404, detail="本命厂商不存在")

    return {
        "message": "已删除"
    }
