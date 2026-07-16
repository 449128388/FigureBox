"""
HomeService - 首页服务层

提供首页所需的业务数据聚合：
- get_activities: 最新动态（新入手/卖出/添加愿望/价格变动）
- get_top_holdings: 持仓市值 Top N
- get_summary: 首页概览摘要
"""
from sqlalchemy.orm import Session
from typing import List, Dict, Any, Optional
from datetime import datetime, date, timedelta
from sqlalchemy import func
from app.models.figure import Figure
from app.models.order import Order
from app.models.sold_order import SoldOrder
from app.models.user import User
from app.models.asset import AssetPriceHistory
from app.services import AssetCalculationService, IndexService
from app.services.dashboard_service.market_service.hpi_service import HPIService


def _human_time(dt: Optional[datetime]) -> str:
    """将 datetime 转为人类可读的相对时间"""
    if not dt:
        return ""
    # 统一去除 tzinfo 做差值（避免混用 aware/naive）
    now = datetime.now()
    if dt.tzinfo is not None:
        dt_naive = dt.replace(tzinfo=None)
    else:
        dt_naive = dt
    diff = now - dt_naive

    if diff.days < 0:
        return "刚刚"
    if diff.days == 0:
        seconds = diff.seconds
        if seconds < 60:
            return "刚刚"
        elif seconds < 3600:
            return f"{seconds // 60} 分钟前"
        elif seconds < 86400:
            return f"{seconds // 3600} 小时前"
    if diff.days < 7:
        return f"{diff.days} 天前"
    if diff.days < 30:
        return f"{diff.days // 7} 周前"
    if diff.days < 365:
        return f"{diff.days // 30} 个月前"
    return f"{diff.days // 365} 年前"


def _get_figure_image(figure: Optional[Figure]) -> Optional[str]:
    """获取手办首图"""
    if figure and figure.images:
        images = figure.images
        if isinstance(images, list) and len(images) > 0:
            return images[0]
    return None


class HomeService:
    """首页服务类"""

    @staticmethod
    def get_activities(db: Session, user_id: int, limit: int = 10) -> List[Dict[str, Any]]:
        """
        获取最新动态，合并四种类型并按 created_at 降序排列

        Args:
            db: 数据库会话
            user_id: 当前用户 ID
            limit: 返回条数上限

        Returns:
            活动列表，按时间降序
        """
        activities: List[Dict[str, Any]] = []

        # 1. 订单动态 - 用户的有效订单（排除愿望清单类型的手办）
        orders = (
            db.query(Order)
            .filter(Order.user_id == user_id, Order.is_active == 1)
            .order_by(Order.created_at.desc())
            .limit(limit)
            .all()
        )
        for o in orders:
            figure = db.query(Figure).filter(Figure.id == o.figure_id).first()
            if not figure or not figure.is_active:
                continue
            # 跳过愿望清单类型的关联手办
            if figure.purchase_type == "wishlist":
                continue
            deposit = o.deposit or 0
            balance = o.balance or 0
            total_price = deposit + balance

            if o.status == "未支付":
                text = f"新预定手办 {figure.name}，定金 ¥{deposit:,.0f}"
                act_type = "buy"
            elif o.status == "已支付":
                text = f"完成 {figure.name} 补款，尾款 ¥{balance:,.0f}"
                act_type = "buy"
            elif o.status == "已取消":
                text = f"取消 {figure.name} 补款"
                act_type = "cancel"
            elif o.status == "已完成":
                text = f"完成 {figure.name} 入库，共计花费 ¥{total_price:,.0f}"
                act_type = "buy"
            else:
                text = f"新入手 {figure.name}，花费 ¥{total_price:,.0f}"
                act_type = "buy"

            activities.append({
                "type": act_type,
                "text": text,
                "figure_name": figure.name,
                "time_label": _human_time(o.created_at),
                "created_at": o.created_at.isoformat() if o.created_at else "",
                "figure_image": _get_figure_image(figure),
                "figure_id": figure.id,
            })

        # 2. 卖出 - 用户的已出售订单
        sold_orders = (
            db.query(SoldOrder)
            .filter(SoldOrder.user_id == user_id, SoldOrder.is_active == 1)
            .order_by(SoldOrder.created_at.desc())
            .limit(limit)
            .all()
        )
        for so in sold_orders:
            figure = db.query(Figure).filter(Figure.id == so.figure_id).first()
            if not figure:
                continue
            activities.append({
                "type": "sell",
                "text": f"卖出 {figure.name}，售价 ¥{so.sell_price:,.0f}",
                "figure_name": figure.name,
                "time_label": _human_time(so.created_at),
                "created_at": so.created_at.isoformat() if so.created_at else "",
                "figure_image": _get_figure_image(figure),
                "figure_id": figure.id,
            })

        # 3. 添加愿望 - 最新愿望清单项
        wishlist_items = (
            db.query(Figure)
            .filter(Figure.purchase_type == "wishlist", Figure.is_active == 1)
            .order_by(Figure.created_at.desc())
            .limit(limit)
            .all()
        )
        for wl in wishlist_items:
            activities.append({
                "type": "wish",
                "text": f"添加愿望 {wl.name}",
                "figure_name": wl.name,
                "time_label": _human_time(wl.created_at),
                "created_at": wl.created_at.isoformat() if wl.created_at else "",
                "figure_image": _get_figure_image(wl),
                "figure_id": wl.id,
            })

        # 4. 价格变动 - 最近的价格变更记录
        price_records = (
            db.query(AssetPriceHistory)
            .order_by(AssetPriceHistory.date.desc())
            .limit(limit)
            .all()
        )
        for pr in price_records:
            figure = db.query(Figure).filter(Figure.id == pr.figure_id).first()
            if not figure:
                continue
            activities.append({
                "type": "price",
                "text": f"价格变动 {figure.name}，现价 ¥{pr.current_price:,.0f}",
                "figure_name": figure.name,
                "time_label": _human_time(pr.date),
                "created_at": pr.date.isoformat() if pr.date else "",
                "figure_image": _get_figure_image(figure),
                "figure_id": figure.id,
            })

        # 合并排序，取前 limit 条
        activities.sort(key=lambda x: x.get("created_at") or "", reverse=True)
        return activities[:limit]

    @staticmethod
    def get_top_holdings(db: Session, user_id: int, limit: int = 5) -> List[Dict[str, Any]]:
        """
        获取持仓市值 Top N

        通过 Order 表找到用户拥有的手办，计算当前市值 × 数量，
        按市值降序排列。

        Args:
            db: 数据库会话
            user_id: 当前用户 ID
            limit: 返回条数上限

        Returns:
            持仓列表，按市值降序
        """
        # 找到用户已入库（订单状态为"已完成"）的所有手办 ID（排除愿望清单）
        order_figure_ids = (
            db.query(Order.figure_id)
            .filter(
                Order.user_id == user_id,
                Order.is_active == 1,
                Order.status == "已完成",
            )
            .distinct()
            .subquery()
        )

        figures = (
            db.query(Figure)
            .filter(
                Figure.id.in_(order_figure_ids),
                Figure.purchase_type != "wishlist",
                Figure.is_active == 1,
            )
            .order_by(Figure.market_price.desc())
            .limit(limit)
            .all()
        )

        result = []
        for fig in figures:
            purchase_price = fig.average_purchase_price or fig.price or 0
            current_price = fig.market_price or 0
            quantity = fig.quantity or 1
            profit_pct = 0.0
            if purchase_price > 0 and current_price > 0:
                profit_pct = round((current_price - purchase_price) / purchase_price * 100, 2)

            result.append({
                "id": fig.id,
                "name": fig.name,
                "manufacturer": fig.manufacturer,
                "scale": fig.scale,
                "image": _get_figure_image(fig),
                "purchase_price": purchase_price,
                "current_price": current_price,
                "profit_pct": profit_pct,
                "quantity": quantity,
            })

        return result

    @staticmethod
    def _generate_greeting(
        db: Session,
        user_id: int,
        figure_count: int,
        wishlist_count: int,
        invest_days: int,
        outperform: float,
    ) -> str:
        """根据优先级生成动态欢迎语"""
        today = date.today()
        now = datetime.now()
        hour = now.hour

        # ── Priority 1: 紧急提醒 ──
        # 1a. 7天内到期的尾款
        seven_days = today + timedelta(days=7)
        due_soon = (
            db.query(Order)
            .filter(
                Order.user_id == user_id,
                Order.is_active == 1,
                Order.status == "未支付",
                Order.due_date.isnot(None),
                Order.due_date <= seven_days,
                Order.due_date >= today,
            )
            .all()
        )
        if due_soon:
            total_due = sum((o.balance or 0) for o in due_soon)
            return f"你有 {len(due_soon)} 笔尾款即将到期，总待付 ¥{total_due:,.0f}，别忘了补款"

        # 1b. 愿望清单今日发售
        today_released = (
            db.query(Figure)
            .filter(
                Figure.purchase_type == "wishlist",
                Figure.is_active == 1,
                Figure.release_date == today,
            )
            .first()
        )
        if today_released:
            return f"{today_released.name} 今日发售，准备好冲了吗？"

        # 1c. 已到货未入库（订单已支付且未标记完成）
        arrived = (
            db.query(Order)
            .filter(
                Order.user_id == user_id,
                Order.is_active == 1,
                Order.status == "已支付",
            )
            .first()
        )
        if arrived:
            figure = db.query(Figure).filter(Figure.id == arrived.figure_id).first()
            name = figure.name if figure else "手办"
            return f"{name} 已到货，记得入库更新持仓"

        # ── Priority 2: 资产涨跌 ──
        if invest_days == 0:
            return "欢迎来到 FigureBox，记录你的第一体塑料小人吧"
        if figure_count == 0 and wishlist_count > 0:
            return "愿望清单已就绪，等待一个合适的入手时机"

        # ── Priority 4: 特殊成就（覆盖资产涨跌话术）──
        # 成就检查仅在投资天数 > 0 时触发
        if invest_days > 0:
            if invest_days == 30:
                return "满月纪念！投资塑料小人已经 30 天"
            if invest_days == 365:
                return f"一周年胶佬，累计交易 {figure_count} 体"

        # 资产涨跌话术（基于跑赢大盘百分比）
        if outperform > 5:
            return f"跑赢大盘 {outperform:+.1f}%，你的眼光真毒"
        if outperform > 0:
            return "资产稳步增长，又是快乐的一天"
        if outperform == 0:
            return "持仓平稳，静待花开"
        if outperform >= -5:
            return "市场微调，长期看好别慌"
        return "今日回调，正是低吸加仓的好时机"

    @staticmethod
    def get_summary(db: Session, user_id: int) -> Dict[str, Any]:
        """
        获取首页概览摘要

        Args:
            db: 数据库会话
            user_id: 当前用户 ID

        Returns:
            摘要数据字典
        """
        user = db.query(User).filter(User.id == user_id).first()

        # figure_count：在柜手办按"体"计（已入库 = 订单状态"已完成"）
        owned_figures = (
            db.query(Figure)
            .filter(
                Figure.id.in_(
                    db.query(Order.figure_id)
                    .filter(
                        Order.user_id == user_id,
                        Order.is_active == 1,
                        Order.status == "已完成",
                    )
                    .distinct()
                    .subquery()
                ),
                Figure.purchase_type != "wishlist",
                Figure.is_active == 1,
            )
            .all()
        )
        figure_count = sum((fig.quantity or 1) for fig in owned_figures)

        # pending_orders：尾款管理中"未支付"订单数量
        pending_orders = (
            db.query(Order)
            .filter(
                Order.user_id == user_id,
                Order.is_active == 1,
                Order.status == "未支付",
            )
            .count()
        )

        # total_assets：用户非愿望清单手办的市值总和
        total_assets = sum(
            (fig.market_price or 0) * (fig.quantity or 1) for fig in owned_figures
        )

        # wishlist_count：仅统计"愿望中"+"已发售"未转采购的记录
        wishlist_count = (
            db.query(Figure)
            .filter(
                Figure.purchase_type == "wishlist",
                Figure.is_active == 1,
                Figure.wishlist_status.in_(["wish", "released"]),
            )
            .count()
        )

        # 跑赢大盘 = 塑料指数涨幅 − 上证指数涨幅（与资产看板-资产模块一致）
        sh_index_data = IndexService.get_cached_sh_index(db)
        sh_index = sh_index_data.get("current_value", AssetCalculationService.BASE_SH_INDEX)
        plastic_index, _ = AssetCalculationService.calculate_plastic_index(
            owned_figures, total_assets,
        )
        outperform = AssetCalculationService.calculate_outperform_percentage(
            plastic_index, sh_index,
        )
        hpi_value = round(plastic_index, 2)
        hpi_change = round(outperform, 2)

        # 塑料小人指数 (HPI) — 用于 HPI Mini 组件，与 q-stat-card 的"跑赢大盘"不同
        hpi_dashboard = HPIService.get_hpi_dashboard(db, user_id)
        hpi_index_value = hpi_dashboard.get("index_value", 1000.0)
        hpi_return = hpi_dashboard.get("avg_return", 0.0)

        # monthly_new：本月内完成入库（"已完成"）的订单数量（按体计）
        first_of_month = date.today().replace(day=1)
        monthly_new = (
            db.query(Order)
            .filter(
                Order.user_id == user_id,
                Order.is_active == 1,
                Order.status == "已完成",
                Order.updated_at >= first_of_month,
            )
            .count()
        )

        # monthly_unpaid：未支付订单与上月对比的变化量
        today = date.today()
        # 本月1号
        first_of_this_month = today.replace(day=1)
        # 上月1号
        last_month = first_of_this_month - timedelta(days=1)
        first_of_last_month = last_month.replace(day=1)

        this_month_unpaid = (
            db.query(Order)
            .filter(
                Order.user_id == user_id,
                Order.is_active == 1,
                Order.status == "未支付",
                Order.created_at >= first_of_this_month,
            )
            .count()
        )
        last_month_unpaid = (
            db.query(Order)
            .filter(
                Order.user_id == user_id,
                Order.is_active == 1,
                Order.status == "未支付",
                Order.created_at >= first_of_last_month,
                Order.created_at < first_of_this_month,
            )
            .count()
        )

        monthly_unpaid = this_month_unpaid - last_month_unpaid

        # monthly_due：本月待付尾款总额（未支付订单，到期日在本月内）
        import calendar
        _, last_day_of_month = calendar.monthrange(today.year, today.month)
        month_end = date(today.year, today.month, last_day_of_month)
        monthly_due_orders = (
            db.query(func.coalesce(func.sum(Order.balance), 0))
            .filter(
                Order.user_id == user_id,
                Order.is_active == 1,
                Order.status == "未支付",
                Order.due_date.isnot(None),
                Order.due_date >= first_of_this_month,
                Order.due_date <= month_end,
            )
            .scalar() or 0
        )
        monthly_due = round(float(monthly_due_orders), 2)

        # sell_correct_count：卖对次数（盈利卖出订单数）
        # win_rate：胜率（盈利卖出 / 总卖出 × 100）
        sold_orders = (
            db.query(SoldOrder)
            .filter(SoldOrder.user_id == user_id, SoldOrder.is_active == 1)
            .all()
        )
        sell_correct_count = 0
        sell_total = 0
        for so in sold_orders:
            profit = (so.sell_price or 0) - (so.cost_price or 0) - abs(so.shipping_fee or 0) - abs(so.platform_fee or 0)
            if profit is None or profit == 0:
                continue
            sell_total += 1
            if profit > 0:
                sell_correct_count += 1
        win_rate = round((sell_correct_count / sell_total) * 100, 1) if sell_total > 0 else 0.0

        # 用户名
        username = user.nickname or user.username if user else "胶佬"

        # invest_days：首次成功买入（"已完成"订单）到今天的自然日天数
        first_order = (
            db.query(func.min(Order.created_at))
            .filter(
                Order.user_id == user_id,
                Order.is_active == 1,
                Order.status == "已完成",
            )
            .scalar()
        )
        invest_days = 0
        if first_order:
            first_date = first_order.date() if isinstance(first_order, datetime) else first_order
            invest_days = (today - first_date).days

        # 动态欢迎语
        greeting = HomeService._generate_greeting(
            db, user_id, figure_count, wishlist_count, invest_days, hpi_change,
        )

        return {
            "figure_count": figure_count,
            "pending_orders": pending_orders,
            "total_assets": round(total_assets, 2),
            "wishlist_count": wishlist_count,
            "hpi_value": hpi_value,
            "hpi_change": hpi_change,
            "hpi_index_value": hpi_index_value,
            "hpi_return": hpi_return,
            "monthly_new": monthly_new,
            "monthly_unpaid": monthly_unpaid,
            "monthly_due": monthly_due,
            "sell_correct_count": sell_correct_count,
            "win_rate": win_rate,
            "username": username,
            "invest_days": invest_days,
            "greeting": greeting,
        }
