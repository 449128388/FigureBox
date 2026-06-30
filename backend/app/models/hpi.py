"""
HPI 模型 - 塑料小人指数（投资生涯全周期收益指数）

功能说明：
- hpi_daily：每日 HPI 快照，存储历史指数值
- hpi_components：成分股明细，记录每手办对指数的贡献

设计定位：
- HPI = 用户"塑料投资生涯全周期收益指数"
- 回答："从我买入每一体手办那天起，它们后来平均涨了多少？"
- 核心差异化：已出手办永久保留跟踪（永不剔除）
"""

from sqlalchemy import Column, Integer, Float, String, Date, DateTime, ForeignKey, UniqueConstraint, Index, text, func
from app.models.database import Base


class HPIDaily(Base):
    """HPI 每日快照表 - 存储历史指数值"""
    __tablename__ = "hpi_daily"
    __table_args__ = (
        UniqueConstraint("user_id", "record_date", name="uk_user_date"),
        {"mysql_engine": "InnoDB", "mysql_charset": "utf8mb4", "comment": "HPI每日快照表"}
    )

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, nullable=False, comment="用户ID")

    # 指数核心数据
    index_value = Column(Float, nullable=False, comment="HPI指数值")
    avg_return = Column(Float, nullable=False, comment="平均超额收益率%")

    # 统计维度
    total_figures = Column(Integer, nullable=False, comment="生涯累计交易手办数")
    holding_figures = Column(Integer, nullable=False, comment="当前在柜数")
    sold_figures = Column(Integer, nullable=False, comment="已出但跟踪数")

    # 盈亏分布
    up_count = Column(Integer, default=0, comment="买入后上涨的手办数")
    flat_count = Column(Integer, default=0, comment="持平")
    down_count = Column(Integer, default=0, comment="买入后下跌的手办数")

    # 卖飞/卖对统计
    sold_up_count = Column(Integer, default=0, comment="卖出后上涨（卖飞）")
    sold_down_count = Column(Integer, default=0, comment="卖出后下跌（卖对）")

    record_date = Column(Date, nullable=False, comment="记录日期")
    created_at = Column(DateTime(timezone=True), server_default=text("CURRENT_TIMESTAMP"), comment="创建时间")


class HPIComponent(Base):
    """HPI 成分明细表 - 记录每手办对指数的贡献"""
    __tablename__ = "hpi_components"
    __table_args__ = (
        Index("idx_user_figure_date", "user_id", "figure_id", "record_date"),
        {"mysql_engine": "InnoDB", "mysql_charset": "utf8mb4", "comment": "HPI成分明细表"}
    )

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, nullable=False, comment="用户ID")
    figure_id = Column(Integer, nullable=False, comment="手办ID")
    record_date = Column(Date, nullable=False, comment="记录日期")

    # 买入时点（锁定）
    first_buy_price = Column(Float, nullable=False, comment="首次买入价")
    first_buy_date = Column(Date, nullable=False, comment="首次买入日期")
    total_buy_amount = Column(Float, nullable=False, comment="累计买入金额")

    # 当前状态
    current_price = Column(Float, nullable=False, comment="当日市场价")
    is_sold = Column(Integer, default=0, comment="是否已出：0=在柜，1=已出")
    sell_price = Column(Float, nullable=True, comment="卖出价（已出时）")

    # 收益计算
    return_pct = Column(Float, nullable=False, comment="相对首次买入的收益率%")
    weight = Column(Float, nullable=False, comment="权重")
    contribution = Column(Float, nullable=False, comment="对HPI的贡献度")

    # 卖飞/卖对标记
    sell_fly = Column(Integer, default=0, comment="1=卖出后上涨(卖飞)")
    sell_right = Column(Integer, default=0, comment="1=卖出后下跌(卖对)")
