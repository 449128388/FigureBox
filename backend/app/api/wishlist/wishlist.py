"""
wishlist.py - 愿望清单 CRUD API
"""
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from datetime import date
from pydantic import BaseModel, Field

from app.models.database import get_db
from app.api.users import get_current_user
from app.models.user import User
from app.services import (
    WishlistQueryService,
    WishlistCrudService,
)

router = APIRouter()


# ========== Schemas ==========
class WishlistCreate(BaseModel):
    name: str
    japanese_name: Optional[str] = None
    manufacturer: Optional[str] = None
    scale: Optional[str] = None
    painting: Optional[str] = None
    original_art: Optional[str] = None
    work: Optional[str] = None
    material: Optional[str] = None
    size: Optional[str] = None
    price: float = 0
    currency: str = "CNY"
    market_price: float = 0
    market_currency: str = "CNY"
    release_date: Optional[date] = None
    source_url: Optional[str] = None
    note: Optional[str] = None
    images: Optional[List[str]] = []
    tag_names: Optional[List[str]] = []
    wishlist_status: str = "wish"


class WishlistUpdate(BaseModel):
    name: Optional[str] = None
    japanese_name: Optional[str] = None
    manufacturer: Optional[str] = None
    scale: Optional[str] = None
    painting: Optional[str] = None
    original_art: Optional[str] = None
    work: Optional[str] = None
    material: Optional[str] = None
    size: Optional[str] = None
    price: Optional[float] = None
    currency: Optional[str] = None
    market_price: Optional[float] = None
    market_currency: Optional[str] = None
    release_date: Optional[date] = None
    source_url: Optional[str] = None
    note: Optional[str] = None
    images: Optional[List[str]] = None
    tag_names: Optional[List[str]] = None
    wishlist_status: Optional[str] = None


class StatusChange(BaseModel):
    status: str = Field(..., description="新状态: wish/released/purchased/cancelled")


class MoveToLibrary(BaseModel):
    purchase_type: str = Field("preorder", description="目标 purchase_type: preorder/spot/secondhand")


# ========== Endpoints ==========
@router.get("/")
def list_wishlist(
    skip: int = 0,
    limit: int = 20,
    name: Optional[str] = None,
    status: Optional[str] = None,
    manufacturer: Optional[str] = None,
    release_start: Optional[date] = None,
    release_end: Optional[date] = None,
    tag_names: Optional[List[str]] = Query(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    获取愿望清单列表
    """
    return WishlistQueryService.get_wishlist_list(
        db=db,
        user_id=current_user.id,
        skip=skip,
        limit=limit,
        name=name,
        status=status,
        manufacturer=manufacturer,
        release_start=release_start,
        release_end=release_end,
        tag_names=tag_names,
    )


@router.post("/", status_code=201)
def create_wishlist(
    payload: WishlistCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    创建愿望清单项
    """
    data = payload.dict(exclude_none=False)
    figure = WishlistCrudService.create_wishlist(db, current_user.id, data)
    return WishlistQueryService._figure_to_item(figure)


@router.get("/{figure_id}")
def get_wishlist_detail(
    figure_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    获取愿望清单详情
    """
    item = WishlistQueryService.get_wishlist_detail(db, current_user.id, figure_id)
    if not item:
        raise HTTPException(status_code=404, detail="愿望清单项不存在")
    return item


@router.put("/{figure_id}")
def update_wishlist(
    figure_id: int,
    payload: WishlistUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    更新愿望清单项
    """
    data = payload.dict(exclude_none=True)
    figure = WishlistCrudService.update_wishlist(db, current_user.id, figure_id, data)
    if not figure:
        raise HTTPException(status_code=404, detail="愿望清单项不存在")
    return WishlistQueryService._figure_to_item(figure)


@router.delete("/{figure_id}")
def delete_wishlist(
    figure_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    软删除愿望清单项
    """
    ok = WishlistCrudService.delete_wishlist(db, current_user.id, figure_id)
    if not ok:
        raise HTTPException(status_code=404, detail="愿望清单项不存在")
    return {"success": True}


@router.post("/{figure_id}/status")
def change_status(
    figure_id: int,
    payload: StatusChange,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    状态流转
    """
    figure = WishlistCrudService.change_status(db, current_user.id, figure_id, payload.status)
    if not figure:
        raise HTTPException(status_code=404, detail="愿望清单项不存在")
    return WishlistQueryService._figure_to_item(figure)


@router.post("/{figure_id}/move-to-library")
def move_to_library(
    figure_id: int,
    payload: MoveToLibrary,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    转入手办库
    """
    figure = WishlistCrudService.move_to_library(
        db, current_user.id, figure_id, payload.purchase_type
    )
    if not figure:
        raise HTTPException(status_code=404, detail="愿望清单项不存在")
    return {"success": True, "figure_id": figure.id, "purchase_type": figure.purchase_type}
