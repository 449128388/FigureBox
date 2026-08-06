"""
wishlist_stats_service - 愿望清单统计服务

提供四类核心指标：
- 愿望总数：purchase_type='wishlist' 的记录数
- 本月即将发售：release_date 落在本月内的手办数
- 预算合计：所有「愿望中」和「已发售」状态的 price 总和（按 currency 折算 CNY）
- 待购数量：已发售但尚未购买的数量
"""
from typing import Dict, Any, List
from datetime import date
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_

from app.models.figure import Figure
from app.services.exchange_rate_service import ExchangeRateService
from .wishlist_query_service import PURCHASE_TYPE


class WishlistStatsService:
    """愿望清单统计服务"""

    @staticmethod
    def get_stats(db: Session, user_id: int) -> Dict[str, Any]:
        """
        获取愿望清单统计指标（2026-08-05 修复：全链路 user_id 数据隔离）

        Returns:
            {
                "total": 愿望总数,
                "releasing_this_month": 本月即将发售,
                "budget_total": 预算合计（CNY）,
                "pending_purchase": 待购数量,
                "status_distribution": 状态分布,
                "top_manufacturers": TOP 厂商,
            }
        """
        # 基础查询（2026-08-05 修复：按用户过滤，防止跨用户汇总）
        base_query = db.query(Figure).filter(
            Figure.purchase_type == PURCHASE_TYPE,
            Figure.is_active == 1,
            Figure.user_id == user_id,
        )

        # 1. 愿望总数
        total = base_query.count()

        # 2. 本月即将发售
        today = date.today()
        first_day = today.replace(day=1)
        if first_day.month == 12:
            next_month_first = first_day.replace(year=first_day.year + 1, month=1)
        else:
            next_month_first = first_day.replace(month=first_day.month + 1)

        releasing_this_month = base_query.filter(
            Figure.release_date >= first_day,
            Figure.release_date < next_month_first,
        ).count()

        # 3. 预算合计：所有「愿望中」+「已发售」状态的 price 总和（折算 CNY）
        budget_total = 0.0
        budget_figures = base_query.filter(
            Figure.wishlist_status.in_(["wish", "released"])
        ).all()
        for fig in budget_figures:
            if fig.price and fig.price > 0:
                cny_price = WishlistStatsService._convert_to_cny(
                    db, float(fig.price), fig.currency or "CNY"
                )
                budget_total += cny_price

        # 4. 待购数量：已发售但未购买
        pending_purchase = base_query.filter(
            Figure.wishlist_status == "released"
        ).count()

        # 5. 状态分布（2026-08-05 修复：补 user_id 过滤）
        status_dist_rows = db.query(
            Figure.wishlist_status,
            func.count(Figure.id).label("count"),
        ).filter(
            Figure.purchase_type == PURCHASE_TYPE,
            Figure.is_active == 1,
            Figure.user_id == user_id,
        ).group_by(Figure.wishlist_status).all()

        status_distribution = {}
        for status, count in status_dist_rows:
            status_distribution[status or "wish"] = count

        # 6. TOP 厂商（2026-08-05 修复：补 user_id 过滤）
        top_mfr_rows = db.query(
            Figure.manufacturer,
            func.count(Figure.id).label("count"),
        ).filter(
            Figure.purchase_type == PURCHASE_TYPE,
            Figure.is_active == 1,
            Figure.user_id == user_id,
            Figure.manufacturer.isnot(None),
            Figure.manufacturer != "",
        ).group_by(Figure.manufacturer) \
         .order_by(func.count(Figure.id).desc()) \
         .limit(10).all()

        top_manufacturers = [
            {"name": name, "count": count}
            for name, count in top_mfr_rows
        ]

        # 7. 较上月新增（上月同期总数，用于趋势展示；2026-08-05 修复：补 user_id 过滤）
        from datetime import timedelta
        last_month_start = (first_day - timedelta(days=1)).replace(day=1)
        last_month_count = db.query(Figure).filter(
            Figure.purchase_type == PURCHASE_TYPE,
            Figure.is_active == 1,
            Figure.user_id == user_id,
            Figure.created_at >= last_month_start,
            Figure.created_at < first_day,
        ).count()
        last_month_total = total - last_month_count

        # 8. 本月即将发售的名称（最多 3 个；2026-08-05 修复：补 user_id 过滤）
        releasing_names = [
            f.name for f in db.query(Figure.name).filter(
                Figure.purchase_type == PURCHASE_TYPE,
                Figure.is_active == 1,
                Figure.user_id == user_id,
                Figure.release_date >= first_day,
                Figure.release_date < next_month_first,
                Figure.name.isnot(None),
            ).order_by(Figure.release_date.asc()).limit(3).all()
        ]

        # 9. 已转采购金额（2026-08-05 修复：补 user_id 过滤）
        transferred_amount = 0.0
        transferred_rows = db.query(Figure).filter(
            Figure.purchase_type != PURCHASE_TYPE,
            Figure.is_active == 1,
            Figure.user_id == user_id,
            Figure.wishlist_status == "purchased",
            Figure.price.isnot(None),
            Figure.price > 0,
        ).all()
        for fig in transferred_rows:
            cny_price = WishlistStatsService._convert_to_cny(
                db, float(fig.price), fig.currency or "CNY"
            )
            transferred_amount += cny_price

        released_purchase_count = pending_purchase

        return {
            "total": total,
            "releasing_this_month": releasing_this_month,
            "budget_total": round(budget_total, 2),
            "pending_purchase": pending_purchase,
            "status_distribution": status_distribution,
            "top_manufacturers": top_manufacturers,
            "last_month_total": last_month_total,
            "releasing_names": releasing_names,
            "transferred_amount": round(transferred_amount, 2),
            "released_purchase_count": released_purchase_count,
        }

    @staticmethod
    def _convert_to_cny(db: Session, amount: float, currency: str) -> float:
        """将金额折算为 CNY"""
        if currency == "CNY" or not currency:
            return amount
        try:
            return ExchangeRateService.to_cny(db, amount, currency)
        except Exception:
            return amount
