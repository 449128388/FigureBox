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
    BuyOrderService,
    SellOrderService,
    TradeFilterService,
    PayBalanceService,
    CancelOrderService
)

router = APIRouter()


@router.get("/dashboard")
async def get_trade_records(
    request: Request,
    response: Response,
    year: Optional[int] = Query(None, description="查询年份，默认为当前年份"),
    month: Optional[int] = Query(None, description="查询月份，默认为当前月份"),
    filter_type: Optional[str] = Query("all", description="筛选类型: all-全部, income-收入, expense-支出, fee-费用"),
    # 高级筛选参数
    time_type: Optional[str] = Query("last30days", description="时间类型: last7days/last30days/thisMonth/lastMonth/thisYear/custom"),
    date_start: Optional[str] = Query(None, description="自定义开始日期 (YYYY-MM-DD)"),
    date_end: Optional[str] = Query(None, description="自定义结束日期 (YYYY-MM-DD)"),
    figure_ids: Optional[str] = Query(None, description="手办ID列表，逗号分隔"),
    platforms: Optional[str] = Query(None, description="平台列表，逗号分隔"),
    status_list: Optional[str] = Query(None, description="状态列表，逗号分隔"),
    min_amount: Optional[float] = Query(None, description="最小金额"),
    max_amount: Optional[float] = Query(None, description="最大金额"),
    keyword: Optional[str] = Query(None, description="关键词搜索"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    获取交易记录数据

    返回交易流水、月度统计、盈亏分析等数据
    支持按指定年月查询历史数据
    支持按类型筛选（全部/收入/支出/费用）
    支持高级筛选（时间范围、手办、平台、状态、金额、关键词）
    """
    user_id = current_user.id

    # 使用传入的年月参数或默认为当前年月
    query_year = year if year else date.today().year
    query_month = month if month else date.today().month

    # 计算月份起止时间（自然月）
    month_start = date(query_year, query_month, 1)
    _, last_day = monthrange(query_year, query_month)
    month_end = date(query_year, query_month, last_day)

    # 获取指定月份交易统计
    monthly_stats = MonthlyStatsService.get_monthly_stats(
        db, user_id, month_start, month_end
    )

    # 构建高级筛选参数
    advanced_filters = {
        "filterType": filter_type,
        "timeType": time_type,
        "dateRange": [date_start, date_end] if date_start and date_end else [],
        "figureIds": [int(x) for x in figure_ids.split(",") if x] if figure_ids else [],
        "platforms": platforms.split(",") if platforms else [],
        "statusList": status_list.split(",") if status_list else [],
        "minAmount": min_amount,
        "maxAmount": max_amount,
        "keyword": keyword
    }

    # 获取交易流水（支持基础筛选）
    transactions = TransactionQueryService.get_transactions(db, user_id, filter_type)

    # 应用高级筛选
    if any([
        time_type != "last30days",
        figure_ids,
        platforms,
        status_list,
        min_amount is not None,
        max_amount is not None,
        keyword
    ]):
        transactions = TradeFilterService.apply_filters_to_transactions(
            transactions, advanced_filters
        )

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
            "type": filter_type,
            "advanced": advanced_filters
        }
    }


@router.get("/monthly-stats")
async def get_monthly_stats(
    request: Request,
    response: Response,
    year: Optional[int] = Query(None, description="查询年份，默认为当前年份"),
    month: Optional[int] = Query(None, description="查询月份，默认为当前月份"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    获取月度汇总统计

    返回指定月份的交易统计数据：
    - 买入统计（订单数、总金额）
    - 卖出统计（订单数、总金额）
    - 费用统计
    - 净收支

    支持按指定年月查询历史数据
    """
    user_id = current_user.id

    # 使用传入的年月参数或默认为当前年月
    query_year = year if year else date.today().year
    query_month = month if month else date.today().month

    # 计算月份起止时间（自然月）
    month_start = date(query_year, query_month, 1)
    _, last_day = monthrange(query_year, query_month)
    month_end = date(query_year, query_month, last_day)

    # 获取指定月份交易统计
    monthly_stats = MonthlyStatsService.get_monthly_stats(
        db, user_id, month_start, month_end
    )

    return {
        "monthly_stats": monthly_stats,
        "query_month": {
            "year": query_year,
            "month": query_month
        }
    }


@router.get("/transactions")
async def get_transactions(
    request: Request,
    response: Response,
    year: Optional[int] = Query(None, description="查询年份，默认为当前年份"),
    month: Optional[int] = Query(None, description="查询月份，默认为当前月份"),
    filter_type: Optional[str] = Query("all", description="筛选类型: all-全部, income-收入, expense-支出, fee-费用"),
    # 高级筛选参数
    time_type: Optional[str] = Query("last30days", description="时间类型: last7days/last30days/thisMonth/lastMonth/thisYear/custom"),
    date_start: Optional[str] = Query(None, description="自定义开始日期 (YYYY-MM-DD)"),
    date_end: Optional[str] = Query(None, description="自定义结束日期 (YYYY-MM-DD)"),
    figure_ids: Optional[str] = Query(None, description="手办ID列表，逗号分隔"),
    platforms: Optional[str] = Query(None, description="平台列表，逗号分隔"),
    status_list: Optional[str] = Query(None, description="状态列表，逗号分隔"),
    min_amount: Optional[float] = Query(None, description="最小金额"),
    max_amount: Optional[float] = Query(None, description="最大金额"),
    keyword: Optional[str] = Query(None, description="关键词搜索"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    获取交易明细列表

    返回交易流水记录列表：
    - 买入交易记录
    - 卖出交易记录
    - 费用流水记录

    支持按类型筛选（全部/收入/支出/费用）
    支持高级筛选（时间范围、手办、平台、状态、金额、关键词）
    """
    user_id = current_user.id

    # 使用传入的年月参数或默认为当前年月
    query_year = year if year else date.today().year
    query_month = month if month else date.today().month

    # 构建高级筛选参数
    advanced_filters = {
        "filterType": filter_type,
        "timeType": time_type,
        "dateRange": [date_start, date_end] if date_start and date_end else [],
        "figureIds": [int(x) for x in figure_ids.split(",") if x] if figure_ids else [],
        "platforms": platforms.split(",") if platforms else [],
        "statusList": status_list.split(",") if status_list else [],
        "minAmount": min_amount,
        "maxAmount": max_amount,
        "keyword": keyword
    }

    # 获取交易流水（支持基础筛选）
    transactions = TransactionQueryService.get_transactions(db, user_id, filter_type)

    # 应用高级筛选
    if any([
        time_type != "last30days",
        figure_ids,
        platforms,
        status_list,
        min_amount is not None,
        max_amount is not None,
        keyword
    ]):
        transactions = TradeFilterService.apply_filters_to_transactions(
            transactions, advanced_filters
        )

    return {
        "transactions": transactions,
        "query_month": {
            "year": query_year,
            "month": query_month
        },
        "filter": {
            "type": filter_type,
            "advanced": advanced_filters
        }
    }


@router.get("/profit-analysis")
async def get_profit_analysis(
    request: Request,
    response: Response,
    year: Optional[int] = Query(None, description="查询年份，默认为当前年份"),
    month: Optional[int] = Query(None, description="查询月份，默认为当前月份"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    获取利润分析数据

    返回年度盈亏分析数据：
    - 年度总览（总买入、总卖出、净利润）
    - 月度趋势（各月买入/卖出/净利润）
    - 图表数据

    支持按指定年份查询
    """
    user_id = current_user.id

    # 使用传入的年份参数或默认为当前年份
    query_year = year if year else date.today().year
    query_month = month if month else date.today().month

    # 获取盈亏分析
    profit_analysis = TradeProfitAnalysisService.get_profit_analysis(
        db, user_id, query_year
    )

    return {
        "profit_analysis": profit_analysis,
        "query_month": {
            "year": query_year,
            "month": query_month
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
    - 订单状态为"已支付"（已付定金，待付尾款）
    - 尾款金额 > 0
    - 尾款到期日 <= 今天 + 7天

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


@router.get("/cancelable-orders")
async def get_cancelable_orders(
    request: Request,
    response: Response,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    获取可取消订单列表

    返回当前用户可取消的订单列表：
    - 状态为'待付尾款'、'已付定金'、'待发货'的订单
    - 包含订单基本信息、已支付金额、是否已入库等

    Returns:
        可取消订单列表
    """
    user_id = current_user.id
    orders = CancelOrderService.get_cancelable_orders(db, user_id)
    return {"orders": orders, "total": len(orders)}


@router.get("/cancelable-orders/{order_id}")
async def get_order_cancel_detail(
    request: Request,
    response: Response,
    order_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    获取订单取消详情

    用于撤单确认弹窗展示：
    - 订单基本信息
    - 已支付金额
    - 是否已入库
    - 退款选项

    Args:
        order_id: 订单ID

    Returns:
        订单取消详情
    """
    user_id = current_user.id
    result = CancelOrderService.get_order_cancel_detail(db, user_id, order_id)

    if "error" in result:
        response.status_code = 404
        return {"error": result["error"]}

    return result


@router.post("/cancel-order/{order_id}")
async def cancel_order(
    request: Request,
    response: Response,
    order_id: int,
    cancel_data: Dict[str, Any],
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    取消订单

    业务流程：
    1. 验证订单状态（必须为可取消状态）
    2. 如果已入库，回滚库存
    3. 如果需要退款，创建退款交易记录
    4. 更新订单状态为"已取消"
    5. 创建订单状态变更记录

    请求参数：
    - refund: 是否退款（bool，默认true）
    - refund_amount: 退款金额（选填，默认为已支付金额）
    - refund_method: 退款方式（选填，默认"原路退回"）
    - reason: 取消原因（选填）

    Returns:
        取消结果，包含退款金额、库存回滚状态等
    """
    user_id = current_user.id

    # 调用服务取消订单
    result = CancelOrderService.cancel_order(db, user_id, order_id, cancel_data)

    if not result.get("success"):
        response.status_code = 400
        return {"error": result.get("error", "取消订单失败")}

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
