from sqlalchemy import Column, Integer, String, Float, Text, Date, JSON
from sqlalchemy.orm import relationship
from app.models.database import Base

class Figure(Base):
    """
    手办模型 - 存储手办的基本信息、价格、购买记录等数据
    
    功能说明：
    - 记录手办的基础信息（名称、制造商、定价等）
    - 跟踪购买信息（入手价格、时间、方式等）
    - 支持多标签关联
    - 支持价格历史记录
    
    关联关系：
    - tags: 多对多关联 Tag 表
    - price_histories: 一对多关联 AssetPriceHistory 表
    """
    __tablename__ = "figures"

    # 主键
    id = Column(Integer, primary_key=True, index=True)  # 手办唯一标识ID
    
    # 基础信息
    name = Column(String(100), nullable=False)  # 手办名称（中文/显示名）
    japanese_name = Column(String(100))  # 日文名称（原始名称）
    manufacturer = Column(String(100))  # 制造商/厂商名称
    
    # 官方定价信息
    price = Column(Float)  # 官方定价（日元或人民币）
    currency = Column(String(10), default="CNY")  # 定价货币类型（CNY/JPY等）
    release_date = Column(Date)  # 官方发售日期/出货日期
    
    # 购买信息
    purchase_price = Column(Float)  # 实际入手价格
    purchase_currency = Column(String(10), default="CNY")  # 入手价格货币类型
    purchase_date = Column(Date)  # 实际入手日期
    purchase_method = Column(String(100))  # 购买渠道/方式（如：淘宝、闲鱼、会员购等）
    purchase_type = Column(String(50))  # 购买类型（预定、现货、转单等）
    quantity = Column(Integer, default=1)  # 购买数量，默认值为1
    
    # 手办规格
    scale = Column(String(50))  # 比例（如：1/7、1/8等）
    painting = Column(String(100))  # 涂装信息
    original_art = Column(String(100))  # 原画/原型师
    work = Column(String(100))  # 作品来源（动漫/游戏名称）
    material = Column(String(100))  # 材质
    size = Column(String(100))  # 尺寸规格
    
    # 描述和媒体
    description = Column(Text)  # 详细描述/备注
    images = Column(JSON, default=list)  # 图片URL列表（JSON数组格式）
    
    # 估值和市场价格
    current_value = Column(Float)  # 当前估值（用户自定义估值）
    market_price = Column(Float)  # 市场价格/市场价
    market_currency = Column(String(10), default="CNY")  # 市场价货币类型
    
    # 关联的标签（多对多关系）
    tags = relationship("Tag", secondary="figure_tag", back_populates="figures")
    # 关联的价格历史
    price_histories = relationship("AssetPriceHistory", back_populates="figure")
