"""
collector_privacy.py - 收藏家隐私设置模型

功能说明：
- 存储用户收藏数据的隐私配置
- 每个用户一条记录，由各字段控制不同维度的可见性
- 包含分享鉴权令牌管理字段
"""

from sqlalchemy import Column, Integer, String, Boolean, DateTime, func
from app.models.database import Base


class CollectorPrivacy(Base):
    """收藏家隐私设置"""
    __tablename__ = "collector_privacy"

    id = Column(Integer, primary_key=True, index=True, comment="主键ID")
    user_id = Column(Integer, nullable=False, unique=True, comment="用户ID")

    # 访问权限
    home_visibility = Column(String(20), default="public", comment="个人主页可见性: public/friends_only/private")

    # 数据展示
    show_total = Column(Boolean, default=True, comment="是否展示藏品总数")
    show_figures = Column(Boolean, default=False, comment="是否展示具体藏品列表")
    show_asset = Column(Boolean, default=False, comment="是否展示资产金额")
    show_tags = Column(Boolean, default=True, comment="是否展示标签云")
    show_feed = Column(Boolean, default=False, comment="是否展示动态流")

    # 分享设置
    poster_level = Column(String(20), default="stats_only", comment="海报展示粒度: full/stats_only/names_only")

    # 分享鉴权令牌
    share_token = Column(String(64), comment="分享鉴权令牌（SHA256 哈希）")
    share_token_raw = Column(String(128), comment="分享鉴权令牌原始值（用于重建 URL）")
    token_version = Column(Integer, default=1, comment="Token 版本号，重置后递增，旧 token 失效")
    token_expires_at = Column(DateTime, comment="Token 过期时间")

    # 分享域名/IP 配置
    share_domain = Column(String(100), comment="分享链接域名或IP，如 192.168.1.100:25600")

    created_at = Column(DateTime(timezone=True), server_default=func.now(), comment="创建时间")
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), comment="更新时间")
