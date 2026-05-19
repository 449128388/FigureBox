"""
trade_records.py - 交易记录接口

功能说明：
- 提供交易记录相关的API端点
- 获取交易流水、月度统计、盈亏分析
- 支持按类型、年份、月份筛选

API端点：
- GET /dashboard: 获取交易记录数据

依赖：
- fastapi.APIRouter
- sqlalchemy.orm.Session
- app.services.trade_records_service

创建时间: 2026-05-18
作者: FigureBox Team
"""

from datetime import date
from typing import Dict, Any, List, Optional
from fastapi import APIRouter, Depends, Request, Response, Query
from sqlalchemy.orm import Session
from calendar import monthrange

from app.models.database import get_db
from app.models.user import User
from app.api.users import get_current_user
from app.services.dashboard_service.trade_records_service import (
    MonthlyStatsService,
    TransactionQueryService,
    TradeProfitAnalysisService
)

router = APIRouter()


@router.get("/dashboard")
async def get_trade_records(
    request: Request,
    response: Response,
    year: Optional[int] = Query(None, description="查询年份，默认为当前年份"),
    month: Optional[int] = Query(None, description="查询月份，默认为当前月份"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    获取交易记录数据

    返回交易流水、月度统计、盈亏分析等数据
    支持按指定年月查询历史数据
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

    # 获取交易流水
    transactions = TransactionQueryService.get_transactions(db, user_id)

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
        }
    }
