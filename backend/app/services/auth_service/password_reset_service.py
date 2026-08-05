"""
password_reset_service.py - 密码重置业务逻辑

功能说明：
- 提供忘记密码的 3 个核心业务：发送验证码、校验验证码、重置密码
- 业务流程：用户在「忘记密码」页输入邮箱 → 后端生成 6 位验证码并通过用户配置的 SMTP 通道发送
  → 用户在「设置新密码」页输入验证码 + 新密码 → 后端校验后写入数据库
- 安全规范：
  1. 验证码有效期 10 分钟
  2. 同一邮箱 60 秒内仅能请求一次（防刷）
  3. 验证码单次有效，用过即作废
  4. 不暴露用户是否存在：未注册邮箱返回通用成功提示
  5. 走企业级服务层架构，与 API 层分离
"""
import logging
import random
import string
import smtplib
from datetime import datetime, timedelta
from email.mime.text import MIMEText
from email.utils import formataddr
from typing import Dict, Any, Tuple

from sqlalchemy.orm import Session
from sqlalchemy import and_

from app.models.user import User
from app.models.password_reset import PasswordResetCode
from app.utils.password import get_password_hash

logger = logging.getLogger(__name__)

CODE_TTL_MINUTES = 10
RESEND_COOLDOWN_SECONDS = 60


def _generate_6_digit_code() -> str:
    """生成 6 位数字验证码"""
    return ''.join(random.choices(string.digits, k=6))


def _build_message(from_name: str, from_email: str, code: str) -> MIMEText:
    """构造重置密码邮件正文"""
    subject = "【FigureBox】密码重置验证码"
    body = (
        f"你好，\n\n"
        f"你正在重置 FigureBox 账号的登录密码，验证码为：\n\n"
        f"    {code}\n\n"
        f"验证码 10 分钟内有效。如非本人操作，请忽略此邮件。\n\n"
        f"—— FigureBox 系统通知"
    )
    msg = MIMEText(body, "plain", "utf-8")
    msg["Subject"] = subject
    msg["From"] = formataddr((from_name, from_email))
    return msg


def _build_smtp_connection(user: User):
    """复用 email_config_service 的 SMTP 连接构造（无循环依赖，直接 import）"""
    from app.services.user_profile_service.email_config_service import EmailConfigService
    return EmailConfigService._build_smtp_connection(user)


def _send_reset_email(user: User, to_email: str, code: str) -> Tuple[bool, str]:
    """通过用户配置的 SMTP 通道发送重置密码邮件

    返回 (success: bool, message: str)
    """
    if not user.smtp_host or not user.smtp_from_email or not user.smtp_password:
        return False, "管理员尚未配置 SMTP 发件通道，请联系管理员"

    from_name = user.smtp_from_name or "FigureBox 系统通知"
    from_email = user.smtp_from_email
    msg = _build_message(from_name, from_email, code)
    msg["To"] = to_email

    try:
        client = _build_smtp_connection(user)
        client.sendmail(from_email, [to_email], msg.as_string())
        client.quit()
        return True, "验证码已发送，请注意查收邮箱"
    except smtplib.SMTPAuthenticationError as e:
        err_msg = e.smtp_error.decode() if isinstance(e.smtp_error, bytes) else str(e.smtp_error)
        logger.warning(f"密码重置邮件发送失败（SMTP 认证）: {err_msg}")
        return False, f"邮件发送失败（SMTP 认证）：{err_msg}"
    except Exception as e:
        logger.error(f"密码重置邮件发送失败: {e}")
        return False, f"邮件发送失败：{str(e)}"


class PasswordResetService:
    """密码重置服务类"""

    @staticmethod
    def request_reset_code(db: Session, email: str) -> Dict[str, Any]:
        """请求密码重置验证码

        - 邮箱不存在：返回通用成功提示（不暴露用户存在性）
        - 60 秒内重复请求：返回错误提示
        - 邮箱已注册且冷却时间已过：生成新验证码、清理旧记录、发送邮件
        """
        normalized_email = email.strip().lower()
        user = db.query(User).filter(User.email == normalized_email).first()

        # 不暴露用户是否存在：未注册邮箱直接返回通用成功
        if not user:
            logger.info(f"密码重置请求：邮箱 {normalized_email} 未注册（不暴露用户存在性）")
            return {
                "success": True,
                "message": "若该邮箱已注册，验证码已发送，请注意查收",
            }

        # 60 秒冷却检查
        latest_code = (
            db.query(PasswordResetCode)
            .filter(PasswordResetCode.email == normalized_email)
            .order_by(PasswordResetCode.created_at.desc())
            .first()
        )
        if latest_code and (datetime.now() - latest_code.created_at).total_seconds() < RESEND_COOLDOWN_SECONDS:
            wait_sec = RESEND_COOLDOWN_SECONDS - int((datetime.now() - latest_code.created_at).total_seconds())
            return {
                "success": False,
                "message": f"操作过于频繁，请 {wait_sec} 秒后再试",
            }

        # 清理该邮箱的旧验证码（未使用的）
        db.query(PasswordResetCode).filter(
            and_(
                PasswordResetCode.email == normalized_email,
                PasswordResetCode.is_used == 0,
            )
        ).delete(synchronize_session=False)

        # 生成新验证码
        code = _generate_6_digit_code()
        record = PasswordResetCode(
            email=normalized_email,
            code=code,
            expires_at=datetime.now() + timedelta(minutes=CODE_TTL_MINUTES),
            is_used=0,
            created_at=datetime.now(),
        )
        db.add(record)
        db.commit()

        # 通过 SMTP 发送
        ok, msg = _send_reset_email(user, normalized_email, code)
        if not ok:
            # 邮件发送失败：删除刚插入的验证码记录
            db.delete(record)
            db.commit()
            return {"success": False, "message": msg}

        logger.info(f"密码重置验证码已发送：{normalized_email}")
        return {
            "success": True,
            "message": "若该邮箱已注册，验证码已发送，请注意查收",
        }

    @staticmethod
    def verify_code(db: Session, email: str, code: str) -> Dict[str, Any]:
        """校验密码重置验证码（不消费，仅校验）

        - 邮箱不存在
        - 验证码错误
        - 验证码已过期
        - 验证码已使用
        - 校验通过
        """
        normalized_email = email.strip().lower()
        record = (
            db.query(PasswordResetCode)
            .filter(
                and_(
                    PasswordResetCode.email == normalized_email,
                    PasswordResetCode.code == code,
                    PasswordResetCode.is_used == 0,
                )
            )
            .order_by(PasswordResetCode.created_at.desc())
            .first()
        )

        if not record:
            return {"success": False, "message": "验证码不正确或已失效"}

        if record.expires_at < datetime.now():
            return {"success": False, "message": "验证码已过期，请重新获取"}

        # 仅校验，不消费
        return {"success": True, "message": "验证码校验通过"}

    @staticmethod
    def reset_password(db: Session, email: str, code: str, new_password: str) -> Dict[str, Any]:
        """通过验证码重置密码（消费验证码）

        - 邮箱不存在
        - 验证码错误 / 过期 / 已使用
        - 校验通过：写入新密码（bcrypt 哈希）、标记验证码已使用
        """
        normalized_email = email.strip().lower()
        user = db.query(User).filter(User.email == normalized_email).first()
        if not user:
            return {"success": False, "message": "验证码不正确或已失效"}

        record = (
            db.query(PasswordResetCode)
            .filter(
                and_(
                    PasswordResetCode.email == normalized_email,
                    PasswordResetCode.code == code,
                    PasswordResetCode.is_used == 0,
                )
            )
            .order_by(PasswordResetCode.created_at.desc())
            .first()
        )

        if not record:
            return {"success": False, "message": "验证码不正确或已失效"}

        if record.expires_at < datetime.now():
            return {"success": False, "message": "验证码已过期，请重新获取"}

        # 写入新密码
        user.password_hash = get_password_hash(new_password)
        # 消费验证码
        record.is_used = 1
        # 先 flush 标记操作，避免后续 delete 把 record 一并删掉导致 StaleDataError
        db.flush()

        # 清理该邮箱的所有其它未使用验证码（避免历史泄漏，排除当前 record）
        db.query(PasswordResetCode).filter(
            and_(
                PasswordResetCode.email == normalized_email,
                PasswordResetCode.is_used == 0,
                PasswordResetCode.id != record.id,
            )
        ).delete(synchronize_session=False)

        db.commit()
        logger.info(f"用户 {user.id} 通过验证码重置密码成功：{normalized_email}")
        return {"success": True, "message": "密码重置成功，请使用新密码重新登录"}
