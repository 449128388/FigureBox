"""
password_reset.py - 密码重置 API 路由

功能说明：
- 提供 3 个公开端点（无需登录）：
  1. POST /auth/forgot-password  请求密码重置验证码
  2. POST /auth/verify-reset-code  校验密码重置验证码（不消费）
  3. POST /auth/reset-password  通过验证码重置密码（消费）
- 业务背景：用户在「忘记密码」流程中依次调用
- API 层仅做入参校验 + 出参包装，业务逻辑全部走 service 层
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.models.database import get_db
from app.schemas.user import (
    ForgotPasswordRequest,
    VerifyResetCodeRequest,
    ResetPasswordRequest,
)
from app.services.auth_service.password_reset_service import PasswordResetService

router = APIRouter()


@router.post("/forgot-password", response_model=dict)
def forgot_password(request: ForgotPasswordRequest, db: Session = Depends(get_db)):
    """请求密码重置验证码（公开端点）

    - 邮箱不存在：返回通用成功提示（不暴露用户存在性）
    - 60 秒内重复请求：返回错误提示
    - 邮箱已注册且冷却时间已过：生成新验证码并通过 SMTP 发送
    """
    return PasswordResetService.request_reset_code(db, request.email)


@router.post("/verify-reset-code", response_model=dict)
def verify_reset_code(request: VerifyResetCodeRequest, db: Session = Depends(get_db)):
    """校验密码重置验证码（公开端点，不消费）

    - 用户在「重置密码」第 1 步输入验证码后调用，仅校验不消费
    - 校验通过：success=True，前端可进入「设置新密码」步骤
    """
    return PasswordResetService.verify_code(db, request.email, request.code)


@router.post("/reset-password", response_model=dict)
def reset_password(request: ResetPasswordRequest, db: Session = Depends(get_db)):
    """通过验证码重置密码（公开端点，消费验证码）

    - 校验通过：写入新密码（bcrypt 哈希）并标记验证码已使用
    - 用户重置后需重新登录
    """
    return PasswordResetService.reset_password(db, request.email, request.code, request.new_password)
