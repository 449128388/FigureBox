"""
license.py - 许可管理 UserLicense 独立模型（2026-08-07 从 users_info 表剥离）

字段语义（与原 users_info.license_* 完全一致，0 业务字段变化）：
- license_key            许可密钥（公开 ID，30-40 位字符串）
- license_plan           授权类型：trial / personal / pro / enterprise
- license_features       功能开关 JSON 字符串
- license_issued_at      许可签发时间
- license_expires_at     许可到期时间
- license_activated_at   本机激活时间
- license_status         许可状态：active / expired / revoked / inactive
- license_source         激活来源：online / offline / trial
- license_filename       离线导入的许可文件名
- license_activated_machine  本机机器指纹（激活时绑定，由后端动态生成不入库）

关联关系：
- user_licenses.user_id → users_info.id（1:1，UNIQUE）
- 双向 relationship：User.license ↔ UserLicense.user
- ON DELETE CASCADE：删除用户时自动删除其许可记录
"""
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Index
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.models.database import Base


class UserLicense(Base):
    """
    用户许可记录表 - 1:1 关联 users_info

    表名：user_licenses
    主键：id
    唯一键：user_id（确保一个用户最多一条许可记录）

    业务访问（service 层）：
        user = db.query(User).options(selectinload(User.license)).first()
        if user.license is None:
            user.license = UserLicense(user_id=user.id)
        user.license.license_key = ...
        db.commit()
    """
    __tablename__ = "user_licenses"

    # 主键
    id = Column(Integer, primary_key=True, index=True, comment="许可记录主键 ID")

    # 外键：1:1 关联 users_info
    # UNIQUE 约束保证一个用户最多一条许可记录
    # ON DELETE CASCADE：删除用户时自动清理
    user_id = Column(
        Integer,
        ForeignKey("users_info.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
        index=True,
        comment="所属用户 ID（1:1 关联 users_info.id，ON DELETE CASCADE）"
    )

    # ===== 许可字段（与原 users_info.license_* 完全一致）=====
    license_key = Column(String(64), default="", comment="许可密钥（公开 ID）")
    license_plan = Column(String(20), default="trial", comment="授权类型：trial / personal / pro / enterprise")
    license_features = Column(String(500), default="", comment="功能开关 JSON 字符串")
    license_issued_at = Column(DateTime, nullable=True, comment="许可签发时间")
    license_expires_at = Column(DateTime, nullable=True, comment="许可到期时间")
    license_activated_at = Column(DateTime, nullable=True, comment="本机激活时间")
    license_status = Column(String(20), default="inactive", comment="许可状态：active / expired / revoked / inactive")
    license_source = Column(String(20), default="", comment="激活来源：online / offline / trial")
    license_filename = Column(String(100), default="", comment="导入的许可文件名（仅离线激活时记录）")
    license_activated_machine = Column(String(64), default="", comment="本机机器指纹（激活时绑定）")

    # ===== 审计时间戳 =====
    created_at = Column(DateTime, server_default=func.now(), comment="记录创建时间")
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), comment="记录更新时间")

    # ===== 关联关系（双向）=====
    user = relationship("User", back_populates="license")

    # 复合索引：按用户 + 状态快速查询「已激活」许可
    __table_args__ = (
        Index("idx_user_license_user_status", "user_id", "license_status"),
    )

    def __repr__(self):
        return f"<UserLicense id={self.id} user_id={self.user_id} plan={self.license_plan} status={self.license_status}>"
