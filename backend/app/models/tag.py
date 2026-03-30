from sqlalchemy import Column, Integer, String, Table, ForeignKey
from sqlalchemy.orm import relationship
from app.models.database import Base

# 手办和标签的多对多关联表
figure_tag = Table(
    'figure_tag',
    Base.metadata,
    Column('figure_id', Integer, ForeignKey('figures.id'), primary_key=True),
    Column('tag_id', Integer, ForeignKey('tags.id'), primary_key=True)
)


class Tag(Base):
    __tablename__ = "tags"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), unique=True, nullable=False, index=True)
    
    # 关联的手办
    figures = relationship("Figure", secondary=figure_tag, back_populates="tags")
