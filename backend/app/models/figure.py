from sqlalchemy import Column, Integer, String, Float, Text, Date, JSON
from sqlalchemy.orm import relationship
from app.models.database import Base

class Figure(Base):
    __tablename__ = "figures"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    japanese_name = Column(String(100))
    manufacturer = Column(String(100))
    price = Column(Float)
    currency = Column(String(10), default="CNY")
    release_date = Column(Date)
    purchase_price = Column(Float)
    purchase_currency = Column(String(10), default="CNY")
    purchase_date = Column(Date)
    purchase_method = Column(String(100))
    purchase_type = Column(String(50))
    scale = Column(String(50))
    painting = Column(String(100))
    original_art = Column(String(100))
    work = Column(String(100))
    material = Column(String(100))
    size = Column(String(100))
    description = Column(Text)
    images = Column(JSON, default=list)
    
    # 关联的标签（多对多关系）
    tags = relationship("Tag", secondary="figure_tag", back_populates="figures")