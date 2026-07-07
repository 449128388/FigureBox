"""
塑料小人指数(HPI)服务模块

设计定位：HPI = 用户"塑料投资生涯全周期收益指数"
- 时间维度：动态全历史（生涯全周期）
- 基准：每手办首次买入价
- 回答：「从我买入每一体手办那天起，它们后来平均涨了多少？」
- 类比：基金经理业绩比较基准 → 累计超额收益

核心差异化：已出手办永久保留跟踪（永不剔除）
- 在柜手办 ✅ 计入
- 已出手办 ✅ 继续跟踪当前市场价（看卖飞/卖对）

计算公式：
HPI = 1000 × (1 + 加权平均收益率)
加权平均收益率 = Σ(每手办收益率 × 每手办权重)
每手办收益率 = (当前市场价 - 首次买入价) / 首次买入价
每手办权重 = 该手办历史交易金额 / 历史总交易金额
涨跌点数 = HPI - 1000
涨跌百分比 = 加权平均收益率 × 100%

成分股管理：
- 纳入：用户首次买入某手办时自动纳入
- 剔除：永不剔除
- 权重：按该手办历史交易金额占比
- 价格：已出用当前市场价，在柜用当前市场价

定时任务：
- 每日北京时间 00:30 跑批计算
"""

import logging
from datetime import datetime, date
from typing import Dict, Optional, Any, List, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import func, desc

from app.models.figure import Figure
from app.models.order import Order
from app.models.sold_order import SoldOrder
from app.models.hpi import HPIDaily, HPIComponent
from app.services.sold_order_service.currency_service import CurrencyService

logger = logging.getLogger(__name__)


class HPIService:
    """塑料小人指数(HPI)服务类 - 投资生涯全周期收益指数"""

    # 基准指数
    BASE_INDEX = 1000.0

    # ========== 公开接口 ==========

    @classmethod
    def get_hpi_dashboard(cls, db: Session, user_id: int) -> Dict[str, Any]:
        """
        获取用户 HPI 行情看板数据

        优先从 hpi_daily 表读取最新快照，
        如果没有今日数据则实时计算并返回。
        """
        # 尝试读取最新快照
        latest = cls._get_latest_snapshot(db, user_id)
        today = date.today()

        if latest and latest.record_date == today:
            # 已有今日快照，直接返回
            components = cls._get_today_components(db, user_id, today)
            return cls._build_dashboard(latest, components)

        # 没有今日快照，实时计算
        return cls._calculate_and_return(db, user_id)

    @classmethod
    def get_hpi_history(cls, db: Session, user_id: int, days: int = 365) -> List[Dict[str, Any]]:
        """获取 HPI 历史数据（用于 K 线图）"""
        records = db.query(HPIDaily).filter(
            HPIDaily.user_id == user_id
        ).order_by(HPIDaily.record_date.asc()).limit(days).all()

        if records:
            return [
                {
                    "date": r.record_date.isoformat(),
                    "value": r.index_value,
                    "avg_return": r.avg_return,
                    "total_figures": r.total_figures,
                    "holding_figures": r.holding_figures,
                    "sold_figures": r.sold_figures,
                    "in_cabinet_value": float(r.in_cabinet_value or 0),
                    "sold_value": float(r.sold_value or 0),
                }
                for r in records
            ]

        # 无历史快照时，尝试实时计算并返回今日数据（兜底）
        calc_result = cls._calculate_hpi(db, user_id, date.today())
        if calc_result:
            return [{
                "date": date.today().isoformat(),
                "value": calc_result["index_value"],
                "avg_return": calc_result["avg_return"],
                "total_figures": calc_result["total_figures"],
                "holding_figures": calc_result["holding_figures"],
                "sold_figures": calc_result["sold_figures"],
                "in_cabinet_value": calc_result.get("in_cabinet_value", 0.0),
                "sold_value": calc_result.get("sold_value", 0.0),
            }]
        return []

    @classmethod
    def get_components(cls, db: Session, user_id: int) -> Dict[str, Any]:
        """获取最新成分股详情"""
        latest = cls._get_latest_snapshot(db, user_id)
        if not latest:
            # 无快照时实时计算并返回
            calc_result = cls._calculate_hpi(db, user_id, date.today())
            if calc_result:
                components = calc_result.get("components", [])
            else:
                components = []
        else:
            components = cls._get_today_components(db, user_id, latest.record_date)

        holding = [c for c in components if not c["is_sold"]]
        sold = [c for c in components if c["is_sold"]]
        return {"holding": holding, "sold": sold}

    @classmethod
    def run_daily_batch(cls, db: Session, user_id: int) -> bool:
        """
        每日跑批计算 HPI（定时任务调用）

        1. 获取用户所有交易过的手办（从 Order + SoldOrder）
        2. 计算每手办的收益率和权重
        3. 计算加权平均收益率和 HPI
        4. 写入 hpi_daily 和 hpi_components

        事务保护：
        - 异常时主动 rollback，防止 session 污染影响后续用户
        """
        try:
            today = date.today()
            return cls._calculate_and_save(db, user_id, today)
        except Exception as e:
            logger.error(f"HPI 每日跑批失败 (user_id={user_id}): {e}")
            # 回滚事务，确保 session 干净（不影响后续用户）
            try:
                db.rollback()
            except Exception:
                pass
            return False

    # ========== 内部方法 ==========

    @classmethod
    def _calculate_and_return(cls, db: Session, user_id: int) -> Dict[str, Any]:
        """实时计算并构建 dashboard 返回"""
        today = date.today()
        result = cls._calculate_hpi(db, user_id, today)
        if result:
            return cls._build_dashboard_from_calc(result, [])
        return cls._empty_dashboard()

    @classmethod
    def _calculate_and_save(cls, db: Session, user_id: int, calc_date: date) -> bool:
        """计算并持久化 HPI（支持覆盖已有数据）"""
        calc_result = cls._calculate_hpi(db, user_id, calc_date)
        if not calc_result:
            return False

        # 先删除该用户该日已有数据（支持覆盖更新）
        db.query(HPIDaily).filter(
            HPIDaily.user_id == user_id,
            HPIDaily.record_date == calc_date
        ).delete()
        db.query(HPIComponent).filter(
            HPIComponent.user_id == user_id,
            HPIComponent.record_date == calc_date
        ).delete()
        db.flush()

        # 写入 hpi_daily
        daily = HPIDaily(
            user_id=user_id,
            index_value=round(calc_result["index_value"], 2),
            avg_return=round(calc_result["avg_return"], 2),
            total_figures=calc_result["total_figures"],
            holding_figures=calc_result["holding_figures"],
            sold_figures=calc_result["sold_figures"],
            up_count=calc_result["up_count"],
            flat_count=calc_result["flat_count"],
            down_count=calc_result["down_count"],
            sold_up_count=calc_result["sold_up_count"],
            sold_down_count=calc_result["sold_down_count"],
            in_cabinet_value=calc_result.get("in_cabinet_value", 0.0),
            sold_value=calc_result.get("sold_value", 0.0),
            record_date=calc_date,
        )
        db.add(daily)

        # 批量写入 hpi_components
        for comp in calc_result["components"]:
            db.add(HPIComponent(
                user_id=user_id,
                figure_id=comp["figure_id"],
                record_date=calc_date,
                first_buy_price=round(comp["first_buy_price"], 2),
                first_buy_date=comp["first_buy_date"],
                quantity=comp["quantity"],
                total_buy_amount=round(comp["total_buy_amount"], 2),
                current_price=round(comp["current_price"], 2),
                is_sold=1 if comp["is_sold"] else 0,
                sell_price=round(comp["sell_price"], 2) if comp["sell_price"] else None,
                return_pct=round(comp["return_pct"], 2),
                weight=round(comp["weight"], 4),
                contribution=round(comp["contribution"], 2),
                sell_fly=1 if comp.get("sell_fly") else 0,
                sell_right=1 if comp.get("sell_right") else 0,
            ))

        db.commit()
        logger.info(f"HPI 跑批完成 (user_id={user_id}, date={calc_date}, value={calc_result['index_value']})")
        return True

    @classmethod
    def _calculate_hpi(cls, db: Session, user_id: int, calc_date: date) -> Optional[Dict[str, Any]]:
        """
        核心计算逻辑

        公式定义：
          HPI = 1000 × (1 + 加权平均收益率)
          加权平均收益率 = Σ(每手办收益率 × 每手办权重)
          每手办收益率 = (当前市场价 - 首次买入价) / 首次买入价
          每手办权重 = 该手办历史交易金额 / 历史总交易金额
          涨跌点数 = HPI - 1000
          涨跌百分比 = 加权平均收益率 × 100%

        走势图拆分贡献（在柜/已出）：
          - 始终满足：HPI = 在柜贡献 + 已出贡献
          - 在柜贡献 = Σ(1000 × 当前市场价/首次买入价 × 权重)  （在柜手办）
          - 已出贡献 = Σ(1000 × 当前市场价/首次买入价 × 权重)  （已出手办）

        1. 获取用户生涯所有交易过的手办（从 Order 表）
        2. 获取每个手办的当前市场价
        3. 判断是否已出（从 SoldOrder 表）
        4. 计算总交易金额、每手办权重、收益率
        5. 计算加权平均收益率和 HPI
        """
        # 1. 获取用户所有买入过的手办
        figure_data = cls._get_all_traded_figures(db, user_id)
        if not figure_data:
            return None

        # 2. 获取手办当前市场价映射
        figure_ids = [fd["figure_id"] for fd in figure_data]
        market_prices = cls._get_market_prices(db, figure_ids)

        # 3. 获取已出手办映射
        sold_figures = cls._get_sold_figure_map(db, user_id)

        # 4. 计算历史总交易金额（权重分母）
        total_amount = sum(fd["total_buy_amount"] for fd in figure_data)
        if total_amount <= 0:
            return None

        # 5. 逐手办计算
        components = []
        total_weighted_return = 0.0  # 累积加权平均收益率（百分比点数）
        up_count = flat_count = down_count = 0
        sold_up_count = sold_down_count = 0
        holding_count = sold_count = 0
        in_cabinet_chart_sum = 0.0  # 在柜走势图贡献（0~1000标尺）
        sold_chart_sum = 0.0        # 已出走势图贡献（0~1000标尺）
        # 涨跌平容差阈值 ±1%，避免微小价格波动被统计为涨跌
        THRESHOLD = 1.0

        for fd in figure_data:
            figure_id = fd["figure_id"]
            first_buy_price = fd["first_buy_price"]
            first_buy_date = fd["first_buy_date"]
            total_qty = max(int(fd["quantity"] or 1), 1)
            total_buy_amount = fd["total_buy_amount"]
            current_price = market_prices.get(figure_id, first_buy_price)

            # 卖出信息（含数量 + 加权平均卖出价）
            sold_info = sold_figures.get(figure_id)
            sold_qty = int((sold_info or {}).get("sold_qty") or 0)
            sold_qty = max(min(sold_qty, total_qty), 0)
            sell_price = (sold_info or {}).get("sell_price") if sold_info else None
            holding_qty = total_qty - sold_qty

            # 单体均价（人民币）—— 作为该手办所有分片的成本参考基准
            unit_cost = total_buy_amount / total_qty if total_qty > 0 else 0

            # 准备本次手办要追加的成分股行
            pending_rows = []  # (qty, buy_amt, is_sold, sell_price, return_pct)

            # 已出部分
            if sold_qty > 0:
                sold_amt = round(unit_cost * sold_qty, 2)
                if sold_amt <= 0:
                    # 防御：成本无效时跳过该分片
                    sold_amt = 0
                if sell_price is not None and sold_amt > 0:
                    sold_return = (sell_price - unit_cost) / unit_cost * 100
                elif sold_amt == 0 and sell_price:
                    sold_return = 0
                else:
                    sold_return = 0
                pending_rows.append({
                    "qty": sold_qty,
                    "buy_amt": sold_amt,
                    "is_sold": True,
                    "sell_price": sell_price,
                    "return_pct": sold_return,
                })

            # 在柜部分
            if holding_qty > 0:
                holding_amt = round(unit_cost * holding_qty, 2)
                # 在柜收益率：以「单体均价」为成本基准，与已出分片保持一致
                holding_return = (
                    (current_price - unit_cost) / unit_cost * 100
                    if unit_cost > 0 else 0
                )
                pending_rows.append({
                    "qty": holding_qty,
                    "buy_amt": holding_amt,
                    "is_sold": False,
                    "sell_price": None,
                    "return_pct": holding_return,
                })

            # 汇总到全用户维度
            for row in pending_rows:
                qty = row["qty"]
                buy_amt = row["buy_amt"]
                is_sold = row["is_sold"]
                sp = row["sell_price"]
                rpct = row["return_pct"]

                # 权重 = 本分片成本 / 全用户总投入
                weight = buy_amt / total_amount if total_amount > 0 else 0
                weighted_return = rpct * weight
                total_weighted_return += weighted_return

                # 走势图贡献值（0~1000 标尺）
                # = 1000 × (当前市场价 / 成本基准) × 权重
                # = 1000 × (1 + 收益率) × 权重
                chart_price = sp if is_sold and sp is not None else current_price
                chart_contribution = (
                    cls.BASE_INDEX * (chart_price / unit_cost) * weight
                    if unit_cost > 0 else 0
                )

                # 盈亏分布（使用 ±1% 容差阈值）
                if rpct > THRESHOLD:
                    up_count += 1
                elif rpct < -THRESHOLD:
                    down_count += 1
                else:
                    flat_count += 1

                # 在柜/已出分类
                if is_sold:
                    sold_count += 1
                    sold_chart_sum += chart_contribution
                    if sp is None:
                        sold_up_count += 0
                        sold_down_count += 0
                    else:
                        # 卖飞/卖对：卖出价 < 当前市场价 为卖飞，卖出价 >= 当前市场价 为卖对
                        if current_price > sp:
                            sold_up_count += 1
                        elif current_price <= sp:
                            sold_down_count += 1
                else:
                    holding_count += 1
                    in_cabinet_chart_sum += chart_contribution

                components.append({
                    "figure_id": figure_id,
                    "figure_name": fd.get("figure_name", ""),
                    "first_image": fd.get("first_image", ""),
                    # 单体均价（人民币），前端的「买入」展示以此为基准
                    "first_buy_price": round(unit_cost, 2),
                    "first_buy_date": first_buy_date,
                    "quantity": qty,
                    "total_buy_amount": buy_amt,
                    "current_price": current_price,
                    "is_sold": is_sold,
                    "sell_price": sp,
                    "return_pct": rpct,
                    "weight": weight,
                    "contribution": round(weighted_return, 2),       # 百分比点数贡献
                    "sell_fly": bool(is_sold and sp is not None and current_price > sp),
                    "sell_right": bool(is_sold and sp is not None and current_price <= sp),
                })

        # 6. 计算 HPI
        avg_return = total_weighted_return  # 加权平均收益率（百分比点数，如 4.6）
        index_value = cls.BASE_INDEX * (1 + avg_return / 100)  # HPI 指数值

        # 走势图拆分（0~1000标尺，恒等式：in_cabinet_value + sold_value = index_value）
        in_cabinet_value = round(in_cabinet_chart_sum, 2)
        sold_value = round(sold_chart_sum, 2)

        # 找出所有成分股中最小的首次买入日期
        earliest_buy_date = None
        for fd in figure_data:
            date_val = fd.get("first_buy_date")
            if date_val:
                if earliest_buy_date is None or date_val < earliest_buy_date:
                    earliest_buy_date = date_val

        return {
            "index_value": round(index_value, 2),
            "avg_return": round(avg_return, 2),
            # total_figures 统计体数总和（混合状态下拆分为多行时累加）
            "total_figures": sum(c["quantity"] for c in components),
            "holding_figures": sum(c["quantity"] for c in components if not c["is_sold"]),
            "sold_figures": sum(c["quantity"] for c in components if c["is_sold"]),
            "up_count": up_count,
            "flat_count": flat_count,
            "down_count": down_count,
            "sold_up_count": sold_up_count,
            "sold_down_count": sold_down_count,
            "in_cabinet_value": in_cabinet_value,
            "sold_value": sold_value,
            "first_buy_date": earliest_buy_date,
            "components": components,
        }

    @staticmethod
    def _get_all_traded_figures(db: Session, user_id: int) -> List[Dict]:
        """
        获取用户生涯所有交易过的手办

        从 Order 表统计每手办的：
        - 首次买入价格（人民币）
        - 首次买入日期
        - 累计买入金额（人民币，经币种汇率转换）
        - 手办名称

        币种处理：deposit 和 balance 可能有不同的币种（deposit_currency / balance_currency），
        统一通过 CurrencyService 转换为人民币后再汇总。
        """
        from collections import OrderedDict

        # 查询所有有效订单（含币种信息）
        orders = (
            db.query(Order)
            .filter(
                Order.user_id == user_id,
                Order.is_active == 1,
                Order.status.in_(['已完成', '已支付']),
            )
            .order_by(Order.created_at.asc())
            .all()
        )
        if not orders:
            return []

        # 按 figure_id 分组聚合
        figure_map = OrderedDict()  # figure_id -> aggregated data
        figure_names = {}  # figure_id -> name
        figure_images = {}  # figure_id -> 首图URL

        # 预查询手办名称与首图
        figure_ids = list(set(o.figure_id for o in orders))
        figures = db.query(Figure).filter(Figure.id.in_(figure_ids)).all()
        figure_names = {f.id: f.name for f in figures}
        for f in figures:
            imgs = f.images or []
            figure_images[f.id] = imgs[0] if imgs else ""

        for order in orders:
            fid = order.figure_id
            if fid not in figure_map:
                figure_map[fid] = {
                    "first_buy_price_cny": None,   # 首次订单的CNY总价
                    "first_buy_date": None,         # 首次订单日期
                    "total_buy_amount_cny": 0.0,    # 累计CNY总金额
                    "quantity": 0,                  # 订单笔数
                }

            # 将本订单的 deposit + balance 转为 CNY
            deposit_cny = CurrencyService.to_cny(
                order.deposit or 0, order.deposit_currency or 'CNY', db=db
            )
            balance_cny = CurrencyService.to_cny(
                order.balance or 0, order.balance_currency or 'CNY', db=db
            )
            order_total_cny = deposit_cny + balance_cny

            record = figure_map[fid]
            # 首次订单记录首次买入价（CNY）
            if record["first_buy_price_cny"] is None:
                record["first_buy_price_cny"] = order_total_cny
                record["first_buy_date"] = order.created_at

            record["total_buy_amount_cny"] += order_total_cny
            record["quantity"] += 1

        # 组装返回数据
        figure_data = []
        for fid, record in figure_map.items():
            first_price_cny = record["first_buy_price_cny"]
            if not first_price_cny or first_price_cny <= 0:
                continue

            buy_date = record["first_buy_date"]
            if hasattr(buy_date, 'date'):
                buy_date = buy_date.date()

            figure_data.append({
                "figure_id": fid,
                "figure_name": figure_names.get(fid, ""),
                "first_image": figure_images.get(fid, ""),
                "first_buy_price": round(first_price_cny, 2),
                "first_buy_date": buy_date,
                "total_buy_amount": round(record["total_buy_amount_cny"], 2),
                "quantity": record["quantity"],
            })

        return figure_data

    @staticmethod
    def _get_market_prices(db: Session, figure_ids: List[int]) -> Dict[int, float]:
        """获取手办当前市场价"""
        figures = db.query(Figure).filter(Figure.id.in_(figure_ids)).all()
        return {
            f.id: (f.market_price or f.price or 0)
            for f in figures
        }

    @staticmethod
    def _get_sold_figure_map(db: Session, user_id: int) -> Dict[int, Dict[str, Any]]:
        """
        获取用户已出手办映射（支持多笔卖出记录与卖出数量）

        Returns:
            Dict[figure_id, {
                "sell_price": 加权平均卖出价（CNY）,
                "sold_qty": 累计卖出体数
            }]
        """
        from app.services.sold_order_service.currency_service import CurrencyService as _CS
        sold_orders = db.query(SoldOrder).filter(
            SoldOrder.user_id == user_id,
            SoldOrder.is_active == True
        ).all()

        sold_map: Dict[int, Dict[str, Any]] = {}
        for so in sold_orders:
            qty = int(so.quantity or 1)
            # 卖出价按币种折算为人民币（用总额÷数量得到单均价，再折算）
            unit_cny = _CS.to_cny(
                (so.sell_price or 0) / qty if qty > 0 else 0,
                so.sell_price_currency or 'CNY', db=db
            )
            prev = sold_map.get(so.figure_id)
            if prev is None:
                sold_map[so.figure_id] = {"sell_price": unit_cny, "sold_qty": qty}
            else:
                # 多次卖出：加权平均卖出价
                total_qty = prev["sold_qty"] + qty
                avg_price = (
                    (prev["sell_price"] * prev["sold_qty"] + unit_cny * qty) / total_qty
                    if total_qty > 0 else 0
                )
                sold_map[so.figure_id] = {"sell_price": avg_price, "sold_qty": total_qty}
        return sold_map

    @staticmethod
    def _get_latest_snapshot(db: Session, user_id: int) -> Optional[HPIDaily]:
        """获取最新 HPI 快照"""
        return db.query(HPIDaily).filter(
            HPIDaily.user_id == user_id
        ).order_by(HPIDaily.record_date.desc()).first()

    @staticmethod
    def _get_today_components(db: Session, user_id: int, record_date: date) -> List[Dict]:
        """获取指定日期的成分股数据"""
        components = db.query(
            HPIComponent,
            Figure.name.label("figure_name"),
            Figure.images.label("figure_images"),
        ).outerjoin(
            Figure, HPIComponent.figure_id == Figure.id
        ).filter(
            HPIComponent.user_id == user_id,
            HPIComponent.record_date == record_date
        ).all()

        result = []
        for row in components:
            c = row[0] if hasattr(row, "_mapping") else row[0] if isinstance(row, tuple) else row
            figure_name = row[1] if hasattr(row, "_mapping") else row[1] if isinstance(row, tuple) else getattr(row, "figure_name", "")
            figure_images = row[2] if hasattr(row, "_mapping") else row[2] if isinstance(row, tuple) else getattr(row, "figure_images", None) or []
            first_image = figure_images[0] if figure_images else ""
            result.append({
                "figure_id": c.figure_id,
                "figure_name": figure_name or f"手办 #{c.figure_id}",
                "first_image": first_image,
                "first_buy_price": c.first_buy_price,
                "first_buy_date": c.first_buy_date.isoformat() if c.first_buy_date else "",
                "quantity": c.quantity or 1,
                "total_buy_amount": c.total_buy_amount,
                "current_price": c.current_price,
                "is_sold": bool(c.is_sold),
                "sell_price": c.sell_price,
                "return_pct": c.return_pct,
                "weight": c.weight,
                "contribution": c.contribution,
                "sell_fly": bool(c.sell_fly),
                "sell_right": bool(c.sell_right),
            })
        return result

    @staticmethod
    def _build_dashboard(snapshot: HPIDaily, components: List[Dict]) -> Dict[str, Any]:
        """构建 dashboard 返回格式（从快照）"""
        # 从组件中找出最早的首次买入日期
        earliest_buy_date = None
        for c in components:
            date_val = c.get("first_buy_date")
            if date_val:
                if earliest_buy_date is None or date_val < earliest_buy_date:
                    earliest_buy_date = date_val

        return {
            "index_value": snapshot.index_value,
            "avg_return": snapshot.avg_return,
            "total_figures": snapshot.total_figures,
            "holding_figures": snapshot.holding_figures,
            "sold_figures": snapshot.sold_figures,
            "up_count": snapshot.up_count,
            "flat_count": snapshot.flat_count,
            "down_count": snapshot.down_count,
            "sold_up_count": snapshot.sold_up_count,
            "sold_down_count": snapshot.sold_down_count,
            "in_cabinet_value": float(snapshot.in_cabinet_value or 0),
            "sold_value": float(snapshot.sold_value or 0),
            "first_buy_date": earliest_buy_date,
            "components": components,
        }

    @staticmethod
    def _build_dashboard_from_calc(result: Dict, components: List) -> Dict[str, Any]:
        """构建 dashboard 返回格式（从实时计算）"""
        return {
            "index_value": result["index_value"],
            "avg_return": result["avg_return"],
            "total_figures": result["total_figures"],
            "holding_figures": result["holding_figures"],
            "sold_figures": result["sold_figures"],
            "up_count": result["up_count"],
            "flat_count": result["flat_count"],
            "down_count": result["down_count"],
            "sold_up_count": result["sold_up_count"],
            "sold_down_count": result["sold_down_count"],
            "in_cabinet_value": result.get("in_cabinet_value", 0.0),
            "sold_value": result.get("sold_value", 0.0),
            "first_buy_date": result.get("first_buy_date"),
            "components": result.get("components", []),
        }

    @staticmethod
    def _empty_dashboard() -> Dict[str, Any]:
        return {
            "index_value": 1000.0,
            "avg_return": 0.0,
            "total_figures": 0,
            "holding_figures": 0,
            "sold_figures": 0,
            "up_count": 0,
            "flat_count": 0,
            "down_count": 0,
            "sold_up_count": 0,
            "sold_down_count": 0,
            "first_buy_date": None,
            "components": [],
        }
