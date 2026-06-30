"""
exchange_rate.py - 汇率数据模型

功能说明：
- exchange_rate_realtime: 当前最新汇率缓存表（每小时更新）
- exchange_rate_history: 汇率历史记录表

汇率数据来源：
- 中国外汇交易中心 http://www.chinamoney.com.cn/r/cms/www/chinamoney/data/fx/ccpr.json
"""

from sqlalchemy import Column, Integer, String, Float, DateTime, TIMESTAMP, Index, text, func
from app.models.database import Base


class ExchangeRateRealtime(Base):
    """最新汇率缓存表 - 缓存当前最新汇率"""
    __tablename__ = "exchange_rate_realtime"
    __table_args__ = (
        Index("idx_realtime_currency", "currency"),
        {"mysql_engine": "InnoDB", "mysql_charset": "utf8mb4", "comment": "最新汇率缓存表"}
    )

    id = Column(Integer, primary_key=True, index=True, comment="记录唯一标识ID")
    currency = Column(String(10), nullable=False, unique=True, comment="币种代码：CNY/USD/JPY/EUR/HKD/GBP 等")
    rate_to_cny = Column(Float, nullable=False, comment="相对人民币的汇率（1单位本币 = ? 人民币）")
    updated_at = Column(DateTime(timezone=True), server_default=text("CURRENT_TIMESTAMP"),
                        onupdate=func.now(), comment="最后更新时间")


class ExchangeRateHistory(Base):
    """汇率历史记录表"""
    __tablename__ = "exchange_rate_history"
    __table_args__ = (
        Index("idx_history_currency_date", "currency", "record_date"),
        {"mysql_engine": "InnoDB", "mysql_charset": "utf8mb4", "comment": "汇率历史记录表"}
    )

    id = Column(Integer, primary_key=True, index=True, comment="记录唯一标识ID")
    currency = Column(String(10), nullable=False, comment="币种代码")
    rate_to_cny = Column(Float, nullable=False, comment="相对人民币的汇率")
    record_date = Column(DateTime(timezone=True), server_default=text("CURRENT_TIMESTAMP"), comment="记录时间")
    created_at = Column(DateTime(timezone=True), server_default=text("CURRENT_TIMESTAMP"), comment="创建时间")
