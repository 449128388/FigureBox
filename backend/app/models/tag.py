from sqlalchemy import Column, Integer, String, Table, ForeignKey
from sqlalchemy.orm import relationship
from app.models.database import Base

# 手办和标签的多对多关联表
# 说明：这是一个关联表（中间表），用于建立 Figure 和 Tag 之间的多对多关系
# - figure_id: 关联的手办ID
# - tag_id: 关联的标签ID
# 联合主键确保一个手办不会重复关联同一个标签
figure_tag = Table(
    'figure_tag',
    Base.metadata,
    Column('figure_id', Integer, ForeignKey('figures.id'), primary_key=True),  # 手办ID（外键关联figures表）
    Column('tag_id', Integer, ForeignKey('tags.id'), primary_key=True)  # 标签ID（外键关联tags表）
)


class Tag(Base):
    """
    标签模型 - 用于对手办进行分类和标记
    
    功能说明：
    - 为手办添加分类标签（如：动漫名称、角色、系列等）
    - 支持多对多关联，一个手办可以有多个标签，一个标签可以对应多个手办
    - 支持按标签筛选和搜索手办
    
    使用场景：
    - 按作品分类（如：火影忍者、海贼王）
    - 按厂商分类（如：GSC、Alter）
    - 按类型分类（如：手办、figma、粘土人）
    - 自定义标签（如：预定中、已到货、已转卖）
    
    关联关系：
    - figures: 多对多关联 Figure 表，通过 figure_tag 中间表建立关系
    """
    __tablename__ = "tags"

    # 主键
    id = Column(Integer, primary_key=True, index=True)  # 标签唯一标识ID
    
    # 标签信息
    name = Column(String(50), unique=True, nullable=False, index=True)  # 标签名称（唯一，如：GSC、火影忍者、预定中）
    
    # 关联的手办（多对多关系）
    figures = relationship("Figure", secondary=figure_tag, back_populates="tags")
    # 说明：通过 figure_tag 中间表关联 Figure 模型
    # - secondary=figure_tag: 指定使用哪个关联表
    # - back_populates="tags": 与 Figure 模型中的 tags 属性形成双向关联
