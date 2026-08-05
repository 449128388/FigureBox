"""
password_reset.py - 密码重置验证码模型

功能说明：
- 存储密码重置流程的 6 位验证码
- 字段：邮箱、6 位明文验证码、过期时间、是否已使用、创建时间
- 业务背景：用户通过「忘记密码」流程向注册邮箱发送验证码，
  输入后端校验通过后允许重置密码
- 安全规范：验证码有效期 10 分钟、单次有效（用过即作废）、
  同一邮箱 60 秒内仅能请求一次（防刷）
"""
from sqlalchemy import Column, Integer, String, DateTime, Index
from datetime import datetime

from app.models.database import Base


class PasswordResetCode(Base):
    """密码重置验证码记录表"""
    __tablename__ = "password_reset_codes"

    id = Column(Integer, primary_key=True, autoincrement=True)
    email = Column(String(255), nullable=False, index=True, comment="注册邮箱")
    code = Column(String(6), nullable=False, comment="6 位验证码（明文存储，仅用于 10 分钟短窗口校验）")
    expires_at = Column(DateTime, nullable=False, comment="过期时间（10 分钟）")
    is_used = Column(Integer, default=0, nullable=False, comment="是否已使用：0 未使用 / 1 已使用")
    created_at = Column(DateTime, default=datetime.now, nullable=False, comment="创建时间")

    __table_args__ = (
        Index("idx_email_used", "email", "is_used"),
    )
