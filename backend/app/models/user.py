import os

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
    - MinIO 配置字段默认从环境变量读取，确保新用户自动填充

    安全说明：
    - 密码使用哈希存储，不保存明文
    - 支持邮箱作为备用登录方式
    - Secret Key 仅保存在用户自己的配置中，供前端直接连接 MinIO 使用

    关联关系：
    - 被 Order、AssetTransaction 等模型关联
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

    # ===== MinIO 云存储配置（用户视角的 MinIO 连接信息） =====
    # 注意：MINIO_ENDPOINT 是内部 Docker 网络地址，供后端服务使用
    # 用户使用的 MinIO 端点应从 MINIO_PUBLIC_ENDPOINT 获取
    minio_endpoint = Column(String(255), default=os.getenv("MINIO_PUBLIC_ENDPOINT", "http://localhost:28640"), comment="MinIO API 端点地址")
    minio_access_key = Column(String(100), default=os.getenv("MINIO_ACCESS_KEY", ""), comment="MinIO Access Key")
    minio_secret_key = Column(String(255), default=os.getenv("MINIO_SECRET_KEY", ""), comment="MinIO Secret Key")
    minio_bucket = Column(String(100), default=os.getenv("MINIO_BUCKET", ""), comment="MinIO Bucket 名称")
    minio_public_url = Column(String(255), default=os.getenv("MINIO_PUBLIC_URL", ""), comment="图片访问域名")
    minio_secure = Column(Boolean, default=os.getenv("MINIO_SECURE", "false").lower() in ("true", "1", "yes"), comment="是否使用 HTTPS")

    # ===== 超时登出配置 =====
    session_timeout_minutes = Column(Integer, default=30, comment="会话超时时间（分钟），0 表示永不超时")
    session_timeout_warning = Column(Boolean, default=True, comment="超时前是否弹窗提醒")

    def __init__(self, **kwargs):
        """自动将环境变量中的 MinIO 默认值注入新用户"""
        # SQLAlchemy 在从 DB 还原时不走 __init__，只影响 Python 侧新建用户
        defaults = {
            "minio_endpoint": os.getenv("MINIO_PUBLIC_ENDPOINT", "http://localhost:28640"),
            "minio_access_key": os.getenv("MINIO_ACCESS_KEY", ""),
            "minio_secret_key": os.getenv("MINIO_SECRET_KEY", ""),
            "minio_bucket": os.getenv("MINIO_BUCKET", ""),
            "minio_public_url": os.getenv("MINIO_PUBLIC_URL", ""),
            "minio_secure": os.getenv("MINIO_SECURE", "false").lower() in ("true", "1", "yes"),
        }
        for key, val in defaults.items():
            if key not in kwargs:
                kwargs[key] = val
        super().__init__(**kwargs)
