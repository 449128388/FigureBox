"""
wishlist_stats.py - 愿望清单统计 API
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.models.database import get_db
from app.api.users import get_current_user
from app.models.user import User
from app.services import WishlistStatsService

router = APIRouter()


@router.get("/stats")
def get_wishlist_stats(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    获取愿望清单统计指标

    Returns:
        {
            "total": 愿望总数,
            "releasing_this_month": 本月即将发售,
            "budget_total": 预算合计（CNY）,
            "pending_purchase": 待购数量,
            "status_distribution": 状态分布,
            "top_manufacturers": TOP 厂商,
        }
    """
    return WishlistStatsService.get_stats(db, current_user.id)
