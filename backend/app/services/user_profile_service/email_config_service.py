"""
email_config_service.py - 邮箱设置（SMTP 发件配置）服务

功能说明：
- 提供 SMTP 邮箱配置的读取、更新、测试连接、发送测试邮件等业务逻辑
- 遵循企业级服务层架构，与 API 层分离
- 业务背景：配置 SMTP 后，系统可向用户发送密码重置邮件、尾款到期提醒、资产周报等系统通知
- 安全性：密码字段不回传前端（仅返回 smtp_password_set 布尔值）
- 签名规范：所有写操作方法显式接收 db 入参（避免 ORM instance 反查 session 的隐性依赖）
"""

import smtplib
import logging
from email.mime.text import MIMEText
from email.utils import formataddr
from datetime import datetime
from typing import Dict, Any

from sqlalchemy.orm import Session

from app.models.user import User
from app.schemas.user import EmailConfigUpdate

logger = logging.getLogger(__name__)


def _build_response(user: User) -> Dict[str, Any]:
    """将 user 表的 SMTP 字段打包为响应 dict（密码不回传）"""
    return {
        "smtp_host": user.smtp_host or "",
        "smtp_port": user.smtp_port or 465,
        "smtp_from_email": user.smtp_from_email or "",
        "smtp_from_name": user.smtp_from_name or "FigureBox 系统通知",
        "smtp_password_set": bool(user.smtp_password),
        "smtp_secure_mode": user.smtp_secure_mode or "ssl",
        "smtp_last_test_at": user.smtp_last_test_at.isoformat() if user.smtp_last_test_at else None,
        "smtp_last_test_status": user.smtp_last_test_status or "",
    }


class EmailConfigService:
    """SMTP 邮箱配置服务类"""

    @staticmethod
    def get_email_config(db: Session, user: User) -> Dict[str, Any]:
        """读取当前用户的 SMTP 邮箱配置（密码不回传）"""
        return _build_response(user)

    @staticmethod
    def update_email_config(db: Session, user: User, config_data: EmailConfigUpdate) -> Dict[str, Any]:
        """更新当前用户的 SMTP 邮箱配置"""
        update_dict = config_data.model_dump(exclude_unset=True)

        field_mapping = {
            "smtp_host": "smtp_host",
            "smtp_port": "smtp_port",
            "smtp_from_email": "smtp_from_email",
            "smtp_from_name": "smtp_from_name",
            "smtp_password": "smtp_password",
            "smtp_secure_mode": "smtp_secure_mode",
        }

        for field, db_field in field_mapping.items():
            if field in update_dict:
                value = update_dict[field]
                if hasattr(user, db_field):
                    setattr(user, db_field, value)

        # 配置更新后，清空旧的测试状态（让用户重新测试）
        user.smtp_last_test_at = None
        user.smtp_last_test_status = ""

        db.commit()
        db.refresh(user)
        logger.info(f"用户 {user.id} SMTP 邮箱配置已更新")

        return EmailConfigService.get_email_config(db, user)

    @staticmethod
    def _build_smtp_connection(user: User):
        """根据用户配置构造 smtplib 连接（不发送任何邮件）"""
        secure_mode = user.smtp_secure_mode or "ssl"
        port = user.smtp_port or 465

        if secure_mode == "ssl":
            client = smtplib.SMTP_SSL(user.smtp_host, port, timeout=10)
        else:
            client = smtplib.SMTP(user.smtp_host, port, timeout=10)
            if secure_mode == "starttls":
                client.starttls()

        client.login(user.smtp_from_email, user.smtp_password)
        return client

    @staticmethod
    def test_connection(db: Session, user: User) -> Dict[str, Any]:
        """测试 SMTP 连接（仅做 login，不发邮件）

        成功：更新 user.smtp_last_test_at + smtp_last_test_status
        失败：更新 smtp_last_test_status = 'failed'，记录异常日志
        """
        if not user.smtp_host or not user.smtp_from_email or not user.smtp_password:
            return {
                "success": False,
                "message": "配置不完整，请填写 SMTP 服务器、发件人邮箱、授权码",
            }

        try:
            client = EmailConfigService._build_smtp_connection(user)
            client.quit()

            user.smtp_last_test_at = datetime.now()
            user.smtp_last_test_status = "success"
            db.commit()
            db.refresh(user)
            logger.info(f"用户 {user.id} SMTP 测试连接成功")
            return {"success": True, "message": "SMTP 连接测试成功"}
        except smtplib.SMTPAuthenticationError as e:
            user.smtp_last_test_status = "failed"
            db.commit()
            err_msg = e.smtp_error.decode() if isinstance(e.smtp_error, bytes) else str(e.smtp_error)
            logger.warning(f"用户 {user.id} SMTP 认证失败: {err_msg}")
            return {"success": False, "message": f"认证失败：{err_msg}（smtp_code={e.smtp_code}）"}
        except Exception as e:
            user.smtp_last_test_status = "failed"
            db.commit()
            logger.error(f"用户 {user.id} SMTP 连接异常: {e}")
            return {"success": False, "message": f"连接失败：{str(e)}"}

    @staticmethod
    def send_test_email(db: Session, user: User, test_to: str) -> Dict[str, Any]:
        """向指定邮箱发送一封测试邮件，验证完整发件链路"""
        if not user.smtp_host or not user.smtp_from_email or not user.smtp_password:
            return {
                "success": False,
                "message": "配置不完整，请先填写 SMTP 服务器、发件人邮箱、授权码",
            }

        from_email = user.smtp_from_email
        from_name = user.smtp_from_name or "FigureBox 系统通知"

        subject = "【FigureBox】SMTP 配置测试邮件"
        body = (
            "你好，\n\n"
            f"这是一封来自 FigureBox 的 SMTP 配置测试邮件，"
            f"由用户 {user.username} 触发。\n\n"
            f"发送时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
            "若你收到此邮件，说明 SMTP 发件配置已正确生效。"
            "系统后续可通过此通道发送密码重置、尾款到期提醒、资产周报等系统通知。\n\n"
            "—— FigureBox 系统通知"
        )

        msg = MIMEText(body, "plain", "utf-8")
        msg["Subject"] = subject
        msg["From"] = formataddr((from_name, from_email))
        msg["To"] = test_to

        try:
            client = EmailConfigService._build_smtp_connection(user)
            client.sendmail(from_email, [test_to], msg.as_string())
            client.quit()

            user.smtp_last_test_at = datetime.now()
            user.smtp_last_test_status = "success"
            db.commit()
            db.refresh(user)
            logger.info(f"用户 {user.id} SMTP 测试邮件发送成功 -> {test_to}")
            return {"success": True, "message": f"测试邮件已发送至 {test_to}"}
        except smtplib.SMTPAuthenticationError as e:
            user.smtp_last_test_status = "failed"
            db.commit()
            err_msg = e.smtp_error.decode() if isinstance(e.smtp_error, bytes) else str(e.smtp_error)
            logger.warning(f"用户 {user.id} SMTP 认证失败: {err_msg}")
            return {"success": False, "message": f"认证失败：{err_msg}"}
        except Exception as e:
            user.smtp_last_test_status = "failed"
            db.commit()
            logger.error(f"用户 {user.id} SMTP 发送失败: {e}")
            return {"success": False, "message": f"发送失败：{str(e)}"}
