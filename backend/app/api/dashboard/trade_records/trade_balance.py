"""
trade_balance.py - 交易模块-尾款支付子路由

功能说明：
- 提供尾款支付相关 API 端点（按业务边界拆分自原 trade_records.py）
- 包含 3 个端点：待补款订单列表、待补款订单详情、尾款支付
- 全部委托给 trade_records_service.pay_balance_service，零业务内联

API端点：
- GET  /pending-balance-orders               获取待补款订单列表
- GET  /pending-balance-orders/{order_id}    获取待补款订单详情
- POST /pay-balance/{order_id}               支付尾款

依赖：
- fastapi.APIRouter
- app.services.dashboard_service.trade_records_service.PayBalanceService
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
from app.services.dashboard_service.trade_records_service import PayBalanceService

router = APIRouter()


@router.get("/pending-balance-orders")
async def get_pending_balance_orders(
    request: Request,
    response: Response,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    获取待补款订单列表

    返回当前用户需要支付尾款的订单列表
    过滤条件：
    - 订单状态为"未支付"（待付尾款）
    - 尾款金额 > 0
    - 展示全部需要支付尾款的数据，不限制时间范围

    排序规则：
    - 逾期订单置顶（标红）
    - 按到期日升序排列

    Returns:
        待补款订单列表，包含订单ID、手办信息、尾款金额、到期日等
    """
    user_id = current_user.id

    # 调用服务获取待补款订单列表
    orders = PayBalanceService.get_pending_balance_orders(db, user_id)

    return {
        "orders": orders,
        "total": len(orders)
    }


@router.get("/pending-balance-orders/{order_id}")
async def get_pending_balance_order_detail(
    request: Request,
    response: Response,
    order_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    获取待补款订单详情

    Args:
        order_id: 订单ID

    Returns:
        订单支付详情，包含尾款金额、到期日等
    """
    user_id = current_user.id

    # 调用服务获取订单详情
    result = PayBalanceService.get_order_payment_detail(db, user_id, order_id)

    if "error" in result:
        response.status_code = 404
        return {"error": result["error"]}

    return result


@router.post("/pay-balance/{order_id}")
async def pay_balance(
    request: Request,
    response: Response,
    order_id: int,
    payment_data: Dict[str, Any],
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    支付尾款

    业务流程：
    1. 验证订单状态（必须为"已支付"）
    2. 创建尾款交易记录
    3. 更新订单状态为"已完成"
    4. 创建资产交易记录（入库）
    5. 更新手办平均入手价格

    请求参数：
    - payment_method: 支付方式（选填，默认"支付宝"）
    - payment_date: 支付时间（选填，默认当前时间，格式：YYYY-MM-DD HH:MM）
    - amount: 本次支付金额（选填，默认为剩余尾款）

    Returns:
        支付结果，包含订单ID、支付金额等
    """
    user_id = current_user.id

    # 调用服务支付尾款
    result = PayBalanceService.pay_balance(db, user_id, order_id, payment_data)

    if not result.get("success"):
        response.status_code = 400
        return {"error": result.get("error", "支付尾款失败")}

    return result
