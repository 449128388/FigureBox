"""
timeline.py - 收藏家看板收藏历程接口

API端点：
- GET /collector/timeline: 获取时间线动态列表

职责：
- 展示最近5条订单动态
- 包含日期、内容、操作按钮
"""

from fastapi import APIRouter, Depends, Request, Response
from sqlalchemy.orm import Session
from datetime import datetime

from app.models.database import get_db
from app.models.order import Order
from app.models.figure import Figure
from app.models.user import User
from app.api.users import get_current_user
from app.api.collector.dashboard import get_valid_orders, check_token_refresh

router = APIRouter()


@router.get("/timeline")
async def get_collector_timeline(
    request: Request,
    response: Response,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    获取收藏家看板收藏历程数据（时间线动态列表）
    
    返回：
    - 最近5条订单动态
    - 每条包含date、content、actions
    """
    # 获取用户的所有有效订单
    valid_orders = get_valid_orders(db, current_user.id)

    # 构建动态流数据（按创建时间倒序，取最近5条）
    activities = []
    for order in sorted(valid_orders, key=lambda x: x.created_at or datetime.min, reverse=True)[:5]:
        if order.figure:
            activities.append({
                "date": order.created_at.strftime("%Y-%m-%d") if order.created_at else "",
                "content": f"入手{order.figure.name}，等待补款",
                "actions": ["查看详情"]
            })

    # 检查token续期
    check_token_refresh(request, response)

    return {
        "activities": activities
    }
