"""
favorite_manufacturer.py - 本命厂商模型

功能说明：
- 存储用户收藏的本命厂商信息
- 支持自定义名称、描述、官网链接等
- 用于收藏家模式我的收藏柜本命厂商列表页

字段说明：
- name: 厂商中文名称（可自定义）
- name_jp: 厂商日文/原文名称
- description: 厂商描述
- logo_url: Logo 图片 URL
- website_url: 官网链接
- twitter_url: 推特/X 链接
- sort_order: 排序顺序
- is_active: 是否激活

关联关系：
- user: 多对一关联 User 表
"""

from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean
from sqlalchemy.sql import func
from app.models.database import Base


class FavoriteManufacturer(Base):
    """本命厂商模型"""
    __tablename__ = "favorite_manufacturers"

    id = Column(Integer, primary_key=True, index=True, comment="厂商唯一标识ID")
    user_id = Column(Integer, nullable=False, index=True, comment="用户ID")

    # 厂商信息
    name = Column(String(200), nullable=False, comment="厂商中文名称（可自定义）")
    name_jp = Column(String(200), comment="厂商日文/原文名称")
    description = Column(Text, comment="厂商描述")
    logo_url = Column(String(500), comment="Logo 图片 URL")

    # 社交链接
    website_url = Column(String(500), comment="官网链接")
    twitter_url = Column(String(500), comment="推特/X 链接")

    # 排序与状态
    sort_order = Column(Integer, default=0, comment="排序顺序（升序）")
    is_active = Column(Boolean, default=True, comment="是否激活")

    # 时间戳
    created_at = Column(DateTime(timezone=True), server_default=func.now(), comment="创建时间")
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), comment="更新时间")
