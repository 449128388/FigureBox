"""
塑料小人指数(HPI)服务模块

功能说明：
- 计算全市场/全品类手办的综合价格指数
- HPI是市场级指标，反映整个手办市场的冷热
- 类比股市：上证指数、沪深300

核心差异：
- 塑料手办指数（资产看板）：仅持仓手办，个人大盘
- 塑料小人指数HPI（行情页）：全市场手办，行业大盘

指数计算（成交量加权法）：
- HPI = Σ(手办市场价 × 该手办成交量) / 总成交量
- 基准值：1000点
- 样本：全站所有手办（全市场）
- 涨跌：与昨日HPI比较

成分股管理：
- 纳入：新发售且有一定成交量的手办
- 剔除：长期无交易、已绝版且无市价的"僵尸股"
- 权重调整：根据成交量动态加权

涨跌定义：
- 涨：今日HPI > 昨日HPI，市场升温
- 跌：今日HPI < 昨日HPI，市场降温
- 平：|今日HPI - 昨日HPI| < 0.1%，市场横盘

与其他模块互动：
- HPI → 资产看板：提供"大盘基准"用于"跑赢大盘"计算
- 资产看板 → HPI：持仓交易数据贡献到成交量统计
- HPI → 持仓卡片：提供涨跌状态判定标准
- 交易 → HPI：卖出成交计入成交量
- HPI → 交易决策：市场冷热信号指导买卖
- HPI → 预警：单日跌幅>5%触发系统性风险预警

创建时间: 2026-05-18
作者: FigureBox Team
"""

from datetime import datetime, date, timedelta
from typing import Dict, Optional, Any, List, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import func, and_

from app.models.figure import Figure
from app.models.sold_order import SoldOrder
from app.models.order import Order


class HPIService:
    """塑料小人指数(HPI)服务类"""

    # 基准日指数
    BASE_INDEX = 1000.0
    # 横盘阈值（0.1%）
    FLAT_THRESHOLD = 0.1
    # 最小成交量阈值（纳入成分股）
    MIN_VOLUME_THRESHOLD = 1
    # 僵尸股判定：90天无交易
    ZOMBIE_DAYS = 90

    @classmethod
    def calculate_hpi(cls, db: Session) -> Dict[str, Any]:
        """
        计算塑料小人指数(HPI) - 成交量加权法

        计算公式：
        HPI = Σ(手办市场价 × 该手办成交量) / 总成交量

        样本范围：全站所有活跃手办（全市场）

        Args:
            db: 数据库会话

        Returns:
            Dict: 包含HPI值、涨跌额、涨跌幅、趋势等信息
        """
        # 获取成分股（活跃手办）
        constituents = cls._get_constituents(db)

        if not constituents:
            # 没有成分股时，返回基准指数
            return {
                "value": cls.BASE_INDEX,
                "change": 0.0,
                "change_percentage": 0.0,
                "trend": "flat",
                "volume": 0,
                "up_count": 0,
                "flat_count": 0,
                "down_count": 0,
                "limit_up": "无",
                "limit_down": "无",
                "constituent_count": 0
            }

        # 计算成交量加权的HPI
        weighted_sum = 0.0  # Σ(手办市场价 × 成交量)
        total_volume = 0    # 总成交量
        total_base_value = 0.0  # 基准总市值（用于计算指数）

        for fig, volume in constituents:
            market_price = fig.market_price or fig.price or 0
            base_price = fig.price or market_price or 0

            weighted_sum += market_price * volume
            total_volume += volume
            total_base_value += base_price * volume

        # 计算今日HPI
        if total_volume > 0 and total_base_value > 0:
            # 当前加权平均价格
            current_avg_price = weighted_sum / total_volume
            # 基准加权平均价格
            base_avg_price = total_base_value / total_volume
            # HPI = 基准指数 × (当前加权均价 / 基准加权均价)
            today_hpi = round(cls.BASE_INDEX * (current_avg_price / base_avg_price), 2)
        else:
            today_hpi = cls.BASE_INDEX

        # 获取昨日HPI用于计算涨跌
        yesterday_hpi = cls._get_yesterday_hpi(db)

        if yesterday_hpi:
            change = round(today_hpi - yesterday_hpi, 2)
            change_percentage = round((change / yesterday_hpi) * 100, 2) if yesterday_hpi > 0 else 0.0
        else:
            # 没有昨日数据，与基准比较
            change = round(today_hpi - cls.BASE_INDEX, 2)
            change_percentage = round((change / cls.BASE_INDEX) * 100, 2)

        # 确定趋势
        if abs(change_percentage) < cls.FLAT_THRESHOLD:
            trend = "flat"
        elif change > 0:
            trend = "up"
        else:
            trend = "down"

        # 计算涨跌平家数统计
        up_count, flat_count, down_count = cls._calculate_market_stats(constituents)

        # 获取涨停/跌停家数（涨幅/跌幅超过10%）
        limit_up_figures, limit_down_figures = cls._get_limit_figures(constituents)

        return {
            "value": today_hpi,
            "change": change,
            "change_percentage": change_percentage,
            "trend": trend,
            "volume": total_volume,
            "up_count": up_count,
            "flat_count": flat_count,
            "down_count": down_count,
            "limit_up": "、".join(limit_up_figures[:3]) if limit_up_figures else "无",
            "limit_down": "、".join(limit_down_figures[:3]) if limit_down_figures else "无",
            "constituent_count": len(constituents)
        }

    @classmethod
    def _get_constituents(cls, db: Session) -> List[Tuple[Figure, int]]:
        """
        获取HPI成分股列表

        成分股筛选规则：
        1. 纳入：有成交量的活跃手办
        2. 剔除：长期无交易的"僵尸股"
        3. 权重：按成交量动态加权

        Args:
            db: 数据库会话

        Returns:
            List[Tuple[Figure, int]]: 成分股列表（手办, 成交量）
        """
        # 获取所有活跃手办
        all_figures = db.query(Figure).filter(Figure.is_active == 1).all()

        constituents = []
        today = date.today()
        zombie_date = today - timedelta(days=cls.ZOMBIE_DAYS)

        for fig in all_figures:
            # 计算该手办的今日成交量
            volume = cls._get_figure_volume(db, fig.id)

            # 检查是否为僵尸股（长期无交易）
            last_trade_date = cls._get_last_trade_date(db, fig.id)

            # 纳入条件：
            # 1. 有成交量 或 近期有交易
            # 2. 有市场价或定价（非僵尸股）
            is_active = (
                volume >= cls.MIN_VOLUME_THRESHOLD or
                (last_trade_date and last_trade_date >= zombie_date)
            )

            has_price = fig.market_price is not None or fig.price is not None

            if is_active and has_price:
                constituents.append((fig, volume))

        return constituents

    @classmethod
    def _get_figure_volume(cls, db: Session, figure_id: int) -> int:
        """
        获取手办的今日成交量

        成交量来源：
        - SoldOrder：今日完成的卖出订单

        Args:
            db: 数据库会话
            figure_id: 手办ID

        Returns:
            int: 今日成交量
        """
        today = date.today()
        tomorrow = today + timedelta(days=1)

        # 查询今日卖出的数量
        sold_volume = db.query(func.coalesce(func.sum(SoldOrder.quantity), 0)).filter(
            SoldOrder.figure_id == figure_id,
            SoldOrder.is_active == 1,
            SoldOrder.status == "已完成",
            SoldOrder.created_at >= today,
            SoldOrder.created_at < tomorrow
        ).scalar() or 0

        return int(sold_volume)

    @classmethod
    def _get_last_trade_date(cls, db: Session, figure_id: int) -> Optional[date]:
        """
        获取手办的最后交易日期

        Args:
            db: 数据库会话
            figure_id: 手办ID

        Returns:
            Optional[date]: 最后交易日期
        """
        # 查询最后完成的卖出订单
        last_sold = db.query(SoldOrder).filter(
            SoldOrder.figure_id == figure_id,
            SoldOrder.is_active == 1,
            SoldOrder.status == "已完成"
        ).order_by(SoldOrder.created_at.desc()).first()

        if last_sold and last_sold.created_at:
            return last_sold.created_at.date() if hasattr(last_sold.created_at, 'date') else last_sold.created_at

        return None

    @classmethod
    def _calculate_market_stats(cls, constituents: List[Tuple[Figure, int]]) -> tuple:
        """
        计算市场涨跌平家数统计

        Args:
            constituents: 成分股列表

        Returns:
            tuple: (上涨家数, 平盘家数, 下跌家数)
        """
        up_count = 0
        flat_count = 0
        down_count = 0

        for fig, volume in constituents:
            if fig.price and fig.price > 0 and fig.market_price and fig.market_price > 0:
                change_percentage = ((fig.market_price - fig.price) / fig.price) * 100

                if change_percentage > 1:
                    up_count += 1
                elif change_percentage >= -1:
                    flat_count += 1
                else:
                    down_count += 1
            else:
                # 没有价格数据，计入平盘
                flat_count += 1

        return up_count, flat_count, down_count

    @classmethod
    def _get_limit_figures(cls, constituents: List[Tuple[Figure, int]]) -> tuple:
        """
        获取涨停和跌停的手办列表

        涨停：涨幅 >= 10%
        跌停：跌幅 <= -10%

        Args:
            constituents: 成分股列表

        Returns:
            tuple: (涨停列表, 跌停列表)
        """
        limit_up = []
        limit_down = []

        for fig, volume in constituents:
            if fig.price and fig.price > 0 and fig.market_price and fig.market_price > 0:
                change_percentage = ((fig.market_price - fig.price) / fig.price) * 100

                if change_percentage >= 10:
                    limit_up.append(fig.name)
                elif change_percentage <= -10:
                    limit_down.append(fig.name)

        return limit_up, limit_down

    @classmethod
    def _get_yesterday_hpi(cls, db: Session) -> Optional[float]:
        """
        获取昨日HPI值

        Args:
            db: 数据库会话

        Returns:
            Optional[float]: 昨日HPI值，如果没有则返回None
        """
        # TODO: 后续可以创建HPI历史记录表，这里暂时返回None
        # 使用基准值作为昨日值
        return None

    @classmethod
    def get_hpi_for_asset_comparison(cls, db: Session) -> Dict[str, Any]:
        """
        获取HPI数据供资产看板对比使用

        资产看板使用HPI作为"大盘基准"计算"跑赢大盘"

        Args:
            db: 数据库会话

        Returns:
            Dict: HPI数据
        """
        return cls.calculate_hpi(db)

    @classmethod
    def check_systemic_risk(cls, db: Session) -> Optional[Dict[str, Any]]:
        """
        检查系统性风险（用于预警模块）

        预警规则：
        - HPI单日跌幅 > 5%：触发市场系统性风险预警

        Args:
            db: 数据库会话

        Returns:
            Optional[Dict]: 预警信息，如果没有风险返回None
        """
        hpi_data = cls.calculate_hpi(db)

        # 单日跌幅超过5%触发预警
        if hpi_data["change_percentage"] < -5:
            return {
                "type": "systemic_risk",
                "level": "high",
                "title": "市场系统性风险预警",
                "message": f"HPI单日跌幅达{abs(hpi_data['change_percentage'])}%，市场出现系统性风险，建议谨慎操作",
                "hpi_value": hpi_data["value"],
                "hpi_change": hpi_data["change"],
                "hpi_change_percentage": hpi_data["change_percentage"]
            }

        return None
