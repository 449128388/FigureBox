"""
settings_annual_limit.py - 年度限额配置层

功能说明：
- 提供年度手办消费上限配置相关API端点
- 包括获取和更新年度消费上限

API端点：
- GET /settings/annual-limit: 获取用户年度手办消费上限
- POST /settings/annual-limit: 更新用户年度手办消费上限

依赖：
- fastapi.APIRouter, HTTPException
- sqlalchemy.orm.Session
- app.models.asset.UserSettings
- pydantic.BaseModel

创建时间: 2026-05-18
作者: FigureBox Team
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.models.database import get_db
from app.models.asset import UserSettings
from app.models.user import User
from app.api.users import get_current_user

router = APIRouter()


class AnnualLimitSetting(BaseModel):
    """年度消费上限设置请求模型"""
    limit: float


@router.get("/settings/annual-limit")
def get_annual_spending_limit(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    获取用户年度手办消费上限
    
    返回当前用户设置的年度消费上限金额
    """
    settings = db.query(UserSettings).filter(
        UserSettings.user_id == current_user.id
    ).first()
    
    if not settings:
        return {
            "annual_spending_limit": 0,
            "message": "未设置年度消费上限"
        }
    
    return {
        "annual_spending_limit": settings.annual_spending_limit,
        "updated_at": settings.updated_at
    }


@router.post("/settings/annual-limit")
def update_annual_spending_limit(
    request: AnnualLimitSetting,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    更新用户年度手办消费上限
    
    设置用户的年度手办消费上限金额
    """
    limit = request.limit
    if limit < 0:
        raise HTTPException(status_code=400, detail="消费上限不能为负数")
    
    settings = db.query(UserSettings).filter(
        UserSettings.user_id == current_user.id
    ).first()
    
    if settings:
        settings.annual_spending_limit = limit
    else:
        settings = UserSettings(
            user_id=current_user.id,
            annual_spending_limit=limit
        )
        db.add(settings)
    
    db.commit()
    db.refresh(settings)
    
    return {
        "annual_spending_limit": settings.annual_spending_limit,
        "updated_at": settings.updated_at,
        "message": "年度消费上限设置成功"
    }
