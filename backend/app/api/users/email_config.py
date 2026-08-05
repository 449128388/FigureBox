"""
email_config.py - 邮箱设置（SMTP 发件配置）API 路由（个人中心-系统备份-邮箱设置模块）

功能说明：
- GET    /api/email/config        - 读取当前用户 SMTP 邮箱配置（密码不回传）
- PUT    /api/email/config        - 更新 SMTP 邮箱配置
- POST   /api/email/test          - 测试 SMTP 连接（仅 login 不发邮件）
- POST   /api/email/test-send     - 向指定邮箱发送测试邮件（验证完整链路）
- 业务逻辑在 EmailConfigService 服务层
- 与 MinIO 配置（/api/minio/*）、备份配置（/api/backup/*）同层，全部由 main.py 单独挂载
- 业务背景：配置 SMTP 后，系统可向用户发送密码重置邮件、尾款到期提醒、资产周报等系统通知
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.models.database import get_db
from app.api.users import get_current_user
from app.models.user import User
from app.services.user_profile_service import EmailConfigService
from app.schemas.user import EmailConfigUpdate, EmailTestRequest

router = APIRouter()


@router.get("/email/config", response_model=dict)
def get_email_config(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取当前用户的 SMTP 邮箱配置（密码字段屏蔽）"""
    return EmailConfigService.get_email_config(db, current_user)


@router.put("/email/config", response_model=dict)
def update_email_config(
    config_data: EmailConfigUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """更新当前用户的 SMTP 邮箱配置"""
    return EmailConfigService.update_email_config(db, current_user, config_data)


@router.post("/email/test", response_model=dict)
def test_email_connection(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """测试 SMTP 连接（仅 login，不发邮件）"""
    return EmailConfigService.test_connection(db, current_user)


@router.post("/email/test-send", response_model=dict)
def send_test_email(
    request: EmailTestRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """向指定邮箱发送一封测试邮件，验证完整发件链路"""
    return EmailConfigService.send_test_email(db, current_user, request.test_to)
