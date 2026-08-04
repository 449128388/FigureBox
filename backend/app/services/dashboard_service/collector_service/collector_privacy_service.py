"""
collector_privacy_service.py - 收藏家隐私设置服务

功能说明：
- 提供用户隐私设置的 CRUD 业务逻辑
- 默认值：个人主页公开、藏品总数公开、本命厂商公开
- 默认不展示：藏品列表、资产金额、动态流
- 提供分享鉴权令牌的生成、验证、重置
"""

from sqlalchemy.orm import Session
from typing import Optional, Dict
from datetime import datetime, timedelta
import secrets
import hashlib

from app.models.collector_privacy import CollectorPrivacy


class CollectorPrivacyService:

    DEFAULTS = {
        "home_visibility": "public",
        "show_total": True,
        "show_figures": False,
        "show_asset": False,
        "show_tags": True,
        "show_feed": False,
        "poster_level": "stats_only"
    }

    # Token 默认有效期（天）
    TOKEN_DAYS_VALID = 30

    @staticmethod
    def _generate_share_token() -> str:
        """生成分享鉴权令牌"""
        return secrets.token_urlsafe(48)

    @staticmethod
    def _hash_token(token: str) -> str:
        """对 token 做哈希，存储哈希值而非原文"""
        return hashlib.sha256(token.encode()).hexdigest()

    @staticmethod
    def get_or_create(db: Session, user_id: int) -> CollectorPrivacy:
        """获取用户的隐私设置，不存在则创建默认"""
        record = db.query(CollectorPrivacy).filter(
            CollectorPrivacy.user_id == user_id
        ).first()
        if not record:
            record = CollectorPrivacy(user_id=user_id, **CollectorPrivacyService.DEFAULTS)
            db.add(record)
            db.commit()
            db.refresh(record)
        return record

    @staticmethod
    def update(db: Session, user_id: int, settings: Dict) -> CollectorPrivacy:
        """更新隐私设置"""
        record = CollectorPrivacyService.get_or_create(db, user_id)
        allowed_fields = {
            "home_visibility", "show_total", "show_figures",
            "show_asset", "show_tags", "show_feed", "poster_level",
            "share_domain"
        }
        for key, value in settings.items():
            if key in allowed_fields:
                setattr(record, key, value)
        db.commit()
        db.refresh(record)
        return record

    @staticmethod
    def generate_share_url(db: Session, user_id: int, base_url: str) -> Dict:
        """
        生成分享链接和 token

        只会在以下情况生成新 token：
        - 从未生成过（share_token_raw 为空）
        - 当前 token 已过期

        Args:
            db: 数据库会话
            user_id: 用户ID
            base_url: 前端基础 URL，如 https://domain.com

        Returns:
            dict: { share_url, share_token, expires_at }
        """
        record = CollectorPrivacyService.get_or_create(db, user_id)
        now = datetime.now()

        # 检查现有 token 是否仍有效
        if record.share_token_raw and record.token_expires_at and now < record.token_expires_at:
            # 复用现有 token，不生成新 token
            raw_token = record.share_token_raw
        else:
            # 无有效 token，生成新 token
            raw_token = CollectorPrivacyService._generate_share_token()
            hashed = CollectorPrivacyService._hash_token(raw_token)
            record.share_token = hashed
            record.share_token_raw = raw_token
            record.token_version = (record.token_version or 1) + 1
            record.token_expires_at = now + timedelta(days=CollectorPrivacyService.TOKEN_DAYS_VALID)
            db.commit()
            db.refresh(record)

        # 优先使用用户配置的 share_domain，否则使用请求的 base_url
        if record.share_domain:
            share_url = f"http://{record.share_domain.rstrip('/')}/share/{user_id}?token={raw_token}"
        else:
            share_url = f"{base_url.rstrip('/')}/share/{user_id}?token={raw_token}"

        return {
            "share_url": share_url,
            "share_token": raw_token,
            "expires_at": record.token_expires_at.isoformat() if record.token_expires_at else None
        }

    @staticmethod
    def validate_share_token(db: Session, user_id: int, token: str) -> Optional[CollectorPrivacy]:
        """
        验证分享 token 是否有效

        Returns:
            CollectorPrivacy if valid, None if invalid/expired
        """
        hashed = CollectorPrivacyService._hash_token(token)
        record = db.query(CollectorPrivacy).filter(
            CollectorPrivacy.user_id == user_id
        ).first()
        if not record:
            return None
        # 验证 token 哈希匹配
        if record.share_token != hashed:
            return None
        # 检查过期
        now = datetime.now()
        if record.token_expires_at and now > record.token_expires_at:
            return None
        return record

    @staticmethod
    def reset_share_token(db: Session, user_id: int) -> Dict:
        """
        重置分享 token（旧 token 立即失效）

        Returns:
            dict: { share_url, share_token, expires_at }
        """
        record = CollectorPrivacyService.get_or_create(db, user_id)
        # 递增版本号使旧 token 失效
        record.token_version = (record.token_version or 1) + 1
        record.share_token = None
        record.share_token_raw = None
        record.token_expires_at = None
        db.commit()
        return {"success": True, "message": "分享链接已重置，旧链接已失效"}

    @staticmethod
    def to_dict(record: CollectorPrivacy) -> Dict:
        """转为 API 返回格式"""
        return {
            "home_visibility": record.home_visibility or "public",
            "show_total": bool(record.show_total) if record.show_total is not None else True,
            "show_figures": bool(record.show_figures) if record.show_figures is not None else False,
            "show_asset": bool(record.show_asset) if record.show_asset is not None else False,
            "show_tags": bool(record.show_tags) if record.show_tags is not None else True,
            "show_feed": bool(record.show_feed) if record.show_feed is not None else False,
            "poster_level": record.poster_level or "stats_only",
            "has_share_token": bool(record.share_token),
            "share_domain": record.share_domain or ""
        }
