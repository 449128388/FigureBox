"""
order_finance.py - 订单资金账模型

从历史 models/asset.py 拆分而来（2026-08-04 重构 #39）。
包含 1 个围绕"订单资金流"领域的模型：

- OrderTransaction: 订单资金流水（buy/sell/refund/fee + adjust 审计）

与 asset_transaction.py 库存账的关系：
- 库存账（AssetTransaction）= 手办数量变动（buy/sell/adjust）
- 资金账（OrderTransaction）= 实际资金流动（buy/sell/refund/fee + 调整审计）
- 严格区分"数量"与"金额"两个维度
"""

from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.models.database import Base


class OrderTransaction(Base):
    """
    订单资金流水记录模型 - 记录手办的真实资金变动（资金账）

    功能说明：
    - 只记录有真实资金流动的交易
    - 严禁记录无资金流动的场景（库存调整、价格调整等）
    - 支持资金流向分析和财务报表

    交易类型说明：
    - buy: 买入支出（订单支付、定金、尾款）
    - sell: 卖出收入（闲鱼出售等）
    - refund: 退款收入（退货/取消订单）
    - fee: 手续费支出（平台扣费）

    资金流向说明：
    - in: 资金流入（收入）
    - out: 资金流出（支出）

    关联关系：
    - user: 多对一关联 User 表
    - figure: 多对一关联 Figure 表
    - order: 多对一关联 Order 表（可选）
    """
    __tablename__ = "order_transactions"

    # 主键
    id = Column(Integer, primary_key=True, index=True, comment="资金流水记录唯一标识ID")

    # 外键关联
    user_id = Column(Integer, ForeignKey("users_info.id"), nullable=False, comment="关联用户ID")
    figure_id = Column(Integer, ForeignKey("figures.id"), nullable=False, comment="关联手办ID")
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=True, comment="关联订单ID（可选）")
    sold_order_id = Column(Integer, ForeignKey("sold_orders.id"), nullable=True, comment="关联卖出订单ID（卖出交易时关联）")

    # 交易信息
    transaction_type = Column(String(50), nullable=False, comment="交易类型：buy(买入)/sell(卖出)/refund(退款)/fee(手续费)")
    direction = Column(String(10), nullable=False, default="out", comment="资金流向：in(收入)/out(支出)")
    quantity = Column(Integer, default=1, comment="交易数量")
    unit_price = Column(Float, nullable=False, comment="交易单价")
    total_amount = Column(Float, nullable=False, comment="交易总金额（unit_price × quantity）")
    currency = Column(String(10), default="CNY", comment="货币类型")

    # 交易详情
    payment_method = Column(String(50), comment="支付方式：支付宝/微信/银行卡/现金等")
    payment_time = Column(DateTime, nullable=True, comment="定金支付时间")
    balance_payment_method = Column(String(20), comment="尾款支付方式：支付宝、微信、银行卡转账、现金")
    balance_payment_time = Column(DateTime, nullable=True, comment="尾款支付时间")
    platform = Column(String(50), comment="交易平台：淘宝/闲鱼/AmiAmi/京东/线下等")

    # 时间字段
    transaction_date = Column(DateTime(timezone=True), nullable=False, comment="交易发生时间（业务时间）")
    created_at = Column(DateTime(timezone=True), server_default=func.now(), comment="系统记录时间（创建时间）")
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), comment="更新时间")

    # 备注
    notes = Column(String(255), comment="交易备注/说明")

    # 变更追踪字段（用于记录订单资金变更历史）
    transaction_subtype = Column(String(50), nullable=True, comment="交易子类型：initial(初始)/adjust(调整)/supplement(追加)/refund(退款)")
    parent_transaction_id = Column(Integer, ForeignKey("order_transactions.id"), nullable=True, comment="关联的原始交易ID")
    change_reason = Column(String(255), nullable=True, comment="变更原因/备注")
    previous_amount = Column(Float, nullable=True, comment="变更前金额（用于审计）")
    current_amount = Column(Float, nullable=True, comment="变更后金额")
    changed_field = Column(String(50), nullable=True, comment="变更的字段：deposit(定金)/balance(尾款)")

    # 软删除字段
    is_active = Column(Boolean, default=True, comment="是否激活")
    deleted_at = Column(DateTime(timezone=True), nullable=True, comment="删除时间")

    # 关系
    user = relationship("User")  # 关联用户对象
    figure = relationship("Figure")  # 关联手办对象
    order = relationship("Order")  # 关联订单对象
    sold_order = relationship("SoldOrder")  # 关联卖出订单对象
    parent_transaction = relationship("OrderTransaction", remote_side=[id])  # 自关联：关联父交易
