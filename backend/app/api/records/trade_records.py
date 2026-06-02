"""
trade_records.py - 交易记录接口

功能说明：
- 提供交易记录相关的API端点
- 获取交易流水、月度统计、盈亏分析
- 支持按类型、年份、月份筛选
- 支持账单导出功能

API端点：
- GET /dashboard: 获取交易记录数据
- GET /export: 导出交易账单

依赖：
- fastapi.APIRouter
- sqlalchemy.orm.Session
- app.services.trade_records_service

创建时间: 2026-05-18
作者: FigureBox Team
"""

import io
from datetime import date
from typing import Dict, Any, List, Optional
from fastapi import APIRouter, Depends, Request, Response, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from calendar import monthrange

from app.models.database import get_db
from app.models.user import User
from app.api.users import get_current_user
from app.services.dashboard_service.trade_records_service import (
    MonthlyStatsService,
    TransactionQueryService,
    TradeProfitAnalysisService,
    BillExportService,
    BuyOrderService
)

router = APIRouter()


@router.get("/dashboard")
async def get_trade_records(
    request: Request,
    response: Response,
    year: Optional[int] = Query(None, description="查询年份，默认为当前年份"),
    month: Optional[int] = Query(None, description="查询月份，默认为当前月份"),
    filter_type: Optional[str] = Query("all", description="筛选类型: all-全部, income-收入, expense-支出, fee-费用"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    获取交易记录数据

    返回交易流水、月度统计、盈亏分析等数据
    支持按指定年月查询历史数据
    支持按类型筛选（全部/收入/支出/费用）
    """
    user_id = current_user.id

    # 使用传入的年月参数或默认为当前年月
    query_year = year if year else date.today().year
    query_month = month if month else date.today().month

    # 计算月份起止时间（自然月）
    # 起始时间：当月1日 00:00:00
    month_start = date(query_year, query_month, 1)
    # 结束时间：当月最后一日 23:59:59（用下月1日前一天表示）
    _, last_day = monthrange(query_year, query_month)
    month_end = date(query_year, query_month, last_day)

    # 获取指定月份交易统计
    monthly_stats = MonthlyStatsService.get_monthly_stats(
        db, user_id, month_start, month_end
    )

    # 获取交易流水（支持筛选）
    transactions = TransactionQueryService.get_transactions(db, user_id, filter_type)

    # 获取盈亏分析
    profit_analysis = TradeProfitAnalysisService.get_profit_analysis(
        db, user_id, query_year
    )

    return {
        "monthly_stats": monthly_stats,
        "transactions": transactions,
        "profit_analysis": profit_analysis,
        "query_month": {
            "year": query_year,
            "month": query_month
        },
        "filter": {
            "type": filter_type
        }
    }


@router.get("/export")
async def export_trade_bill(
    request: Request,
    response: Response,
    range: str = Query("current", description="导出范围: current-当前月份, all-全部历史"),
    format: str = Query("xlsx", description="文件格式: xlsx-Excel, csv-CSV"),
    year: Optional[int] = Query(None, description="年份（当range=current时必填）"),
    month: Optional[int] = Query(None, description="月份（当range=current时必填）"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    导出交易账单

    支持导出当前月份或全部历史交易记录
    支持Excel(.xlsx)或CSV格式
    """
    user_id = current_user.id

    # 生成文件内容
    file_content = BillExportService.export_bill(
        db=db,
        user_id=user_id,
        export_range=range,
        year=year,
        month=month,
        file_format=format
    )

    # 设置文件名
    if range == "current" and year and month:
        filename = f"交易账单_{year}年{month}月.{format}"
    else:
        filename = f"交易账单_全部历史.{format}"

    # 设置响应头
    media_type = (
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        if format == "xlsx"
        else "text/csv; charset=utf-8"
    )

    return StreamingResponse(
        io.BytesIO(file_content),
        media_type=media_type,
        headers={
            "Content-Disposition": f"attachment; filename={filename.encode('utf-8').decode('latin-1')}"
        }
    )


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
