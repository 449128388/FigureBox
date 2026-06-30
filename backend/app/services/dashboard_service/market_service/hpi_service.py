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
HPI = 1000 × (1 + 平均超额收益率)
平均超额收益率 = Σ(每手办收益率 × 该手办权重)
每手办收益率 = (当前市场价 - 首次买入价) / 首次买入价
权重 = 该手办历史交易金额 / 历史总交易金额

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
        """
        try:
            today = date.today()
            return cls._calculate_and_save(db, user_id, today)
        except Exception as e:
            logger.error(f"HPI 每日跑批失败 (user_id={user_id}): {e}")
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

        1. 获取用户生涯所有交易过的手办（从 Order 表获取买入记录）
        2. 获取每个手办的当前市场价
        3. 判断是否已出（从 SoldOrder 表）
        4. 计算每手办收益率、权重
        5. 汇总计算 HPI
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

        # 4. 计算总交易金额（权重分母）
        total_amount = sum(fd["total_buy_amount"] for fd in figure_data)
        if total_amount <= 0:
            return None

        # 5. 逐手办计算
        components = []
        total_weighted_return = 0.0
        up_count = flat_count = down_count = 0
        sold_up_count = sold_down_count = 0
        holding_count = sold_count = 0
        # 涨跌平容差阈值 ±1%，避免微小价格波动被统计为涨跌
        THRESHOLD = 1.0

        for fd in figure_data:
            figure_id = fd["figure_id"]
            first_buy_price = fd["first_buy_price"]
            first_buy_date = fd["first_buy_date"]
            total_buy_amount = fd["total_buy_amount"]
            current_price = market_prices.get(figure_id, first_buy_price)
            is_sold = figure_id in sold_figures
            sell_price = sold_figures.get(figure_id)

            # 收益率
            return_pct = (current_price - first_buy_price) / first_buy_price * 100 if first_buy_price > 0 else 0

            # 权重
            weight = total_buy_amount / total_amount

            # 加权收益率
            weighted_return = return_pct * weight
            total_weighted_return += weighted_return

            # 盈亏分布（使用 ±1% 容差阈值）
            if return_pct > THRESHOLD:
                up_count += 1
            elif return_pct < -THRESHOLD:
                down_count += 1
            else:
                flat_count += 1

            # 在柜/已出
            if is_sold:
                sold_count += 1
                # 卖飞/卖对判断
                if current_price > sell_price:
                    sold_up_count += 1
                elif current_price < sell_price:
                    sold_down_count += 1
            else:
                holding_count += 1

            components.append({
                "figure_id": figure_id,
                "figure_name": fd.get("figure_name", ""),
                "first_buy_price": first_buy_price,
                "first_buy_date": first_buy_date,
                "total_buy_amount": total_buy_amount,
                "current_price": current_price,
                "is_sold": is_sold,
                "sell_price": sell_price,
                "return_pct": return_pct,
                "weight": weight,
                "contribution": weighted_return,
                "sell_fly": is_sold and current_price > sell_price,
                "sell_right": is_sold and current_price < sell_price,
            })

        # 6. 计算 HPI
        avg_return = total_weighted_return
        index_value = cls.BASE_INDEX * (1 + avg_return / 100)

        return {
            "index_value": round(index_value, 2),
            "avg_return": round(avg_return, 2),
            "total_figures": len(components),
            "holding_figures": holding_count,
            "sold_figures": sold_count,
            "up_count": up_count,
            "flat_count": flat_count,
            "down_count": down_count,
            "sold_up_count": sold_up_count,
            "sold_down_count": sold_down_count,
            "components": components,
        }

    @staticmethod
    def _get_all_traded_figures(db: Session, user_id: int) -> List[Dict]:
        """
        获取用户生涯所有交易过的手办

        从 Order 表统计每手办的：
        - 首次买入价格
        - 首次买入日期
        - 累计买入金额
        - 手办名称
        """
        # 使用 SQL 聚合查询
        from sqlalchemy import text

        sql = text("""
            SELECT
                o.figure_id,
                f.name AS figure_name,
                (SELECT o2.deposit + o2.balance
                 FROM orders o2
                 WHERE o2.figure_id = o.figure_id
                   AND o2.user_id = o.user_id
                   AND o2.is_active = 1
                   AND o2.status IN ('已完成', '已支付')
                 ORDER BY o2.created_at ASC
                 LIMIT 1) AS first_buy_price,
                MIN(o.created_at) AS first_buy_date,
                SUM(o.deposit + o.balance) AS total_buy_amount
            FROM orders o
            JOIN figures f ON f.id = o.figure_id
            WHERE o.user_id = :user_id
              AND o.is_active = 1
              AND o.status IN ('已完成', '已支付')
            GROUP BY o.figure_id
        """)
        result = db.execute(sql, {"user_id": user_id})
        rows = result.fetchall()

        figure_data = []
        for row in rows:
            first_price = float(row.first_buy_price) if row.first_buy_price else 0
            if first_price <= 0:
                continue

            # first_buy_date 可能是 datetime 或 date
            buy_date = row.first_buy_date
            if hasattr(buy_date, 'date'):
                buy_date = buy_date.date()

            figure_data.append({
                "figure_id": row.figure_id,
                "figure_name": row.figure_name or "",
                "first_buy_price": first_price,
                "first_buy_date": buy_date,
                "total_buy_amount": float(row.total_buy_amount or 0),
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
    def _get_sold_figure_map(db: Session, user_id: int) -> Dict[int, Optional[float]]:
        """
        获取用户已出手办映射

        Returns:
            Dict[figure_id, sell_price]
        """
        sold_orders = db.query(SoldOrder).filter(
            SoldOrder.user_id == user_id,
            SoldOrder.is_active == True
        ).all()

        sold_map = {}
        for so in sold_orders:
            sold_map[so.figure_id] = so.sell_price or 0
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
        components = db.query(HPIComponent).filter(
            HPIComponent.user_id == user_id,
            HPIComponent.record_date == record_date
        ).all()

        result = []
        for c in components:
            result.append({
                "figure_id": c.figure_id,
                "first_buy_price": c.first_buy_price,
                "first_buy_date": c.first_buy_date.isoformat() if c.first_buy_date else "",
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
            "components": [],
        }
