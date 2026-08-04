"""
seed_activity_feed.py - 动态流历史数据回填脚本

功能说明：
- 从现有业务表中回填 activity_feed 的历史数据
- 支持幂等执行（已存在的记录不会重复写入）

数据来源：
- orders 表 → BUY 事件
- sold_orders 表 → SELL 事件
- cabinet_figure_exclusions 表 → OUT 事件
- order_transactions 表 → FULL_PAY / IN_STOCK 事件

使用方式：
在容器内执行: python -m app.services.dashboard_service.collector_service.seed_activity_feed
"""

import logging
from datetime import datetime

from sqlalchemy.orm import Session

from app.models.database import SessionLocal
from app.models.order import Order
from app.models.figure import Figure
from app.models.sold_order import SoldOrder
from app.models.cabinet_exclusion import CabinetFigureExclusion
from app.models.asset import OrderTransaction
from app.models.activity_feed import ActivityFeed
from app.services.dashboard_service.collector_service.collector_activity_service import CollectorActivityService

logger = logging.getLogger(__name__)

# 收藏柜分类名称映射
CABINET_NAMES = {
    'star': '海景房专区', 'new': '最近入柜', 'fix': '修复工坊',
    'air': '预定中', 'dup': '复数专区', 'wait': '待出荷', 'maker': '本命厂商'
}


class ActivityFeedSeeder:
    """动态流历史数据回填器"""

    def __init__(self, db: Session):
        self.db = db
        self.stats = {"BUY": 0, "SELL": 0, "OUT": 0, "FULL_PAY": 0, "IN_STOCK": 0, "skipped": 0}

    def run(self):
        """执行所有数据回填"""
        logger.info("开始回填动态流历史数据...")
        self._seed_buy_events()
        self._seed_sell_events()
        self._seed_out_events()
        self.db.commit()
        logger.info(f"回填完成: {self.stats}")

    def _event_exists(self, user_id: int, figure_id: int, event_type: str, target_id: int = None) -> bool:
        """检查事件是否已存在（幂等判断）"""
        query = self.db.query(ActivityFeed.id).filter(
            ActivityFeed.user_id == user_id,
            ActivityFeed.figure_id == figure_id,
            ActivityFeed.event_type == event_type
        )
        if target_id:
            query = query.filter(ActivityFeed.target_id == target_id)
        return query.first() is not None

    def _get_figure_name(self, figure_id: int) -> str:
        """获取手办名称"""
        if not figure_id:
            return "未知"
        fig = self.db.query(Figure).filter(Figure.id == figure_id).first()
        return fig.name if fig else "未知"

    def _seed_buy_events(self):
        """从 orders 表回填 BUY 事件"""
        orders = self.db.query(Order).filter(
            Order.is_active == 1,
            Order.status.in_(['未支付', '已支付', '已完成'])
        ).all()

        for order in orders:
            if self._event_exists(order.user_id, order.figure_id, "BUY", order.id):
                self.stats["skipped"] += 1
                continue

            figure_name = self._get_figure_name(order.figure_id)
            status_text = "等待补款" if order.status == "已支付" else ("已付清" if order.status == "已完成" else "未支付")
            paid_type = "定金" if order.order_type == "定金预定" else "全款"

            event = ActivityFeed(
                user_id=order.user_id,
                figure_id=order.figure_id,
                event_type="BUY",
                event_title=f"入手「{figure_name}」" + (f"，{status_text}" if status_text != "已付清" else ""),
                target_type="order",
                target_id=order.id,
                detail_data={
                    "figure_id": order.figure_id,
                    "figure_name": figure_name,
                    "order_id": order.id,
                    "order_no": order.order_number or order.display_order_number or "",
                    "amount": order.deposit or 0,
                    "paid_type": paid_type,
                    "status": status_text,
                    "total_amount": (order.deposit or 0) + (order.balance or 0),
                    "balance": order.balance or 0,
                    "balance_currency": order.balance_currency or "CNY"
                },
                event_date=order.created_at.date() if order.created_at else datetime.now().date(),
                created_at=order.created_at or datetime.now()
            )
            self.db.add(event)
            self.stats["BUY"] += 1

    def _seed_sell_events(self):
        """从 sold_orders 表回填 SELL 事件（所有数据预计算后写入 detail_data 快照）"""
        sold_orders = self.db.query(SoldOrder).filter(
            SoldOrder.is_active == 1
        ).all()

        for so in sold_orders:
            if self._event_exists(so.user_id, so.figure_id, "SELL", so.id):
                self.stats["skipped"] += 1
                continue

            figure_name = self._get_figure_name(so.figure_id)
            profit = so.net_profit or (so.sell_price - so.cost_price - abs(so.shipping_fee or 0) - abs(so.platform_fee or 0))

            # 预计算收益率
            cost_price = so.cost_price or 0
            profit_rate = round((profit / abs(cost_price)) * 100, 2) if cost_price != 0 else 0.0

            # 预计算持有天数
            hold_days = 0
            if so.created_at:
                figure = self.db.query(Figure).filter(Figure.id == so.figure_id).first()
                if figure and figure.purchase_date:
                    out_date = so.created_at.date()
                    hold_days = max((out_date - figure.purchase_date).days, 0)

            # 根据订单状态生成不同的标题
            status_labels = {
                "待发货": "等待发货",
                "已发货": "已发货",
                "已完成": "交易完成",
                "退款/纠纷": "退款/纠纷中"
            }
            status_label = status_labels.get(so.status, so.status)
            event_title = f"「{figure_name}」已售出，售价 ¥{int(so.sell_price)}（{status_label}）"

            event = ActivityFeed(
                user_id=so.user_id,
                figure_id=so.figure_id,
                event_type="SELL",
                event_title=event_title,
                target_type="order",
                target_id=so.id,
                detail_data={
                    "figure_id": so.figure_id,
                    "figure_name": figure_name,
                    "sell_price": so.sell_price,
                    "cost_price": cost_price,
                    "profit": round(profit, 2),
                    "profit_rate": profit_rate,
                    "buyer": so.buyer_phone or "",
                    "out_date": so.created_at.strftime("%Y-%m-%d") if so.created_at else "",
                    "hold_days": hold_days,
                    "order_no": so.order_number or so.display_order_number or "",
                    "status": so.status
                },
                event_date=so.created_at.date() if so.created_at else datetime.now().date(),
                created_at=so.created_at or datetime.now()
            )
            self.db.add(event)
            self.stats["SELL"] += 1

    def _seed_out_events(self):
        """从 cabinet_figure_exclusions 表回填 OUT 事件"""
        exclusions = self.db.query(CabinetFigureExclusion).all()

        for ex in exclusions:
            if self._event_exists(ex.user_id, ex.figure_id, "OUT", ex.id):
                self.stats["skipped"] += 1
                continue

            figure_name = self._get_figure_name(ex.figure_id)
            cabinet_name = CABINET_NAMES.get(ex.cabinet_type, ex.cabinet_type)

            event = ActivityFeed(
                user_id=ex.user_id,
                figure_id=ex.figure_id,
                event_type="OUT",
                event_title=f"「{figure_name}」已移出{cabinet_name}",
                detail_data={
                    "figure_id": ex.figure_id,
                    "figure_name": figure_name,
                    "from_cabinet": cabinet_name,
                    "reason": ex.exclude_reason or ""
                },
                event_date=ex.excluded_at.date() if ex.excluded_at else datetime.now().date(),
                created_at=ex.excluded_at or datetime.now()
            )
            self.db.add(event)
            self.stats["OUT"] += 1


def main():
    """主入口"""
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    db = SessionLocal()
    try:
        seeder = ActivityFeedSeeder(db)
        seeder.run()
    finally:
        db.close()


if __name__ == "__main__":
    main()
