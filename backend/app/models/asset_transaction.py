"""
asset_transaction.py - 手办资产核心模型

从历史 models/asset.py 拆分而来（2026-08-04 重构 #39）。
包含 4 个围绕"用户手办资产数据"领域的模型：

- AssetPriceHistory:    单手办价格历史
- AssetTransaction:     库存账流水（buy/sell/adjust）
- AssetValueCache:      用户资产市值缓存
- PlasticIndexHistory:  塑料手办指数 (PI) 历史
"""

from sqlalchemy import Column, Integer, String, Float, Date, ForeignKey, DateTime, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.models.database import Base


class AssetPriceHistory(Base):
    """
    资产价格历史记录模型 - 记录手办价格变化历史

    功能说明：
    - 记录手办每次价格更新的历史
    - 用于生成价格趋势图表
    - 支持资产增值分析

    关联关系：
    - figure: 多对一关联 Figure 表
    """
    __tablename__ = "asset_price_history"

    # 主键
    id = Column(Integer, primary_key=True, index=True, comment="记录唯一标识ID")

    # 外键关联
    figure_id = Column(Integer, ForeignKey("figures.id"), nullable=False, comment="关联手办ID")

    # 价格信息
    current_price = Column(Float, nullable=False, comment="当前估价/记录时的价格")
    date = Column(DateTime(timezone=True), server_default=func.now(), comment="记录日期时间")

    # 关系
    figure = relationship("Figure")  # 关联手办对象


class AssetTransaction(Base):
    """
    资产交易记录模型 - 记录手办的买卖交易

    功能说明：
    - 记录手办的买入和卖出交易
    - 用于计算投资收益
    - 支持交易备注记录
    - 支持股票式补仓功能（记录数量、剩余持仓等）

    交易类型说明：
    - buy: 买入/购买
    - sell: 卖出/转让

    关联关系：
    - user: 多对一关联 User 表
    - figure: 多对一关联 Figure 表
    - order: 多对一关联 Order 表（买入交易关联订单）
    - sold_order: 多对一关联 SoldOrder 表（卖出交易关联）
    """
    __tablename__ = "asset_transactions"

    # 主键
    id = Column(Integer, primary_key=True, index=True, comment="交易记录唯一标识ID")

    # 外键关联
    user_id = Column(Integer, ForeignKey("users_info.id"), nullable=False, comment="关联用户ID")
    figure_id = Column(Integer, ForeignKey("figures.id"), nullable=False, comment="关联手办ID")
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=True, comment="关联订单ID（买入交易时关联）")
    sold_order_id = Column(Integer, ForeignKey("sold_orders.id"), nullable=True, comment="关联卖出订单ID（卖出交易关联）")

    # 交易信息
    transaction_type = Column(String(50), nullable=False, comment="交易类型：buy（买入）、sell（卖出）")
    price = Column(Float, nullable=False, comment="交易价格（单价）")
    quantity = Column(Integer, nullable=False, default=1, comment="交易数量")
    total_amount = Column(Float, nullable=False, comment="交易总金额（price × quantity）")
    remaining_quantity = Column(Integer, nullable=True, comment="单条交易记录剩余持仓数量（用于部分卖出后的持仓计算）,不是总库存的汇总值")
    transaction_date = Column(DateTime(timezone=True), server_default=func.now(), comment="交易日期时间")
    notes = Column(String(255), comment="交易备注/说明")

    # 时间戳字段
    created_at = Column(DateTime(timezone=True), server_default=func.now(), comment="创建时间")
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), comment="更新时间")

    # 软删除字段
    is_active = Column(Boolean, default=True, comment="是否激活")
    deleted_at = Column(DateTime(timezone=True), nullable=True, comment="删除时间")

    # 关系
    user = relationship("User")  # 关联用户对象
    figure = relationship("Figure")  # 关联手办对象
    order = relationship("Order")  # 关联订单对象
    sold_order = relationship("SoldOrder")  # 关联卖出订单对象


class AssetValueCache(Base):
    """
    资产市值缓存模型 - 缓存用户每日资产总市值

    功能说明：
    - 记录用户每日的资产总市值
    - 用于计算日涨跌（对比昨日市值）
    - 支持资产趋势分析

    关联关系：
    - user: 多对一关联 User 表
    """
    __tablename__ = "asset_value_cache"

    # 主键
    id = Column(Integer, primary_key=True, index=True, comment="缓存记录唯一标识ID")

    # 外键关联
    user_id = Column(Integer, ForeignKey("users_info.id"), nullable=False, comment="关联用户ID")

    # 资产数据
    total_value = Column(Float, nullable=False, comment="当日总市值（所有手办当前价值总和）")
    cache_date = Column(Date, nullable=False, comment="缓存日期（哪一天的数据）")
    created_at = Column(DateTime(timezone=True), server_default=func.now(), comment="记录创建时间")

    # 关系
    user = relationship("User")  # 关联用户对象


class PlasticIndexHistory(Base):
    """
    塑料手办指数历史记录模型 - 记录每日塑料手办指数变化

    功能说明：
    - 记录用户每日的塑料手办指数值
    - 用于计算指数涨跌（对比昨日指数）
    - 支持指数趋势分析

    关联关系：
    - user: 多对一关联 User 表
    """
    __tablename__ = "plastic_index_history"

    # 主键
    id = Column(Integer, primary_key=True, index=True, comment="记录唯一标识ID")

    # 外键关联
    user_id = Column(Integer, ForeignKey("users_info.id"), nullable=False, comment="关联用户ID")

    # 指数数据
    current_value = Column(Float, nullable=False, comment="当前指数值")
    change_value = Column(Float, default=0, comment="涨跌值（相对于昨日）")
    change_percentage = Column(Float, default=0, comment="涨跌幅百分比")
    base_value = Column(Float, default=1000.0, comment="基准日指数值（默认1000）")
    base_date = Column(Date, nullable=False, comment="基准日期")

    # 时间信息
    record_date = Column(Date, nullable=False, comment="记录日期（哪一天的数据）")
    created_at = Column(DateTime(timezone=True), server_default=func.now(), comment="记录创建时间")
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), comment="最后更新时间")

    # 关系
    user = relationship("User")  # 关联用户对象
