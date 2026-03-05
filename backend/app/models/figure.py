from sqlalchemy import Column, Integer, String, Float, Text, Date, JSON
from app.models.database import Base

class Figure(Base):
    __tablename__ = "figures"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    manufacturer = Column(String(100))
    price = Column(Float)
    currency = Column(String(10), default="CNY")
    attribute = Column(String(100))
    release_date = Column(Date)
    scale = Column(String(50))
    prototype = Column(String(100))
    painting = Column(String(100))
    original_art = Column(String(100))
    work = Column(String(100))
    material = Column(String(100))
    size = Column(String(100))
    description = Column(Text)
    image_url = Column(String(255))
    images = Column(JSON, default=list)