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
from datetime import datetime, timedelta
from sqlalchemy import func, extract

from app.models.database import get_db
from app.models.order import Order
from app.models.figure import Figure
from app.models.user import User
from app.models.sold_order import SoldOrder
from app.models.asset import AssetTransaction
from app.api.users import get_current_user

router = APIRouter()


def get_valid_orders(db: Session, user_id: int):
    """获取用户的所有有效订单（排除已取消状态）"""
    return db.query(Order).filter(
        Order.user_id == user_id,
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
    - 核心指标统计（藏品总数、本月新入柜、已出藏品）
    - 高价值藏品列表
    - 标签云数据
    - 动态流
    """
    # 获取用户的所有有效订单
    valid_orders = get_valid_orders(db, current_user.id)
    
    # 获取有有效订单的手办列表
    figures = get_figures_with_valid_orders(db, valid_orders)
    
    # 获取当前年月
    now = datetime.now()
    current_year = now.year
    current_month = now.month

    # ========== 左卡片：藏品总数 ==========
    # 当前仓库里实际有多少体手办
    total_collection = len(figures)
    
    # 涉及多少个不同作品（work）和手办制造商（manufacturer）
    unique_works = set(fig.work for fig in figures if fig.work)
    unique_manufacturers = set(fig.manufacturer for fig in figures if fig.manufacturer)
    
    # ========== 中卡片：本月新入柜 ==========
    # 本月内完成入库的手办数量（以 asset_transactions 的入库时间为准）
    current_month_start = datetime(current_year, current_month, 1)
    current_month_end = datetime(current_year, current_month + 1, 1) if current_month < 12 else datetime(current_year + 1, 1, 1)
    
    this_month_transactions = db.query(AssetTransaction).filter(
        AssetTransaction.user_id == current_user.id,
        AssetTransaction.transaction_type == 'buy',
        AssetTransaction.transaction_date >= current_month_start,
        AssetTransaction.transaction_date < current_month_end,
        AssetTransaction.is_active == True
    ).order_by(AssetTransaction.transaction_date.desc()).all()
    
    this_month_count = len(this_month_transactions)
    
    # 取本月入库的最近3只手办名称
    recent_figures = []
    for trans in this_month_transactions[:3]:
        if trans.figure and trans.figure.name:
            recent_figures.append(trans.figure.name)
    recent_figures_text = ' / '.join(recent_figures) if recent_figures else '暂无新入库'
    
    # ========== 右卡片：已出藏品 ==========
    # 历史上累计卖出的手办总件数
    sold_orders = db.query(SoldOrder).filter(
        SoldOrder.user_id == current_user.id,
        SoldOrder.is_active == True
    ).all()
    
    total_sold_count = len(sold_orders)
    
    # 计算陪伴时长（陪伴时长 = 卖出日期 - 首次入库日期）
    total_companion_days = 0
    for sold_order in sold_orders:
        if sold_order.created_at and sold_order.figure_id:
            # 查找该手办的首次入库日期（最早的买入交易）
            first_transaction = db.query(AssetTransaction).filter(
                AssetTransaction.user_id == current_user.id,
                AssetTransaction.figure_id == sold_order.figure_id,
                AssetTransaction.transaction_type == 'buy',
                AssetTransaction.is_active == True
            ).order_by(AssetTransaction.transaction_date.asc()).first()
            
            if first_transaction and first_transaction.transaction_date:
                companion_days = (sold_order.created_at - first_transaction.transaction_date).days
                if companion_days > 0:
                    total_companion_days += companion_days
    
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

            # 获取第一张图片
            image_url = ""
            if fig.images and isinstance(fig.images, list) and len(fig.images) > 0:
                image_url = fig.images[0]

            valuable_items.append({
                "id": fig.id,
                "name": fig.name,
                "image": image_url,
                "profit": round(profit, 2),
                "status": status
            })

    # 添加已转卖的手办
    for sold_order in sold_orders:
        if sold_order.figure:
            # 获取第一张图片
            image_url = ""
            if sold_order.figure.images and isinstance(sold_order.figure.images, list) and len(sold_order.figure.images) > 0:
                image_url = sold_order.figure.images[0]

            valuable_items.append({
                "id": sold_order.figure.id,
                "name": sold_order.figure.name,
                "image": image_url,
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
        "summary": {
            "total_collection": total_collection,
            "unique_works": len(unique_works),
            "unique_manufacturers": len(unique_manufacturers),
            "this_month_count": this_month_count,
            "recent_figures": recent_figures_text,
            "total_sold_count": total_sold_count,
            "total_companion_days": total_companion_days
        },
        "valuable_items": valuable_items[:10],
        "tags": tags,
        "activities": activities
    }
