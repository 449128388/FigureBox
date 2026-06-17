from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.sql import func
from app.models.database import Base


class CabinetRating(Base):
    """
    收藏柜喜爱度评分模型 - 用户在手办在每个收藏柜中的喜爱度评分
    
    功能说明：
    - 允许用户对每个收藏柜中的每个手办进行 1-5 星评分
    - 不同收藏柜中可以对同一个手办设置不同评分
    - user_id + figure_id + cabinet_type 作为联合唯一键
    
    评分说明：
    - rating = 0: 未评分（默认）
    - rating = 1-5: 1星到5星
    
    关联关系：
    - user: 多对一关联 User 表
    - figure: 多对一关联 Figure 表
    """
    __tablename__ = "cabinet_ratings"

    # 主键
    id = Column(Integer, primary_key=True, index=True, comment="评分唯一标识ID")
    
    # 外键关联
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, comment="用户ID")
    figure_id = Column(Integer, ForeignKey("figures.id"), nullable=False, comment="手办ID")
    
    # 收藏柜类型
    cabinet_type = Column(String(20), nullable=False, comment="收藏柜分类类型: star/new/fix/out/air/dup/wait/role")
    
    # 评分
    rating = Column(Integer, nullable=False, default=0, comment="喜爱度评分: 0=未评分, 1-5=星级评分")
    
    # 时间戳
    created_at = Column(DateTime(timezone=True), server_default=func.now(), comment="创建时间")
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), comment="更新时间")

    # 联合唯一约束
    __table_args__ = (
        UniqueConstraint('user_id', 'figure_id', 'cabinet_type', name='uq_user_figure_cabinet_rating'),
    )
