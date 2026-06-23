"""
cabinet_exclusion.py - 展示分类排除表模型

功能说明：
- 记录用户手动将某手办从某个展示分类中排除的记录
- 用于"软出柜"：不删除藏品，仅从展示分类中隐藏
- 所有自动分类查询都需要 LEFT JOIN 此表排除已移出的记录

支持的分类：
- star:  海景房专区
- new:   最近入柜
- fix:   修复工坊
- air:   预定中
- dup:   复数专区
- wait:  待出荷
- maker: 本命厂商
"""

from sqlalchemy import Column, Integer, BigInteger, String, DateTime, TIMESTAMP, UniqueConstraint, text
from app.models.database import Base


class CabinetFigureExclusion(Base):
    """
    展示分类手动排除表

    记录用户从某个展示分类中手动移出的手办。
    被排除的手办在对应分类的自动统计中不再出现。
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
