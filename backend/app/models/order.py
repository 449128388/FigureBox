from sqlalchemy import Column, Integer, String, Float, Date, ForeignKey
from sqlalchemy.orm import relationship
from app.models.database import Base

class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    figure_id = Column(Integer, ForeignKey("figures.id"), nullable=False)
    deposit = Column(Float, nullable=False)
    balance = Column(Float, nullable=False)
    due_date = Column(Date, nullable=False)
    status = Column(String(20), default="pending")  # pending, paid, cancelled

    # 关系
    user = relationship("User")
    figure = relationship("Figure")