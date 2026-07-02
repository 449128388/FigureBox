from sqlalchemy import Column, Integer, String, Boolean, Float, DateTime, Date, Text
from sqlalchemy.sql import func
from app.models.database import Base


class User(Base):
    """
    用户模型 - 存储系统用户的基本信息和认证信息

    功能说明：
    - 存储用户登录凭证（用户名、密码哈希）
    - 支持用户权限管理（普通用户/管理员）
    - 支持用户状态控制（激活/禁用）
    - 合并 user_settings 表字段，统一管理用户配置

    安全说明：
    - 密码使用哈希存储，不保存明文
    - 支持邮箱作为备用登录方式

    关联关系：
    - 被 Order、AssetAlert、AssetTransaction 等模型关联
    """
    __tablename__ = "users_info"

    # 主键
    id = Column(Integer, primary_key=True, index=True, comment="用户唯一标识ID")

    # 登录凭证
    username = Column(String(50), unique=True, index=True, nullable=False, comment="用户名（登录账号，唯一）")
    email = Column(String(100), unique=True, index=True, nullable=False, comment="邮箱地址（唯一，可用于登录）")
    password_hash = Column(String(255), nullable=False, comment="密码哈希值（使用安全算法加密，不存明文）")

    # 用户状态
    is_active = Column(Boolean, default=True, comment="账号是否激活（True=正常，False=禁用）")
    is_admin = Column(Boolean, default=False, comment="是否为管理员（True=管理员，False=普通用户）")

    # ===== 个人资料字段 =====
    nickname = Column(String(50), default="", comment="用户昵称（展示名称，最长25字）")
    signature = Column(String(100), default="", comment="个人签名（最长24字）")
    gender = Column(String(10), default="secret", comment="性别：male/female/secret")
    birthday = Column(Date, nullable=True, comment="出生日期")
    bio = Column(Text, default="", comment="自我介绍（最长500字）")
    avatar_url = Column(String(500), default="", comment="头像URL")

    # ===== 隐私/推送/屏蔽设置（JSON 字符串存储） =====
    block_settings = Column(String(1000), default="{}", comment="屏蔽设置 JSON")
    privacy_settings = Column(String(1000), default="{}", comment="隐私设置 JSON")
    push_settings = Column(String(1000), default="{}", comment="推送设置 JSON")

    # ===== 联系方式 =====
    phone = Column(String(20), default="", comment="手机号码")
    wechat = Column(String(50), default="", comment="微信号")

    # 用户配置（原 user_settings 表字段）
    annual_spending_limit = Column(Float, default=0, comment="年度手办消费上限（0表示未设置）")
    settings_updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), comment="配置最后更新时间")
