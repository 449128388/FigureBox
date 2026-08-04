"""
backup_settings_service.py - 自动备份配置读写服务

功能说明：
- BackupSettingsService.get(db, user)      → 读取当前用户 4 字段配置
- BackupSettingsService.update(db, user, settings) → 校验并写入
- 业务规则：frequency 必须是 daily/weekly/monthly，retain ≥ 0
"""
from typing import Dict, Any
from datetime import datetime
from sqlalchemy.orm import Session

from app.models.user import User
from app.schemas.user import BackupSettingsUpdate


class BackupSettingsService:
    """自动备份配置读写服务"""

    @staticmethod
    def get(db: Session, user: User) -> Dict[str, Any]:
        """读取当前用户的自动备份配置"""
        return {
            "enabled": bool(user.auto_backup_enabled),
            "frequency": user.auto_backup_frequency or "weekly",
            "retain": int(user.auto_backup_retain or 0),
            "last_auto_backup_at": (
                user.last_auto_backup_at.isoformat() if user.last_auto_backup_at else None
            )
        }

    @staticmethod
    def update(db: Session, user: User, settings: BackupSettingsUpdate) -> Dict[str, Any]:
        """更新当前用户的自动备份配置（部分字段更新）"""
        if settings.enabled is not None:
            user.auto_backup_enabled = settings.enabled
        if settings.frequency is not None:
            # 二次校验（schema 已校验，此处防止外部直接传非枚举值）
            if settings.frequency not in ("daily", "weekly", "monthly"):
                raise ValueError(f"frequency must be daily/weekly/monthly, got {settings.frequency}")
            user.auto_backup_frequency = settings.frequency
        if settings.retain is not None:
            if settings.retain < 0:
                raise ValueError(f"retain must be >= 0, got {settings.retain}")
            user.auto_backup_retain = settings.retain

        db.commit()
        db.refresh(user)
        return BackupSettingsService.get(db, user)
