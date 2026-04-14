from fastapi import APIRouter, Depends, HTTPException, Query, Request, Response
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from datetime import datetime, timedelta, date
from typing import List, Optional
import asyncio
from concurrent.futures import ThreadPoolExecutor
from pydantic import BaseModel

from app.models.database import get_db
from app.models.asset import (
    AssetPriceHistory, AssetAlert, AssetTransaction, 
    StockIndexCache, StockIndexHistory, AssetValueCache, UserSettings
)
from app.models.figure import Figure
from app.models.order import Order
from app.schemas.asset import (
    AssetSummary, AssetDetail, AssetKlineData, AssetRanking, AssetAdvice,
    AssetDashboard, AssetPriceHistoryCreate, AssetPriceHistory as AssetPriceHistorySchema,
    AssetAlertCreate, AssetAlert as AssetAlertSchema,
    AssetTransactionCreate, AssetTransaction as AssetTransactionSchema,
    AnnualLimitSetting
)
from app.api.users import get_current_user
from app.models.user import User

# 引入服务层
from app.services import (
    IndexService,
    AssetCalculationService,
    HoldingAnalysisService,
    PriceUpdateService
)

router = APIRouter()


@router.get("/dashboard")
async def get_asset_dashboard(
    request: Request,
    response: Response,
    time_range: str = Query("1m", description="时间范围: 1m, 3m, 1y, all"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取资产看板数据"""
    # 计算时间范围
    if time_range == "1m":
        start_date = datetime.now() - timedelta(days=30)
    elif time_range == "3m":
        start_date = datetime.now() - timedelta(days=90)
    elif time_range == "1y":
        start_date = datetime.now() - timedelta(days=365)
    else:  # all
        start_date = datetime(2000, 1, 1)
    
    # 获取所有手办
    figures = db.query(Figure).all()
    
    # 使用服务层计算总资产和总成本
    total_assets = AssetCalculationService.calculate_total_assets(figures)
    total_cost = AssetCalculationService.calculate_total_cost(figures)
    
    # 使用服务层计算日涨跌
    daily_change, daily_change_percentage, has_daily_change = \
        AssetCalculationService.calculate_daily_change(db, current_user.id, total_assets)
    
    # 使用服务层保存今日市值缓存
    AssetCalculationService.save_daily_cache(db, current_user.id, total_assets)
    
    # 使用服务层计算塑料指数
    plastic_index, base_date = AssetCalculationService.calculate_plastic_index(
        figures, total_assets
    )
    
    # 并行获取指数数据（使用线程池避免阻塞事件循环）
    async def fetch_index_data():
        # 为每个线程创建独立的数据库会话
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
            # 提交所有指数数据获取任务
            loop = asyncio.get_event_loop()
            tasks = [
                loop.run_in_executor(executor, get_sh_index),
                loop.run_in_executor(executor, get_hs300_index),
                loop.run_in_executor(executor, get_sh_comparison),
                loop.run_in_executor(executor, get_hs300_comparison)
            ]
            # 并行执行并等待所有任务完成
            return await asyncio.gather(*tasks)
    
    # 执行并行获取
    sh_index_data, hs300_index_data, sh_index_comparison, hs300_index_comparison = await fetch_index_data()
    
    sh_index = sh_index_data["current_value"]
    hs300_index = hs300_index_data["current_value"]
    
    # 使用服务层计算跑赢大盘百分比
    outperform_percentage = AssetCalculationService.calculate_outperform_percentage(
        plastic_index, sh_index
    )
    
    # 使用服务层计算仓位信息
    position_info = AssetCalculationService.calculate_position(
        db, current_user.id, figures
    )
    
    # 本月入手数量（模拟数据，后续可改为实际统计）
    monthly_purchases = 3
    
    # 构建资产摘要
    summary = {
        "total_assets": total_assets or 128500,
        "daily_change": daily_change,
        "daily_change_percentage": daily_change_percentage,
        "has_daily_change": has_daily_change,
        "plastic_index": plastic_index,
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
        "monthly_purchases": monthly_purchases
    }
    
    # 构建盈亏分析数据（模拟数据）
    profit = {
        "floating": 23400,
        "realized": 8200,
        "total_rate": 24.6
    }
    
    # 构建K线数据（模拟数据）
    kline_data = []
    for i in range(30):
        kline_data.append({
            "date": datetime.now() - timedelta(days=30 - i),
            "value": 2500 + i * 10 + (i % 5)
        })
    
    # 构建涨跌排行（模拟数据）
    rankings = [
        {"figure_id": 1, "figure_name": "初音韶华", "change_percentage": 15, "trend": "up"},
        {"figure_id": 2, "figure_name": "蕾姆婚纱", "change_percentage": 8, "trend": "up"},
        {"figure_id": 3, "figure_name": "Saber", "change_percentage": -12, "trend": "down"}
    ]
    
    # 构建操作建议（模拟数据）
    advice = [
        {"figure_name": "Saber", "advice": "Saber跌幅超10%,建议持有或止损"}
    ]
    
    # 使用服务层分析所有分布数据
    distribution_data = HoldingAnalysisService.analyze_all_distributions(
        figures, total_assets
    )
    
    # 检查是否需要返回新的token（自动续期）
    if hasattr(request.state, 'new_token'):
        response.headers['X-New-Token'] = request.state.new_token
    
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


@router.get("/settings/annual-limit")
def get_annual_spending_limit(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取用户年度手办消费上限"""
    settings = db.query(UserSettings).filter(
        UserSettings.user_id == current_user.id
    ).first()
    
    if not settings:
        return {
            "annual_spending_limit": 0,
            "message": "未设置年度消费上限"
        }
    
    return {
        "annual_spending_limit": settings.annual_spending_limit,
        "updated_at": settings.updated_at
    }


@router.post("/settings/annual-limit")
def update_annual_spending_limit(
    request: AnnualLimitSetting,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """更新用户年度手办消费上限"""
    limit = request.limit
    if limit < 0:
        raise HTTPException(status_code=400, detail="消费上限不能为负数")
    
    settings = db.query(UserSettings).filter(
        UserSettings.user_id == current_user.id
    ).first()
    
    if settings:
        settings.annual_spending_limit = limit
    else:
        settings = UserSettings(
            user_id=current_user.id,
            annual_spending_limit=limit
        )
        db.add(settings)
    
    db.commit()
    db.refresh(settings)
    
    return {
        "annual_spending_limit": settings.annual_spending_limit,
        "updated_at": settings.updated_at,
        "message": "年度消费上限设置成功"
    }


@router.get("/figures/{figure_id}/price-info")
def get_figure_price_info(
    figure_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取手办价格信息（用于修改现价弹窗）"""
    figure = PriceUpdateService.get_figure_current_price(db, figure_id)
    if not figure:
        raise HTTPException(status_code=404, detail="手办不存在")
    
    # 获取最新价格历史
    latest_history = PriceUpdateService.get_price_history(db, figure_id)
    
    # 计算影响（使用当前价格，即无变化时的影响）
    current_price = figure.market_price or figure.price or 0
    impact = PriceUpdateService.calculate_impact(db, current_user.id, figure, current_price)
    
    return {
        "figure_id": figure.id,
        "figure_name": figure.name,
        "current_price": current_price,
        "last_updated": latest_history.date if latest_history else figure.purchase_date,
        "quantity": figure.quantity or 1,
        "total_assets": impact["old_total_assets"],
        "profit_percentage": impact["old_profit_percentage"]
    }


class PriceUpdateRequest(BaseModel):
    new_price: float


@router.post("/figures/{figure_id}/update-price")
def update_figure_price(
    figure_id: int,
    request: PriceUpdateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """更新手办现价"""
    try:
        result = PriceUpdateService.update_figure_price(
            db, figure_id, request.new_price, current_user.id
        )
        
        # 确定新状态
        new_status = PriceUpdateService.determine_status(
            result["impact"]["new_profit_percentage"]
        )
        
        return {
            "message": "价格更新成功",
            "figure_id": figure_id,
            "figure_name": result["figure"].name,
            "old_price": result["old_price"],
            "new_price": result["new_price"],
            "new_status": new_status,
            "impact": {
                "old_total_assets": result["impact"]["old_total_assets"],
                "new_total_assets": result["impact"]["new_total_assets"],
                "old_profit_percentage": result["impact"]["old_profit_percentage"],
                "new_profit_percentage": result["impact"]["new_profit_percentage"]
            }
        }
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"价格更新失败: {str(e)}")
