"""
license.py - 许可管理 Pydantic Schemas（2026-08-07 从 schemas/user.py 剥离）

设计：
- 5 个许可相关的请求/响应模型从 schemas/user.py 独立出来
- 与许可服务层（services/license_service/）一一对应
- 0 业务字段含义变更，与旧版完全兼容
- license_config.py 改为从此处导入

Schema 列表：
- LicenseActivateRequest  在线激活请求（前端传 license_key）
- LicenseImportRequest    离线导入请求（前端传 .lic 文件名 + 内容）
- LicenseResponse         许可状态响应
- LicenseHistoryItem      许可历史记录项
- LicenseHistoryResponse  许可历史记录响应
"""
from typing import Optional
from pydantic import BaseModel, field_validator


class LicenseActivateRequest(BaseModel):
    """在线激活许可请求（前端传 license_key）"""
    license_key: str

    @field_validator('license_key')
    @classmethod
    def validate_license_key(cls, v):
        if v is None or not v.strip():
            raise ValueError('请输入许可密钥')
        # 移除中划线和空格，校验长度
        cleaned = v.strip().replace('-', '').replace(' ', '')
        if len(cleaned) < 16 or len(cleaned) > 64:
            raise ValueError('许可密钥长度无效')
        return v.strip()


class LicenseImportRequest(BaseModel):
    """离线导入许可请求（前端传 .lic 文件内容与文件名）"""
    filename: str
    content: str  # .lic 文件原始内容（base64 或文本）

    @field_validator('filename')
    @classmethod
    def validate_filename(cls, v):
        if v is None or not v.strip():
            raise ValueError('文件名不能为空')
        if not v.lower().endswith('.lic'):
            raise ValueError('仅支持 .lic 格式')
        return v.strip()

    @field_validator('content')
    @classmethod
    def validate_content(cls, v):
        if v is None or not v.strip():
            raise ValueError('许可文件内容不能为空')
        return v


class LicenseResponse(BaseModel):
    """许可状态响应"""
    license_key: str
    plan: str
    plan_label: str
    features: list
    issued_at: Optional[str] = None
    expires_at: Optional[str] = None
    activated_at: Optional[str] = None
    status: str
    source: str
    filename: str
    machine_fingerprint: str
    machine_hostname: str


class LicenseHistoryItem(BaseModel):
    """许可历史记录项"""
    id: int
    license_key: str
    plan: str
    plan_label: str
    filename: str
    source: str
    issued_at: Optional[str] = None
    expires_at: Optional[str] = None
    activated_at: Optional[str] = None
    status: str
    is_current: bool
    machine_fingerprint: str


class LicenseHistoryResponse(BaseModel):
    """许可历史记录响应"""
    items: list
    total: int
