"""
summary.py - 收藏家看板顶部概览+三指标卡片接口

API端点：
- GET /collector/summary: 获取用户基础信息+藏品统计

职责：
- 左卡片：藏品总数（覆盖作品数/厂商数）
- 中卡片：本月新入柜（最近3只手办名称）
- 右卡片：已出藏品（陪伴时长）
"""

from fastapi import APIRouter, Depends, Request, Response
from sqlalchemy.orm import Session
from datetime import datetime, date

from app.models.database import get_db
from app.models.order import Order
from app.models.figure import Figure
from app.models.user import User
from app.models.sold_order import SoldOrder
from app.models.asset_transaction import AssetTransaction, AssetValueCache
from app.api.users import get_current_user
from app.api.dashboard.collector.dashboard import get_valid_orders, get_figures_with_valid_orders, check_token_refresh
from app.services.dashboard_service.assets_service.profit_analysis_service import ProfitAnalysisService

router = APIRouter()


@router.get("/summary")
async def get_collector_summary(
    request: Request,
    response: Response,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    获取收藏家看板顶部概览+三指标卡片数据
    
    返回：
    - 藏品总数、覆盖作品数、覆盖厂商数
    - 本月新入柜数量、最近入库手办名称
    - 已出藏品数量、总陪伴时长
    """
    # 获取用户的所有有效订单
    valid_orders = get_valid_orders(db, current_user.id)
    
    # 获取有有效订单的手办列表
    figures = get_figures_with_valid_orders(db, valid_orders)
    
    # 获取当前年月
    now = datetime.now()
    current_year = now.year
    current_month = now.month

    # ========== 左卡片：藏品总数 ==========
    # 从 asset_transactions 表中统计各个手办的遗留总数（买入交易的 remaining_quantity 总和）
    buy_transactions = db.query(AssetTransaction).filter(
        AssetTransaction.user_id == current_user.id,
        AssetTransaction.transaction_type == 'buy',
        AssetTransaction.is_active == True
    ).all()

    # 计算藏品总数（所有买入交易的 remaining_quantity 总和）
    total_collection = sum(
        trans.remaining_quantity or 0
        for trans in buy_transactions
        if trans.remaining_quantity and trans.remaining_quantity > 0
    )

    # 获取有持仓的手办ID列表
    figure_ids_with_stock = set(
        trans.figure_id
        for trans in buy_transactions
        if trans.remaining_quantity and trans.remaining_quantity > 0
    )

    # 获取这些手办的详细信息
    figures_with_stock = db.query(Figure).filter(Figure.id.in_(figure_ids_with_stock)).all() if figure_ids_with_stock else []

    # 统计覆盖的作品数和厂商数
    unique_works = set(fig.work for fig in figures_with_stock if fig.work)
    unique_manufacturers = set()
    for fig in figures_with_stock:
        if fig.manufacturer:
            for m in fig.manufacturer.split("、"):
                m = m.strip()
                if m:
                    unique_manufacturers.add(m)
    
    # ========== 中卡片：本月新入柜 ==========
    current_month_start = datetime(current_year, current_month, 1)
    current_month_end = datetime(current_year, current_month + 1, 1) if current_month < 12 else datetime(current_year + 1, 1, 1)
    
    this_month_transactions = db.query(AssetTransaction).filter(
        AssetTransaction.user_id == current_user.id,
        AssetTransaction.transaction_type == 'buy',
        AssetTransaction.transaction_date >= current_month_start,
        AssetTransaction.transaction_date < current_month_end,
        AssetTransaction.is_active == True
    ).order_by(AssetTransaction.transaction_date.desc()).all()
    
    this_month_count = len(this_month_transactions)
    
    # 取本月入库的最近3只手办名称
    recent_figures = []
    recent_figures_detail = []
    for trans in this_month_transactions[:3]:
        if trans.figure and trans.figure.name:
            fig = trans.figure
            recent_figures.append(fig.name)
            recent_figures_detail.append({
                "name": fig.name,
                "price": fig.market_price or fig.price or 0,
                "image": (fig.images[0] if fig.images and isinstance(fig.images, list) and len(fig.images) > 0 else ""),
                "spec": f"{fig.work} · {fig.scale} · {fig.manufacturer}" if (fig.work or fig.scale or fig.manufacturer) else ""
            })
    recent_figures_text = ' / '.join(recent_figures) if recent_figures else '暂无新入库'
    
    # ========== 右卡片：已出藏品 ==========
    sold_orders = db.query(SoldOrder).filter(
        SoldOrder.user_id == current_user.id,
        SoldOrder.is_active == True
    ).all()
    
    total_sold_count = len(sold_orders)
    
    # 计算陪伴时长 + 收益率
    total_companion_days = 0
    total_sold_cost = 0.0
    total_sold_profit = 0.0
    for sold_order in sold_orders:
        if sold_order.created_at and sold_order.figure_id:
            first_transaction = db.query(AssetTransaction).filter(
                AssetTransaction.user_id == current_user.id,
                AssetTransaction.figure_id == sold_order.figure_id,
                AssetTransaction.transaction_type == 'buy',
                AssetTransaction.is_active == True
            ).order_by(AssetTransaction.transaction_date.asc()).first()
            
            if first_transaction and first_transaction.transaction_date:
                companion_days = (sold_order.created_at - first_transaction.transaction_date).days
                if companion_days > 0:
                    total_companion_days += companion_days
            # 累计成本和利润（用于海报返回）
            if first_transaction and first_transaction.price:
                cost = first_transaction.price
                sell_price = sold_order.sell_price or 0
                total_sold_cost += cost
                total_sold_profit += sell_price - cost

    # 计算总资产价值（从 asset_value_cache 取当日缓存数据）
    today = date.today()
    cached = db.query(AssetValueCache).filter(
        AssetValueCache.user_id == current_user.id,
        AssetValueCache.cache_date == today
    ).first()
    total_asset_value = cached.total_value if cached else 0.0

    # 使用盈亏分析服务计算总收益率（含浮动盈亏 + 实现盈亏）
    total_return_rate = ProfitAnalysisService.calculate_total_return_rate(db, current_user.id)
    prefix = "+" if total_return_rate >= 0 else ""
    profit_rate = f"{prefix}{total_return_rate}%"

    # 检查token续期
    check_token_refresh(request, response)

    return {
        "total_collection": total_collection,
        "unique_works": len(unique_works),
        "unique_manufacturers": len(unique_manufacturers),
        "manufacturer_list": sorted(unique_manufacturers) if unique_manufacturers else [],
        "this_month_count": this_month_count,
        "recent_figures": recent_figures_text,
        "recent_figures_detail": recent_figures_detail,
        "total_sold_count": total_sold_count,
        "total_companion_days": total_companion_days,
        "total_asset_value": total_asset_value,
        "profit_rate": profit_rate
    }
