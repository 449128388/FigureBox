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
from datetime import date, datetime, timedelta
from typing import Optional, List, Dict
from sqlalchemy import func, text

from app.models.activity_feed import ActivityFeed
from app.models.figure import Figure

# 汇率配置：相对人民币的汇率（与 asset_core_calculations.py 保持一致）
PRICE_EXCHANGE_RATES = {
    'CNY': 1.0,
    'JPY': 1/23,
    'USD': 7.0,
    'EUR': 8.0
}


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
            created_at=now,
            updated_at=now
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
        currency: Optional[str] = "CNY",
        balance: Optional[float] = 0,
        balance_currency: Optional[str] = "CNY"
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
            "currency": currency or "CNY",
            "balance": balance or 0,
            "balance_currency": balance_currency or "CNY"
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
        pay_date: str,
        deposit_paid: Optional[float] = None,
        character: Optional[str] = None,
        scale: Optional[str] = None,
        maker: Optional[str] = None,
        due_date: Optional[str] = None
    ) -> ActivityFeed:
        """记录尾款付清事件"""
        title = f"「{figure_name}」尾款已付清，等待出荷"
        detail = {
            "figure_id": figure_id,
            "figure_name": figure_name,
            "character": character or "",
            "scale": scale or "",
            "maker": maker or "",
            "order_id": order_id,
            "order_no": order_no,
            "deposit_paid": deposit_paid or 0,
            "paid_amount": paid_amount,
            "total_paid": total_paid,
            "status": "等待出荷",
            "pay_date": pay_date,
            "due_date": due_date or ""
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
        cabinet: Optional[str] = None,
        target_id: Optional[int] = None,
        target_type: Optional[str] = None
    ) -> ActivityFeed:
        """记录手办到库事件"""
        title = f"「{figure_name}」已入库，入柜登记完成"
        detail = {
            "figure_id": figure_id,
            "figure_name": figure_name,
            "in_date": in_date,
            "order_no": order_no or "",
            "cost": cost or 0,
            "cabinet": cabinet or "",
            "status": "完成入库"
        }
        return CollectorActivityService.record_event(
            db=db,
            user_id=user_id,
            figure_id=figure_id,
            event_type="IN_STOCK",
            event_title=title,
            target_type=target_type or "",
            target_id=target_id or 0,
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
        profit_rate: Optional[float] = None,
        buyer: Optional[str] = None,
        out_date: Optional[str] = None,
        hold_days: Optional[int] = None,
        order_no: Optional[str] = None,
        status: Optional[str] = None,
        target_id: Optional[int] = None,
        tracking_number: Optional[str] = None,
        logistics_company: Optional[str] = None,
        refund_amount: Optional[float] = None
    ) -> ActivityFeed:
        """记录售出事件（所有数据一次性写入 detail_data 快照）"""
        if profit_rate is None and cost_price and cost_price != 0:
            profit_rate = round((profit / abs(cost_price)) * 100, 2)

        # 根据状态生成标题
        if status == "待发货":
            profit_text = f"盈利 ¥{profit}" if profit >= 0 else f"亏损 ¥{abs(profit)}"
            title = f"「{figure_name}」已完成售出，当前待安排寄出，售价 ¥{sell_price}（{profit_text}）"
        elif status == "已发货":
            tn = tracking_number or "暂无"
            lc = logistics_company or "暂无"
            title = f"「{figure_name}」已完成售出，当前已安排寄出，快递单号 {tn} (物流公司 {lc})"
        elif status == "已完成":
            profit_text = f"盈利 ¥{profit}" if profit >= 0 else f"亏损 ¥{abs(profit)}"
            title = f"「{figure_name}」订单交易完成，买家已签收，售价 ¥{sell_price}（{profit_text}）"
        elif status == "退款/纠纷":
            refund = refund_amount or sell_price
            title = f"「{figure_name}」订单产生售后争议，已完成退款，退款金额 ¥{refund}"
        else:
            profit_text = f"盈利 ¥{profit}" if profit >= 0 else f"亏损 ¥{abs(profit)}"
            title = f"「{figure_name}」已售出，售价 ¥{int(sell_price)}（{profit_text}）"

        detail = {
            "figure_id": figure_id,
            "figure_name": figure_name,
            "sell_price": sell_price,
            "cost_price": cost_price,
            "profit": profit,
            "profit_rate": profit_rate or 0.0,
            "buyer": buyer or "",
            "out_date": out_date or "",
            "hold_days": hold_days or 0,
            "order_no": order_no or "",
            "status": status or "",
            "tracking_number": tracking_number or "",
            "logistics_company": logistics_company or "",
            "refund_amount": refund_amount or 0
        }
        return CollectorActivityService.record_event(
            db=db,
            user_id=user_id,
            figure_id=figure_id,
            event_type="SELL",
            event_title=title,
            target_type="order",
            target_id=target_id,
            detail_data=detail
        )

    @staticmethod
    def record_sell_update_event(
        db: Session,
        user_id: int,
        figure_id: int,
        figure_name: str,
        sell_price: float,
        cost_price: float,
        profit: float,
        profit_rate: Optional[float] = None,
        buyer: Optional[str] = None,
        out_date: Optional[str] = None,
        hold_days: Optional[int] = None,
        order_no: Optional[str] = None,
        status: Optional[str] = None,
        target_id: Optional[int] = None,
        tracking_number: Optional[str] = None,
        logistics_company: Optional[str] = None,
        refund_amount: Optional[float] = None
    ) -> ActivityFeed:
        """
        记录售出事件更新（追加新记录，不修改历史）

        Append-only 设计：编辑已出售订单后创建一条新的 SELL 事件记录，
        保留原始 SELL 事件作为历史快照。

        Returns:
            ActivityFeed: 创建的事件记录
        """
        if profit_rate is None and cost_price and cost_price != 0:
            profit_rate = round((profit / abs(cost_price)) * 100, 2)

        # 根据状态生成标题
        if status == "待发货":
            profit_text = f"盈利 ¥{profit}" if profit >= 0 else f"亏损 ¥{abs(profit)}"
            title = f"「{figure_name}」已完成售出，当前待安排寄出，售价 ¥{sell_price}（{profit_text}）"
        elif status == "已发货":
            tn = tracking_number or "暂无"
            lc = logistics_company or "暂无"
            title = f"「{figure_name}」已完成售出，当前已安排寄出，快递单号 {tn} (物流公司 {lc})"
        elif status == "已完成":
            profit_text = f"盈利 ¥{profit}" if profit >= 0 else f"亏损 ¥{abs(profit)}"
            title = f"「{figure_name}」订单交易完成，买家已签收，售价 ¥{sell_price}（{profit_text}）"
        elif status == "退款/纠纷":
            refund = refund_amount or sell_price
            title = f"「{figure_name}」订单产生售后争议，已完成退款，退款金额 ¥{refund}"
        else:
            profit_text = f"盈利 ¥{profit}" if profit >= 0 else f"亏损 ¥{abs(profit)}"
            title = f"「{figure_name}」已售出，售价 ¥{int(sell_price)}（{profit_text}）"

        detail = {
            "figure_id": figure_id,
            "figure_name": figure_name,
            "sell_price": sell_price,
            "cost_price": cost_price,
            "profit": profit,
            "profit_rate": profit_rate or 0.0,
            "buyer": buyer or "",
            "out_date": out_date or "",
            "hold_days": hold_days or 0,
            "order_no": order_no or "",
            "status": status or "",
            "tracking_number": tracking_number or "",
            "logistics_company": logistics_company or "",
            "refund_amount": refund_amount or 0
        }
        return CollectorActivityService.record_event(
            db=db,
            user_id=user_id,
            figure_id=figure_id,
            event_type="SELL",
            event_title=title,
            target_type="order",
            target_id=target_id,
            detail_data=detail
        )

    @staticmethod
    def _get_currency_symbol(currency: str) -> str:
        """获取货币符号"""
        symbols = {
            'CNY': '¥', 'JPY': 'JP ¥', 'USD': '$', 'EUR': '€',
            'GBP': '£', 'HKD': 'HK$', 'TWD': 'NT$', 'KRW': '₩'
        }
        return symbols.get(currency, currency)

    @staticmethod
    def record_buy_update_event(
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
        currency: Optional[str] = "CNY",
        balance: Optional[float] = 0,
        balance_currency: Optional[str] = "CNY",
        old_deposit: Optional[float] = None,
        old_deposit_currency: Optional[str] = None,
        old_balance: Optional[float] = None,
        old_balance_currency: Optional[str] = None
    ) -> ActivityFeed:
        """
        记录买入事件更新（追加新记录，不修改历史）

        Append-only 设计：编辑订单后创建一条新的 BUY 事件记录，
        保留原始 BUY 事件作为历史快照。自动检测定金/尾款金额和币种变更，
        在 event_title 中描述具体变更内容。

        Returns:
            ActivityFeed: 创建的事件记录
        """
        # 检测变更类型并生成标题（支持多字段组合变更）
        deposit_desc = None
        balance_desc = None

        # 检测定金相关变更（金额或币种任一变化）
        if old_deposit is not None and old_deposit_currency is not None:
            old_amt = old_deposit or 0
            new_amt = amount or 0
            old_cur = old_deposit_currency or "CNY"
            new_cur = currency or "CNY"
            if old_amt != new_amt or old_cur != new_cur:
                old_sym = CollectorActivityService._get_currency_symbol(old_cur)
                new_sym = CollectorActivityService._get_currency_symbol(new_cur)
                deposit_desc = f"定金 {old_sym}{old_amt} 修改为 {new_sym}{new_amt}"

        # 检测尾款相关变更（金额或币种任一变化）
        if old_balance is not None and old_balance_currency is not None:
            old_bal = old_balance or 0
            new_bal = balance or 0
            old_bcur = old_balance_currency or "CNY"
            new_bcur = balance_currency or "CNY"
            if old_bal != new_bal or old_bcur != new_bcur:
                old_bsym = CollectorActivityService._get_currency_symbol(old_bcur)
                new_bsym = CollectorActivityService._get_currency_symbol(new_bcur)
                balance_desc = f"尾款 {old_bsym}{old_bal} 修改为 {new_bsym}{new_bal}"

        # 组合标题
        title = None
        if deposit_desc and balance_desc:
            title = f"「{figure_name}」订单定金和尾款发生变动，{deposit_desc}, {balance_desc}"
        elif deposit_desc:
            title = f"「{figure_name}」定金发生变动，{deposit_desc}"
        elif balance_desc:
            title = f"「{figure_name}」尾款发生变动，{balance_desc}"

        # 无变更时使用默认标题
        if title is None:
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
            "currency": currency or "CNY",
            "balance": balance or 0,
            "balance_currency": balance_currency or "CNY"
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
    def record_price_update_event(
        db: Session,
        user_id: int,
        figure_id: int,
        figure_name: str,
        old_price: float,
        new_price: float,
        old_currency: Optional[str] = "CNY",
        new_currency: Optional[str] = "CNY"
    ) -> ActivityFeed:
        """记录市场价变动事件"""
        old_sym = CollectorActivityService._get_currency_symbol(old_currency or "CNY")
        new_sym = CollectorActivityService._get_currency_symbol(new_currency or "CNY")

        # 统一折算为人民币计算变动金额和幅度
        old_cny = old_price * PRICE_EXCHANGE_RATES.get(old_currency or "CNY", 1.0)
        new_cny = new_price * PRICE_EXCHANGE_RATES.get(new_currency or "CNY", 1.0)
        change = round(new_cny - old_cny, 2)
        change_rate = ""
        if old_cny and old_cny != 0:
            rate = round((change / old_cny) * 100, 2)
            change_rate = f"{rate:+.2f}%"

        title = f"「{figure_name}」市场价更新：{old_sym}{old_price} → {new_sym}{new_price}"
        now = datetime.now()
        detail = {
            "figure_id": figure_id,
            "figure_name": figure_name,
            "old_price": old_price,
            "new_price": new_price,
            "change": change,
            "change_rate": change_rate,
            "old_currency": old_currency or "CNY",
            "new_currency": new_currency or "CNY",
            "update_date": now.strftime("%Y-%m-%d")
        }
        return CollectorActivityService.record_event(
            db=db,
            user_id=user_id,
            figure_id=figure_id,
            event_type="PRICE_UPDATE",
            event_title=title,
            target_type="figure",
            target_id=figure_id,
            detail_data=detail
        )

    @staticmethod
    def record_tag_snapshot_event(
        db: Session,
        user_id: int,
        figure_id: int,
        figure_name: str,
        tags: List[Dict]
    ) -> ActivityFeed:
        """
        记录手办标签全量快照事件（追加新记录，不修改历史）

        每次手办标签变更时记录当前全部标签作为快照，而非仅记录增量差异。

        Args:
            db: 数据库会话
            user_id: 用户ID
            figure_id: 手办ID
            figure_name: 手办名称
            tags: 标签列表，每项包含 id/name/color

        Returns:
            ActivityFeed: 创建的事件记录
        """
        if not tags:
            raise ValueError("tags cannot be empty")
        now = datetime.now()
        tag_names = [t["name"] for t in tags]
        tag_names_str = "、".join(f"#{n}" for n in tag_names)
        title = f"为「{figure_name}」添加标签 {tag_names_str}"
        detail = {
            "figure_id": figure_id,
            "figure_name": figure_name,
            "tags": [
                {
                    "tag_id": t["id"],
                    "tag_name": t["name"],
                    "tag_color": t.get("color", "")
                }
                for t in tags
            ],
            "add_date": now.strftime("%Y-%m-%d %H:%M:%S")
        }
        first_tag_id = tags[0]["id"]
        return CollectorActivityService.record_event(
            db=db,
            user_id=user_id,
            figure_id=figure_id,
            event_type="TAG_ADD",
            event_title=title,
            target_type="tag",
            target_id=first_tag_id,
            detail_data=detail
        )

    @staticmethod
    def record_out_event(
        db: Session,
        user_id: int,
        figure_id: int,
        figure_name: str,
        from_cabinet: str,
        reason: Optional[str] = None,
        target_id: Optional[int] = None
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
            target_type="cabinet_exclusion",
            target_id=target_id,
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
        now = datetime.now()
        title = f"为「{figure_name}」添加标签 #{tag_name}"
        detail = {
            "figure_id": figure_id,
            "figure_name": figure_name,
            "tags": [
                {
                    "tag_id": tag_id,
                    "tag_name": tag_name,
                    "tag_color": tag_color or ""
                }
            ],
            "add_date": now.strftime("%Y-%m-%d %H:%M:%S")
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
    def record_batch_tag_add_events(
        db: Session,
        user_id: int,
        figure_id: int,
        figure_name: str,
        tags: List[Dict]
    ) -> ActivityFeed:
        """
        批量记录添加标签事件（合并为一条记录）

        当在同一时间对单个手办新增多个标签时，将多条标签合并为一条 TAG_ADD 事件，
        标题展示所有标签名称，detail_data 中 tags 字段包含所有标签的列表。

        Args:
            db: 数据库会话
            user_id: 用户ID
            figure_id: 手办ID
            figure_name: 手办名称
            tags: 标签列表，每项包含 name/id/color

        Returns:
            ActivityFeed: 创建的事件记录
        """
        if not tags:
            raise ValueError("tags cannot be empty")
        now = datetime.now()
        tag_names = [t["name"] for t in tags]
        tag_names_str = "、".join(f"#{n}" for n in tag_names)
        title = f"为「{figure_name}」添加标签 {tag_names_str}"
        detail = {
            "figure_id": figure_id,
            "figure_name": figure_name,
            "tags": [
                {
                    "tag_id": t["id"],
                    "tag_name": t["name"],
                    "tag_color": t.get("color", "")
                }
                for t in tags
            ],
            "add_date": now.strftime("%Y-%m-%d %H:%M:%S")
        }
        # 使用第一个标签 ID 作为 target_id
        first_tag_id = tags[0]["id"]
        return CollectorActivityService.record_event(
            db=db,
            user_id=user_id,
            figure_id=figure_id,
            event_type="TAG_ADD",
            event_title=title,
            target_type="tag",
            target_id=first_tag_id,
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
            "refund_amount": refund_amount or 0,
            "status": "取消订单"
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
                'buy': ['BUY'],
                'full_pay': ['FULL_PAY'],
                'in_stock': ['IN_STOCK'],
                'sell': ['SELL'],
                'out': ['OUT'],
                'order': ['BUY', 'FULL_PAY', 'ORDER_CREATE', 'ORDER_CANCEL'],
                'order_cancel': ['ORDER_CANCEL'],
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
    ) -> tuple:
        """
        获取按日期分组的事件列表
        内部查询 limit+1 条用于判断 has_more

        Returns:
            tuple: (groups, has_more)
            groups: list[dict] 按日期分组的事件列表
            has_more: bool 是否还有更多数据
        """
        # 查询 limit+1 条，用来判断是否还有更多数据
        events = CollectorActivityService.get_events(
            db=db,
            user_id=user_id,
            event_type=event_type,
            offset=offset,
            limit=limit + 1
        )

        # 判断是否有更多数据
        has_more = len(events) > limit
        if has_more:
            events = events[:-1]  # 移除多余的1条

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

        return result, has_more

    @staticmethod
    def get_event_detail(db: Session, event_id: int) -> Optional[Dict]:
        """
        获取单条事件详情

        Args:
            db: 数据库会话
            event_id: 事件ID

        Returns:
            dict: 事件详情（包含 figure_image 字段）
        """
        ev = db.query(ActivityFeed).filter(ActivityFeed.id == event_id).first()
        if not ev:
            return None

        result = CollectorActivityService._format_event(ev)

        # 获取手办图片和信息
        figure_image = ""
        figure_work = ""
        figure_scale = ""
        figure_manufacturer = ""
        if ev.figure_id:
            figure = db.query(Figure).filter(Figure.id == ev.figure_id).first()
            if figure:
                if figure.images and isinstance(figure.images, list) and len(figure.images) > 0:
                    figure_image = figure.images[0]
                figure_work = figure.work or ""
                figure_scale = figure.scale or ""
                figure_manufacturer = figure.manufacturer or ""
        result["figure_image"] = figure_image
        result["figure_work"] = figure_work
        result["figure_scale"] = figure_scale
        result["figure_manufacturer"] = figure_manufacturer

        # IN_STOCK 事件：实时计算手办当前所属藏品柜
        if ev.event_type == "IN_STOCK" and ev.figure_id:
            cabinets = CollectorActivityService._get_figure_cabinets(
                db=db, user_id=ev.user_id, figure_id=ev.figure_id
            )
            result["figure_cabinets"] = cabinets

        return result

    # ========== 私有方法 ==========

    @staticmethod
    def _get_figure_cabinets(db: Session, user_id: int, figure_id: int) -> List[str]:
        """
        实时计算手办当前所属的藏品柜列表

        根据 cabinets.py 中的业务规则判断手办属于哪些收藏柜分类。
        Returns:
            List[str]: 藏品柜展示名称列表，如 ["最近入柜", "海景房专区"]
        """
        from app.models.asset import AssetTransaction
        from app.models.order import Order
        from app.models.sold_order import SoldOrder
        from app.models.tag import Tag

        now = datetime.now()
        cabinets = []

        # 1. 海景房专区：持有 > 180 天 + 仍在库
        active_holdings = db.query(AssetTransaction).filter(
            AssetTransaction.user_id == user_id,
            AssetTransaction.figure_id == figure_id,
            AssetTransaction.transaction_type == 'buy',
            AssetTransaction.is_active == True,
            AssetTransaction.remaining_quantity > 0
        ).order_by(AssetTransaction.transaction_date.asc()).all()
        if active_holdings:
            first_buy = active_holdings[0]
            if first_buy.transaction_date:
                holding_days = (now - first_buy.transaction_date).days
                if holding_days > 180:
                    cabinets.append("海景房专区")

        # 2. 最近入柜：30天内入库
        thirty_days_ago = now - timedelta(days=30)
        recent_buy = db.query(AssetTransaction).filter(
            AssetTransaction.user_id == user_id,
            AssetTransaction.figure_id == figure_id,
            AssetTransaction.transaction_type == 'buy',
            AssetTransaction.transaction_date >= thirty_days_ago,
            AssetTransaction.is_active == True
        ).first()
        if recent_buy:
            cabinets.append("最近入柜")

        # 3. 修复工坊：有关联修复标签
        repair_tag_names = ['待修复', '缺件', '断桩', '待补色', '蹭色']
        repair_tags = db.query(Tag).filter(Tag.name.in_(repair_tag_names)).all()
        repair_tag_ids = [t.id for t in repair_tags]
        if repair_tag_ids:
            from app.models.tag import figure_tag
            link = db.execute(
                text("SELECT 1 FROM figure_tag WHERE figure_id = :fid AND tag_id IN :tids"),
                {"fid": figure_id, "tids": tuple(repair_tag_ids)}
            ).first()
            if link:
                cabinets.append("修复工坊")

        # 4. 已出藏品：有卖出记录
        sold = db.query(SoldOrder).filter(
            SoldOrder.user_id == user_id,
            SoldOrder.figure_id == figure_id,
            SoldOrder.is_active == True
        ).first()
        if sold:
            cabinets.append("已出藏品")

        # 5. 预定中：有未支付/已支付的定金预定订单
        air_order = db.query(Order).filter(
            Order.user_id == user_id,
            Order.figure_id == figure_id,
            Order.order_type == '定金预定',
            Order.status.in_(['未支付', '已支付']),
            Order.is_active == 1
        ).first()
        if air_order:
            cabinets.append("预定中")

        # 6. 复数专区：库存 >= 2
        total_stock = db.query(
            func.coalesce(func.sum(AssetTransaction.remaining_quantity), 0)
        ).filter(
            AssetTransaction.user_id == user_id,
            AssetTransaction.figure_id == figure_id,
            AssetTransaction.transaction_type == 'buy',
            AssetTransaction.is_active == True,
            AssetTransaction.remaining_quantity > 0
        ).scalar() or 0
        if total_stock >= 2:
            cabinets.append("复数专区")

        # 7. 待出荷：有已完成订单
        wait_order = db.query(Order).filter(
            Order.user_id == user_id,
            Order.figure_id == figure_id,
            Order.status == '已完成',
            Order.is_active == 1
        ).first()
        if wait_order:
            cabinets.append("待出荷")

        return cabinets

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
