"""
持仓快照服务
提供持仓快照的生成、查询等功能
采用企业级服务层架构
"""
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, date, timedelta
from decimal import Decimal

from app.models.holding_snapshot import HoldingSnapshot, HoldingSnapshotSummary
from app.models.asset import AssetTransaction
from app.models.figure import Figure
from app.models.user import User


class HoldingSnapshotService:
    """
    持仓快照服务类

    提供以下核心功能：
    1. 生成每日持仓快照
    2. 查询历史持仓快照
    3. 计算历史日期的收益曲线
    """

    @staticmethod
    def generate_daily_snapshot(
        db: Session,
        user_id: int,
        snapshot_date: date = None
    ) -> Dict[str, Any]:
        """
        生成指定日期的持仓快照

        Args:
            db: 数据库会话
            user_id: 用户ID
            snapshot_date: 快照日期，默认为今天

        Returns:
            Dict: 包含生成的快照信息和汇总数据
        """
        if snapshot_date is None:
            snapshot_date = datetime.now().date()

        # 查询用户所有有持仓的手办
        holdings = db.query(
            AssetTransaction.figure_id,
            func.sum(AssetTransaction.remaining_quantity).label('total_quantity'),
            func.sum(AssetTransaction.price * AssetTransaction.remaining_quantity).label('total_cost')
        ).filter(
            AssetTransaction.user_id == user_id,
            AssetTransaction.transaction_type == "buy",
            AssetTransaction.remaining_quantity > 0,
            AssetTransaction.is_active == True
        ).group_by(AssetTransaction.figure_id).all()

        if not holdings:
            # 无持仓，生成空快照
            summary = HoldingSnapshotService._create_empty_summary(db, user_id, snapshot_date)
            return {
                "success": True,
                "snapshot_date": snapshot_date.isoformat(),
                "holding_count": 0,
                "summary": summary
            }

        # 获取手办ID列表
        figure_ids = [h.figure_id for h in holdings]

        # 获取手办信息（包括市场价）
        figures = db.query(Figure).filter(Figure.id.in_(figure_ids)).all()
        figure_map = {f.id: f for f in figures}

        # 计算每个手办的首次买入日期（用于计算持仓天数）
        first_buy_dates = db.query(
            AssetTransaction.figure_id,
            func.min(AssetTransaction.transaction_date).label('first_buy_date')
        ).filter(
            AssetTransaction.user_id == user_id,
            AssetTransaction.transaction_type == "buy",
            AssetTransaction.figure_id.in_(figure_ids),
            AssetTransaction.is_active == True
        ).group_by(AssetTransaction.figure_id).all()
        first_buy_map = {f.figure_id: f.first_buy_date for f in first_buy_dates}

        # 生成持仓快照明细
        snapshot_details = []
        total_market_value = Decimal('0')
        total_cost = Decimal('0')
        total_quantity = 0

        for holding in holdings:
            figure_id = holding.figure_id
            quantity = int(holding.total_quantity or 0)
            cost = Decimal(str(holding.total_cost or 0))

            if quantity <= 0:
                continue

            # 获取手办信息
            figure = figure_map.get(figure_id)
            if not figure:
                continue

            # 计算加权平均成本
            avg_cost = cost / quantity

            # 获取市场价
            market_price = Decimal(str(figure.market_price or figure.price or 0))

            # 计算市值
            market_value = market_price * quantity

            # 计算浮动盈亏
            floating_pnl = market_value - cost
            floating_pnl_rate = (floating_pnl / cost * 100) if cost > 0 else Decimal('0')

            # 计算持仓天数
            first_buy_date = first_buy_map.get(figure_id, snapshot_date)
            if isinstance(first_buy_date, datetime):
                first_buy_date = first_buy_date.date()
            days_held = (snapshot_date - first_buy_date).days + 1

            # 创建持仓快照记录
            snapshot = HoldingSnapshot(
                user_id=user_id,
                snapshot_date=snapshot_date,
                figure_id=figure_id,
                quantity=quantity,
                avg_cost=avg_cost,
                total_cost=cost,
                market_price=market_price,
                market_value=market_value,
                floating_pnl=floating_pnl,
                floating_pnl_rate=floating_pnl_rate,
                days_held=days_held
            )
            db.merge(snapshot)  # 使用merge实现upsert

            snapshot_details.append({
                "figure_id": figure_id,
                "figure_name": figure.name,
                "quantity": quantity,
                "avg_cost": float(avg_cost),
                "market_price": float(market_price),
                "floating_pnl": float(floating_pnl)
            })

            # 累加汇总数据
            total_market_value += market_value
            total_cost += cost
            total_quantity += quantity

        # 计算汇总数据
        total_floating_pnl = total_market_value - total_cost
        total_floating_pnl_rate = (total_floating_pnl / total_cost * 100) if total_cost > 0 else Decimal('0')
        holding_count = len(snapshot_details)

        # 创建汇总记录
        summary = HoldingSnapshotSummary(
            user_id=user_id,
            snapshot_date=snapshot_date,
            total_market_value=total_market_value,
            total_cost=total_cost,
            total_floating_pnl=total_floating_pnl,
            total_floating_pnl_rate=total_floating_pnl_rate,
            holding_count=holding_count,
            total_quantity=total_quantity
        )
        db.merge(summary)  # 使用merge实现upsert

        db.commit()

        return {
            "success": True,
            "snapshot_date": snapshot_date.isoformat(),
            "holding_count": holding_count,
            "total_quantity": total_quantity,
            "total_market_value": float(total_market_value),
            "total_cost": float(total_cost),
            "total_floating_pnl": float(total_floating_pnl),
            "total_floating_pnl_rate": float(total_floating_pnl_rate),
            "details": snapshot_details
        }

    @staticmethod
    def _create_empty_summary(
        db: Session,
        user_id: int,
        snapshot_date: date
    ) -> HoldingSnapshotSummary:
        """
        创建空的汇总记录（无持仓时）

        Args:
            db: 数据库会话
            user_id: 用户ID
            snapshot_date: 快照日期

        Returns:
            HoldingSnapshotSummary: 空的汇总记录
        """
        summary = HoldingSnapshotSummary(
            user_id=user_id,
            snapshot_date=snapshot_date,
            total_market_value=Decimal('0'),
            total_cost=Decimal('0'),
            total_floating_pnl=Decimal('0'),
            total_floating_pnl_rate=Decimal('0'),
            holding_count=0,
            total_quantity=0
        )
        db.merge(summary)
        db.commit()
        return summary

    @staticmethod
    def get_historical_profit_curve(
        db: Session,
        user_id: int,
        days: int = 30
    ) -> List[Dict[str, Any]]:
        """
        获取历史收益曲线数据（基于持仓快照）

        Args:
            db: 数据库会话
            user_id: 用户ID
            days: 查询天数，默认30天

        Returns:
            List[Dict]: 收益曲线数据列表
        """
        end_date = datetime.now().date()
        start_date = end_date - timedelta(days=days)

        # 查询历史汇总记录
        summaries = db.query(HoldingSnapshotSummary).filter(
            HoldingSnapshotSummary.user_id == user_id,
            HoldingSnapshotSummary.snapshot_date >= start_date,
            HoldingSnapshotSummary.snapshot_date <= end_date
        ).order_by(HoldingSnapshotSummary.snapshot_date.asc()).all()

        if not summaries:
            return []

        return [
            {
                "date": s.snapshot_date.isoformat(),
                "profit": float(s.total_floating_pnl),
                "market_value": float(s.total_market_value),
                "total_cost": float(s.total_cost),
                "holding_count": s.holding_count
            }
            for s in summaries
        ]

    @staticmethod
    def get_snapshot_by_date(
        db: Session,
        user_id: int,
        snapshot_date: date
    ) -> Optional[Dict[str, Any]]:
        """
        获取指定日期的持仓快照

        Args:
            db: 数据库会话
            user_id: 用户ID
            snapshot_date: 快照日期

        Returns:
            Optional[Dict]: 快照数据，如果不存在则返回None
        """
        summary = db.query(HoldingSnapshotSummary).filter(
            HoldingSnapshotSummary.user_id == user_id,
            HoldingSnapshotSummary.snapshot_date == snapshot_date
        ).first()

        if not summary:
            return None

        # 查询明细
        details = db.query(HoldingSnapshot).filter(
            HoldingSnapshot.user_id == user_id,
            HoldingSnapshot.snapshot_date == snapshot_date
        ).all()

        return {
            "snapshot_date": summary.snapshot_date.isoformat(),
            "total_market_value": float(summary.total_market_value),
            "total_cost": float(summary.total_cost),
            "total_floating_pnl": float(summary.total_floating_pnl),
            "total_floating_pnl_rate": float(summary.total_floating_pnl_rate),
            "holding_count": summary.holding_count,
            "total_quantity": summary.total_quantity,
            "details": [
                {
                    "figure_id": d.figure_id,
                    "figure_name": d.figure.name if d.figure else None,
                    "quantity": d.quantity,
                    "avg_cost": float(d.avg_cost),
                    "market_price": float(d.market_price),
                    "market_value": float(d.market_value),
                    "floating_pnl": float(d.floating_pnl),
                    "floating_pnl_rate": float(d.floating_pnl_rate),
                    "days_held": d.days_held
                }
                for d in details
            ]
        }

    @staticmethod
    def generate_all_users_snapshot(
        db: Session,
        snapshot_date: date = None
    ) -> Dict[str, Any]:
        """
        为所有用户生成持仓快照（用于定时任务）

        Args:
            db: 数据库会话
            snapshot_date: 快照日期，默认为今天

        Returns:
            Dict: 生成结果统计
        """
        if snapshot_date is None:
            snapshot_date = datetime.now().date()

        # 查询所有用户
        users = db.query(User).filter(User.is_active == True).all()

        results = {
            "snapshot_date": snapshot_date.isoformat(),
            "total_users": len(users),
            "success_count": 0,
            "failed_count": 0,
            "details": []
        }

        for user in users:
            try:
                result = HoldingSnapshotService.generate_daily_snapshot(
                    db, user.id, snapshot_date
                )
                results["success_count"] += 1
                results["details"].append({
                    "user_id": user.id,
                    "username": user.username,
                    "status": "success",
                    "holding_count": result.get("holding_count", 0)
                })
            except Exception as e:
                results["failed_count"] += 1
                results["details"].append({
                    "user_id": user.id,
                    "username": user.username,
                    "status": "failed",
                    "error": str(e)
                })

        return results
