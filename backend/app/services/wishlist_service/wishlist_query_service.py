"""
wishlist_query_service - 愿望清单查询服务

提供列表/详情查询能力：
- 分页 + 多条件过滤（名称/状态/厂商/发售时间区间/标签）
- 元数据组装（cover、status_label、source_label）
- 排序（按发售日期升序）
"""
from typing import List, Optional, Dict, Any
from datetime import date
from sqlalchemy.orm import Session
from sqlalchemy import desc, or_, text

from app.models.figure import Figure


# 状态映射
STATUS_MAP = {
    "wish": "愿望中",
    "released": "已发售",
    "purchased": "已购买",
    "cancelled": "已取消",
}
PURCHASE_TYPE = "wishlist"

# 来源映射（基于 source_url 域名推断）
SOURCE_MAP = [
    ("hpoi.net", "HPOI", "earth-line"),
    ("amiami.com", "Amiami", "earth-line"),
    ("myfigurecollection.net", "MFC", "earth-line"),
    ("bilibili.com", "B站", "earth-line"),
    ("taobao.com", "淘宝", "earth-line"),
]


def _detect_source(source_url: Optional[str]) -> Dict[str, str]:
    """根据 URL 推断来源平台"""
    if not source_url:
        return {"label": "手动录入", "icon": "edit-box-line"}
    url_lower = source_url.lower()
    for domain, label, icon in SOURCE_MAP:
        if domain in url_lower:
            return {"label": label, "icon": icon}
    return {"label": "其他", "icon": "link"}


def _resolve_status(figure: Figure) -> str:
    """获取手办状态（默认 wish）"""
    s = figure.wishlist_status
    if s and s in STATUS_MAP:
        return s
    return "wish"


class WishlistQueryService:
    """愿望清单查询服务"""

    @staticmethod
    def get_wishlist_list(
        db: Session,
        user_id: int,
        skip: int = 0,
        limit: int = 20,
        name: Optional[str] = None,
        status: Optional[str] = None,
        manufacturer: Optional[str] = None,
        release_start: Optional[date] = None,
        release_end: Optional[date] = None,
        tag_names: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """
        获取愿望清单列表（分页 + 多条件过滤）

        Returns:
            {"items": [...], "total": int, "skip": int, "limit": int}
        """
        # 基础查询（2026-08-05 修复：补充 user_id 过滤，否则全量泄漏他人愿望清单）
        query = db.query(Figure).filter(
            Figure.purchase_type == PURCHASE_TYPE,
            Figure.is_active == 1,
            Figure.user_id == user_id,
        )

        if name:
            query = query.filter(
                or_(
                    Figure.name.like(f"%{name}%"),
                    Figure.japanese_name.like(f"%{name}%"),
                )
            )

        if status and status in STATUS_MAP:
            query = query.filter(Figure.wishlist_status == status)

        if manufacturer:
            query = query.filter(Figure.manufacturer == manufacturer)

        if release_start:
            query = query.filter(Figure.release_date >= release_start)
        if release_end:
            query = query.filter(Figure.release_date <= release_end)

        # 标签过滤（2026-07-29 重构：使用 JSON_CONTAINS 替代 figure_tag 关联表；必须使用真实表名 figures.tags）
        if tag_names:
            for tag_name in tag_names:
                if not tag_name:
                    continue
                tag_name_escaped = tag_name.replace('"', '\\"')
                query = query.filter(
                    text(f"JSON_CONTAINS(figures.tags, '\"{tag_name_escaped}\"')")
                )

        # 排序：新创建的在前面
        query = query.order_by(desc(Figure.created_at))

        total = query.count()
        figures = query.offset(skip).limit(limit).all()

        items = [WishlistQueryService._figure_to_item(fig) for fig in figures]

        return {
            "items": items,
            "total": total,
            "skip": skip,
            "limit": limit,
        }

    @staticmethod
    def get_manufacturers(db: Session, user_id: int) -> List[str]:
        """获取当前用户手办中去重后的厂商列表（2026-08-05 修复：补充 user_id 过滤）"""
        results = db.query(Figure.manufacturer).filter(
            Figure.is_active == 1,
            Figure.manufacturer.isnot(None),
            Figure.manufacturer != '',
            Figure.user_id == user_id,
        ).distinct().order_by(Figure.manufacturer).all()
        return [r[0] for r in results]

    @staticmethod
    def get_scales(db: Session, user_id: int) -> List[str]:
        """获取当前用户手办中去重后的比例列表（2026-08-05 修复：补充 user_id 过滤）"""
        results = db.query(Figure.scale).filter(
            Figure.is_active == 1,
            Figure.scale.isnot(None),
            Figure.scale != '',
            Figure.user_id == user_id,
        ).distinct().order_by(Figure.scale).all()
        return [r[0] for r in results]

    @staticmethod
    def get_wishlist_detail(db: Session, user_id: int, figure_id: int) -> Optional[Dict[str, Any]]:
        """获取愿望清单详情（2026-08-05 修复：补充 user_id 过滤，防止越权读取他人愿望）"""
        figure = db.query(Figure).filter(
            Figure.id == figure_id,
            Figure.purchase_type == PURCHASE_TYPE,
            Figure.is_active == 1,
            Figure.user_id == user_id,
        ).first()
        if not figure:
            return None
        return WishlistQueryService._figure_to_item(figure)

    @staticmethod
    def _figure_to_item(figure: Figure) -> Dict[str, Any]:
        """Figure → API 响应项"""
        images = figure.images or []
        cover = images[0] if images else None

        # 2026-07-29 重构：tags 直接使用 figure.tags JSON 字段（List[str]），不再包装为对象
        tags = list(figure.tags or []) if figure.tags else []
        real_status = _resolve_status(figure)

        return {
            "id": figure.id,
            "name": figure.name,
            "japanese_name": figure.japanese_name,
            "manufacturer": figure.manufacturer,
            "scale": figure.scale,
            "painting": figure.painting,
            "original_art": figure.original_art,
            "work": figure.work,
            "material": figure.material,
            "size": figure.size,
            "price": figure.price or 0,
            "currency": figure.currency or "CNY",
            "market_price": figure.market_price or 0,
            "market_currency": figure.market_currency or "CNY",
            "release_date": figure.release_date.isoformat() if figure.release_date else None,
            "purchase_type": figure.purchase_type,
            "source_url": figure.source_url,
            "note": figure.note,
            "cover": cover,
            "images": images,
            "tags": tags,
            "status": real_status,
            "status_label": STATUS_MAP[real_status],
            "source": _detect_source(figure.source_url),
            "created_at": figure.created_at.isoformat() if figure.created_at else None,
            "updated_at": figure.updated_at.isoformat() if figure.updated_at else None,
        }
