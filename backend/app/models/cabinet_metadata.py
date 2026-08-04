"""
cabinet_metadata.py - 收藏柜用户级元数据模型

合并自历史两个文件（2026-08-04 重构 #38）：
- cabinet_rating.py:    CabinetRating（1-5 星喜爱度评分）
- cabinet_exclusion.py: CabinetFigureExclusion（展示分类手动排除 / 软出柜）

合并理由：
- 业务领域同属"用户对收藏柜手办的细粒度控制"
- 完全相同的联合唯一键 (user_id, figure_id, cabinet_type)
- 表名均为 cabinet_ 前缀，常一起 LEFT JOIN 查询
- 跟随项目模型合并模式（asset.py 8 模型 / hpi.py 2 模型 / exchange_rate.py 2 模型）

包含：
- CabinetRating: 用户对每个收藏柜手办的 1-5 星喜爱度评分
- CabinetFigureExclusion: 用户将手办从某个展示分类中移出（软出柜）
"""

from sqlalchemy import (
    Column, Integer, BigInteger, String, DateTime, TIMESTAMP,
    ForeignKey, UniqueConstraint, text
)
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
    user_id = Column(Integer, ForeignKey("users_info.id"), nullable=False, comment="用户ID")
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


class CabinetFigureExclusion(Base):
    """
    展示分类手动排除表

    记录用户从某个展示分类中手动移出的手办。
    被排除的手办在对应分类的自动统计中不再出现。
    用于"软出柜"：不删除藏品，仅从展示分类中隐藏。

    联合唯一键：(user_id, figure_id, cabinet_type)
    """
    __tablename__ = "cabinet_figure_exclusions"
    __table_args__ = (
        UniqueConstraint("user_id", "figure_id", "cabinet_type", name="uk_user_figure_cabinet"),
        {
            "mysql_engine": "InnoDB",
            "mysql_charset": "utf8mb4",
            "comment": "展示分类手动排除表"
        }
    )

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    user_id = Column(Integer, nullable=False, comment="用户ID")
    figure_id = Column(Integer, nullable=False, comment="手办ID")
    cabinet_type = Column(String(32), nullable=False, comment="分类标识: star,new,fix,air,dup,wait,maker")
    source_cabinet = Column(String(32), default=None, comment="触发移出的源分类")
    exclude_reason = Column(String(255), default=None, comment="移出原因（用户可选填）")
    excluded_at = Column(TIMESTAMP, server_default=text("CURRENT_TIMESTAMP"), comment="移出时间")
    created_at = Column(TIMESTAMP, server_default=text("CURRENT_TIMESTAMP"), comment="创建时间")
    updated_at = Column(TIMESTAMP, server_default=text("CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP"), comment="更新时间")
