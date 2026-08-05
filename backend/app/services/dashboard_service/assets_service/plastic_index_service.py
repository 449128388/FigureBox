"""
塑料手办指数服务模块
提供塑料手办指数的涨跌计算和历史记录管理
（简称 PI = Plastic Index；对应另一指数 HPI = Hobby Plastic Index / 塑料小人指数）

指数涨跌核心逻辑：
- 持仓手办市场价上涨（闲鱼成交价↑）→ 指数涨（成分股市值增加）
- 持仓手办市场价下跌（破发、再版）→ 指数跌（成分股市值缩水）
- 买入高价/热门手办 → 指数涨（通常）（新增高市值成分股）
- 卖出低价/亏损手办 → 指数涨（可能）（剔除低市值成分股，指数提纯）
- 卖出高价/盈利手办 → 指数跌（可能）（优质成分股被剔除）
- 手办再版/大量出货 → 指数跌（市场供给增加，价格崩盘）
"""
from datetime import datetime, date
from typing import Dict, Optional, Any, List, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import desc

from app.models.asset_transaction import PlasticIndexHistory
from app.models.figure import Figure


class PlasticIndexService:
    """塑料手办指数服务类"""

    # 基准日指数
    BASE_INDEX = 1000.0

    @classmethod
    def calculate_plastic_index(
        cls,
        db: Session,
        user_id: int,
        figures: List[Figure],
        total_assets: float
    ) -> Dict[str, Any]:
        """
        计算塑料手办指数及其涨跌

        计算公式：
        塑料指数 = 基准日指数 × (当前总市值 / 基准日总市值)

        基准日 = 最早购买手办的日期（开户首日）
        基准日总市值 = 基准日当天所有持仓手办的平均入手价格总和

        Args:
            db: 数据库会话
            user_id: 用户ID
            figures: 手办列表
            total_assets: 当前总资产

        Returns:
            Dict: 包含指数值、涨跌额、涨跌幅、基准日等信息
        """
        # 找到最早的购买日期作为基准日
        purchase_dates = [
            fig.purchase_date for fig in figures if fig.purchase_date
        ]

        if not purchase_dates:
            # 没有手办时，返回基准指数
            return {
                "current_value": cls.BASE_INDEX,
                "base_value": cls.BASE_INDEX,
                "change_value": 0.0,
                "change_percentage": 0.0,
                "base_date": date.today(),
                "trend": "flat"
            }

        base_date = min(purchase_dates)

        # 基准日总市值 = 基准日当天所有持仓手办的平均入手价格总和
        base_total_value = sum(
            (fig.average_purchase_price or 0) * (fig.quantity or 1)
            for fig in figures
        )

        # 如果没有成本数据，使用当前总资产作为基准
        if base_total_value <= 0:
            base_total_value = total_assets if total_assets > 0 else cls.BASE_INDEX

        # 计算当前塑料指数
        current_index = round(cls.BASE_INDEX * (total_assets / base_total_value), 2)

        # 获取昨日的指数记录用于计算涨跌
        yesterday_record = cls._get_yesterday_index(db, user_id)

        if yesterday_record:
            # 有昨日数据，计算涨跌
            change_value = round(current_index - yesterday_record.current_value, 2)
            change_percentage = round(
                (change_value / yesterday_record.current_value) * 100, 2
            ) if yesterday_record.current_value > 0 else 0.0
        else:
            # 没有昨日数据，与基准日比较
            change_value = round(current_index - cls.BASE_INDEX, 2)
            change_percentage = round(
                (change_value / cls.BASE_INDEX) * 100, 2
            )

        # 确定趋势
        if change_value > 0:
            trend = "up"
        elif change_value < 0:
            trend = "down"
        else:
            trend = "flat"

        return {
            "current_value": current_index,
            "base_value": cls.BASE_INDEX,
            "change_value": change_value,
            "change_percentage": change_percentage,
            "base_date": base_date,
            "trend": trend,
            "has_history": yesterday_record is not None
        }

    @classmethod
    def _get_yesterday_index(
        cls,
        db: Session,
        user_id: int
    ) -> Optional[PlasticIndexHistory]:
        """
        获取昨日的指数记录

        Args:
            db: 数据库会话
            user_id: 用户ID

        Returns:
            Optional[PlasticIndexHistory]: 昨日记录，如果没有则返回None
        """
        today = date.today()

        # 查询最近的历史记录（非今天）
        record = db.query(PlasticIndexHistory).filter(
            PlasticIndexHistory.user_id == user_id,
            PlasticIndexHistory.record_date < today
        ).order_by(desc(PlasticIndexHistory.record_date)).first()

        return record

    @classmethod
    def save_daily_index(
        cls,
        db: Session,
        user_id: int,
        index_data: Dict[str, Any]
    ) -> None:
        """
        保存每日指数记录

        Args:
            db: 数据库会话
            user_id: 用户ID
            index_data: 指数数据字典
        """
        today = date.today()
        now = datetime.now()

        # 检查今天是否已有记录
        existing = db.query(PlasticIndexHistory).filter(
            PlasticIndexHistory.user_id == user_id,
            PlasticIndexHistory.record_date == today
        ).first()

        if existing:
            # 更新现有记录
            existing.current_value = index_data["current_value"]
            existing.change_value = index_data["change_value"]
            existing.change_percentage = index_data["change_percentage"]
            existing.updated_at = now
        else:
            # 创建新记录
            new_record = PlasticIndexHistory(
                user_id=user_id,
                current_value=index_data["current_value"],
                change_value=index_data["change_value"],
                change_percentage=index_data["change_percentage"],
                base_value=index_data["base_value"],
                base_date=index_data["base_date"],
                record_date=today,
                created_at=now,
                updated_at=now
            )
            db.add(new_record)

        db.commit()

    @classmethod
    def get_index_comparison_data(
        cls,
        db: Session,
        user_id: int
    ) -> Optional[Dict[str, Any]]:
        """
        获取指数对比数据（用于前端显示）

        Args:
            db: 数据库会话
            user_id: 用户ID

        Returns:
            Optional[Dict]: 对比数据，如果没有历史记录返回None
        """
        records = db.query(PlasticIndexHistory).filter(
            PlasticIndexHistory.user_id == user_id
        ).order_by(desc(PlasticIndexHistory.record_date)).limit(2).all()

        if not records:
            return None

        if len(records) == 1:
            # 只有一条记录，与基准比较
            latest = records[0]
            change = latest.current_value - cls.BASE_INDEX
            pct = (change / cls.BASE_INDEX) * 100 if cls.BASE_INDEX > 0 else 0
            trend = "up" if change > 0 else ("down" if change < 0 else "flat")

            return {
                "current_value": latest.current_value,
                "change_value": round(change, 2),
                "change_percentage": round(pct, 2),
                "has_history": False,
                "trend": trend
            }

        # 有两条或以上记录，计算相对变化
        latest, prev = records[0], records[1]
        change = latest.current_value - prev.current_value
        pct = (change / prev.current_value) * 100 if prev.current_value > 0 else 0
        trend = "up" if change > 0 else ("down" if change < 0 else "flat")

        return {
            "current_value": latest.current_value,
            "change_value": round(change, 2),
            "change_percentage": round(pct, 2),
            "has_history": True,
            "trend": trend
        }

    @classmethod
    def get_plastic_index_history(
        cls,
        db: Session,
        user_id: int,
        days: int = 30
    ) -> List[Dict[str, Any]]:
        """
        获取塑料手办指数历史数据

        Args:
            db: 数据库会话
            user_id: 用户ID
            days: 查询天数

        Returns:
            List[Dict]: 历史数据列表
        """
        records = db.query(PlasticIndexHistory).filter(
            PlasticIndexHistory.user_id == user_id
        ).order_by(desc(PlasticIndexHistory.record_date)).limit(days).all()

        return [
            {
                "date": record.record_date.isoformat(),
                "value": record.current_value,
                "change_value": record.change_value,
                "change_percentage": record.change_percentage
            }
            for record in reversed(records)
        ]
