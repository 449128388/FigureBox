from sqlalchemy import Column, Integer, String, Float, Date, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.models.database import Base

class AssetPriceHistory(Base):
    """资产价格历史记录"""
    __tablename__ = "asset_price_history"

    id = Column(Integer, primary_key=True, index=True)
    figure_id = Column(Integer, ForeignKey("figures.id"), nullable=False)
    current_price = Column(Float, nullable=False)  # 当前估价
    date = Column(DateTime(timezone=True), server_default=func.now())  # 记录日期

    # 关系
    figure = relationship("Figure")

class AssetAlert(Base):
    """资产预警设置"""
    __tablename__ = "asset_alerts"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    figure_id = Column(Integer, ForeignKey("figures.id"), nullable=False)
    alert_type = Column(String(50), nullable=False)  # 预警类型：price_drop, price_rise, etc.
    threshold = Column(Float, nullable=False)  # 预警阈值
    is_active = Column(Integer, default=1)  # 是否激活
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # 关系
    user = relationship("User")
    figure = relationship("Figure")

class AssetTransaction(Base):
    """资产交易记录"""
    __tablename__ = "asset_transactions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    figure_id = Column(Integer, ForeignKey("figures.id"), nullable=False)
    transaction_type = Column(String(50), nullable=False)  # 交易类型：buy, sell
    price = Column(Float, nullable=False)  # 交易价格
    transaction_date = Column(DateTime(timezone=True), server_default=func.now())  # 交易日期
    notes = Column(String(255))  # 交易备注

    # 关系
    user = relationship("User")
    figure = relationship("Figure")


class StockIndexCache(Base):
    """股票指数缓存（上证指数）"""
    __tablename__ = "stock_index_cache"

    id = Column(Integer, primary_key=True, index=True)
    index_code = Column(String(20), nullable=False, unique=True, index=True)  # 指数代码，如 sh000001
    index_name = Column(String(50), nullable=False)  # 指数名称
    current_value = Column(Float, nullable=False)  # 当前指数值
    change_value = Column(Float, default=0)  # 涨跌值
    change_percentage = Column(Float, default=0)  # 涨跌幅百分比
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())  # 更新时间
    request_count = Column(Integer, default=0)  # 当日请求次数
    request_date = Column(Date, nullable=False)  # 请求日期


class AssetValueCache(Base):
    """资产市值缓存（用于计算日涨跌）"""
    __tablename__ = "asset_value_cache"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    total_value = Column(Float, nullable=False)  # 当日总市值
    cache_date = Column(Date, nullable=False)  # 缓存日期
    created_at = Column(DateTime(timezone=True), server_default=func.now())  # 创建时间

    # 关系
    user = relationship("User")


class UserSettings(Base):
    """用户设置（年度手办消费上限等）"""
    __tablename__ = "user_settings"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, unique=True)
    annual_spending_limit = Column(Float, default=0)  # 年度手办消费上限（0表示未设置）
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())  # 更新时间

    # 关系
    user = relationship("User")
