"""
dashboard.py - 行情看板业务层

功能说明：
- 提供行情看板相关API端点
- 包括塑料小人指数(HPI)、K线技术指标、板块排行、自选股、智能投研等

API端点：
- GET /dashboard: 获取行情看板数据

依赖：
- fastapi.APIRouter
- sqlalchemy.orm.Session
- app.services.dashboard_service.market_service

HPI与其他模块互动：
- HPI → 资产看板：提供"大盘基准"用于"跑赢大盘"计算
- 资产看板 → HPI：持仓交易数据贡献到成交量统计
- HPI → 持仓卡片：提供涨跌状态判定标准
- 交易 → HPI：卖出成交计入成交量
- HPI → 交易决策：市场冷热信号指导买卖
- HPI → 预警：单日跌幅>5%触发系统性风险预警

创建时间: 2026-05-18
作者: FigureBox Team
"""

from fastapi import APIRouter, Depends, Request, Response
from sqlalchemy.orm import Session

from app.models.database import get_db
from app.models.user import User
from app.api.users import get_current_user
from app.services.dashboard_service.market_service.hpi_service import HPIService
from app.services.dashboard_service.market_service.sector_service import SectorService
from app.services.dashboard_service.market_service.watchlist_service import WatchlistService
from app.services.dashboard_service.market_service.research_service import ResearchService

router = APIRouter()


def check_token_refresh(request, response):
    """检查是否需要返回新的token（自动续期）"""
    if hasattr(request.state, 'new_token'):
        response.headers['X-New-Token'] = request.state.new_token


@router.get("/dashboard")
async def get_market_dashboard(
    request: Request,
    response: Response,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    获取行情看板数据

    返回市场行情相关数据，包括：
    - 塑料小人指数（HPI）：全市场/全品类手办综合价格指数（成交量加权法）
    - K线技术指标（MACD、RSI）
    - 板块涨幅排行
    - 自选股列表
    - 智能投研报告
    """
    # 计算塑料小人指数(HPI) - 全市场指标（成交量加权法）
    hpi_data = HPIService.calculate_hpi(db)

    # 构建指数数据
    index_data = {
        "value": hpi_data["value"],
        "change": hpi_data["change"],
        "change_percentage": hpi_data["change_percentage"],
        "trend": hpi_data["trend"],
        "volume": hpi_data["volume"],
        "constituent_count": hpi_data["constituent_count"],
        "up_count": hpi_data["up_count"],
        "flat_count": hpi_data["flat_count"],
        "down_count": hpi_data["down_count"],
        "limit_up": hpi_data["limit_up"],
        "limit_down": hpi_data["limit_down"]
    }

    # 构建K线技术指标
    kline_data = {
        "macd": "金叉" if hpi_data["change_percentage"] > 0 else "死叉",
        "rsi": min(70, max(30, 50 + int(hpi_data["change_percentage"] * 2)))
    }

    # 获取板块涨幅排行
    sectors = SectorService.get_sector_performance(db)

    # 获取自选股列表
    watchlist = WatchlistService.get_watchlist(db)

    # 获取智能投研报告
    research_data = ResearchService.get_research_report(db)

    # 检查token续期
    check_token_refresh(request, response)

    return {
        "index": index_data,
        "kline": kline_data,
        "sectors": sectors,
        "watchlist": watchlist,
        "research": research_data
    }
