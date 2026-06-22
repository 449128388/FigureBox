"""
cabinets.py - 收藏家看板我的收藏柜接口

API端点：
- GET /collector/cabinets: 获取我的收藏柜8个分类橱窗卡片
- POST /api/v1/cabinets/remove-figure: 将藏品从收藏柜移出

职责：
- 返回8个固定收藏柜分类，即使无数据也展示
- 4个分类有真实统计逻辑：海景房专区、最近入柜、修复工坊、已出藏品
- 4个分类默认为空数据：预定中、复数专区、待出荷、本命角色
- 支持出柜登记：将藏品从当前收藏柜分类移出

各分类统计逻辑：
1. 海景房专区（镇柜之宝）: 收藏天数>180天+入手价高+当前仍在库
2. 最近入柜（新欢）: asset_transactions 中 type='buy'，30天内，按figure_id去重
3. 修复工坊（待修复）: figure_tag关联tags表中name=待修复/缺件/断桩/待补色/蹭色
4. 已出藏品（已出坑）: asset_transactions 中 type='sell'，按figure_id去重

出柜登记逻辑：
- 海景房专区：移除star标签
- 最近入柜：无需处理（30天自动过期）
- 修复工坊：移除修复相关标签
- 其他分类：根据具体逻辑处理
"""

from fastapi import APIRouter, Depends, Request, Response, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func, text
from pydantic import BaseModel
from datetime import datetime, timedelta
from collections import defaultdict

from app.models.database import get_db
from app.models.figure import Figure
from app.models.user import User
from app.models.sold_order import SoldOrder
from app.models.tag import Tag, figure_tag
from app.models.asset import AssetTransaction
from app.models.order import Order
from app.api.users import get_current_user
from app.services.collector_service.collector_manufacturer_service import CollectorManufacturerService

router = APIRouter()


def get_image_url(figure):
    """从images列表中获取第一张图片URL"""
    if figure.images and isinstance(figure.images, list) and len(figure.images) > 0:
        return figure.images[0]
    return ""


def get_figure_stock(db, user_id, figure_id):
    """获取手办当前总库存（所有入库记录的 remaining_quantity 之和）"""
    from sqlalchemy import func
    result = db.query(
        func.coalesce(func.sum(AssetTransaction.remaining_quantity), 0)
    ).filter(
        AssetTransaction.user_id == user_id,
        AssetTransaction.figure_id == figure_id,
        AssetTransaction.transaction_type == 'buy',
        AssetTransaction.is_active == True
    ).scalar()
    return result or 0


@router.get("/cabinets")
async def get_collector_cabinets(
    request: Request,
    response: Response,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    获取收藏家看板-我的收藏柜数据（8个固定分类）
    
    返回8个橱窗卡片，每个包含：
    - key: 分类标识
    - name: 分类名称
    - description: 描述
    - icon: 图标emoji
    - icon_bg: 图标背景色
    - count: 藏品数量
    - meta: 底部文案
    """
    now = datetime.now()
    current_year = now.year
    current_month = now.month

    # ====== 1. 海景房专区（镇柜之宝） ======
    # 兜底规则：收藏天数 > 180 天 + 当前仍在库
    star_figures = []
    # 查询所有还有剩余持仓的买入交易
    active_holdings = db.query(AssetTransaction).filter(
        AssetTransaction.user_id == current_user.id,
        AssetTransaction.transaction_type == 'buy',
        AssetTransaction.is_active == True,
        AssetTransaction.remaining_quantity > 0
    ).all()

    # 按figure_id去重，取最早的transaction_date
    figure_holdings = {}
    for trans in active_holdings:
        if trans.figure_id not in figure_holdings:
            figure_holdings[trans.figure_id] = trans
        else:
            # 取最早的transaction_date
            existing = figure_holdings[trans.figure_id]
            if trans.transaction_date and existing.transaction_date and trans.transaction_date < existing.transaction_date:
                figure_holdings[trans.figure_id] = trans

    for figure_id, trans in figure_holdings.items():
        if trans.transaction_date:
            holding_days = (now - trans.transaction_date).days
            if holding_days > 180 and trans.figure:
                star_figures.append({
                    "id": figure_id,
                    "name": trans.figure.name or "未知",
                    "image": get_image_url(trans.figure),
                    "holding_days": holding_days,
                    "work": trans.figure.work or "未知",
                    "scale": trans.figure.scale or "未知",
                    "manufacturer": trans.figure.manufacturer or "未知",
                    "transaction_date": trans.transaction_date.strftime("%Y-%m-%d") if trans.transaction_date else None,
                    "purchase_price": trans.price or 0,
                    "stock": get_figure_stock(db, current_user.id, figure_id)
                })

    # 按年限从高到低排序
    star_figures.sort(key=lambda x: x["holding_days"], reverse=True)

    # ====== 2. 最近入柜（新欢） ======
    thirty_days_ago = now - timedelta(days=30)
    recent_transactions = db.query(AssetTransaction).filter(
        AssetTransaction.user_id == current_user.id,
        AssetTransaction.transaction_type == 'buy',
        AssetTransaction.transaction_date >= thirty_days_ago,
        AssetTransaction.is_active == True
    ).order_by(AssetTransaction.transaction_date.desc()).all()

    # 按figure_id去重，保留最新入库的那1体
    recent_figure_map = {}
    for trans in recent_transactions:
        if trans.figure_id not in recent_figure_map:
            recent_figure_map[trans.figure_id] = trans

    new_figures = []
    for figure_id, trans in recent_figure_map.items():
        if trans.figure:
            # 取该手办最早的入库时间计算陪伴天数（从第一次拥有开始算）
            first_buy = db.query(AssetTransaction).filter(
                AssetTransaction.figure_id == figure_id,
                AssetTransaction.user_id == current_user.id,
                AssetTransaction.transaction_type == 'buy',
                AssetTransaction.is_active == True
            ).order_by(AssetTransaction.transaction_date.asc()).first()

            holding_days = 0
            first_buy_date = None
            if first_buy and first_buy.transaction_date:
                days = (now - first_buy.transaction_date).days
                if days > 0:
                    holding_days = days
                first_buy_date = first_buy.transaction_date

            new_figures.append({
                "id": figure_id,
                "name": trans.figure.name or "未知",
                "image": get_image_url(trans.figure),
                "holding_days": holding_days,
                "work": trans.figure.work or "未知",
                "scale": trans.figure.scale or "未知",
                "manufacturer": trans.figure.manufacturer or "未知",
                "transaction_date": first_buy_date.strftime("%Y-%m-%d") if first_buy_date else None,
                "purchase_price": trans.price or 0,
                "stock": get_figure_stock(db, current_user.id, figure_id)
            })

    # ====== 3. 修复工坊（待修复） ======
    repair_tag_names = ['待修复', '缺件', '断桩', '待补色', '蹭色']
    repair_tags = db.query(Tag).filter(
        Tag.name.in_(repair_tag_names)
    ).all()
    repair_tag_ids = [tag.id for tag in repair_tags]

    repair_figures = []
    if repair_tag_ids:
        # 通过 figure_tag 中间表查询有关联这些tag的figure
        result = db.execute(
            text("SELECT figure_id FROM figure_tag WHERE tag_id IN :tag_ids"),
            {"tag_ids": tuple(repair_tag_ids)}
        ).fetchall()

        repair_figure_ids = set(row[0] for row in result)
        for fid in repair_figure_ids:
            fig = db.query(Figure).filter(Figure.id == fid).first()
            if fig:
                # 计算陪伴天数（首次入库日期至今）
                holding_days = 0
                first_buy = db.query(AssetTransaction).filter(
                    AssetTransaction.figure_id == fid,
                    AssetTransaction.user_id == current_user.id,
                    AssetTransaction.transaction_type == 'buy',
                    AssetTransaction.is_active == True
                ).order_by(AssetTransaction.transaction_date.asc()).first()
                if first_buy and first_buy.transaction_date:
                    days = (now - first_buy.transaction_date).days
                    if days > 0:
                        holding_days = days
                # 获取首次入库日期
                first_buy_date = first_buy.transaction_date if first_buy and first_buy.transaction_date else None
                repair_figures.append({
                    "id": fid,
                    "name": fig.name or "未知",
                    "image": get_image_url(fig),
                    "holding_days": holding_days,
                    "work": fig.work or "未知",
                    "scale": fig.scale or "未知",
                    "manufacturer": fig.manufacturer or "未知",
                    "transaction_date": first_buy_date.strftime("%Y-%m-%d") if first_buy_date else None,
                    "purchase_price": first_buy.price if first_buy else 0,
                    "stock": get_figure_stock(db, current_user.id, fid)
                })

    # ====== 4. 已出藏品（已出坑） ======
    sold_orders = db.query(SoldOrder).filter(
        SoldOrder.user_id == current_user.id,
        SoldOrder.is_active == True
    ).all()

    # 按figure_id去重
    sold_figure_ids = set()
    for so in sold_orders:
        if so.figure_id:
            sold_figure_ids.add(so.figure_id)

    sold_figures = []
    for fid in sold_figure_ids:
        fig = db.query(Figure).filter(Figure.id == fid).first()
        if fig:
            # 计算陪伴天数（卖出日期 - 首次入库日期）
            holding_days = 0
            sold_order = db.query(SoldOrder).filter(
                SoldOrder.figure_id == fid,
                SoldOrder.user_id == current_user.id,
                SoldOrder.is_active == True
            ).order_by(SoldOrder.created_at.desc()).first()
            if sold_order and sold_order.created_at:
                first_buy = db.query(AssetTransaction).filter(
                    AssetTransaction.figure_id == fid,
                    AssetTransaction.user_id == current_user.id,
                    AssetTransaction.transaction_type == 'buy',
                    AssetTransaction.is_active == True
                ).order_by(AssetTransaction.transaction_date.asc()).first()
                if first_buy and first_buy.transaction_date:
                    days = (sold_order.created_at - first_buy.transaction_date).days
                    if days > 0:
                        holding_days = days

            # 获取首次入库日期
            first_buy_date = first_buy.transaction_date if first_buy and first_buy.transaction_date else None
            sold_figures.append({
                "id": fid,
                "name": fig.name or "未知",
                "image": get_image_url(fig),
                "holding_days": holding_days,
                "work": fig.work or "未知",
                "scale": fig.scale or "未知",
                "manufacturer": fig.manufacturer or "未知",
                "transaction_date": first_buy_date.strftime("%Y-%m-%d") if first_buy_date else None,
                "purchase_price": first_buy.price if first_buy else 0,
                "stock": get_figure_stock(db, current_user.id, fid)
            })

    # ====== 5. 预定中（空气谷） ======
    # 订单类型为"定金预定"、尾款状态为未付款的订单
    air_orders = db.query(Order).filter(
        Order.user_id == current_user.id,
        Order.order_type == '定金预定',
        Order.status.in_(['未支付', '已支付']),
        Order.is_active == 1
    ).all()

    air_figures = []
    seen_air_figure_ids = set()
    for order in air_orders:
        if order.figure_id not in seen_air_figure_ids and order.figure:
            seen_air_figure_ids.add(order.figure_id)
            air_figures.append({
                "id": order.figure_id,
                "name": order.figure.name or "未知",
                "image": get_image_url(order.figure),
                "holding_days": 0,
                "work": order.figure.work or "未知",
                "scale": order.figure.scale or "未知",
                "manufacturer": order.figure.manufacturer or "未知",
                "transaction_date": order.created_at.strftime("%Y-%m-%d") if order.created_at else None,
                "purchase_price": order.deposit or 0,
                "stock": get_figure_stock(db, current_user.id, order.figure_id)
            })

    # ====== 6. 复数专区 ======
    # 同一款手办 remaining_quantity > 0 且总量 >= 2
    dup_stock = db.query(
        AssetTransaction.figure_id,
        func.sum(AssetTransaction.remaining_quantity).label('total_stock')
    ).filter(
        AssetTransaction.user_id == current_user.id,
        AssetTransaction.transaction_type == 'buy',
        AssetTransaction.is_active == True,
        AssetTransaction.remaining_quantity > 0
    ).group_by(AssetTransaction.figure_id).having(
        func.sum(AssetTransaction.remaining_quantity) >= 2
    ).all()

    dup_figure_ids = [r.figure_id for r in dup_stock]
    dup_stock_map = {r.figure_id: int(getattr(r, 'total_stock', 0) or 0) for r in dup_stock}
    dup_figures = []
    for fid in dup_figure_ids:
        fig = db.query(Figure).filter(Figure.id == fid).first()
        if fig:
            # 取最早入库日期
            first_buy = db.query(AssetTransaction).filter(
                AssetTransaction.figure_id == fid,
                AssetTransaction.user_id == current_user.id,
                AssetTransaction.transaction_type == 'buy',
                AssetTransaction.is_active == True
            ).order_by(AssetTransaction.transaction_date.asc()).first()
            first_buy_date = first_buy.transaction_date if first_buy and first_buy.transaction_date else None
            holding_days = (now - first_buy_date).days if first_buy_date else 0
            dup_figures.append({
                "id": fid,
                "name": fig.name or "未知",
                "image": get_image_url(fig),
                "holding_days": max(holding_days, 0),
                "work": fig.work or "未知",
                "scale": fig.scale or "未知",
                "manufacturer": fig.manufacturer or "未知",
                "transaction_date": first_buy_date.strftime("%Y-%m-%d") if first_buy_date else None,
                "purchase_price": first_buy.price if first_buy else 0,
                "stock": dup_stock_map.get(fid, 0)
            })

    # ====== 7. 待出荷 ======
    # 钱已付清（已完成），等待出荷发货
    wait_orders = db.query(Order).filter(
        Order.user_id == current_user.id,
        Order.status == '已完成',
        Order.is_active == 1
    ).all()

    wait_figures = []
    seen_wait_figure_ids = set()
    for order in wait_orders:
        if order.figure_id not in seen_wait_figure_ids and order.figure:
            seen_wait_figure_ids.add(order.figure_id)
            wait_figures.append({
                "id": order.figure_id,
                "name": order.figure.name or "未知",
                "image": get_image_url(order.figure),
                "holding_days": 0,
                "work": order.figure.work or "未知",
                "scale": order.figure.scale or "未知",
                "manufacturer": order.figure.manufacturer or "未知",
                "transaction_date": order.created_at.strftime("%Y-%m-%d") if order.created_at else None,
                "purchase_price": (order.deposit or 0) + (order.balance or 0),
                "stock": get_figure_stock(db, current_user.id, order.figure_id)
            })

    # ====== 8. 本命厂商 ======
    # 已入库的手办按 manufacturer 分组聚合
    role_transactions = db.query(AssetTransaction).filter(
        AssetTransaction.user_id == current_user.id,
        AssetTransaction.transaction_type == 'buy',
        AssetTransaction.is_active == True,
        AssetTransaction.remaining_quantity > 0
    ).all()

    # 按 figure_id 去重
    role_figure_map = {}
    for trans in role_transactions:
        if trans.figure_id not in role_figure_map and trans.figure:
            role_figure_map[trans.figure_id] = trans

    # 按 manufacturer 分组
    manufacturer_groups = defaultdict(list)
    for figure_id, trans in role_figure_map.items():
        manufacturer = trans.figure.manufacturer or "未知厂商"
        manufacturer_groups[manufacturer].append(trans)

    role_figures = []
    role_work_count = len(manufacturer_groups)
    role_total_count = sum(len(items) for items in manufacturer_groups.values())

    # 获取已添加的本命厂商数量（仅统计 favorite_manufacturers 表中的数据）
    manufacturer_count = CollectorManufacturerService.get_count(db, current_user.id)

    # 取各 manufacturer 的代表性手办
    for manufacturer, trans_list in sorted(manufacturer_groups.items(), key=lambda x: len(x[1]), reverse=True):
        trans = trans_list[0]
        # 计算该 manufacturer 组下所有藏品的陪伴天数总和
        total_group_days = 0
        for t in trans_list:
            buy = db.query(AssetTransaction).filter(
                AssetTransaction.figure_id == t.figure_id,
                AssetTransaction.user_id == current_user.id,
                AssetTransaction.transaction_type == 'buy',
                AssetTransaction.is_active == True
            ).order_by(AssetTransaction.transaction_date.asc()).first()
            if buy and buy.transaction_date:
                days = (now - buy.transaction_date).days
                if days > 0:
                    total_group_days += days
        role_figures.append({
            "id": trans.figure_id,
            "name": f"{manufacturer} ({len(trans_list)} 体)",
            "image": get_image_url(trans.figure),
            "holding_days": total_group_days,
            "work": manufacturer,
            "scale": trans.figure.scale or "未知",
            "manufacturer": trans.figure.manufacturer or "未知",
            "transaction_date": None,
            "purchase_price": 0,
            "stock": len(trans_list)
        })

    # ====== 计算各分类陪伴天数 ======
    def calc_total_days(items, field='holding_days'):
        """计算items中某个字段的总和"""
        return sum(item.get(field, 0) or 0 for item in items)

    def calc_avg_days(items, field='holding_days'):
        """计算items中某个字段的平均值"""
        total = calc_total_days(items, field)
        count = len(items)
        if count == 0:
            return 0
        return round(total / count)

    # ====== 构建8个分类 ======
    cabinets = [
        {
            "key": "star",
            "name": "海景房专区",
            "description": "镇柜之宝",
            "icon": "🖼️",
            "icon_bg": "#E8F4F8",
            "count": len(star_figures),
            "companion_days": calc_total_days(star_figures, 'holding_days'),
            "meta": f"{len(star_figures)} 体 · 入柜 180+ 天" if star_figures else "暂无镇柜藏品",
            "items": star_figures[:3]
        },
        {
            "key": "new",
            "name": "最近入柜",
            "description": "新欢",
            "icon": "✨",
            "icon_bg": "#F0F5E8",
            "count": len(new_figures),
            "companion_days": calc_avg_days(new_figures, 'holding_days'),
            "meta": f"{len(new_figures)} 体 · 30 天内新成员" if new_figures else "暂无新入库",
            "items": new_figures[:3]
        },
        {
            "key": "fix",
            "name": "修复工坊",
            "description": "待修复",
            "icon": "🔧",
            "icon_bg": "#FDF6EE",
            "count": len(repair_figures),
            "companion_days": calc_avg_days(repair_figures, 'holding_days'),
            "meta": f"{len(repair_figures)} 体 · 补件/补色中" if repair_figures else "暂无待修复藏品",
            "items": repair_figures[:3]
        },
        {
            "key": "out",
            "name": "已出藏品",
            "description": "已出坑",
            "icon": "📦",
            "icon_bg": "#F5F5F5",
            "count": len(sold_figures),
            "companion_days": calc_avg_days(sold_figures, 'holding_days'),
            "meta": f"{len(sold_figures)} 体 · 找到新主人" if sold_figures else "暂无已出藏品",
            "items": sold_figures[:3]
        },
        {
            "key": "air",
            "name": "预定中",
            "description": "空气谷",
            "icon": "☁️",
            "icon_bg": "#F3E8FF",
            "count": len(air_figures),
            "companion_days": 0,
            "meta": f"{len(air_figures)} 体 · 待付尾款" if air_figures else "暂无预定",
            "items": air_figures[:3]
        },
        {
            "key": "dup",
            "name": "复数专区",
            "description": "复数",
            "icon": "👯",
            "icon_bg": "#FFF2F0",
            "count": len(dup_figures),
            "companion_days": calc_total_days(dup_figures, 'holding_days'),
            "meta": f"{len(dup_figures)} 体 · 同款复购" if dup_figures else "暂无复数藏品",
            "items": dup_figures[:3]
        },
        {
            "key": "wait",
            "name": "待出荷",
            "description": "待出荷",
            "icon": "📅",
            "icon_bg": "#E6F7FF",
            "count": len(wait_figures),
            "companion_days": 0,
            "meta": f"{len(wait_figures)} 体 · 等待出货" if wait_figures else "暂无待出荷",
            "items": wait_figures[:3]
        },
        {
            "key": "role",
            "name": "本命厂商",
            "description": "本命",
            "icon": "🏭",
            "icon_bg": "#E8F4F8",
            "count": manufacturer_count,
            "companion_days": calc_total_days(role_figures, 'holding_days'),
            "meta": f"{manufacturer_count} 家 · 追厂狂魔" if manufacturer_count > 0 else "暂无本命厂商",
            "items": role_figures[:3]
        }
    ]

    return {
        "cabinets": cabinets
    }


# ========== 出柜登记接口 ==========

class RemoveFigureRequest(BaseModel):
    """出柜登记请求参数"""
    figure_id: int
    cabinet_key: str


@router.post("/api/v1/cabinets/remove-figure")
async def remove_figure_from_cabinet(
    request: RemoveFigureRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    将藏品从收藏柜移出（出柜登记）

    根据 cabinet_key 执行不同的移出逻辑：
    - star (海景房专区): 移除 'star' 标签
    - fix (修复工坊): 移除修复相关标签（待修复、缺件、断桩、待补色、蹭色）
    - 其他分类: 暂不支持直接移出

    Args:
        request: 包含 figure_id 和 cabinet_key 的请求体

    Returns:
        { success: bool, message: str }
    """
    figure_id = request.figure_id
    cabinet_key = request.cabinet_key

    # 验证藏品是否存在且属于当前用户

    # 检查该用户是否有该藏品的持仓记录
    has_holding = db.query(AssetTransaction).filter(
        AssetTransaction.figure_id == figure_id,
        AssetTransaction.user_id == current_user.id,
        AssetTransaction.transaction_type == 'buy',
        AssetTransaction.is_active == True,
        AssetTransaction.remaining_quantity > 0
    ).first()

    if not has_holding:
        raise HTTPException(status_code=404, detail="未找到该藏品或无权操作")

    # 根据 cabinet_key 执行不同的移出逻辑
    if cabinet_key == 'star':
        # 海景房专区：移除 star 标签
        star_tag = db.query(Tag).filter(Tag.name == 'star').first()
        if star_tag:
            # 检查是否有关联
            existing = db.execute(
                text("SELECT 1 FROM figure_tag WHERE figure_id = :figure_id AND tag_id = :tag_id"),
                {"figure_id": figure_id, "tag_id": star_tag.id}
            ).fetchone()

            if existing:
                # 删除关联
                db.execute(
                    text("DELETE FROM figure_tag WHERE figure_id = :figure_id AND tag_id = :tag_id"),
                    {"figure_id": figure_id, "tag_id": star_tag.id}
                )
                db.commit()
                return {"success": True, "message": "已从海景房专区移出"}
            else:
                return {"success": True, "message": "该藏品不在海景房专区"}
        else:
            return {"success": True, "message": "无需移出"}

    elif cabinet_key == 'fix':
        # 修复工坊：移除修复相关标签
        repair_tag_names = ['待修复', '缺件', '断桩', '待补色', '蹭色']
        repair_tags = db.query(Tag).filter(Tag.name.in_(repair_tag_names)).all()

        if repair_tags:
            repair_tag_ids = [tag.id for tag in repair_tags]
            # 删除所有修复相关标签的关联
            db.execute(
                text("""
                    DELETE FROM figure_tag
                    WHERE figure_id = :figure_id AND tag_id IN :tag_ids
                """),
                {"figure_id": figure_id, "tag_ids": tuple(repair_tag_ids)}
            )
            db.commit()
            return {"success": True, "message": "已从修复工坊移出"}
        else:
            return {"success": True, "message": "无需移出"}

    elif cabinet_key == 'new':
        # 最近入柜：30天内自动计算，无法手动移出
        return {"success": False, "message": "最近入柜分类由系统自动管理，无法手动移出"}

    elif cabinet_key == 'out':
        # 已出藏品：需要通过卖出流程
        return {"success": False, "message": "已出藏品需要通过卖出订单流程处理"}

    else:
        # 其他分类暂不支持
        return {"success": False, "message": f"暂不支持从 {cabinet_key} 分类移出"}
