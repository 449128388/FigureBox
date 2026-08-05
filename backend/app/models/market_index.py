"""
market_index.py - 公共市场指数模型

从历史 models/asset.py 拆分而来（2026-08-04 重构 #39）。
包含 2 个围绕"公共市场指数数据"领域的模型：

- StockIndexCache:   股票指数缓存（上证/沪深300 等）
- StockIndexHistory: 股票指数历史

与 asset_transaction.py 私有数据形成对比：
- 私有数据 = 用户级（手办、订单、PI 指数）
- 公共数据 = 全市场级（股票指数）

Cache 与 History 的区别：
- Cache：只保存最新数据，用于快速查询 + 限流控制
- History：保存所有历史记录，用于趋势分析
"""

from sqlalchemy import Column, Integer, String, Float, Date, DateTime
from sqlalchemy.sql import func
from app.models.database import Base


class StockIndexCache(Base):
    """
    股票指数缓存模型 - 缓存上证指数等市场指数数据

    功能说明：
    - 缓存股票指数（如上证指数）的当前数据
    - 用于对比手办资产与市场表现
    - 控制API请求频率（避免频繁调用外部API）

    字段说明：
    - 存储指数代码、名称、当前值、涨跌等
    - 记录请求次数和日期（用于限流）
    """
    __tablename__ = "stock_index_cache"

    # 主键
    id = Column(Integer, primary_key=True, index=True, comment="缓存记录唯一标识ID")

    # 指数基本信息
    index_code = Column(String(20), nullable=False, unique=True, index=True, comment="指数代码，如 sh000001（上证指数）")
    index_name = Column(String(50), nullable=False, comment="指数名称（如：上证指数）")

    # 指数数据
    current_value = Column(Float, nullable=False, comment="当前指数值")
    change_value = Column(Float, default=0, comment="涨跌值（相对于昨日收盘）")
    change_percentage = Column(Float, default=0, comment="涨跌幅百分比")

    # 缓存控制
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), comment="最后更新时间")
    request_count = Column(Integer, default=0, comment="当日请求次数（用于限流控制）")
    request_date = Column(Date, nullable=False, comment="请求日期（用于按天统计）")


class StockIndexHistory(Base):
    """
    上证指数历史记录模型 - 保存每次请求的历史数据

    功能说明：
    - 记录每次获取的指数详细数据
    - 用于生成指数走势图
    - 支持历史数据分析

    与 StockIndexCache 的区别：
    - Cache：只保存最新数据，用于快速查询
    - History：保存所有历史记录，用于趋势分析
    """
    __tablename__ = "stock_index_history"

    # 主键
    id = Column(Integer, primary_key=True, index=True, comment="历史记录唯一标识ID")

    # 指数基本信息
    index_code = Column(String(20), nullable=False, index=True, comment="指数代码，如 sh000001")
    index_name = Column(String(50), nullable=False, comment="指数名称")

    # 指数详细数据
    current_value = Column(Float, nullable=False, comment="当前指数值")
    change_value = Column(Float, default=0, comment="涨跌值")
    change_percentage = Column(Float, default=0, comment="涨跌幅百分比")
    prev_close = Column(Float, nullable=True, comment="昨日收盘价")
    open_value = Column(Float, nullable=True, comment="今日开盘价")

    # 时间信息
    request_time = Column(DateTime(timezone=True), server_default=func.now(), comment="请求时间（精确到秒）")
    request_date = Column(Date, nullable=False, comment="请求日期（用于按天分组）")

    # 索引优化
    __table_args__ = (
        {'mysql_engine': 'InnoDB'},
    )
