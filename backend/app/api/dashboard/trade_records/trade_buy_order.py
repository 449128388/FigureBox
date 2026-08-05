"""
trade_buy_order.py - 交易模块-买入订单子路由

功能说明：
- 提供买入订单相关 API 端点（按业务边界拆分自原 trade_records.py）
- 包含 4 个端点：详情查询、备注更新、物流更新、订单创建
- 全部委托给 trade_records_service.buy_order_service，零业务内联

API端点：
- GET  /buy-order/{order_id}               获取买入订单详情
- PUT  /buy-order/{order_id}/remarks       更新买入订单备注
- PUT  /buy-order/{order_id}/logistics     更新买入订单物流
- POST /buy-orders                         创建新的买入订单

依赖：
- fastapi.APIRouter
- app.services.dashboard_service.trade_records_service.BuyOrderService
- app.api.users.get_current_user

创建时间: 2026-08-04（从 trade_records.py 拆分）
作者: FigureBox Team
"""

from typing import Dict, Any
from fastapi import APIRouter, Depends, Request, Response
from sqlalchemy.orm import Session

from app.models.database import get_db
from app.models.user import User
from app.api.users import get_current_user
from app.services.dashboard_service.trade_records_service import BuyOrderService

router = APIRouter()


@router.get("/buy-order/{order_id}")
async def get_buy_order_detail(
    request: Request,
    response: Response,
    order_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    获取买入订单详情

    返回买入订单的完整信息，包括：
    - 订单头部信息（手办名称、平台等）
    - 订单基本信息（订单编号、类型、状态等）
    - 支付明细（全款/定金+尾款）
    - 物流信息
    - 备注
    - 可用操作按钮

    Args:
        order_id: 订单ID

    Returns:
        订单详情数据
    """
    user_id = current_user.id

    # 获取订单详情
    order_detail = BuyOrderService.get_order_detail(db, user_id, order_id)

    if "error" in order_detail:
        response.status_code = 404
        return {"error": order_detail["error"]}

    # 获取可用操作按钮
    status_code = order_detail.get("order_info", {}).get("status_code", "")
    available_actions = BuyOrderService.get_available_actions(status_code)

    return {
        "order": order_detail,
        "actions": available_actions
    }


@router.put("/buy-order/{order_id}/remarks")
async def update_buy_order_remarks(
    request: Request,
    response: Response,
    order_id: int,
    remarks_data: Dict[str, str],
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    更新买入订单备注

    Args:
        order_id: 订单ID
        remarks_data: {"remarks": "新备注内容"}

    Returns:
        更新结果
    """
    user_id = current_user.id
    remarks = remarks_data.get("remarks", "")

    result = BuyOrderService.update_remarks(db, user_id, order_id, remarks)

    if not result.get("success"):
        response.status_code = 400
        return {"error": result.get("error", "更新失败")}

    return result


@router.put("/buy-order/{order_id}/logistics")
async def update_buy_order_logistics(
    request: Request,
    response: Response,
    order_id: int,
    logistics_data: Dict[str, str],
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    更新买入订单物流信息

    Args:
        order_id: 订单ID
        logistics_data: {"tracking_number": "快递单号"}

    Returns:
        更新结果
    """
    user_id = current_user.id
    tracking_number = logistics_data.get("tracking_number", "")

    if not tracking_number:
        response.status_code = 400
        return {"error": "快递单号不能为空"}

    result = BuyOrderService.update_logistics(db, user_id, order_id, tracking_number)

    if not result.get("success"):
        response.status_code = 400
        return {"error": result.get("error", "更新失败")}

    return result


@router.post("/buy-orders")
async def create_buy_order(
    request: Request,
    response: Response,
    order_data: Dict[str, Any],
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    创建新的买入订单

    支持四种业务类型：
    - 预定：定金+尾款模式，需要填写定金、尾款、尾款到期日、出荷日期
    - 全款预定：定金+尾款模式（一次性付清），需要填写定金、尾款、出荷日期
    - 现货：一次性付清，只需填写实付金额
    - 补仓：一次性付清，平台自动设置为"补仓"，备注自动填充

    请求参数：
    - figure_id: 手办ID（必填）
    - quantity: 数量（必填，默认1）
    - platform: 购买平台（必填）
    - order_type: 订单类型（必填：预定/全款预定/现货/补仓）
    - deposit: 定金（预定/全款预定时必填）
    - balance: 尾款（预定/全款预定时必填）
    - payment_due_date: 尾款到期日（预定/全款预定时必填）
    - due_date: 出荷日期（预定/全款预定时必填）
    - total_amount: 实付金额（现货/补仓时必填）
    - tracking_number: 快递单号（选填）
    - logistics_company: 物流公司（选填）
    - remarks: 备注（选填）

    Returns:
        创建结果，包含新订单ID
    """
    user_id = current_user.id

    # 调用服务创建订单
    result = BuyOrderService.create_buy_order(db, user_id, order_data)

    if not result.get("success"):
        response.status_code = 400
        return {"error": result.get("error", "创建订单失败")}

    return result
