from sqlalchemy import Column, Integer, String, Float, Date, DateTime, Text
from sqlalchemy.dialects.mysql import JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.models.database import Base


class Figure(Base):
    """
    手办模型 - 存储手办的基本信息

    功能说明：
    - 存储手办的基本信息
    - 包含价格、币种、市场价、入手价等财务信息
    - 关联标签、订单等其他模型

    字段说明：
    - name: 手办名称
    - japanese_name: 日文名称
    - manufacturer: 制造商
    - price: 定价
    - currency: 定价币种
    - market_price: 市场价
    - market_currency: 市场价币种
    - release_date: 发售日期
    - average_purchase_price: 平均入手价
    - purchase_currency: 入手价币种
    - purchase_date: 入手日期
    - purchase_method: 入手方式
    - purchase_type: 入手类型
    - scale: 比例
    - painting: 涂装师
    - original_art: 原画作者
    - work: 作品出处
    - material: 材质
    - size: 尺寸
    - images: 图片列表
    - quantity: 持有数量
    - is_active: 是否激活（软删除标记）
    - deleted_at: 删除时间
    - created_at: 创建时间
    - updated_at: 更新时间
    """
    __tablename__ = "figures"

    # 主键
    id = Column(Integer, primary_key=True, index=True, comment="手办唯一标识ID")

    # 基本信息
    name = Column(String(200), nullable=False, comment="手办名称（中文/英文）")
    japanese_name = Column(String(200), comment="日文名称")
    manufacturer = Column(String(100), comment="制造商（如：Good Smile Company）")
    scale = Column(String(50), comment="比例（如：1/8、1/7、1/6等）")
    painting = Column(String(100), comment="涂装师")
    original_art = Column(String(100), comment="原画作者")
    work = Column(String(200), comment="作品出处（如：VOCALOID、Fate系列等）")
    material = Column(String(100), comment="材质（PVC、ABS、树脂等）")
    size = Column(String(100), comment="尺寸（如：H=200mm）")

    # 价格信息
    price = Column(Float, default=0, comment="定价（官方定价）")
    currency = Column(String(10), default="CNY", comment="定价币种：CNY/JPY/USD/EUR")
    market_price = Column(Float, default=0, comment="当前市场价/估值")
    market_currency = Column(String(10), default="CNY", comment="市场价币种")
    average_purchase_price = Column(Float, default=0, comment="平均入手价（自动计算）")
    purchase_currency = Column(String(10), default="CNY", comment="入手价币种")

    # 购买信息
    purchase_date = Column(Date, comment="入手日期")
    purchase_method = Column(String(50), comment="入手方式（淘宝、会员购、日拍等）")
    purchase_type = Column(String(20), default="OTHER", comment="入手类型：PREORDER(预定)/INSTOCK(现货)/SECONDHAND(二手)/LOOSE(散货)/DOMESTIC(国产)/OTHER(其他)")

    # 发售信息
    release_date = Column(Date, comment="发售日期")

    # 媒体信息
    images = Column(JSON, default=[], comment="图片URL列表")

    # 库存信息
    quantity = Column(Integer, default=1, comment="持有数量")

    # 软删除标记
    is_active = Column(Integer, default=1, comment="是否激活：1=正常，0=已删除")
    deleted_at = Column(DateTime, nullable=True, comment="删除时间（软删除标记）")

    # 时间戳
    created_at = Column(DateTime(timezone=True), server_default=func.now(), comment="创建时间")
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), comment="更新时间")

    # 关系
    orders = relationship("Order", back_populates="figure")  # 关联订单列表
    tags = relationship("Tag", secondary="figure_tag", back_populates="figures")  # 多对多关联标签
