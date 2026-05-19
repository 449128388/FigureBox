"""
dashboard_asset.py - 资产看板业务层

功能说明：
- 提供资产看板相关API端点
- 包括资产摘要、盈亏分析、K线数据、持仓分布等

API端点：
- GET /dashboard: 获取资产看板数据

依赖：
- fastapi.APIRouter
- sqlalchemy.orm.Session
- app.services.*

创建时间: 2026-05-18
作者: FigureBox Team
"""

from fastapi import APIRouter, Depends, Query, Request, Response
from sqlalchemy.orm import Session
from typing import List
import asyncio
from concurrent.futures import ThreadPoolExecutor

from app.models.database import get_db
from app.models.order import Order
from app.models.figure import Figure
from app.models.user import User
from app.api.users import get_current_user
from app.services import IndexService, AssetCalculationService, HoldingAnalysisService
from app.services.dashboard_service.assets_service.profit_analysis_service import ProfitAnalysisService
from app.services.dashboard_service.assets_service.plastic_index_service import PlasticIndexService
from app.services.dashboard_service.assets_service.asset_core_calculations import (
    TotalAssetsCalculator, PositionCalculator
)
from .assets_common import AssetsCommonService

router = APIRouter()


@router.get("/dashboard")
async def get_asset_dashboard(
    request: Request,
    response: Response,
    time_range: str = Query("1m", description="时间范围: 1m, 3m, 1y, all"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    获取资产看板数据
    
    返回资产看板的完整数据，包括：
    - 资产摘要（总资产、日涨跌、塑料指数等）
    - 盈亏分析（浮动盈亏、实现盈亏、总收益率等）
    - K线数据
    - 涨跌排行
    - 持仓分布数据
    """
    # 计算时间范围
    start_date = AssetsCommonService.calculate_time_range(time_range)
    
    # 获取所有有效订单
    valid_orders = AssetsCommonService.get_valid_orders(db)
    
    # 获取有有效订单的手办列表
    figures = AssetsCommonService.get_figures_with_valid_orders(db, valid_orders)
    
    # 使用基于已完成订单的方法计算总资产
    total_assets = TotalAssetsCalculator.calculate_by_orders(db, current_user.id, valid_orders)
    
    # 使用基于订单的计算方法计算仓位
    position_info = PositionCalculator.calculate_by_orders(db, current_user.id, valid_orders)
    
    # 向后兼容：保留原有的总成本计算
    total_cost = AssetCalculationService.calculate_total_cost(figures)
    
    # 使用服务层计算日涨跌
    daily_change, daily_change_percentage, has_daily_change = \
        AssetCalculationService.calculate_daily_change(db, current_user.id, total_assets)
    
    # 保存今日市值缓存
    AssetCalculationService.save_daily_cache(db, current_user.id, total_assets)
    
    # 使用塑料手办指数服务计算指数及涨跌
    plastic_index_data = PlasticIndexService.calculate_plastic_index(
        db, current_user.id, figures, total_assets
    )
    PlasticIndexService.save_daily_index(db, current_user.id, plastic_index_data)
    plastic_index_comparison = PlasticIndexService.get_index_comparison_data(db, current_user.id)
    
    # 并行获取指数数据
    async def fetch_index_data():
        from app.models.database import get_db
        
        def get_sh_index():
            db_session = next(get_db())
            try:
                return IndexService.get_cached_sh_index(db_session)
            finally:
                db_session.close()
        
        def get_hs300_index():
            db_session = next(get_db())
            try:
                return IndexService.get_cached_hs300_index(db_session)
            finally:
                db_session.close()
        
        def get_sh_comparison():
            db_session = next(get_db())
            try:
                return IndexService.get_index_comparison_data(db_session, "sh000001")
            finally:
                db_session.close()
        
        def get_hs300_comparison():
            db_session = next(get_db())
            try:
                return IndexService.get_index_comparison_data(db_session, "sh000300")
            finally:
                db_session.close()
        
        with ThreadPoolExecutor() as executor:
            loop = asyncio.get_event_loop()
            tasks = [
                loop.run_in_executor(executor, get_sh_index),
                loop.run_in_executor(executor, get_hs300_index),
                loop.run_in_executor(executor, get_sh_comparison),
                loop.run_in_executor(executor, get_hs300_comparison)
            ]
            return await asyncio.gather(*tasks)
    
    sh_index_data, hs300_index_data, sh_index_comparison, hs300_index_comparison = await fetch_index_data()
    
    sh_index = sh_index_data["current_value"]
    hs300_index = hs300_index_data["current_value"]
    
    # 计算跑赢大盘百分比
    outperform_percentage = AssetCalculationService.calculate_outperform_percentage(
        plastic_index_data["current_value"], sh_index
    )
    
    # 本月入手数量
    monthly_purchases = ProfitAnalysisService.calculate_monthly_purchases(db, current_user.id)
    
    # 构建资产摘要
    summary = {
        "total_assets": total_assets or 0,
        "daily_change": daily_change,
        "daily_change_percentage": daily_change_percentage,
        "has_daily_change": has_daily_change,
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

    # 构建盈亏分析数据
    profit_data = ProfitAnalysisService.get_profit_analysis(db, current_user.id)
    profit = {
        "floating": profit_data["floating"],
        "realized": profit_data["realized"],
        "total_rate": profit_data["total_rate"],
        "annualized_rate": profit_data["annualized_rate"],
        "realization_rate": profit_data["realization_rate"],
        "max_drawdown": profit_data["max_drawdown"]
    }

    # 构建K线数据
    kline_data = []
    if figures:
        from app.models.asset import AssetValueCache
        history = db.query(AssetValueCache).filter(
            AssetValueCache.user_id == current_user.id
        ).order_by(AssetValueCache.cache_date.desc()).limit(30).all()
        for record in reversed(history):
            kline_data.append({
                "date": record.cache_date.isoformat(),
                "value": record.total_value
            })

    # 构建涨跌排行
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
    rankings = rankings[:10]
    
    # 操作建议
    advice = [
        {"figure_name": "Saber", "advice": "Saber跌幅超10%,建议持有或止损"}
    ]

    # 持仓分布数据
    distribution_data = HoldingAnalysisService.analyze_all_distributions(
        db, figures, total_assets, current_user.id
    )
    
    # 检查token续期
    AssetsCommonService.check_token_refresh(request, response)
    
    return {
        "summary": summary,
        "profit": profit,
        "kline_data": kline_data,
        "rankings": rankings,
        "advice": advice,
        "holdings": distribution_data["holdings"],
        "risk_distribution": distribution_data["risk_distribution"],
        "manufacturer_distribution": distribution_data["manufacturer_distribution"],
        "holding_period_distribution": distribution_data["holding_period_distribution"],
        "tier_distribution": distribution_data["tier_distribution"]
    }
