"""
日涨跌计算服务
提供日涨跌计算、历史回溯、快照管理等功能
采用企业级服务层架构
"""
from datetime import date, timedelta, datetime
from typing import Dict, Any, Optional, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.models.user_asset_snapshot import UserAssetSnapshot
from app.models.asset_transaction import AssetTransaction
from app.models.figure import Figure
from app.models.order import Order


class DailyChangeService:
    """
    日涨跌计算服务类

    提供以下核心功能：
    1. 计算日涨跌金额和百分比
    2. 支持向前回溯到最近有缓存的日期
    3. 首次使用/无昨日缓存时的特殊处理
    4. 连续多日未刷新时的历史对比
    """

    @staticmethod
    def calculate_daily_change(
        db: Session,
        user_id: int,
        total_assets: float
    ) -> Dict[str, Any]:
        """
        计算日涨跌（支持T-1/T-2/最近日期/30天提示）

        优先级：
        1. 昨天（T-1）- 正常情况，最理想
        2. 前天（T-2）- 昨天漏拍/未刷新行情
        3. 最近有数据的日期 - 连续多日未打开系统（超过30天加提示）
        4. 无历史数据 - 全新用户，首次使用

        Args:
            db: 数据库会话
            user_id: 用户ID
            total_assets: 当前总资产

        Returns:
            Dict包含: {
                daily_change: 涨跌金额,
                daily_change_percentage: 涨跌百分比,
                has_daily_change: 是否有对比数据,
                comparison_date: 对比日期（用于展示"较X月X日"）,
                comparison_type: 对比类型（yesterday/day_before_yesterday/recent/stale）,
                days_since_last_update: 距离上次更新的天数,
                show_stale_warning: 是否显示过期警告
            }
        """
        today = date.today()
        yesterday = today - timedelta(days=1)
        day_before_yesterday = today - timedelta(days=2)

        # 1. 优先级1：尝试获取昨天（T-1）的快照
        yesterday_snapshot = DailyChangeService._get_snapshot(db, user_id, yesterday)
        if yesterday_snapshot:
            return DailyChangeService._calculate_change_v2(
                total_assets,
                float(yesterday_snapshot.total_asset),
                yesterday,
                comparison_type="yesterday"
            )

        # 2. 优先级2：尝试获取前天（T-2）的快照
        day_before_yesterday_snapshot = DailyChangeService._get_snapshot(db, user_id, day_before_yesterday)
        if day_before_yesterday_snapshot:
            return DailyChangeService._calculate_change_v2(
                total_assets,
                float(day_before_yesterday_snapshot.total_asset),
                day_before_yesterday,
                comparison_type="day_before_yesterday"
            )

        # 3. 优先级3：向前回溯到最近有缓存的日期
        latest_snapshot = DailyChangeService._get_latest_snapshot_before_date(
            db, user_id, day_before_yesterday
        )

        if latest_snapshot:
            days_since = (today - latest_snapshot.snapshot_date).days
            # 超过30天标记为stale
            comparison_type = "stale" if days_since > 30 else "recent"
            return DailyChangeService._calculate_change_v2(
                total_assets,
                float(latest_snapshot.total_asset),
                latest_snapshot.snapshot_date,
                comparison_type=comparison_type,
                days_since_last_update=days_since
            )

        # 4. 优先级4：没有任何历史记录
        return {
            "daily_change": 0,
            "daily_change_percentage": 0,
            "has_daily_change": False,
            "comparison_date": None,
            "comparison_type": None,
            "days_since_last_update": None,
            "show_stale_warning": False
        }

    @staticmethod
    def _get_snapshot(
        db: Session,
        user_id: int,
        snapshot_date: date
    ) -> Optional[UserAssetSnapshot]:
        """
        获取指定日期的资产快照

        Args:
            db: 数据库会话
            user_id: 用户ID
            snapshot_date: 快照日期

        Returns:
            UserAssetSnapshot对象或None
        """
        return db.query(UserAssetSnapshot).filter(
            UserAssetSnapshot.user_id == user_id,
            UserAssetSnapshot.snapshot_date == snapshot_date
        ).first()

    @staticmethod
    def _get_latest_snapshot_before_date(
        db: Session,
        user_id: int,
        before_date: date
    ) -> Optional[UserAssetSnapshot]:
        """
        获取指定日期之前最新的资产快照

        Args:
            db: 数据库会话
            user_id: 用户ID
            before_date: 查询此日期之前的记录

        Returns:
            UserAssetSnapshot对象或None
        """
        return db.query(UserAssetSnapshot).filter(
            UserAssetSnapshot.user_id == user_id,
            UserAssetSnapshot.snapshot_date < before_date
        ).order_by(UserAssetSnapshot.snapshot_date.desc()).first()

    @staticmethod
    def _calculate_change(
        current_assets: float,
        base_assets: float,
        base_date: date,
        is_historical: bool = False
    ) -> Dict[str, Any]:
        """
        计算涨跌数据（旧版本，保持兼容性）

        Args:
            current_assets: 当前资产
            base_assets: 基准资产
            base_date: 基准日期
            is_historical: 是否是历史对比

        Returns:
            涨跌数据字典
        """
        if base_assets <= 0:
            return {
                "daily_change": 0,
                "daily_change_percentage": 0,
                "has_daily_change": True,
                "comparison_date": base_date.isoformat(),
                "is_historical_comparison": is_historical
            }

        daily_change = current_assets - base_assets
        daily_change_percentage = (daily_change / base_assets) * 100

        return {
            "daily_change": round(daily_change, 2),
            "daily_change_percentage": round(daily_change_percentage, 2),
            "has_daily_change": True,
            "comparison_date": base_date.isoformat(),
            "is_historical_comparison": is_historical
        }

    @staticmethod
    def _calculate_change_v2(
        current_assets: float,
        base_assets: float,
        base_date: date,
        comparison_type: str,
        days_since_last_update: int = None
    ) -> Dict[str, Any]:
        """
        计算涨跌数据（新版本，支持T-1/T-2/最近日期/30天提示）

        Args:
            current_assets: 当前资产
            base_assets: 基准资产
            base_date: 基准日期
            comparison_type: 对比类型（yesterday/day_before_yesterday/recent/stale）
            days_since_last_update: 距离上次更新的天数

        Returns:
            涨跌数据字典
        """
        if base_assets <= 0:
            return {
                "daily_change": 0,
                "daily_change_percentage": 0,
                "has_daily_change": True,
                "comparison_date": base_date.isoformat(),
                "comparison_type": comparison_type,
                "days_since_last_update": days_since_last_update,
                "show_stale_warning": comparison_type == "stale"
            }

        daily_change = current_assets - base_assets
        daily_change_percentage = (daily_change / base_assets) * 100

        return {
            "daily_change": round(daily_change, 2),
            "daily_change_percentage": round(daily_change_percentage, 2),
            "has_daily_change": True,
            "comparison_date": base_date.isoformat(),
            "comparison_type": comparison_type,
            "days_since_last_update": days_since_last_update,
            "show_stale_warning": comparison_type == "stale"
        }

    @staticmethod
    def create_snapshot(
        db: Session,
        user_id: int,
        snapshot_date: date,
        total_asset: float,
        total_cost: float = 0,
        pi_index: Optional[float] = None
    ) -> UserAssetSnapshot:
        """
        创建资产快照

        Args:
            db: 数据库会话
            user_id: 用户ID
            snapshot_date: 快照日期
            total_asset: 总资产
            total_cost: 总成本
            pi_index: 塑料手办指数 (PI)

        Returns:
            创建的快照对象
        """
        # 检查是否已存在
        existing = DailyChangeService._get_snapshot(db, user_id, snapshot_date)
        if existing:
            # 更新现有记录
            existing.total_asset = total_asset
            existing.total_cost = total_cost
            # pi_index = None 也要写入（清空当日无 PI 时的旧值）
            existing.pi_index = pi_index
            db.commit()
            return existing

        # 创建新记录
        snapshot = UserAssetSnapshot(
            user_id=user_id,
            snapshot_date=snapshot_date,
            total_asset=total_asset,
            total_cost=total_cost,
            pi_index=pi_index,
            created_at=datetime.now()
        )
        db.add(snapshot)
        db.commit()
        return snapshot

    @staticmethod
    def get_or_create_yesterday_snapshot(
        db: Session,
        user_id: int,
        current_total_assets: float
    ) -> UserAssetSnapshot:
        """
        获取或创建昨日快照（用于首次使用场景）

        当用户首次点击【刷新资产】时，自动将当前总资产作为昨日基准数据

        Args:
            db: 数据库会话
            user_id: 用户ID
            current_total_assets: 当前总资产

        Returns:
            昨日快照对象
        """
        yesterday = date.today() - timedelta(days=1)

        # 检查是否已存在
        existing = DailyChangeService._get_snapshot(db, user_id, yesterday)
        if existing:
            return existing

        # 创建昨日快照
        return DailyChangeService.create_snapshot(
            db=db,
            user_id=user_id,
            snapshot_date=yesterday,
            total_asset=current_total_assets,
            total_cost=0  # 首次使用场景：昨日无任何历史数据可回溯，成本按 0 占位
        )

    @staticmethod
    def has_any_orders(db: Session, user_id: int) -> bool:
        """
        判断用户是否曾经有过任何订单（不论状态）

        用于过滤纯测试账户（无任何交易记录），避免为这些账户产生冗余快照。

        Args:
            db: 数据库会话
            user_id: 用户ID

        Returns:
            True=有过订单，False=从未下过单
        """
        return db.query(Order).filter(
            Order.user_id == user_id,
            Order.is_active == 1,
        ).first() is not None

    @staticmethod
    def calculate_total_assets_from_transactions(
        db: Session,
        user_id: int
    ) -> float:
        """
        基于库存账计算当前总资产

        Args:
            db: 数据库会话
            user_id: 用户ID

        Returns:
            总资产金额
        """
        # 查询所有买入记录的剩余数量，并关联手办信息计算市值
        subquery = db.query(
            AssetTransaction.figure_id,
            func.sum(AssetTransaction.remaining_quantity).label('total_remaining')
        ).filter(
            AssetTransaction.user_id == user_id,
            AssetTransaction.transaction_type == "buy",
            AssetTransaction.is_active == True
        ).group_by(AssetTransaction.figure_id).subquery()

        # 关联手办表计算总市值
        total_assets = db.query(
            func.sum(
                (func.coalesce(Figure.market_price, Figure.price, 0) *
                 func.coalesce(subquery.c.total_remaining, 0))
            )
        ).select_from(subquery).outerjoin(Figure, Figure.id == subquery.c.figure_id).scalar()

        return total_assets or 0
