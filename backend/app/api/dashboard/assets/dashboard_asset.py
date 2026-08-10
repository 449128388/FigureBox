"""
dashboard_asset.py - 资产看板业务层

功能说明：
- 提供资产看板相关API端点
- 包括资产摘要、盈亏分析、K线数据、持仓分布等

2026-08-06 拆分重构：原 `/dashboard` 单接口返回 10 个顶层字段（含 holdings + 4 个分布 + 30 天 K 线 + 排行榜），
单次响应体过大，前端 Network 看到一次大请求（>40KB）。现按业务领域拆为 5 个独立端点：
- GET /dashboard/summary        资产摘要（总资产/日涨跌/塑料指数/SH+HS300/仓位/本月入手）
- GET /dashboard/profit         盈亏分析（浮动/实现/收益率/年化/最大回撤）
- GET /dashboard/profit-curve   收益曲线 K 线（默认近 30 天）
- GET /dashboard/rankings       涨跌排行榜 Top10
- GET /dashboard/holdings       持仓列表 + 4 个分布（风险/厂商/持有期/分级）
前端用 Promise.all 并发 5 个请求，拼成同结构对象喂给子组件，每个端点独立可缓存。
`POST /dashboard/init-daily-change`（初始化日涨跌基准）保持原样不动。

API端点：
- GET  /dashboard/summary
- GET  /dashboard/profit
- GET  /dashboard/profit-curve
- GET  /dashboard/rankings
- GET  /dashboard/holdings
- POST /dashboard/init-daily-change

依赖：
- fastapi.APIRouter
- sqlalchemy.orm.Session
- app.services.*

创建时间: 2026-05-18
作者: FigureBox Team
"""

from fastapi import APIRouter, Depends, Query, Request, Response
from sqlalchemy.orm import Session
import asyncio
from concurrent.futures import ThreadPoolExecutor

from app.models.database import get_db
from app.models.user import User
from app.api.users import get_current_user
from app.services import IndexService, AssetCalculationService, HoldingAnalysisService
from app.services.dashboard_service.assets_service.profit_analysis_service import ProfitAnalysisService
from app.services.dashboard_service.assets_service.profit_curve_service import ProfitCurveService
from app.services.dashboard_service.assets_service.plastic_index_service import PlasticIndexService
from app.services.dashboard_service.assets_service.asset_core_calculations import (
    TotalAssetsCalculator, PositionCalculator
)
from app.services.dashboard_service.assets_service.daily_change_service import DailyChangeService
from .assets_common import AssetsCommonService

router = APIRouter()


# ============== 内部辅助：用户上下文（避免在 5 个端点里重复拉 valid_orders/figures/total_assets） ==============

def _load_user_context(db: Session, user_id: int):
    """
    加载用户维度的共享数据：有效订单、有订单的手办、总资产、仓位。
    这是 5 个端点都要用到的基础上下文，单独抽出来避免每个端点各自重跑 SQL。
    """
    valid_orders = AssetsCommonService.get_valid_orders(db, user_id)
    figures = AssetsCommonService.get_figures_with_valid_orders(db, valid_orders, user_id)
    total_assets = TotalAssetsCalculator.calculate_by_orders(db, user_id, valid_orders)
    position_info = PositionCalculator.calculate_by_orders(db, user_id, valid_orders)
    return {
        "valid_orders": valid_orders,
        "figures": figures,
        "total_assets": total_assets,
        "position_info": position_info,
    }


def _fetch_index_data_async():
    """
    并行拉取 SH / HS300 指数及其涨跌对比数据。
    复用原 /dashboard 里的 ThreadPoolExecutor + asyncio.gather 模式，0 改动。
    """
    async def fetch():
        from app.models.database import get_db as _get_db

        def get_sh_index():
            s = next(_get_db())
            try:
                return IndexService.get_cached_sh_index(s)
            finally:
                s.close()

        def get_hs300_index():
            s = next(_get_db())
            try:
                return IndexService.get_cached_hs300_index(s)
            finally:
                s.close()

        def get_sh_comparison():
            s = next(_get_db())
            try:
                return IndexService.get_index_comparison_data(s, "sh000001")
            finally:
                s.close()

        def get_hs300_comparison():
            s = next(_get_db())
            try:
                return IndexService.get_index_comparison_data(s, "sh000300")
            finally:
                s.close()

        with ThreadPoolExecutor() as executor:
            loop = asyncio.get_event_loop()
            tasks = [
                loop.run_in_executor(executor, get_sh_index),
                loop.run_in_executor(executor, get_hs300_index),
                loop.run_in_executor(executor, get_sh_comparison),
                loop.run_in_executor(executor, get_hs300_comparison),
            ]
            return await asyncio.gather(*tasks)

    return fetch()


# ============== 端点 1/5：资产摘要 ==============

@router.get("/dashboard/summary")
async def get_asset_dashboard_summary(
    request: Request,
    response: Response,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    资产摘要：总资产、日涨跌、塑料指数、SH/HS300 指数、仓位、本月入手等。
    """
    ctx = _load_user_context(db, current_user.id)
    total_assets = ctx["total_assets"]
    position_info = ctx["position_info"]
    figures = ctx["figures"]

    # 日涨跌
    daily_change_data = DailyChangeService.calculate_daily_change(db, current_user.id, total_assets)
    daily_change = daily_change_data["daily_change"]
    daily_change_percentage = daily_change_data["daily_change_percentage"]
    has_daily_change = daily_change_data["has_daily_change"]
    comparison_date = daily_change_data.get("comparison_date")
    comparison_type = daily_change_data.get("comparison_type")
    days_since_last_update = daily_change_data.get("days_since_last_update")
    show_stale_warning = daily_change_data.get("show_stale_warning", False)
    is_historical_comparison = comparison_type in ["day_before_yesterday", "recent", "stale"]

    # 今日市值缓存（向后兼容）
    AssetCalculationService.save_daily_cache(db, current_user.id, total_assets)

    # 塑料手办指数
    plastic_index_data = PlasticIndexService.calculate_plastic_index(
        db, current_user.id, figures, total_assets
    )
    PlasticIndexService.save_daily_index(db, current_user.id, plastic_index_data)
    plastic_index_comparison = PlasticIndexService.get_index_comparison_data(db, current_user.id)

    # SH / HS300 指数（异步并行）
    sh_index_data, hs300_index_data, sh_index_comparison, hs300_index_comparison = await _fetch_index_data_async()
    sh_index = sh_index_data["current_value"]
    hs300_index = hs300_index_data["current_value"]

    outperform_percentage = AssetCalculationService.calculate_outperform_percentage(
        plastic_index_data["current_value"], sh_index
    )

    # 本月入手数量
    monthly_purchases = ProfitAnalysisService.calculate_monthly_purchases(db, current_user.id)

    summary = {
        "total_market_value": total_assets or 0,
        "daily_change": daily_change,
        "daily_change_percentage": daily_change_percentage,
        "has_daily_change": has_daily_change,
        "comparison_date": comparison_date,
        "comparison_type": comparison_type,
        "days_since_last_update": days_since_last_update,
        "show_stale_warning": show_stale_warning,
        "is_historical_comparison": is_historical_comparison,
        "plastic_index": plastic_index_data["current_value"],
        "plastic_index_comparison": plastic_index_comparison or {
            "current_value": plastic_index_data["current_value"],
            "change_value": plastic_index_data["change_value"],
            "change_percentage": plastic_index_data["change_percentage"],
            "has_history": plastic_index_data["has_history"],
            "trend": plastic_index_data["trend"]
        },
        "sh_index": sh_index,
        "sh_index_comparison": sh_index_comparison,
        "hs300_index": hs300_index,
        "hs300_index_comparison": hs300_index_comparison,
        "outperform_percentage": outperform_percentage,
        "position": position_info["position"],
        "position_percentage": position_info["position_percentage"],
        "position_color": position_info["position_color"],
        "investment_budget": position_info["investment_budget"],
        "invested_cost": position_info["invested_cost"],
        "monthly_purchases": monthly_purchases,
        "has_figures": len(figures) > 0
    }

    AssetsCommonService.check_token_refresh(request, response)
    return {"summary": summary}


# ============== 端点 2/5：盈亏分析 ==============

@router.get("/dashboard/profit")
def get_asset_dashboard_profit(
    request: Request,
    response: Response,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    盈亏分析：浮动盈亏、实现盈亏、总收益率、年化收益率、实现率、最大回撤。
    """
    profit_data = ProfitAnalysisService.get_profit_analysis(db, current_user.id)
    profit = {
        "floating": profit_data["floating"],
        "realized": profit_data["realized"],
        "total_rate": profit_data["total_rate"],
        "annualized_rate": profit_data["annualized_rate"],
        "realization_rate": profit_data["realization_rate"],
        "max_drawdown": profit_data["max_drawdown"]
    }

    AssetsCommonService.check_token_refresh(request, response)
    return {"profit": profit}


# ============== 端点 3/5：收益曲线 ==============

@router.get("/dashboard/profit-curve")
def get_asset_dashboard_profit_curve(
    request: Request,
    response: Response,
    days: int = Query(30, ge=1, le=365, description="曲线天数（1-365）"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    收益曲线 K 线：每日收益 = 当日总市值 - 当日总成本，默认近 30 天。
    """
    kline_data = ProfitCurveService.get_profit_curve_data(db, current_user.id, days=days)

    AssetsCommonService.check_token_refresh(request, response)
    return {"kline_data": kline_data}


# ============== 端点 4/5：涨跌排行榜 ==============

@router.get("/dashboard/rankings")
def get_asset_dashboard_rankings(
    request: Request,
    response: Response,
    limit: int = Query(10, ge=1, le=50, description="Top N"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    涨跌排行：按涨跌幅绝对值降序，取前 N 条。
    """
    ctx = _load_user_context(db, current_user.id)
    figures = ctx["figures"]

    rankings = []
    for fig in figures:
        if fig.price and fig.price > 0 and fig.market_price and fig.market_price > 0:
            change_percentage = ((fig.market_price - fig.price) / fig.price) * 100
            rankings.append({
                "figure_id": fig.id,
                "figure_name": fig.name,
                "change_percentage": round(change_percentage, 2),
                "trend": "up" if change_percentage >= 0 else "down"
            })
    rankings.sort(key=lambda x: abs(x["change_percentage"]), reverse=True)
    rankings = rankings[:limit]

    AssetsCommonService.check_token_refresh(request, response)
    return {"rankings": rankings}


# ============== 端点 5/5：持仓 + 4 个分布 ==============

@router.get("/dashboard/holdings")
def get_asset_dashboard_holdings(
    request: Request,
    response: Response,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    持仓列表 + 4 个分布（风险 / 厂商 / 持有期 / 分级）。
    """
    ctx = _load_user_context(db, current_user.id)
    figures = ctx["figures"]
    total_assets = ctx["total_assets"]

    distribution_data = HoldingAnalysisService.analyze_all_distributions(
        db, figures, total_assets, current_user.id
    )

    AssetsCommonService.check_token_refresh(request, response)
    return {
        "holdings": distribution_data["holdings"],
        "risk_distribution": distribution_data["risk_distribution"],
        "manufacturer_distribution": distribution_data["manufacturer_distribution"],
        "holding_period_distribution": distribution_data["holding_period_distribution"],
        "tier_distribution": distribution_data["tier_distribution"]
    }


# ============== 原 /dashboard 已删除 ==============
# 2026-08-06 拆分重构：原 GET /dashboard（单接口 10 个顶层字段、>40KB）已替换为上方 5 个独立端点
# 原 /dashboard/init-daily-change 保持不变（POST，初始化日涨跌基准，与拆分无关）


@router.post("/dashboard/init-daily-change")
def init_daily_change_baseline(
    request: Request,
    response: Response,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    初始化日涨跌基准数据

    首次使用时调用，将当前总资产作为昨日基准数据写入快照表
    明天即可正常计算日涨跌

    Returns:
        {"message": "基准数据已创建", "yesterday_snapshot": {...}}
    """
    from app.services.dashboard_service.assets_service.asset_core_calculations import TotalAssetsCalculator
    from app.models.order import Order

    valid_orders = db.query(Order).filter(
        Order.user_id == current_user.id,
        Order.status == "已完成",
        Order.is_active == True
    ).all()

    total_assets = TotalAssetsCalculator.calculate_by_orders(db, current_user.id, valid_orders)

    yesterday_snapshot = DailyChangeService.get_or_create_yesterday_snapshot(
        db, current_user.id, total_assets
    )

    AssetsCommonService.check_token_refresh(request, response)

    return {
        "message": "日涨跌基准数据已创建，明天开始正常计算",
        "yesterday_snapshot": {
            "snapshot_date": yesterday_snapshot.snapshot_date.isoformat(),
            "total_asset": float(yesterday_snapshot.total_asset)
        }
    }
