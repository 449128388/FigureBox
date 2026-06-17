"""
tags.py - 收藏家看板标签云接口

API端点：
- GET /collector/tags: 获取多维分组筛选标签

职责：
- 展示分类标签（海景房、破发区、待补款、已出坑）
- 支持按标签筛选藏品
"""

from fastapi import APIRouter, Depends, Request, Response
from sqlalchemy.orm import Session

from app.models.database import get_db
from app.models.order import Order
from app.models.figure import Figure
from app.models.user import User
from app.models.sold_order import SoldOrder
from app.api.users import get_current_user
from app.api.collector.dashboard import get_valid_orders, get_figures_with_valid_orders, check_token_refresh

router = APIRouter()


def get_image_url(figure):
    """从images列表中获取第一张图片URL"""
    if figure.images and isinstance(figure.images, list) and len(figure.images) > 0:
        return figure.images[0]
    return ""


@router.get("/tags")
async def get_collector_tags(
    request: Request,
    response: Response,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    获取收藏家看板标签云数据
    
    返回：
    - 标签列表（包含name、count）
    - 标签包括：海景房、破发区、待补款、已出坑
    """
    # 获取用户的所有有效订单
    valid_orders = get_valid_orders(db, current_user.id)
    
    # 获取有有效订单的手办列表
    figures = get_figures_with_valid_orders(db, valid_orders)
    
    # 获取已转卖的手办
    sold_orders = db.query(SoldOrder).filter(
        SoldOrder.user_id == current_user.id,
        SoldOrder.is_active == True
    ).all()

    # 计算各类标签数量
    # 1. 海景房（涨幅 >= 50%）
    sea_view_count = 0
    # 2. 破发区（涨幅 < 0%）
    loss_count = 0
    
    for fig in figures:
        cost_price = fig.average_purchase_price or fig.price or 0
        current_price = fig.market_price or fig.price or 0
        
        if cost_price > 0:
            profit_percentage = ((current_price - cost_price) / cost_price) * 100
            if profit_percentage >= 50:
                sea_view_count += 1
            elif profit_percentage < 0:
                loss_count += 1

    # 3. 待补款
    pending_payment_count = len([o for o in valid_orders if o.status == "待补款"])
    
    # 4. 已出坑（已转卖）
    sold_count = len(sold_orders)

    # 构建标签云数据
    tags = [
        {"name": "海景房", "count": sea_view_count},
        {"name": "破发区", "count": loss_count},
        {"name": "待补款", "count": pending_payment_count},
        {"name": "已出坑", "count": sold_count}
    ]

    # 检查token续期
    check_token_refresh(request, response)

    return {
        "tags": tags
    }
