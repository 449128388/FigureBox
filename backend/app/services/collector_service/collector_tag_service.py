"""
collector_tag_service.py - 收藏家模式标签云服务

功能说明：
- 提供系统标签（自动计算）和用户标签（手动添加）的业务逻辑
- 系统标签基于业务规则动态计算：海景房、破发区、待补款、已出坑
- 用户标签来自 figure_tag 中间表中的用户自定义标签

系统标签计算规则：
1. 海景房: 持有180天以上 + 当前在库
2. 破发区: 当前市场价 < 买入加权平均成本
3. 待补款: 已付定金但尾款未支付的订单
4. 已出坑: 已卖出的手办（SoldOrder）
"""

from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, timedelta
from typing import List, Set, Dict

from app.models.figure import Figure
from app.models.tag import Tag, figure_tag
from app.models.order import Order
from app.models.asset import AssetTransaction
from app.models.sold_order import SoldOrder


class CollectorTagService:
    """收藏家模式标签云服务类"""

    # 系统标签定义
    SYSTEM_TAGS = {
        "海景房": "持有 180+ 天且当前在库",
        "破发区": "当前市场价 < 买入成本",
        "待补款": "已付定金但尾款未支付",
        "已出坑": "已卖出的手办"
    }

    @staticmethod
    def get_user_tags(db: Session, user_id: int) -> list:
        """
        获取用户标签（手动添加的 tags，来自 figure_tag 中间表）

        统计该用户关联的所有手办（通过 orders/asset_transactions）中使用的 tag

        Returns:
            list[dict]: [{ name: str, count: int, type: "user" }, ...]
        """
        # 获取该用户所有有关联的手办ID
        user_figure_ids = CollectorTagService._get_user_figure_ids(db, user_id)

        if not user_figure_ids:
            return []

        # 查询这些手办关联的所有标签
        tag_links = db.execute(
            figure_tag.select().where(figure_tag.c.figure_id.in_(user_figure_ids))
        ).fetchall()

        tag_figure_map: Dict[int, Set[int]] = {}
        for link in tag_links:
            tag_id = link.tag_id
            figure_id = link.figure_id
            if tag_id not in tag_figure_map:
                tag_figure_map[tag_id] = set()
            tag_figure_map[tag_id].add(figure_id)

        if not tag_figure_map:
            return []

        # 获取标签名称
        tag_ids = list(tag_figure_map.keys())
        tags = db.query(Tag).filter(Tag.id.in_(tag_ids)).all()
        tag_name_map = {t.id: t.name for t in tags}

        result = []
        for tag_id, figure_ids in tag_figure_map.items():
            name = tag_name_map.get(tag_id)
            if name and name not in CollectorTagService.SYSTEM_TAGS:
                result.append({
                    "name": name,
                    "count": len(figure_ids),
                    "type": "user"
                })

        return result

    @staticmethod
    def get_system_tags(db: Session, user_id: int) -> list:
        """
        获取系统标签（自动计算）

        Returns:
            list[dict]: [{ name: str, count: int, type: "system", description: str }, ...]
        """
        now = datetime.now()

        # 获取用户所有有效买入持仓
        holdings = db.query(AssetTransaction).filter(
            AssetTransaction.user_id == user_id,
            AssetTransaction.transaction_type == 'buy',
            AssetTransaction.is_active == True,
            AssetTransaction.remaining_quantity > 0
        ).all()

        # 按 figure_id 去重，取最早的交易
        figure_holdings: Dict[int, AssetTransaction] = {}
        for h in holdings:
            if h.figure_id not in figure_holdings:
                figure_holdings[h.figure_id] = h
            else:
                existing = figure_holdings[h.figure_id]
                if h.transaction_date and existing.transaction_date and h.transaction_date < existing.transaction_date:
                    figure_holdings[h.figure_id] = h

        # 获取有有效订单的手办列表（用于待补款计算）
        valid_orders = db.query(Order).filter(
            Order.user_id == user_id,
            Order.is_active == 1,
            Order.status != "已取消"
        ).all()

        # 1. 海景房: 涨幅 >= 50% 并且 持有180天以上
        sea_view_count = 0
        # 2. 破发区: 当前市场价 < 买入加权平均成本
        loss_count = 0

        for figure_id, trans in figure_holdings.items():
            if not trans.transaction_date:
                continue

            fig = db.query(Figure).filter(Figure.id == figure_id).first()
            if not fig:
                continue

            holding_days = (now - trans.transaction_date).days
            cost_price = fig.average_purchase_price or trans.price or 0
            current_price = fig.market_price or fig.price or 0

            # 海景房: 持有 180 天以上 + 当前在库
            if holding_days > 180:
                sea_view_count += 1

            # 破发区: 当前市场价 < 买入加权平均成本
            if cost_price > 0:
                profit_percentage = ((current_price - cost_price) / cost_price) * 100
                if profit_percentage < 0:
                    loss_count += 1

        # 3. 待补款: 已付定金但尾款未支付的订单（按 figure_id 去重）
        pending_payment_orders = db.query(Order.figure_id).filter(
            Order.user_id == user_id,
            Order.order_type == '定金预定',
            Order.status == '未支付',
            Order.is_active == 1
        ).distinct().all()
        pending_payment_count = len(pending_payment_orders)

        # 4. 已出坑: 已卖出的手办（SoldOrder，按 figure_id 去重）
        sold_figure_ids = db.query(SoldOrder.figure_id).filter(
            SoldOrder.user_id == user_id,
            SoldOrder.is_active == True
        ).distinct().all()
        sold_count = len(sold_figure_ids)

        tags = [
            {"name": "海景房", "count": sea_view_count, "type": "system", "description": CollectorTagService.SYSTEM_TAGS["海景房"]},
            {"name": "破发区", "count": loss_count, "type": "system", "description": CollectorTagService.SYSTEM_TAGS["破发区"]},
            {"name": "待补款", "count": pending_payment_count, "type": "system", "description": CollectorTagService.SYSTEM_TAGS["待补款"]},
            {"name": "已出坑", "count": sold_count, "type": "system", "description": CollectorTagService.SYSTEM_TAGS["已出坑"]}
        ]

        return tags

    @staticmethod
    def get_figures_by_tag(db: Session, user_id: int, tag_name: str) -> list:
        """
        根据标签名称获取匹配的手办列表

        Args:
            db: 数据库会话
            user_id: 用户ID
            tag_name: 标签名称

        Returns:
            list[dict]: 手办列表
        """
        figure_ids = set()

        if tag_name in CollectorTagService.SYSTEM_TAGS:
            # 系统标签 - 用业务规则匹配
            figure_ids = CollectorTagService._get_system_tag_figure_ids(db, user_id, tag_name)
        else:
            # 用户标签 - 从 figure_tag 中间表查询
            tag = db.query(Tag).filter(Tag.name == tag_name).first()
            if tag:
                links = db.execute(
                    figure_tag.select().where(figure_tag.c.tag_id == tag.id)
                ).fetchall()
                figure_ids = set(link.figure_id for link in links)

        if not figure_ids:
            return []

        # 获取手办详细信息
        figures = db.query(Figure).filter(Figure.id.in_(figure_ids), Figure.is_active == True).all()
        result = []
        for fig in figures:
            # 获取库存
            stock = db.query(
                func.coalesce(func.sum(AssetTransaction.remaining_quantity), 0)
            ).filter(
                AssetTransaction.figure_id == fig.id,
                AssetTransaction.user_id == user_id,
                AssetTransaction.transaction_type == 'buy',
                AssetTransaction.is_active == True
            ).scalar() or 0

            # 获取入库日期
            first_buy = db.query(AssetTransaction).filter(
                AssetTransaction.figure_id == fig.id,
                AssetTransaction.user_id == user_id,
                AssetTransaction.transaction_type == 'buy',
                AssetTransaction.is_active == True
            ).order_by(AssetTransaction.transaction_date.asc()).first()

            result.append({
                "id": fig.id,
                "name": fig.name or "未知",
                "image": fig.images[0] if fig.images and len(fig.images) > 0 else "",
                "work": fig.work or "未知",
                "scale": fig.scale or "未知",
                "manufacturer": fig.manufacturer or "未知",
                "stock": stock,
                "transaction_date": first_buy.transaction_date.strftime("%Y-%m-%d") if first_buy and first_buy.transaction_date else None,
                "purchase_price": first_buy.price if first_buy else 0,
                "market_price": fig.market_price or 0,
                "average_purchase_price": fig.average_purchase_price or 0
            })

        return result

    # ========== 私有方法 ==========

    @staticmethod
    def _get_user_figure_ids(db: Session, user_id: int) -> set:
        """获取用户有关联的所有手办ID集合"""
        ids = set()

        # 从资产交易中获取
        buy_ids = db.query(AssetTransaction.figure_id).filter(
            AssetTransaction.user_id == user_id,
            AssetTransaction.is_active == True
        ).distinct().all()
        ids.update(f[0] for f in buy_ids if f[0])

        # 从订单中获取
        order_ids = db.query(Order.figure_id).filter(
            Order.user_id == user_id,
            Order.is_active == 1
        ).distinct().all()
        ids.update(f[0] for f in order_ids if f[0])

        # 从卖出记录获取
        sold_ids = db.query(SoldOrder.figure_id).filter(
            SoldOrder.user_id == user_id,
            SoldOrder.is_active == True
        ).distinct().all()
        ids.update(f[0] for f in sold_ids if f[0])

        return ids

    @staticmethod
    def _get_system_tag_figure_ids(db: Session, user_id: int, tag_name: str) -> set:
        """根据系统标签名称获取匹配的手办ID集合"""
        now = datetime.now()
        figure_ids = set()

        if tag_name == "海景房":
            holdings = db.query(AssetTransaction).filter(
                AssetTransaction.user_id == user_id,
                AssetTransaction.transaction_type == 'buy',
                AssetTransaction.is_active == True,
                AssetTransaction.remaining_quantity > 0
            ).all()

            # 按figure_id去重取最早
            figure_holdings = {}
            for h in holdings:
                if h.figure_id not in figure_holdings:
                    figure_holdings[h.figure_id] = h
                else:
                    existing = figure_holdings[h.figure_id]
                    if h.transaction_date and existing.transaction_date and h.transaction_date < existing.transaction_date:
                        figure_holdings[h.figure_id] = h

            for figure_id, trans in figure_holdings.items():
                if not trans.transaction_date:
                    continue
                holding_days = (now - trans.transaction_date).days
                if holding_days <= 180:
                    continue
                # 海景房: 持有 180 天以上 + 当前在库
                figure_ids.add(figure_id)

        elif tag_name == "破发区":
            holdings = db.query(AssetTransaction).filter(
                AssetTransaction.user_id == user_id,
                AssetTransaction.transaction_type == 'buy',
                AssetTransaction.is_active == True,
                AssetTransaction.remaining_quantity > 0
            ).all()

            figure_holdings = {}
            for h in holdings:
                if h.figure_id not in figure_holdings:
                    figure_holdings[h.figure_id] = h

            for figure_id, trans in figure_holdings.items():
                fig = db.query(Figure).filter(Figure.id == figure_id).first()
                if not fig:
                    continue
                cost_price = fig.average_purchase_price or trans.price or 0
                current_price = fig.market_price or fig.price or 0
                if cost_price > 0 and current_price < cost_price:
                    figure_ids.add(figure_id)

        elif tag_name == "待补款":
            orders = db.query(Order).filter(
                Order.user_id == user_id,
                Order.order_type == '定金预定',
                Order.status == '未支付',
                Order.is_active == 1
            ).all()
            figure_ids = set(o.figure_id for o in orders if o.figure_id)

        elif tag_name == "已出坑":
            sold_orders = db.query(SoldOrder).filter(
                SoldOrder.user_id == user_id,
                SoldOrder.is_active == True
            ).all()
            figure_ids = set(so.figure_id for so in sold_orders if so.figure_id)

        return figure_ids
