"""
资产日涨跌快照定时任务调度器
每天北京时间00:05自动保存所有用户的总资产快照到user_asset_snapshots表
用于明日计算日涨跌的对比基准
"""
import logging
from datetime import datetime, date
from typing import Dict
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from pytz import timezone
from sqlalchemy.orm import Session

from app.models.database import SessionLocal
from app.models.user import User
from app.models.order import Order
from app.models.asset_transaction import AssetTransaction, PlasticIndexHistory
from app.services.dashboard_service.assets_service.daily_change_service import DailyChangeService
from app.services.sold_order_service.currency_service import CurrencyService

logger = logging.getLogger(__name__)

# 北京时间时区
BEIJING_TZ = timezone('Asia/Shanghai')


class DailySnapshotScheduler:
    """资产日涨跌快照定时任务调度器"""

    _instance = None
    _scheduler = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if self._scheduler is None:
            # 使用北京时间时区
            self._scheduler = BackgroundScheduler(timezone=BEIJING_TZ)

    def start(self):
        """启动定时任务调度器"""
        if not self._scheduler.running:
            # 添加每日北京时间00:05执行的任务
            self._scheduler.add_job(
                func=self._daily_save_asset_snapshot,
                trigger=CronTrigger(hour=0, minute=5, timezone=BEIJING_TZ),
                id='daily_asset_snapshot_save',
                name='每日资产快照保存（用于日涨跌计算）',
                replace_existing=True
            )
            self._scheduler.start()
            logger.info("资产日涨跌快照定时任务调度器已启动，每日北京时间00:05执行")

    def stop(self):
        """停止定时任务调度器"""
        if self._scheduler.running:
            self._scheduler.shutdown()
            logger.info("资产日涨跌快照定时任务调度器已停止")

    def _daily_save_asset_snapshot(self):
        """
        每日保存所有用户的资产快照

        执行逻辑：
        1. 获取所有用户
        2. 对每个用户计算当前总资产
        3. 保存到user_asset_snapshots表（snapshot_date = 今天）
           这样明天计算日涨跌时，今天的数据就是"昨日总资产"
        """
        db = SessionLocal()
        try:
            today = date.today()
            logger.info(f"开始执行每日资产快照保存任务 - {datetime.now()}")

            # 获取所有用户
            users = db.query(User).all()
            logger.info(f"共找到 {len(users)} 个用户")

            for user in users:
                try:
                    self._save_user_asset_snapshot(db, user.id, today)
                except Exception as e:
                    logger.error(f"保存用户 {user.id} 的资产快照失败: {e}")
                    continue

            logger.info(f"每日资产快照保存任务完成 - {datetime.now()}")

        except Exception as e:
            logger.error(f"执行每日资产快照保存任务失败: {e}")
        finally:
            db.close()

    def _save_user_asset_snapshot(self, db: Session, user_id: int, snapshot_date: date):
        """
        保存指定用户的资产快照

        Args:
            db: 数据库会话
            user_id: 用户ID
            snapshot_date: 快照日期
        """
        try:
            # 跳过从未有过任何订单的"空用户"（纯测试账户），避免产生冗余 total_asset=0 快照
            if not DailyChangeService.has_any_orders(db, user_id):
                logger.info(f"用户 {user_id} 无任何订单记录，跳过快照保存")
                return

            # 计算当前总资产
            total_assets = DailyChangeService.calculate_total_assets_from_transactions(db, user_id)

            # 计算 total_cost：在柜 FIFO 累计 + 未入库预购订单累计（双向口径合并）
            #   在柜部分 = Σ(buy.price + Σadjust) × remaining_quantity（HoldingPositionService 口径）
            #   预购部分 = Σ(deposit + balance) 转 CNY（status in 未支付/已支付/已取消）
            #   「未支付」/「已支付」/「已取消」3 状态订单未生成 asset_transactions buy 行，
            #   故 FIFO 路径不覆盖这些"在路上"或"已付钱未入库"的钱，需补齐
            in_cabinet_cost = self._calculate_total_cost_fifo(db, user_id)
            pending_cost = self._calculate_pending_orders_cost_cny(db, user_id)
            total_cost = in_cabinet_cost + pending_cost

            # 查询当日塑料手办指数 (PI)（plastic_index_history 表）
            #   PI = 资产模块的个人持仓相对基准日涨跌指数，与 HPI（市场加权平均）口径不同
            pi_record = db.query(PlasticIndexHistory).filter(
                PlasticIndexHistory.user_id == user_id,
                PlasticIndexHistory.record_date == snapshot_date,
            ).order_by(PlasticIndexHistory.record_date.desc()).first()
            pi_index = float(pi_record.current_value) if pi_record else None

            # 创建或更新快照
            DailyChangeService.create_snapshot(
                db=db,
                user_id=user_id,
                snapshot_date=snapshot_date,
                total_asset=total_assets,
                total_cost=round(total_cost, 2),
                pi_index=pi_index
            )

            logger.info(
                f"用户 {user_id} 的资产快照已保存: total_asset={total_assets}, "
                f"total_cost={round(total_cost, 2)}, pi_index={pi_index}"
            )

        except Exception as e:
            logger.error(f"保存用户 {user_id} 的资产快照时出错: {e}")
            raise

    @staticmethod
    def _calculate_pending_orders_cost_cny(db: Session, user_id: int) -> float:
        """
        累计未入库预购订单的「已实际投入」成本（折算 CNY）

        业务背景：
        - orders 表 status in ('未支付', '已支付', '已取消') 的订单没有生成
          asset_transactions 表的 buy 行（因为还没「入库」动作），所以 FIFO 路径
          （_calculate_total_cost_fifo）覆盖不到这部分钱
        - 这些订单的 deposit（定金）+ balance（尾款）已付出去或已锁定，
          属于"在路上 / 预购中 / 已取消待退款"的资金占用，应计入 total_cost

        汇率口径：
        - 每笔订单 deposit + balance 各自按 deposit_currency / balance_currency
          折算 CNY（实时汇率，ExchangeRateService 不可用时降级 FALLBACK_RATES）
        - 与 HPI 跑批（hpi_components.total_buy_amount）口径一致

        Args:
            db: 数据库会话
            user_id: 用户ID

        Returns:
            pending_cost（人民币元）
        """
        pending_orders = (
            db.query(Order)
            .filter(
                Order.user_id == user_id,
                Order.is_active == 1,
                Order.status.in_(("未支付", "已支付", "已取消")),
            )
            .all()
        )

        pending_cost = 0.0
        for order in pending_orders:
            deposit_cny = CurrencyService.to_cny(
                order.deposit or 0, order.deposit_currency or "CNY", db
            )
            balance_cny = CurrencyService.to_cny(
                order.balance or 0, order.balance_currency or "CNY", db
            )
            pending_cost += deposit_cny + balance_cny

        return pending_cost

    @staticmethod
    def _calculate_total_cost_fifo(db: Session, user_id: int) -> float:
        """
        按 FIFO 成本均价口径计算用户当前在柜全部手办的总成本

        算法：
        1. 聚合同 order_id 下所有 adjust 调整记录（带符号：追加为正、减少为负）
        2. 查所有 transaction_type='buy' 且 remaining_quantity > 0 的行
        3. 每行 final_price = buy.price + Σadjust
        4. sum(final_price × remaining_quantity) 即为 total_cost

        与 holding_snapshot_service.generate_daily_snapshot 第 48-82 行
        聚合口径完全一致，保证两表数据自洽。

        Args:
            db: 数据库会话
            user_id: 用户ID

        Returns:
            total_cost（人民币元）
        """
        # 1. 聚合 adjust 调整（同 order_id 求和，带符号）
        adjust_map: Dict[int, float] = {}
        adjust_rows = db.query(
            AssetTransaction.order_id,
            AssetTransaction.price,
        ).filter(
            AssetTransaction.user_id == user_id,
            AssetTransaction.transaction_type == "adjust",
            AssetTransaction.is_active == True,
        ).all()
        for order_id, adj_price in adjust_rows:
            adjust_map[order_id] = adjust_map.get(order_id, 0.0) + (adj_price or 0.0)

        # 2. 查所有 buy + remaining_quantity > 0 的行
        buy_rows = db.query(
            AssetTransaction.figure_id,
            AssetTransaction.order_id,
            AssetTransaction.remaining_quantity,
            AssetTransaction.price,
        ).filter(
            AssetTransaction.user_id == user_id,
            AssetTransaction.transaction_type == "buy",
            AssetTransaction.remaining_quantity > 0,
            AssetTransaction.is_active == True,
        ).all()

        # 3. 累计 total_cost
        total_cost = 0.0
        for row in buy_rows:
            final_price = (row.price or 0) + adjust_map.get(row.order_id, 0.0)
            total_cost += final_price * (row.remaining_quantity or 0)

        return total_cost


# 全局调度器实例
daily_snapshot_scheduler = DailySnapshotScheduler()


def start_daily_snapshot_scheduler():
    """启动日涨跌快照定时任务（用于应用启动时调用）"""
    daily_snapshot_scheduler.start()


def stop_daily_snapshot_scheduler():
    """停止日涨跌快照定时任务（用于应用关闭时调用）"""
    daily_snapshot_scheduler.stop()
