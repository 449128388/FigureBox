"""
trade_sell_order.py - 交易模块-卖出订单子路由

功能说明：
- 提供卖出订单相关 API 端点（按业务边界拆分自原 trade_records.py）
- 包含 3 个端点：详情查询、备注更新、物流更新
- 全部委托给 trade_records_service.sell_order_service，零业务内联

API端点：
- GET /sell-order/{sold_order_id}              获取卖出订单详情
- PUT /sell-order/{sold_order_id}/remarks      更新卖出订单备注
- PUT /sell-order/{sold_order_id}/logistics    更新卖出订单物流

依赖：
- fastapi.APIRouter
- app.services.dashboard_service.trade_records_service.SellOrderService
- app.api.users.get_current_user

创建时间: 2026-08-04（从 trade_records.py 拆分）
作者: FigureBox Team
"""

from typing import Dict
from fastapi import APIRouter, Depends, Request, Response
from sqlalchemy.orm import Session

from app.models.database import get_db
from app.models.user import User
from app.api.users import get_current_user
from app.services.dashboard_service.trade_records_service import SellOrderService

router = APIRouter()


@router.get("/sell-order/{sold_order_id}")
async def get_sell_order_detail(
    request: Request,
    response: Response,
    sold_order_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    获取卖出订单详情

    返回卖出订单的完整信息，包括：
    - 头部信息（订单号）
    - 手办信息
    - 订单信息（平台、成交时间、状态等）
    - 收款明细（卖出价、运费、手续费、实到账）
    - 盈亏信息（成本、净利润、利润率）
    - 物流信息
    - 买家信息
    - 备注

    Args:
        sold_order_id: 卖出订单ID

    Returns:
        订单详情数据
    """
    user_id = current_user.id

    # 获取订单详情
    order_detail = SellOrderService.get_order_detail(db, user_id, sold_order_id)

    if "error" in order_detail:
        response.status_code = 404
        return {"error": order_detail["error"]}

    return {
        "order": order_detail
    }


@router.put("/sell-order/{sold_order_id}/remarks")
async def update_sell_order_remarks(
    request: Request,
    response: Response,
    sold_order_id: int,
    remarks_data: Dict[str, str],
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    更新卖出订单备注

    Args:
        sold_order_id: 卖出订单ID
        remarks_data: {"remarks": "新备注内容"}

    Returns:
        更新结果
    """
    user_id = current_user.id
    remarks = remarks_data.get("remarks", "")

    result = SellOrderService.update_remarks(db, user_id, sold_order_id, remarks)

    if not result.get("success"):
        response.status_code = 400
        return {"error": result.get("error", "更新失败")}

    return result


@router.put("/sell-order/{sold_order_id}/logistics")
async def update_sell_order_logistics(
    request: Request,
    response: Response,
    sold_order_id: int,
    logistics_data: Dict[str, str],
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    更新卖出订单物流信息

    Args:
        sold_order_id: 卖出订单ID
        logistics_data: {"tracking_number": "快递单号"}

    Returns:
        更新结果
    """
    user_id = current_user.id
    tracking_number = logistics_data.get("tracking_number", "")

    if not tracking_number:
        response.status_code = 400
        return {"error": "快递单号不能为空"}

    result = SellOrderService.update_logistics(db, user_id, sold_order_id, tracking_number)

    if not result.get("success"):
        response.status_code = 400
        return {"error": result.get("error", "更新失败")}

    return result
