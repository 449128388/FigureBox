"""
collector_activity_service.py - 收藏家模式动态流服务

功能说明：
- 提供动态流事件记录的写入和查询
- 采用事件驱动模式，在业务操作完成后异步写入
- 支持按事件类型筛选、按日期分组、分页查询

事件类型：
- BUY: 入手（创建订单）
- FULL_PAY: 尾款已付清
- IN_STOCK: 手办到库
- SELL: 已售出
- OUT: 移出收藏柜
- TAG_ADD: 添加标签
- FIX: 待修复标记
- ORDER_CREATE: 创建订单
- ORDER_CANCEL: 取消订单
- PRICE_UPDATE: 价格更新
"""

from sqlalchemy.orm import Session
from datetime import date, datetime
from typing import Optional, List, Dict

from app.models.activity_feed import ActivityFeed


class CollectorActivityService:
    """收藏家模式动态流服务类"""

    @staticmethod
    def record_event(
        db: Session,
        user_id: int,
        figure_id: int,
        event_type: str,
        event_title: str,
        target_type: Optional[str] = None,
        target_id: Optional[int] = None,
        detail_data: Optional[dict] = None
    ) -> ActivityFeed:
        """
        记录一条动态流事件

        Args:
            db: 数据库会话
            user_id: 用户ID
            figure_id: 手办ID
            event_type: 事件类型（BUY/SELL/OUT等）
            event_title: 展示标题
            target_type: 关联对象类型（order/tag）
            target_id: 关联对象ID
            detail_data: 详情数据JSON

        Returns:
            ActivityFeed: 创建的事件记录
        """
        now = datetime.now()
        feed = ActivityFeed(
            user_id=user_id,
            figure_id=figure_id,
            event_type=event_type,
            event_title=event_title,
            target_type=target_type,
            target_id=target_id,
            detail_data=detail_data,
            event_date=now.date(),
            created_at=now
        )
        db.add(feed)
        db.commit()
        db.refresh(feed)
        return feed

    @staticmethod
    def record_buy_event(
        db: Session,
        user_id: int,
        figure_id: int,
        figure_name: str,
        order_id: int,
        order_no: str,
        amount: float,
        paid_type: str,
        status: str,
        character: Optional[str] = None,
        scale: Optional[str] = None,
        maker: Optional[str] = None,
        cover_image: Optional[str] = None
    ) -> ActivityFeed:
        """记录买入事件"""
        title = f"入手「{figure_name}」，等待补款" if status == "等待补款" else f"入手「{figure_name}」"
        detail = {
            "figure_id": figure_id,
            "figure_name": figure_name,
            "character": character or "",
            "scale": scale or "",
            "maker": maker or "",
            "order_id": order_id,
            "order_no": order_no,
            "amount": amount,
            "paid_type": paid_type,
            "status": status,
            "cover_image": cover_image or ""
        }
        return CollectorActivityService.record_event(
            db=db,
            user_id=user_id,
            figure_id=figure_id,
            event_type="BUY",
            event_title=title,
            target_type="order",
            target_id=order_id,
            detail_data=detail
        )

    @staticmethod
    def record_full_pay_event(
        db: Session,
        user_id: int,
        figure_id: int,
        figure_name: str,
        order_id: int,
        order_no: str,
        paid_amount: float,
        total_paid: float,
        pay_date: str
    ) -> ActivityFeed:
        """记录尾款付清事件"""
        title = f"「{figure_name}」尾款已付清，等待出荷"
        detail = {
            "figure_id": figure_id,
            "figure_name": figure_name,
            "order_id": order_id,
            "order_no": order_no,
            "paid_amount": paid_amount,
            "total_paid": total_paid,
            "status": "已付清待出荷",
            "pay_date": pay_date
        }
        return CollectorActivityService.record_event(
            db=db,
            user_id=user_id,
            figure_id=figure_id,
            event_type="FULL_PAY",
            event_title=title,
            target_type="order",
            target_id=order_id,
            detail_data=detail
        )

    @staticmethod
    def record_in_stock_event(
        db: Session,
        user_id: int,
        figure_id: int,
        figure_name: str,
        in_date: str,
        order_no: Optional[str] = None,
        cost: Optional[float] = None,
        cabinet: Optional[str] = None
    ) -> ActivityFeed:
        """记录手办到库事件"""
        title = f"「{figure_name}」已入库，入柜登记完成"
        detail = {
            "figure_id": figure_id,
            "figure_name": figure_name,
            "in_date": in_date,
            "order_no": order_no or "",
            "cost": cost or 0,
            "cabinet": cabinet or ""
        }
        return CollectorActivityService.record_event(
            db=db,
            user_id=user_id,
            figure_id=figure_id,
            event_type="IN_STOCK",
            event_title=title,
            detail_data=detail
        )

    @staticmethod
    def record_sell_event(
        db: Session,
        user_id: int,
        figure_id: int,
        figure_name: str,
        sell_price: float,
        cost_price: float,
        profit: float,
        buyer: Optional[str] = None,
        out_date: Optional[str] = None,
        hold_days: Optional[int] = None
    ) -> ActivityFeed:
        """记录售出事件"""
        profit_text = f"盈利 ¥{profit}" if profit >= 0 else f"亏损 ¥{abs(profit)}"
        title = f"「{figure_name}」已售出，售价 ¥{int(sell_price)}（{profit_text}）"
        detail = {
            "figure_id": figure_id,
            "figure_name": figure_name,
            "sell_price": sell_price,
            "cost_price": cost_price,
            "profit": profit,
            "buyer": buyer or "",
            "out_date": out_date or "",
            "hold_days": hold_days or 0
        }
        return CollectorActivityService.record_event(
            db=db,
            user_id=user_id,
            figure_id=figure_id,
            event_type="SELL",
            event_title=title,
            detail_data=detail
        )

    @staticmethod
    def record_out_event(
        db: Session,
        user_id: int,
        figure_id: int,
        figure_name: str,
        from_cabinet: str,
        reason: Optional[str] = None
    ) -> ActivityFeed:
        """记录移出收藏柜事件"""
        title = f"「{figure_name}」已移出{from_cabinet}"
        detail = {
            "figure_id": figure_id,
            "figure_name": figure_name,
            "from_cabinet": from_cabinet,
            "reason": reason or ""
        }
        return CollectorActivityService.record_event(
            db=db,
            user_id=user_id,
            figure_id=figure_id,
            event_type="OUT",
            event_title=title,
            detail_data=detail
        )

    @staticmethod
    def record_tag_add_event(
        db: Session,
        user_id: int,
        figure_id: int,
        figure_name: str,
        tag_name: str,
        tag_id: int,
        tag_color: Optional[str] = None
    ) -> ActivityFeed:
        """记录添加标签事件"""
        title = f"为「{figure_name}」添加标签 #{tag_name}"
        detail = {
            "figure_id": figure_id,
            "figure_name": figure_name,
            "tag_name": tag_name,
            "tag_id": tag_id,
            "tag_color": tag_color or ""
        }
        return CollectorActivityService.record_event(
            db=db,
            user_id=user_id,
            figure_id=figure_id,
            event_type="TAG_ADD",
            event_title=title,
            target_type="tag",
            target_id=tag_id,
            detail_data=detail
        )

    @staticmethod
    def record_order_cancel_event(
        db: Session,
        user_id: int,
        figure_id: int,
        figure_name: str,
        order_id: int,
        order_no: str,
        cancel_reason: Optional[str] = None,
        refund_amount: Optional[float] = None
    ) -> ActivityFeed:
        """记录取消订单事件"""
        title = f"取消「{figure_name}」订单"
        detail = {
            "figure_id": figure_id,
            "figure_name": figure_name,
            "order_id": order_id,
            "order_no": order_no,
            "cancel_reason": cancel_reason or "",
            "refund_amount": refund_amount or 0
        }
        return CollectorActivityService.record_event(
            db=db,
            user_id=user_id,
            figure_id=figure_id,
            event_type="ORDER_CANCEL",
            event_title=title,
            target_type="order",
            target_id=order_id,
            detail_data=detail
        )

    # ========== 查询方法 ==========

    @staticmethod
    def get_events(
        db: Session,
        user_id: int,
        event_type: Optional[str] = None,
        offset: int = 0,
        limit: int = 20
    ) -> List[ActivityFeed]:
        """
        获取动态流事件列表（按时间倒序）

        Args:
            db: 数据库会话
            user_id: 用户ID
            event_type: 事件类型筛选（None=全部）
            offset: 分页偏移
            limit: 每页条数

        Returns:
            list[ActivityFeed]: 事件列表
        """
        query = db.query(ActivityFeed).filter(
            ActivityFeed.user_id == user_id
        )

        if event_type and event_type != 'all':
            # 支持分类筛选
            type_map = {
                'buy': ['BUY', 'FULL_PAY', 'IN_STOCK'],
                'sell': ['SELL'],
                'order': ['BUY', 'FULL_PAY', 'ORDER_CREATE', 'ORDER_CANCEL'],
                'tag': ['TAG_ADD', 'FIX'],
                'price': ['PRICE_UPDATE']
            }
            types = type_map.get(event_type, [event_type])
            query = query.filter(ActivityFeed.event_type.in_(types))

        return query.order_by(
            ActivityFeed.created_at.desc()
        ).offset(offset).limit(limit).all()

    @staticmethod
    def get_event_groups(
        db: Session,
        user_id: int,
        event_type: Optional[str] = None,
        offset: int = 0,
        limit: int = 20
    ) -> List[Dict]:
        """
        获取按日期分组的事件列表

        Returns:
            list[dict]: [{ date: str, label: str, items: [...] }, ...]
        """
        events = CollectorActivityService.get_events(
            db=db,
            user_id=user_id,
            event_type=event_type,
            offset=offset,
            limit=limit
        )

        # 按日期分组
        groups = {}
        for ev in events:
            d = ev.event_date.isoformat() if hasattr(ev.event_date, 'isoformat') else str(ev.event_date)
            if d not in groups:
                groups[d] = []
            groups[d].append(ev)

        # 构建返回结果
        today = date.today()
        result = []
        for d in sorted(groups.keys(), reverse=True):
            group_date = date.fromisoformat(d)
            label = CollectorActivityService._get_date_label(group_date, today)
            result.append({
                "date": d,
                "label": label,
                "items": [CollectorActivityService._format_event(ev) for ev in groups[d]]
            })

        return result

    @staticmethod
    def get_event_detail(db: Session, event_id: int) -> Optional[Dict]:
        """
        获取单条事件详情

        Args:
            db: 数据库会话
            event_id: 事件ID

        Returns:
            dict: 事件详情
        """
        ev = db.query(ActivityFeed).filter(ActivityFeed.id == event_id).first()
        if not ev:
            return None
        return CollectorActivityService._format_event(ev)

    # ========== 私有方法 ==========

    @staticmethod
    def _get_date_label(event_date: date, today: date) -> str:
        """获取日期标签（今天/昨天/前天）"""
        delta = (today - event_date).days
        if delta == 0:
            return "今天"
        elif delta == 1:
            return "昨天"
        elif delta == 2:
            return "前天"
        return ""

    @staticmethod
    def _format_event(ev: ActivityFeed) -> Dict:
        """格式化事件为API返回格式"""
        detail = ev.detail_data if ev.detail_data else {}
        if isinstance(detail, str):
            import json
            try:
                detail = json.loads(detail)
            except (json.JSONDecodeError, TypeError):
                detail = {}

        return {
            "id": ev.id,
            "event_type": ev.event_type.lower(),
            "event_title": ev.event_title,
            "figure_id": ev.figure_id,
            "target_type": ev.target_type,
            "target_id": ev.target_id,
            "detail_data": detail,
            "event_date": ev.event_date.isoformat() if hasattr(ev.event_date, 'isoformat') else str(ev.event_date),
            "created_at": ev.created_at.isoformat() if ev.created_at else None
        }
