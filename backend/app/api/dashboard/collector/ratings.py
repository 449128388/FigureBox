"""
ratings.py - 收藏柜喜爱度评分接口

API端点：
- GET /collector/ratings: 获取某个收藏柜下所有手办的的喜爱度评分
- POST /collector/ratings: 保存/更新某个手办在当前收藏柜的喜爱度评分

职责：
- 管理用户在每个收藏柜中对每个手办的 1-5 星评分
- 支持 upsert（存在则更新，不存在则创建）
- 用于前端收藏柜详情页面的喜爱度交互
"""

from fastapi import APIRouter, Depends, Request, Response, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.models.database import get_db
from app.models.user import User
from app.models.cabinet_metadata import CabinetRating
from app.api.users import get_current_user

router = APIRouter()


class RatingSaveRequest(BaseModel):
    figure_id: int
    cabinet_type: str
    rating: int


@router.get("/ratings")
async def get_cabinet_ratings(
    request: Request,
    response: Response,
    cabinet_type: str = None,
    figure_ids: str = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    获取收藏柜喜爱度评分

    参数：
    - cabinet_type: 收藏柜类型（可选），如 star/new/fix/out
    - figure_ids: 手办ID列表（可选），用逗号分隔

    返回：
    - ratings: 评分列表，每项包含 figure_id, cabinet_type, rating
    """
    query = db.query(CabinetRating).filter(
        CabinetRating.user_id == current_user.id
    )

    if cabinet_type:
        query = query.filter(CabinetRating.cabinet_type == cabinet_type)

    if figure_ids:
        ids = [int(fid.strip()) for fid in figure_ids.split(',') if fid.strip().isdigit()]
        if ids:
            query = query.filter(CabinetRating.figure_id.in_(ids))

    ratings = query.all()

    return {
        "ratings": [
            {
                "figure_id": r.figure_id,
                "cabinet_type": r.cabinet_type,
                "rating": r.rating
            }
            for r in ratings
        ]
    }


@router.post("/ratings")
async def save_cabinet_rating(
    request: Request,
    response: Response,
    data: RatingSaveRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    保存/更新收藏柜喜爱度评分

    请求体：
    - figure_id: 手办ID
    - cabinet_type: 收藏柜类型
    - rating: 评分值 0-5（0=取消评分）

    说明：
    - 如果已存在评分记录则更新，否则新建
    - rating 范围：0（未评分）或 1-5（星级）
    """
    if data.rating < 0 or data.rating > 5:
        raise HTTPException(status_code=400, detail="评分必须在 0-5 之间")

    # 查询是否已存在评分记录
    existing = db.query(CabinetRating).filter(
        CabinetRating.user_id == current_user.id,
        CabinetRating.figure_id == data.figure_id,
        CabinetRating.cabinet_type == data.cabinet_type
    ).first()

    if existing:
        # 更新现有评分
        existing.rating = data.rating
        db.commit()
        db.refresh(existing)
        return {
            "success": True,
            "message": "评分已更新",
            "rating": {
                "figure_id": existing.figure_id,
                "cabinet_type": existing.cabinet_type,
                "rating": existing.rating
            }
        }
    else:
        # 新建评分记录
        new_rating = CabinetRating(
            user_id=current_user.id,
            figure_id=data.figure_id,
            cabinet_type=data.cabinet_type,
            rating=data.rating
        )
        db.add(new_rating)
        db.commit()
        db.refresh(new_rating)
        return {
            "success": True,
            "message": "评分已保存",
            "rating": {
                "figure_id": new_rating.figure_id,
                "cabinet_type": new_rating.cabinet_type,
                "rating": new_rating.rating
            }
        }
