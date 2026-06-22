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

from fastapi import APIRouter, Depends, Request, Response, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional

from app.models.database import get_db
from app.models.user import User
from app.api.users import get_current_user
from app.services.collector_service.collector_manufacturer_service import CollectorManufacturerService

router = APIRouter()


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
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取所有本命厂商列表"""
    manufacturers = CollectorManufacturerService.get_all(db, current_user.id)
    return {
        "manufacturers": manufacturers,
        "total": len(manufacturers)
    }


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

    manufacturer = CollectorManufacturerService.create(db, current_user.id, body.dict())
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
