"""
collector_manufacturer_service.py - 收藏家模式本命厂商服务

功能说明：
- 提供本命厂商的 CRUD 业务逻辑
- 统计厂商下关联手办的数量（总藏品、在柜、预定中、已出）
- 与收藏柜数据联动，展示厂商维度的收藏统计

API端点对应：
- GET /collector/manufacturers: 获取所有本命厂商列表
- POST /collector/manufacturers: 新增本命厂商
- PUT /collector/manufacturers/{id}: 更新本命厂商
- DELETE /collector/manufacturers/{id}: 删除本命厂商
- GET /collector/manufacturers/{id}: 获取单个厂商详情（含手办列表）
"""

from sqlalchemy.orm import Session
from sqlalchemy import desc
from datetime import datetime, timezone

from app.models.favorite_manufacturer import FavoriteManufacturer
from app.models.asset import AssetTransaction


class CollectorManufacturerService:
    """收藏家模式本命厂商服务类"""

    @staticmethod
    def get_all(db: Session, user_id: int) -> list:
        """获取用户的所有本命厂商列表"""
        manufacturers = db.query(FavoriteManufacturer).filter(
            FavoriteManufacturer.user_id == user_id,
            FavoriteManufacturer.is_active == True
        ).order_by(FavoriteManufacturer.sort_order.asc(), FavoriteManufacturer.created_at.desc()).all()

        result = []
        for m in manufacturers:
            # 统计该厂商下关联手办的数量（通过 manufacturer 字段匹配）
            figure_stats = CollectorManufacturerService._get_figure_stats(db, user_id, m.name)
            result.append({
                "id": m.id,
                "name": m.name,
                "name_jp": m.name_jp or "",
                "description": m.description or "",
                "logo_url": m.logo_url or "",
                "website_url": m.website_url or "",
                "twitter_url": m.twitter_url or "",
                "total_count": figure_stats["total_count"],
                "in_count": figure_stats["in_count"],
                "sort_order": m.sort_order or 0,
                "created_at": m.created_at.strftime("%Y-%m-%d %H:%M:%S") if m.created_at else None,
                "updated_at": m.updated_at.strftime("%Y-%m-%d %H:%M:%S") if m.updated_at else None
            })
        return result

    @staticmethod
    def get_by_id(db: Session, user_id: int, manufacturer_id: int) -> dict:
        """获取单个本命厂商详情含手办列表"""
        m = db.query(FavoriteManufacturer).filter(
            FavoriteManufacturer.id == manufacturer_id,
            FavoriteManufacturer.user_id == user_id,
            FavoriteManufacturer.is_active == True
        ).first()
        if not m:
            return None

        figure_stats = CollectorManufacturerService._get_figure_stats(db, user_id, m.name)
        # 获取该厂商下的手办列表
        figures = CollectorManufacturerService._get_figures_by_manufacturer(db, user_id, m.name)

        return {
            "id": m.id,
            "name": m.name,
            "name_jp": m.name_jp or "",
            "description": m.description or "",
            "logo_url": m.logo_url or "",
            "website_url": m.website_url or "",
            "twitter_url": m.twitter_url or "",
            "total_count": figure_stats["total_count"],
            "in_count": figure_stats["in_count"],
            "air_count": figure_stats["air_count"],
            "out_count": figure_stats["out_count"],
            "figures": figures,
            "sort_order": m.sort_order or 0,
            "created_at": m.created_at.strftime("%Y-%m-%d %H:%M:%S") if m.created_at else None,
            "updated_at": m.updated_at.strftime("%Y-%m-%d %H:%M:%S") if m.updated_at else None
        }

    @staticmethod
    def create(db: Session, user_id: int, data: dict) -> FavoriteManufacturer:
        """新增本命厂商"""
        manufacturer = FavoriteManufacturer(
            user_id=user_id,
            name=data["name"],
            name_jp=data.get("name_jp", ""),
            description=data.get("description", ""),
            logo_url=data.get("logo_url", ""),
            website_url=data.get("website_url", ""),
            twitter_url=data.get("twitter_url", ""),
            sort_order=data.get("sort_order", 0)
        )
        db.add(manufacturer)
        db.commit()
        db.refresh(manufacturer)
        return manufacturer

    @staticmethod
    def update(db: Session, user_id: int, manufacturer_id: int, data: dict) -> FavoriteManufacturer:
        """更新本命厂商"""
        m = db.query(FavoriteManufacturer).filter(
            FavoriteManufacturer.id == manufacturer_id,
            FavoriteManufacturer.user_id == user_id,
            FavoriteManufacturer.is_active == True
        ).first()
        if not m:
            return None

        update_fields = ["name", "name_jp", "description", "logo_url",
                         "website_url", "twitter_url", "sort_order"]
        for field in update_fields:
            if field in data:
                setattr(m, field, data[field])

        db.commit()
        db.refresh(m)
        return m

    @staticmethod
    def delete(db: Session, user_id: int, manufacturer_id: int) -> bool:
        """删除本命厂商（软删除）"""
        m = db.query(FavoriteManufacturer).filter(
            FavoriteManufacturer.id == manufacturer_id,
            FavoriteManufacturer.user_id == user_id,
            FavoriteManufacturer.is_active == True
        ).first()
        if not m:
            return False
        m.is_active = False
        db.commit()
        return True

    @staticmethod
    def get_count(db: Session, user_id: int) -> int:
        """获取用户本命厂商数量"""
        return db.query(FavoriteManufacturer).filter(
            FavoriteManufacturer.user_id == user_id,
            FavoriteManufacturer.is_active == True
        ).count()

    # ========== 私有辅助方法 ==========

    @staticmethod
    def _get_figure_stats(db: Session, user_id: int, manufacturer_name: str) -> dict:
        """
        获取该厂商下关联手办的统计信息

        统计逻辑：
        - total_count: asset_transactions 中已入库（type=buy）且 remaining_quantity > 0 的去重 figure 数量
        - in_count: 在柜数量（当前有库存且未被卖出的 figure）
        - air_count: 预定中数量（有 active 订单的 figure）
        - out_count: 已出数量（有 sell 记录的 figure）
        """
        # 统计有库存的 figure ID（在柜 + 总藏品）
        in_figures = db.query(AssetTransaction.figure_id).filter(
            AssetTransaction.user_id == user_id,
            AssetTransaction.transaction_type == 'buy',
            AssetTransaction.is_active == True,
            AssetTransaction.remaining_quantity > 0
        ).distinct().all()
        in_figure_ids = set(f[0] for f in in_figures)

        # 已卖出的 figure ID
        sold_figures = db.query(AssetTransaction.figure_id).filter(
            AssetTransaction.user_id == user_id,
            AssetTransaction.transaction_type == 'sell',
            AssetTransaction.is_active == True
        ).distinct().all()
        sold_figure_ids = set(f[0] for f in sold_figures)

        # 预定中的 figure ID（通过订单表）
        from app.models.order import Order
        air_orders = db.query(Order.figure_id).filter(
            Order.user_id == user_id,
            Order.order_type.in_(['定金预定', '全款预定']),
            Order.status.in_(['未支付', '已支付']),
            Order.is_active == 1
        ).distinct().all()
        air_figure_ids = set(f[0] for f in air_orders)

        # 获取所有在手 figure 中 manufacturer 匹配的
        # 简化处理：直接从 figures 表根据 manufacturer 名称匹配
        from app.models.figure import Figure
        from sqlalchemy import func

        # 总藏品数（只要有 buy 记录且 manufacturer 匹配）
        total = db.query(Figure.id).filter(
            Figure.manufacturer.ilike(f"%{manufacturer_name}%"),
            Figure.is_active == True
        ).count()

        # 在柜数（有库存且 manufacturer 匹配）
        in_count = 0
        air_count = 0
        out_count = 0

        # 从 asset_transactions 关联 figure 表计算更准确
        matched_figure_ids = db.query(Figure.id).filter(
            Figure.manufacturer.ilike(f"%{manufacturer_name}%"),
            Figure.is_active == True
        ).all()
        matched_ids = set(f[0] for f in matched_figure_ids)

        in_count = len(matched_ids & in_figure_ids)
        air_count = len(matched_ids & air_figure_ids)
        out_count = len(matched_ids & sold_figure_ids)

        return {
            "total_count": total or len(matched_ids),
            "in_count": in_count,
            "air_count": air_count,
            "out_count": out_count
        }

    @staticmethod
    def _get_figures_by_manufacturer(db: Session, user_id: int, manufacturer_name: str) -> list:
        """
        获取该厂商下的手办列表（用于厂商详情页）

        从 asset_transactions 中查询该用户、该厂商关联的 figure 列表
        """
        from app.models.figure import Figure

        # 获取 manufacturer 匹配的 figure
        figures = db.query(Figure).filter(
            Figure.manufacturer.ilike(f"%{manufacturer_name}%"),
            Figure.is_active == True
        ).all()

        result = []
        for fig in figures:
            # 获取该 figure 的所有状态（同一手办可同时存在多种状态）
            statuses = []

            # 1. 检查是否有预定中订单
            from app.models.order import Order
            air_orders = db.query(Order).filter(
                Order.figure_id == fig.id,
                Order.user_id == user_id,
                Order.order_type.in_(['定金预定', '全款预定']),
                Order.status.in_(['未支付', '已支付']),
                Order.is_active == 1
            ).all()
            if air_orders:
                has_paid = any(o.status == '已支付' for o in air_orders)
                has_unpaid = any(o.status == '未支付' for o in air_orders)
                if has_paid:
                    statuses.append('air_paid')
                if has_unpaid:
                    statuses.append('air_unpaid')

            # 2. 检查是否有在库库存
            stock_count = db.query(AssetTransaction).filter(
                AssetTransaction.figure_id == fig.id,
                AssetTransaction.user_id == user_id,
                AssetTransaction.transaction_type == 'buy',
                AssetTransaction.is_active == True,
                AssetTransaction.remaining_quantity > 0
            ).count()
            if stock_count > 0:
                statuses.append('in')

            # 3. 检查是否有已出记录
            sell_count = db.query(AssetTransaction).filter(
                AssetTransaction.figure_id == fig.id,
                AssetTransaction.user_id == user_id,
                AssetTransaction.transaction_type == 'sell',
                AssetTransaction.is_active == True
            ).count()
            if sell_count > 0:
                statuses.append('out')

            # 兜底：没有任何状态时默认为在柜
            if not statuses:
                statuses.append('in')

            # 获取首次入库日期
            first_buy = db.query(AssetTransaction).filter(
                AssetTransaction.figure_id == fig.id,
                AssetTransaction.user_id == user_id,
                AssetTransaction.transaction_type == 'buy',
                AssetTransaction.is_active == True
            ).order_by(AssetTransaction.transaction_date.asc()).first()

            # 计算陪伴天数
            companion_days = 0
            if first_buy and first_buy.transaction_date:
                days = (datetime.now() - first_buy.transaction_date).days
                if days > 0:
                    companion_days = days

            result.append({
                "id": fig.id,
                "name": fig.name or "未知",
                "image": (fig.images[0] if fig.images and len(fig.images) > 0 else ""),
                "work": fig.work or "未知",
                "scale": fig.scale or "未知",
                "manufacturer": fig.manufacturer or "未知",
                "statuses": statuses,
                "transaction_date": first_buy.transaction_date.strftime("%Y-%m-%d") if first_buy and first_buy.transaction_date else None,
                "purchase_price": first_buy.price if first_buy else 0,
                "companion_days": companion_days
            })

        return result
