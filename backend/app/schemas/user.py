from pydantic import BaseModel, EmailStr, field_validator
from datetime import date, datetime
from typing import Optional


class UserBase(BaseModel):
    username: str
    email: EmailStr


class UserCreate(UserBase):
    password: str


class UserUpdate(BaseModel):
    username: str | None = None
    email: EmailStr | None = None
    password: str | None = None


class User(UserBase):
    id: int
    is_active: bool
    is_admin: bool
    avatar_url: str

    class Config:
        from_attributes = True


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    user_id: int | None = None


# ===== 个人资料 Schemas =====

class ProfileUpdate(BaseModel):
    """个人资料更新请求"""
    nickname: Optional[str] = None
    signature: Optional[str] = None
    gender: Optional[str] = None
    birthday: Optional[str] = None  # "1995-07-15" 格式
    bio: Optional[str] = None
    avatar_url: Optional[str] = None
    phone: Optional[str] = None
    wechat: Optional[str] = None

    @field_validator('gender')
    @classmethod
    def validate_gender(cls, v):
        if v is not None and v not in ('male', 'female', 'secret'):
            raise ValueError('gender must be male/female/secret')
        return v

    @field_validator('nickname')
    @classmethod
    def validate_nickname(cls, v):
        if v is not None and len(v) > 25:
            raise ValueError('nickname max 25 characters')
        return v

    @field_validator('signature')
    @classmethod
    def validate_signature(cls, v):
        if v is not None and len(v) > 24:
            raise ValueError('signature max 24 characters')
        return v

    @field_validator('bio')
    @classmethod
    def validate_bio(cls, v):
        if v is not None and len(v) > 500:
            raise ValueError('bio max 500 characters')
        return v


class ProfileResponse(BaseModel):
    """个人资料响应"""
    id: int
    username: str
    email: str
    nickname: str
    signature: str
    gender: str
    birthday: Optional[str] = None
    bio: str
    avatar_url: str
    phone: str
    wechat: str
    is_active: bool
    is_admin: bool
    annual_spending_limit: float

    class Config:
        from_attributes = True


class SettingsUpdate(BaseModel):
    """设置更新（屏蔽/隐私/推送）"""
    block_settings: Optional[str] = None
    privacy_settings: Optional[str] = None
    push_settings: Optional[str] = None


class MinIOConfigUpdate(BaseModel):
    """MinIO 配置更新请求"""
    endpoint: Optional[str] = None
    access_key: Optional[str] = None
    secret_key: Optional[str] = None
    bucket: Optional[str] = None
    public_url: Optional[str] = None
    secure: Optional[bool] = None


class TimeoutConfigUpdate(BaseModel):
    """超时登出配置更新请求"""
    timeout_minutes: Optional[int] = None
    timeout_warning: Optional[bool] = None


# ===== 自动备份设置 Schemas =====

class BackupSettingsUpdate(BaseModel):
    """自动备份设置更新请求"""
    enabled: Optional[bool] = None
    frequency: Optional[str] = None  # daily / weekly / monthly
    retain: Optional[int] = None     # 0=不限制，≥1

    @field_validator('frequency')
    @classmethod
    def validate_frequency(cls, v):
        if v is not None and v not in ('daily', 'weekly', 'monthly'):
            raise ValueError('frequency must be daily/weekly/monthly')
        return v

    @field_validator('retain')
    @classmethod
    def validate_retain(cls, v):
        if v is not None and v < 0:
            raise ValueError('retain must be >= 0')
        return v


class BackupSettingsResponse(BaseModel):
    """自动备份设置响应"""
    enabled: bool
    frequency: str
    retain: int
    last_auto_backup_at: Optional[str] = None

    class Config:
        from_attributes = True
