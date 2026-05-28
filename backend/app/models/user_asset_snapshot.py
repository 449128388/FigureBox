"""
用户资产每日快照模型
记录用户每日的资产状况，用于计算日涨跌
"""
from sqlalchemy import Column, Integer, Date, DateTime, Numeric, ForeignKey, Index
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.models.database import Base


class UserAssetSnapshot(Base):
    """
    用户资产每日快照模型

    功能说明：
    - 每日固定时间（00:05:00）记录用户的资产状况
    - 用于计算日涨跌的对比基准
    - 支持回溯到最近有缓存的日期计算涨跌

    字段说明：
    - user_id: 用户ID
    - snapshot_date: 快照日期
    - total_asset: 当日总资产
    - total_cost: 当日总成本
    - hpi_index: 当日塑料手办指数（可选）
    - created_at: 记录创建时间
    """
    __tablename__ = "user_asset_snapshots"

    # 主键
    id = Column(Integer, primary_key=True, index=True)

    # 外键关联
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)

    # 快照数据
    snapshot_date = Column(Date, nullable=False, index=True)
    total_asset = Column(Numeric(15, 2), nullable=False, default=0)
    total_cost = Column(Numeric(15, 2), nullable=False, default=0)
    hpi_index = Column(Numeric(10, 4), nullable=True)

    # 时间戳
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # 关系
    user = relationship("User")

    # 联合唯一索引：每个用户每天只有一条记录
    __table_args__ = (
        Index('idx_user_snapshot_date', 'user_id', 'snapshot_date', unique=True),
    )
