"""
share.py - 收藏家分享接口（拆分式 API）

API端点：
- POST /collector/share/generate: 生成分享链接
- POST /collector/share/reset: 重置分享链接
- GET /share/profile/{user_id}: 获取用户基础信息和隐私级别
- GET /share/summary/{user_id}: 获取公开统计数据
- GET /share/cabinets/{user_id}: 获取公开收藏柜
- GET /share/tags/{user_id}: 获取公开标签云
- GET /share/activities/{user_id}: 获取公开动态流
"""

from fastapi import APIRouter, Depends, Request, Response, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, timedelta, date

from app.models.database import get_db
from app.models.user import User
from app.models.figure import Figure
from app.models.sold_order import SoldOrder
from app.models.order import Order
from app.models.asset import AssetTransaction, AssetValueCache
from app.models.activity_feed import ActivityFeed
from app.models.collector_privacy import CollectorPrivacy
from app.api.users import get_current_user
from app.api.collector.dashboard import check_token_refresh
from app.services.dashboard_service.collector_service.collector_privacy_service import CollectorPrivacyService
from app.services.dashboard_service.collector_service.collector_manufacturer_service import CollectorManufacturerService
from app.services.dashboard_service.collector_service.collector_exclusion_service import CollectorExclusionService
from app.services.dashboard_service.collector_service.collector_tag_service import CollectorTagService
from app.services.dashboard_service.assets_service.profit_analysis_service import ProfitAnalysisService

router = APIRouter()


def _get_image_url(figure):
    if figure.images and isinstance(figure.images, list) and len(figure.images) > 0:
        return figure.images[0]
    return ""


def _get_figure_stock(db, user_id, figure_id):
    result = db.query(
        func.coalesce(func.sum(AssetTransaction.remaining_quantity), 0)
    ).filter(
        AssetTransaction.user_id == user_id,
        AssetTransaction.figure_id == figure_id,
        AssetTransaction.transaction_type == 'buy',
        AssetTransaction.is_active == True
    ).scalar()
    return result or 0


def _build_figure_item(fig, extra=None):
    item = {
        "id": fig.id,
        "name": fig.name or "未知",
        "image": _get_image_url(fig),
        "work": fig.work or "未知",
        "scale": fig.scale or "未知",
        "manufacturer": fig.manufacturer or "未知",
    }
    if extra:
        item.update(extra)
    return item


async def _verify_share_access(db: Session, user_id: int, token: str) -> CollectorPrivacy:
    """验证分享 token 并返回隐私设置，未通过则抛出 HTTP 异常"""
    privacy = CollectorPrivacyService.validate_share_token(db, user_id, token)
    if not privacy:
        raise HTTPException(status_code=403, detail="链接已失效，请让收藏家重新生成分享链接")
    if privacy.home_visibility == "private":
        raise HTTPException(status_code=403, detail="该用户主页已设为私密")
    return privacy


def _feed_to_dict(ev):
    return {
        "id": ev.id,
        "event_type": ev.event_type.lower(),
        "event_title": ev.event_title,
        "detail_data": ev.detail_data,
        "created_at": ev.created_at.isoformat() if ev.created_at else "",
        "event_date": ev.event_date.isoformat() if ev.event_date else ""
    }


@router.post("/share/generate")
async def generate_share_link(
    request: Request,
    response: Response,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """生成分享链接"""
    base_url = str(request.base_url).rstrip('/')
    result = CollectorPrivacyService.generate_share_url(db, current_user.id, base_url)
    check_token_refresh(request, response)
    return result


@router.post("/share/reset")
async def reset_share_link(
    request: Request,
    response: Response,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """重置分享链接，旧链接立即失效"""
    result = CollectorPrivacyService.reset_share_token(db, current_user.id)
    check_token_refresh(request, response)
    return result


@router.get("/share/profile/{user_id}")
async def get_shared_profile(
    user_id: int,
    token: str = Query(..., description="分享鉴权令牌"),
    poster: str = Query("0", description="标记来自海报分享"),
    db: Session = Depends(get_db)
):
    """
    获取用户基础信息和隐私级别

    前端根据返回的 poster_level / summary_only / names_only 决定展示模式。
    """
    privacy = await _verify_share_access(db, user_id, token)
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")

    return {
        "visible": True,
        "user_id": user_id,
        "nickname": user.nickname or user.username or "收藏家",
        "avatar_url": user.avatar_url or "",
        "home_visibility": privacy.home_visibility,
        "from_poster": poster == "1",
        "show_total": privacy.show_total,
        "show_figures": privacy.show_figures,
        "show_asset": privacy.show_asset,
        "show_feed": privacy.show_feed,
        "show_tags": privacy.show_tags,
    }


@router.get("/share/summary/{user_id}")
async def get_shared_summary(
    user_id: int,
    token: str = Query(..., description="分享鉴权令牌"),
    db: Session = Depends(get_db)
):
    """获取公开统计数据"""
    privacy = await _verify_share_access(db, user_id, token)
    if not privacy.show_total:
        return {}

    now = datetime.now()

    buy_transactions = db.query(AssetTransaction).filter(
        AssetTransaction.user_id == user_id,
        AssetTransaction.transaction_type == 'buy',
        AssetTransaction.is_active == True
    ).all()

    total_collection = sum(t.remaining_quantity or 0 for t in buy_transactions if t.remaining_quantity and t.remaining_quantity > 0)

    figure_ids_with_stock = set(t.figure_id for t in buy_transactions if t.remaining_quantity and t.remaining_quantity > 0)
    figures_with_stock = db.query(Figure).filter(Figure.id.in_(figure_ids_with_stock)).all() if figure_ids_with_stock else []
    unique_works = set(fig.work for fig in figures_with_stock if fig.work)
    unique_manufacturers = set()
    for fig in figures_with_stock:
        if fig.manufacturer:
            for m in fig.manufacturer.split("、"):
                m = m.strip()
                if m:
                    unique_manufacturers.add(m)

    current_month_start = datetime(now.year, now.month, 1)
    if now.month < 12:
        current_month_end = datetime(now.year, now.month + 1, 1)
    else:
        current_month_end = datetime(now.year + 1, 1, 1)
    this_month_transactions = db.query(AssetTransaction).filter(
        AssetTransaction.user_id == user_id,
        AssetTransaction.transaction_type == 'buy',
        AssetTransaction.transaction_date >= current_month_start,
        AssetTransaction.transaction_date < current_month_end,
        AssetTransaction.is_active == True
    ).order_by(AssetTransaction.transaction_date.desc()).all()
    this_month_count = len(this_month_transactions)
    recent_figures = []
    recent_figures_detail = []
    for trans in this_month_transactions[:3]:
        if trans.figure and trans.figure.name:
            fig = trans.figure
            recent_figures.append(fig.name)
            recent_figures_detail.append({
                "name": fig.name,
                "price": fig.market_price or fig.price or 0,
                "image": _get_image_url(fig),
                "spec": f"{fig.work} · {fig.scale} · {fig.manufacturer}" if (fig.work or fig.scale or fig.manufacturer) else ""
            })
    recent_figures_text = ' / '.join(recent_figures) if recent_figures else '暂无新入库'

    sold_orders = db.query(SoldOrder).filter(
        SoldOrder.user_id == user_id,
        SoldOrder.is_active == True
    ).all()
    total_sold_count = len(sold_orders)
    total_companion_days = 0
    # 计算收益率
    total_sold_cost = 0.0
    total_sold_profit = 0.0
    for sold_order in sold_orders:
        if sold_order.created_at and sold_order.figure_id:
            first = db.query(AssetTransaction).filter(
                AssetTransaction.user_id == user_id,
                AssetTransaction.figure_id == sold_order.figure_id,
                AssetTransaction.transaction_type == 'buy',
                AssetTransaction.is_active == True
            ).order_by(AssetTransaction.transaction_date.asc()).first()
            if first and first.transaction_date:
                days = (sold_order.created_at - first.transaction_date).days
                if days > 0:
                    total_companion_days += days
            # 累计成本和利润
            if first and first.price:
                cost = first.price
                sell_price = sold_order.sell_price or 0
                total_sold_cost += cost
                total_sold_profit += sell_price - cost

    # 计算总资产价值（从 asset_value_cache 取当日缓存数据）
    today = date.today()
    cached = db.query(AssetValueCache).filter(
        AssetValueCache.user_id == user_id,
        AssetValueCache.cache_date == today
    ).first()
    total_asset_value = cached.total_value if cached else 0.0

    # 使用盈亏分析服务计算总收益率（含浮动盈亏 + 实现盈亏）
    total_return_rate = ProfitAnalysisService.calculate_total_return_rate(db, user_id)
    prefix = "+" if total_return_rate >= 0 else ""
    profit_rate = f"{prefix}{total_return_rate}%"

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


@router.get("/share/cabinets/{user_id}")
async def get_shared_cabinets(
    user_id: int,
    token: str = Query(..., description="分享鉴权令牌"),
    db: Session = Depends(get_db)
):
    """获取公开收藏柜数据"""
    privacy = await _verify_share_access(db, user_id, token)
    now = datetime.now()

    exclusion_map = CollectorExclusionService.bulk_get_excluded_ids_by_cabinet(db, user_id)

    # 1. 海景房（仅统计数量）
    active_holdings = db.query(AssetTransaction).filter(
        AssetTransaction.user_id == user_id,
        AssetTransaction.transaction_type == 'buy',
        AssetTransaction.is_active == True,
        AssetTransaction.remaining_quantity > 0
    ).all()
    fh = {}
    for t in active_holdings:
        if t.figure_id not in fh or (t.transaction_date and fh[t.figure_id] and t.transaction_date < fh[t.figure_id]):
            fh[t.figure_id] = t.transaction_date
    star_count = 0
    for fid, first_date in fh.items():
        if fid in exclusion_map.get('star', set()):
            continue
        if first_date and (now - first_date).days > 180:
            star_count += 1

    # 2. 最近入柜（仅统计数量）
    thirty_days_ago = now - timedelta(days=30)
    recent_trans = db.query(AssetTransaction).filter(
        AssetTransaction.user_id == user_id,
        AssetTransaction.transaction_type == 'buy',
        AssetTransaction.transaction_date >= thirty_days_ago,
        AssetTransaction.is_active == True
    ).all()
    rfm = set()
    for t in recent_trans:
        rfm.add(t.figure_id)
    new_count = 0
    for fid in rfm:
        if fid in exclusion_map.get('new', set()):
            continue
        new_count += 1

    # ====== 4. 已出藏品（已出坑） ======
    sold_orders = db.query(SoldOrder).filter(
        SoldOrder.user_id == user_id,
        SoldOrder.is_active == True
    ).all()

    sold_figure_ids = set()
    for so in sold_orders:
        if so.figure_id:
            sold_figure_ids.add(so.figure_id)
    sold_count = sum(1 for fid in sold_figure_ids if fid not in exclusion_map.get('out', set()))

    # ====== 5. 预定中（空气谷） ======
    air_orders = db.query(Order).filter(
        Order.user_id == user_id,
        Order.order_type == '定金预定',
        Order.status.in_(['未支付', '已支付']),
        Order.is_active == 1
    ).all()
    seen_air = set()
    air_count = 0
    for order in air_orders:
        if order.figure_id in seen_air or not order.figure:
            continue
        if order.figure_id in exclusion_map.get('air', set()):
            continue
        seen_air.add(order.figure_id)
        air_count += 1

    # ====== 6. 复数专区 ======
    dup_rows = db.query(
        AssetTransaction.figure_id,
        func.sum(AssetTransaction.remaining_quantity).label('total_stock')
    ).filter(
        AssetTransaction.user_id == user_id,
        AssetTransaction.transaction_type == 'buy',
        AssetTransaction.is_active == True,
        AssetTransaction.remaining_quantity > 0
    ).group_by(AssetTransaction.figure_id).having(
        func.sum(AssetTransaction.remaining_quantity) >= 2
    ).all()
    dup_count = sum(1 for r in dup_rows if r.figure_id not in exclusion_map.get('dup', set()))

    # ====== 7. 待出荷 ======
    wait_orders = db.query(Order).filter(
        Order.user_id == user_id,
        Order.status == '已完成',
        Order.is_active == 1
    ).all()
    seen_wait = set()
    wait_count = 0
    for order in wait_orders:
        if order.figure_id in seen_wait or not order.figure:
            continue
        if order.figure_id in exclusion_map.get('wait', set()):
            continue
        seen_wait.add(order.figure_id)
        wait_count += 1

    # ====== 8. 本命厂商（仅统计数量） ======
    manufacturer_count = CollectorManufacturerService.get_count(db, user_id)

    # ====== 构建8个分类，meta 与 cabinets.py 保持完全一致 ======
    cabinets_list = [
        {"key": "star", "name": "海景房专区", "description": "镇柜之宝", "icon": "🖼️", "icon_bg": "#E8F4F8",
         "count": star_count,
         "meta": f"{star_count} 体 · 入柜 180+ 天" if star_count > 0 else "暂无镇柜藏品"},
        {"key": "new", "name": "最近入柜", "description": "新欢", "icon": "✨", "icon_bg": "#F0F5E8",
         "count": new_count,
         "meta": f"{new_count} 体 · 30 天内新成员" if new_count > 0 else "暂无新入库"},
        {"key": "fix", "name": "修复工坊", "description": "待修复", "icon": "🔧", "icon_bg": "#FDF6EE",
         "count": 0, "meta": "暂无待修复藏品"},
        {"key": "out", "name": "已出藏品", "description": "已出坑", "icon": "📦", "icon_bg": "#F5F5F5",
         "count": sold_count,
         "meta": f"{sold_count} 体 · 找到新主人" if sold_count > 0 else "暂无已出藏品"},
        {"key": "air", "name": "预定中", "description": "空气谷", "icon": "☁️", "icon_bg": "#F3E8FF",
         "count": air_count,
         "meta": f"{air_count} 体 · 待付尾款" if air_count > 0 else "暂无预定"},
        {"key": "dup", "name": "复数专区", "description": "复数", "icon": "👯", "icon_bg": "#FFF2F0",
         "count": dup_count,
         "meta": f"{dup_count} 体 · 同款复购" if dup_count > 0 else "暂无复数藏品"},
        {"key": "wait", "name": "待出荷", "description": "待出荷", "icon": "📅", "icon_bg": "#E6F7FF",
         "count": wait_count,
         "meta": f"{wait_count} 体 · 等待出货" if wait_count > 0 else "暂无待出荷"},
        {"key": "role", "name": "本命厂商", "description": "本命", "icon": "🏭", "icon_bg": "#E8F4F8",
         "count": manufacturer_count,
         "meta": f"{manufacturer_count} 家 · 追厂狂魔" if manufacturer_count > 0 else "暂无本命厂商"},
    ]
    return cabinets_list


@router.get("/share/tags/{user_id}")
async def get_shared_tags(
    user_id: int,
    token: str = Query(..., description="分享鉴权令牌"),
    db: Session = Depends(get_db)
):
    """获取公开标签云"""
    await _verify_share_access(db, user_id, token)
    system_tags = CollectorTagService.get_system_tags(db, user_id)
    user_tags = CollectorTagService.get_user_tags(db, user_id)
    return {
        "tags": system_tags + user_tags,
        "system_tags": system_tags,
        "user_tags": user_tags
    }


@router.get("/share/activities/{user_id}")
async def get_shared_activities(
    user_id: int,
    token: str = Query(..., description="分享鉴权令牌"),
    limit: int = Query(20, description="返回条数"),
    db: Session = Depends(get_db)
):
    """获取公开动态流"""
    privacy = await _verify_share_access(db, user_id, token)

    if privacy.show_feed:
        activities = db.query(ActivityFeed).filter(
            ActivityFeed.user_id == user_id
        ).order_by(ActivityFeed.created_at.desc()).limit(limit).all()
        return [_feed_to_dict(a) for a in activities]

    return []
