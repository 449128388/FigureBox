"""
持仓快照模型
记录用户每日的持仓明细，用于历史收益曲线计算
"""
from sqlalchemy import Column, Integer, Date, DateTime, Numeric, ForeignKey, Index
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.models.database import Base


class HoldingSnapshot(Base):
    """
    持仓快照模型

    功能说明：
    - 每天记录用户的持仓明细（每个手办一条记录）
    - 用于计算历史日期的收益曲线
    - 支持回溯到任意历史日期的持仓状况

    字段说明：
    - user_id: 用户ID
    - snapshot_date: 快照日期
    - figure_id: 手办ID
    - quantity: 当日收盘持仓数量
    - avg_cost: 当日该手办加权平均成本（单价）
    - total_cost: avg_cost × quantity，当日该手办总成本
    - market_price: 当日该手办市场价
    - market_value: market_price × quantity，当日该手办总市值
    - floating_pnl: market_value − total_cost，当日该手办浮动盈亏
    - floating_pnl_rate: floating_pnl / total_cost × 100%，浮动盈亏率
    - days_held: 该手办截至当日的累计持仓天数
    - created_at: 快照生成时间
    """
    __tablename__ = "holding_snapshots"

    # 主键
    id = Column(Integer, primary_key=True, index=True)

    # 外键关联
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    figure_id = Column(Integer, ForeignKey("figures.id"), nullable=False, index=True)

    # 快照日期
    snapshot_date = Column(Date, nullable=False, index=True)

    # 持仓数据
    quantity = Column(Integer, nullable=False, default=0)  # 当日收盘持仓数量
    avg_cost = Column(Numeric(12, 2), nullable=False, default=0)  # 加权平均成本（单价）
    total_cost = Column(Numeric(14, 2), nullable=False, default=0)  # 总成本

    # 市值数据
    market_price = Column(Numeric(12, 2), nullable=False, default=0)  # 当日市场价
    market_value = Column(Numeric(14, 2), nullable=False, default=0)  # 总市值

    # 盈亏数据
    floating_pnl = Column(Numeric(14, 2), nullable=False, default=0)  # 浮动盈亏
    floating_pnl_rate = Column(Numeric(8, 4), nullable=False, default=0)  # 浮动盈亏率

    # 持仓天数
    days_held = Column(Integer, nullable=False, default=0)  # 累计持仓天数

    # 时间戳
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # 关系
    user = relationship("User")  # 关联用户对象
    figure = relationship("Figure")  # 关联手办对象

    # 联合唯一索引：每个用户每天每个手办只有一条记录
    __table_args__ = (
        Index('idx_user_date_figure', 'user_id', 'snapshot_date', 'figure_id', unique=True),
        Index('idx_snapshot_date', 'snapshot_date'),  # 便于按日期查询
    )


class HoldingSnapshotSummary(Base):
    """
    持仓快照汇总记录

    功能说明：
    - 每天记录用户持仓的汇总数据
    - 用于快速查询某日的整体持仓状况
    - 避免频繁聚合计算

    字段说明：
    - user_id: 用户ID
    - snapshot_date: 快照日期
    - total_market_value: 当日总市值
    - total_cost: 当日总成本
    - total_floating_pnl: 当日总浮动盈亏
    - total_floating_pnl_rate: 当日总浮动盈亏率
    - holding_count: 当日持仓手办种数
    - total_quantity: 当日持仓总件数
    - created_at: 快照生成时间
    """
    __tablename__ = "holding_snapshot_summaries"

    # 主键
    id = Column(Integer, primary_key=True, index=True)

    # 外键关联
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)

    # 快照日期
    snapshot_date = Column(Date, nullable=False, index=True)

    # 汇总数据
    total_market_value = Column(Numeric(16, 2), nullable=False, default=0)  # 当日总市值
    total_cost = Column(Numeric(16, 2), nullable=False, default=0)  # 当日总成本
    total_floating_pnl = Column(Numeric(16, 2), nullable=False, default=0)  # 当日总浮动盈亏
    total_floating_pnl_rate = Column(Numeric(8, 4), nullable=False, default=0)  # 当日总浮动盈亏率

    # 持仓统计
    holding_count = Column(Integer, nullable=False, default=0)  # 持仓手办种数
    total_quantity = Column(Integer, nullable=False, default=0)  # 持仓总件数

    # 时间戳
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # 关系
    user = relationship("User")  # 关联用户对象

    # 联合唯一索引：每个用户每天只有一条汇总记录
    __table_args__ = (
        Index('idx_user_summary_date', 'user_id', 'snapshot_date', unique=True),
    )
