"""
home.py - 首页 API 路由

提供首页所需的三个端点：
- GET /activities: 最新动态
- GET /top-holdings: 持仓市值 Top N
- GET /summary: 首页概览摘要
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.models.database import get_db
from app.api.users import get_current_user
from app.models.user import User
from app.services.home_service.home_service import HomeService

router = APIRouter()


@router.get("/activities")
def get_activities(
    limit: int = 10,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return HomeService.get_activities(db, current_user.id, limit)


@router.get("/top-holdings")
def get_top_holdings(
    limit: int = 5,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return HomeService.get_top_holdings(db, current_user.id, limit)


@router.get("/summary")
def get_summary(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return HomeService.get_summary(db, current_user.id)
