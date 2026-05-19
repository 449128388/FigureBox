"""
dashboard.py - 收藏家看板业务层

功能说明：
- 提供收藏家模式看板相关API端点
- 包括收藏统计、高价值藏品、标签云、动态流等

API端点：
- GET /collector/dashboard: 获取收藏家看板数据

依赖：
- fastapi.APIRouter
- sqlalchemy.orm.Session
- app.models.*

创建时间: 2026-05-18
作者: FigureBox Team
"""

from fastapi import APIRouter, Depends, Request, Response
from sqlalchemy.orm import Session
from datetime import datetime

from app.models.database import get_db
from app.models.order import Order
from app.models.figure import Figure
from app.models.user import User
from app.models.sold_order import SoldOrder
from app.api.users import get_current_user

router = APIRouter()


def get_valid_orders(db: Session):
    """获取所有有效订单（排除已取消状态）"""
    return db.query(Order).filter(
        Order.is_active == 1,
        Order.status != "已取消"
    ).all()


def get_figures_with_valid_orders(db: Session, orders):
    """获取有有效订单的手办列表"""
    figure_ids = set(order.figure_id for order in orders)
    if not figure_ids:
        return []
    all_figures = db.query(Figure).all()
    return [fig for fig in all_figures if fig.id in figure_ids]


def check_token_refresh(request, response):
    """检查是否需要返回新的token（自动续期）"""
    if hasattr(request.state, 'new_token'):
        response.headers['X-New-Token'] = request.state.new_token


@router.get("/dashboard")
async def get_collector_dashboard(
    request: Request,
    response: Response,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    获取收藏家模式看板数据
    
    返回收藏家视角的数据，包括：
    - 收藏统计（总投入、现估值、回血额）
    - 高价值藏品列表
    - 标签云数据
    - 动态流
    """
    # 获取所有有效订单
    valid_orders = get_valid_orders(db)
    
    # 获取有有效订单的手办列表
    figures = get_figures_with_valid_orders(db, valid_orders)

    # 计算总投入（基于订单的定金+尾款）
    total_investment = 0.0
    for order in valid_orders:
        deposit = order.deposit or 0
        balance = order.balance or 0
        total_investment += deposit + balance

    # 计算现估值（基于手办市场价）
    total_valuation = sum(
        (fig.market_price or fig.price or 0) * (fig.quantity or 1)
        for fig in figures
    )

    # 计算回血额（基于已出售订单）
    sold_orders = db.query(SoldOrder).filter(
        SoldOrder.user_id == current_user.id,
        SoldOrder.is_active == True
    ).all()
    blood_money = sum(order.sell_price or 0 for order in sold_orders)

    # 构建高价值藏品列表
    valuable_items = []
    for fig in figures:
        cost_price = fig.average_purchase_price or fig.price or 0
        current_price = fig.market_price or fig.price or 0
        quantity = fig.quantity or 1

        if cost_price > 0:
            profit = (current_price - cost_price) * quantity
            profit_percentage = ((current_price - cost_price) / cost_price) * 100

            # 确定状态
            if profit_percentage >= 50:
                status = "海景房"
            elif profit_percentage >= 0:
                status = "小赚"
            else:
                status = "破发"

            valuable_items.append({
                "id": fig.id,
                "name": fig.name,
                "image": fig.image_url or "",
                "profit": round(profit, 2),
                "status": status
            })

    # 添加已转卖的手办
    for sold_order in sold_orders:
        if sold_order.figure:
            valuable_items.append({
                "id": sold_order.figure.id,
                "name": sold_order.figure.name,
                "image": sold_order.figure.image_url or "",
                "status": "已转卖",
                "sold_profit": round(sold_order.net_profit or 0, 2)
            })

    # 构建标签云数据
    tags = [
        {"name": "海景房", "count": len([i for i in valuable_items if i.get("status") == "海景房"])},
        {"name": "破发区", "count": len([i for i in valuable_items if i.get("status") == "破发"])},
        {"name": "待补款", "count": len([o for o in valid_orders if o.status == "待补款"])},
        {"name": "已出坑", "count": len([i for i in valuable_items if i.get("status") == "已转卖"])}
    ]

    # 构建动态流数据
    activities = []
    for order in sorted(valid_orders, key=lambda x: x.order_date or datetime.min, reverse=True)[:5]:
        if order.figure:
            activities.append({
                "date": order.order_date.strftime("%Y-%m-%d") if order.order_date else "",
                "content": f"入手{order.figure.name}，等待补款",
                "actions": ["查看详情"]
            })

    # 检查token续期
    check_token_refresh(request, response)

    return {
        "summary": {
            "total_investment": round(total_investment, 2),
            "total_valuation": round(total_valuation, 2),
            "blood_money": round(blood_money, 2)
        },
        "valuable_items": valuable_items[:10],
        "tags": tags,
        "activities": activities
    }
