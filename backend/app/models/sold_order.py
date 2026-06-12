from sqlalchemy import Column, Integer, String, Float, Date, DateTime, ForeignKey, func
from sqlalchemy.orm import relationship
from app.models.database import Base
from datetime import datetime

class SoldOrder(Base):
    """
    已出售订单模型 - 存储手办卖出订单的详细信息
    
    功能说明：
    - 记录每个手办的卖出订单详情
    - 支持计算净利润和利润率
    - 跟踪订单状态和物流信息
    - 关联用户和手办
    
    订单状态说明：
    - 待发货：订单已创建，等待发货
    - 已发货：已发货，等待买家确认
    - 已完成：交易完成，款项已到账
    - 退款/纠纷：存在退款或纠纷
    
    关联关系：
    - user: 多对一关联 User 表（订单所属用户）
    - figure: 多对一关联 Figure 表（订单对应的手办）
    """
    __tablename__ = "sold_orders"

    # 主键
    id = Column(Integer, primary_key=True, index=True, comment="订单唯一标识ID")
    
    # 外键关联
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, comment="关联用户ID（订单所属用户）")
    figure_id = Column(Integer, ForeignKey("figures.id"), nullable=False, comment="关联手办ID（订单对应的手办）")
    
    # 卖出信息
    quantity = Column(Integer, default=1, comment="卖出数量")
    sell_price = Column(Float, nullable=False, comment="卖出价格（总价）")
    cost_price = Column(Float, nullable=False, comment="成本价格（总价）")
    shipping_fee = Column(Float, default=0, comment="运费（负数表示支出）")
    platform_fee = Column(Float, default=0, comment="平台手续费（负数表示支出）")
    
    # 币种信息
    sell_price_currency = Column(String(10), default="CNY", comment="卖出价格币种：CNY/USD/JPY/EUR")
    cost_price_currency = Column(String(10), default="CNY", comment="成本价币种：CNY/USD/JPY/EUR")
    shipping_fee_currency = Column(String(10), default="CNY", comment="运费币种：CNY/USD/JPY/EUR")
    platform_fee_currency = Column(String(10), default="CNY", comment="平台手续费币种：CNY/USD/JPY/EUR")
    
    # 净利润计算（可由后端计算或存储）
    net_profit = Column(Float, comment="净利润 = 卖出价 - 成本价 + 运费 + 手续费")
    profit_rate = Column(Float, comment="利润率 = 净利润 / 成本价 * 100")
    
    # 卖出平台信息
    sell_platform = Column(String(50), comment="卖出平台：闲鱼、淘宝、转转等")
    order_number = Column(String(100), comment="订单编号（平台订单号）")
    display_order_number = Column(String(100), comment="展示订单编号（系统生成，格式：SALE-YYYYMMDD-XXX）")
    buyer_phone = Column(String(20), comment="买家手机号（脱敏显示）")
    buyer_address = Column(String(500), comment="买家地址")
    tracking_number = Column(String(100), comment="快递单号")
    logistics_company = Column(String(50), comment="物流公司：顺丰、圆通、中通、申通、韵达、EMS、其他")
    shipping_date = Column(Date, comment="发货日期")
    
    # 订单状态
    status = Column(String(20), default="待发货", comment="订单状态：待发货、已发货、已完成、退款/纠纷")
    
    # 备注信息
    remark = Column(String(1000), comment="订单备注")
    
    # 软删除标记
    is_active = Column(Integer, default=1, comment="是否激活：1=正常，0=已删除")
    deleted_at = Column(DateTime, nullable=True, comment="删除时间（软删除标记）")
    created_at = Column(DateTime(timezone=True), default=datetime.now, server_default=func.now(), comment="创建时间")
    updated_at = Column(DateTime(timezone=True), default=datetime.now, onupdate=func.now(), comment="更新时间")

    # 关系
    user = relationship("User")  # 关联用户对象
    figure = relationship("Figure")  # 关联手办对象