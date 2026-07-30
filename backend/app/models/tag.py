from sqlalchemy import Column, Integer, String
from app.models.database import Base


class Tag(Base):
    """
    标签模型

    业务说明：
    - 作为手办标签的「标签字典」，存储唯一标签名称
    - 供 FormTagsTab 等下拉候选组件拉取候选标签名
    - 标签与手办的多对多关系已改为 figures.tags JSON 字段（List[str]）反范式存储
    - 2026-07-29 关联表 figure_tag 已删除，本表不再维护反向关系
    """
    __tablename__ = "tags"

    # 主键
    id = Column(Integer, primary_key=True, index=True, comment="标签唯一标识ID")

    # 标签信息
    name = Column(String(50), unique=True, nullable=False, index=True, comment="标签名称（唯一，如：GSC、火影忍者、预定中）")
