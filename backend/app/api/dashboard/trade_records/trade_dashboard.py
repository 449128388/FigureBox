"""
trade_dashboard.py - 交易模块-大盘统计子路由

功能说明：
- 提供交易记录大板块相关 API 端点（按业务边界拆分自原 trade_records.py）
- 包含 4 个聚合统计端点：交易大盘、月度统计、交易流水、盈亏分析
- 全部委托给 trade_records_service 子服务，业务逻辑零内联

API端点：
- GET /dashboard       交易大盘（聚合月度统计 + 交易流水 + 盈亏分析）
- GET /monthly-stats   月度汇总统计
- GET /transactions    交易明细列表（含高级筛选）
- GET /profit-analysis 盈亏分析（年度）

依赖：
- fastapi.APIRouter
- app.services.dashboard_service.trade_records_service
- app.api.users.get_current_user

创建时间: 2026-08-04（从 trade_records.py 拆分）
作者: FigureBox Team
"""

from datetime import date
from typing import Optional
from fastapi import APIRouter, Depends, Request, Response, Query
from sqlalchemy.orm import Session
from calendar import monthrange

from app.models.database import get_db
from app.models.user import User
from app.api.users import get_current_user
from app.services.dashboard_service.trade_records_service import (
    MonthlyStatsService,
    TransactionQueryService,
    TradeProfitAnalysisService,
    TradeFilterService,
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
