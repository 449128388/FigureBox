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


class ChangePasswordRequest(BaseModel):
    """修改登录密码请求"""
    current_password: str
    new_password: str


# ===== 密码重置 Schemas =====

class ForgotPasswordRequest(BaseModel):
    """请求密码重置验证码"""
    email: EmailStr


class VerifyResetCodeRequest(BaseModel):
    """校验密码重置验证码"""
    email: EmailStr
    code: str

    @field_validator('code')
    @classmethod
    def validate_code(cls, v):
        if v is None or not v.strip():
            raise ValueError('请输入验证码')
        if not v.strip().isdigit() or len(v.strip()) != 6:
            raise ValueError('验证码为 6 位数字')
        return v.strip()


class ResetPasswordRequest(BaseModel):
    """通过验证码重置密码"""
    email: EmailStr
    code: str
    new_password: str

    @field_validator('code')
    @classmethod
    def validate_code(cls, v):
        if v is None or not v.strip():
            raise ValueError('请输入验证码')
        if not v.strip().isdigit() or len(v.strip()) != 6:
            raise ValueError('验证码为 6 位数字')
        return v.strip()

    @field_validator('new_password')
    @classmethod
    def validate_new_password(cls, v):
        if not v or len(v) < 8 or len(v) > 20:
            raise ValueError('新密码长度需在 8-20 位之间')
        return v


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


# ===== 邮箱设置 Schemas =====

class EmailConfigUpdate(BaseModel):
    """SMTP 邮箱设置更新请求"""
    smtp_host: Optional[str] = None
    smtp_port: Optional[int] = None
    smtp_from_email: Optional[str] = None
    smtp_from_name: Optional[str] = None
    smtp_password: Optional[str] = None
    smtp_secure_mode: Optional[str] = None  # ssl / starttls / none

    @field_validator('smtp_secure_mode')
    @classmethod
    def validate_secure_mode(cls, v):
        if v is not None and v not in ('ssl', 'starttls', 'none'):
            raise ValueError('smtp_secure_mode must be ssl/starttls/none')
        return v

    @field_validator('smtp_port')
    @classmethod
    def validate_port(cls, v):
        if v is not None and (v < 1 or v > 65535):
            raise ValueError('smtp_port must be in [1, 65535]')
        return v


class EmailConfigResponse(BaseModel):
    """SMTP 邮箱设置响应（密码字段屏蔽返回）"""
    smtp_host: str
    smtp_port: int
    smtp_from_email: str
    smtp_from_name: str
    smtp_password_set: bool  # 仅返回是否已设置，原始密码不回传
    smtp_secure_mode: str
    smtp_last_test_at: Optional[str] = None
    smtp_last_test_status: str


class EmailTestRequest(BaseModel):
    """SMTP 测试邮件请求"""
    test_to: str  # 测试收件邮箱

    @field_validator('test_to')
    @classmethod
    def validate_test_to(cls, v):
        if v is None or v.strip() == '':
            raise ValueError('请输入测试收件邮箱')
        pattern = r'^[^\s@]+@[^\s@]+\.[^\s@]+$'
        if not __import__('re').match(pattern, v):
            raise ValueError('收件邮箱格式不正确')
        return v
