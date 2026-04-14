from sqlalchemy import Column, Integer, String, Boolean
from app.models.database import Base

class User(Base):
    """
    用户模型 - 存储系统用户的基本信息和认证信息
    
    功能说明：
    - 存储用户登录凭证（用户名、密码哈希）
    - 支持用户权限管理（普通用户/管理员）
    - 支持用户状态控制（激活/禁用）
    
    安全说明：
    - 密码使用哈希存储，不保存明文
    - 支持邮箱作为备用登录方式
    
    关联关系：
    - 被 Order、AssetAlert、AssetTransaction 等模型关联
    """
    __tablename__ = "users"

    # 主键
    id = Column(Integer, primary_key=True, index=True)  # 用户唯一标识ID
    
    # 登录凭证
    username = Column(String(50), unique=True, index=True, nullable=False)  # 用户名（登录账号，唯一）
    email = Column(String(100), unique=True, index=True, nullable=False)  # 邮箱地址（唯一，可用于登录）
    password_hash = Column(String(255), nullable=False)  # 密码哈希值（使用安全算法加密，不存明文）
    
    # 用户状态
    is_active = Column(Boolean, default=True)  # 账号是否激活（True=正常，False=禁用）
    is_admin = Column(Boolean, default=False)  # 是否为管理员（True=管理员，False=普通用户）
