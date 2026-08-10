"""
license_service.py - 许可管理服务（业务逻辑层）

功能说明：
- 处理许可的在线激活、离线导入、状态查询、吊销、机器指纹等业务
- 遵循企业级服务层架构，与 API 层解耦
- 签名规范：所有方法显式接收 db 入参
- 业务背景：FigureBox 商业化，详见 docs/license-system-design.md

设计要点（2026-08-07 演化至 v3 独立表）：
- 许可数据存储在独立表 user_licenses，通过 User.license 1:1 relationship 访问
- 机器指纹由后端在调用时动态生成（不入库），绑定后写入 user.license.license_activated_machine
- 当前许可状态在 user_licenses 表中存储（避免每次启动都解析 .lic 文件）
- 历史记录通过比对 user_licenses 历史快照 + 审计字段实现
- 真正的 Ed25519 签名验证与外部授权服务对接在 P2 实施；MVP 阶段仅做格式校验
"""

import json
import logging
import hashlib
import platform
import socket
import uuid
import subprocess
import re
from datetime import datetime
from typing import Dict, Any, List, Optional

from sqlalchemy.orm import Session

from app.models.user import User
from app.models.license import UserLicense

logger = logging.getLogger(__name__)


# ===== 计划类型映射 =====
PLAN_LABELS = {
    "trial": "试用版",
    "personal": "个人版",
    "pro": "高级版",
    "enterprise": "企业版"
}


def _plan_label(plan: str) -> str:
    """获取计划类型的中文标签"""
    return PLAN_LABELS.get(plan, "未知")


def _get_hardware_uuid() -> str:
    """
    获取硬件 UUID（优先使用 wmic 获取稳定的主板 UUID，失败时回退到 mac 地址）
    """
    # 尝试使用 wmic 获取主板 UUID（Windows 平台稳定）
    if platform.system() == "Windows":
        try:
            result = subprocess.run(
                ["wmic", "csproduct", "get", "UUID"],
                capture_output=True,
                text=True,
                timeout=5
            )
            # 解析输出，格式为 "\n\nUUID\n\nXXXXXXXX-XXXX-XXXX-XXXX-XXXXXXXXXXXX\n\n"
            output = result.stdout.strip()
            # 去除 "UUID" 头部
            uuid_match = re.search(
                r'([0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12})',
                output
            )
            if uuid_match:
                return uuid_match.group(1)
        except Exception:
            pass

    # 回退到 mac 地址（macOS/Linux 或 wmic 失败时）
    try:
        mac = uuid.getnode()
        if (mac >> 40) % 2 == 0:  # 避免 multicast bit
            return f"{mac:012x}"
    except Exception:
        pass
    return "000000000000"


def _collect_machine_fingerprint() -> str:
    """
    采集本机机器指纹

    MVP 阶段采用轻量方案：
    - hostname + hardware_uuid（wmic 获取的稳定主板 UUID 或 mac 地址） + platform 信息
    - P2 实施时替换为 docs/license-system-design.md 第 4 章的 5 项硬件指纹
    """
    parts = []

    # 1. hostname
    try:
        parts.append(socket.gethostname() or "unknown-host")
    except Exception:
        parts.append("unknown-host")

    # 2. 硬件 UUID（优先主板 UUID，回退 mac 地址）
    parts.append(_get_hardware_uuid())

    # 3. platform 信息
    try:
        parts.append(platform.platform() or "unknown-platform")
    except Exception:
        parts.append("unknown-platform")

    raw = "|".join(parts)
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()[:32]


def _collect_hostname() -> str:
    """获取本机主机名（展示用，不参与指纹计算）"""
    try:
        return socket.gethostname() or "unknown-host"
    except Exception:
        return "unknown-host"


def _parse_features(raw: str) -> List[str]:
    """解析 features JSON 字符串，解析失败时返回空列表"""
    if not raw:
        return []
    try:
        data = json.loads(raw)
        return data if isinstance(data, list) else []
    except Exception:
        return []


def _ensure_license(db: Session, user: User) -> UserLicense:
    """
    确保 user 存在关联的 UserLicense 记录，不存在则自动创建空记录

    触发场景：
    - 老用户（v2 时期激活过许可）→ 迁移后 license 关系可能为 None
    - 新用户（v3 后注册）→ 首次访问许可面板时自动创建空记录
    - 重复调用幂等：若 license 已存在则直接返回
    """
    if user.license is None:
        lic = UserLicense(user_id=user.id)
        db.add(lic)
        db.flush()  # 写库但不 commit
        db.refresh(user)  # 刷新 user.license 关系
        logger.info(f"为用户 {user.id} 创建空白 UserLicense 记录 (id={lic.id})")
    return user.license


def _build_license_response(user: User) -> Dict[str, Any]:
    """
    将 user.license 关系记录打包为响应 dict
    - features 从 JSON 字符串解析回 list
    - 时间戳转 ISO 字符串
    - 当 user.license 为 None（未迁移老用户）时返回「未激活」默认值
    """
    if user.license is None:
        return {
            "license_key": "",
            "plan": "trial",
            "plan_label": _plan_label("trial"),
            "features": [],
            "issued_at": None,
            "expires_at": None,
            "activated_at": None,
            "status": "inactive",
            "source": "",
            "filename": "",
            # 机器指纹每次实时采集（不存库）
            "machine_fingerprint": _collect_machine_fingerprint(),
            "machine_hostname": _collect_hostname()
        }

    lic = user.license
    return {
        "license_key": lic.license_key or "",
        "plan": lic.license_plan or "trial",
        "plan_label": _plan_label(lic.license_plan or "trial"),
        "features": _parse_features(lic.license_features or ""),
        "issued_at": lic.license_issued_at.isoformat() if lic.license_issued_at else None,
        "expires_at": lic.license_expires_at.isoformat() if lic.license_expires_at else None,
        "activated_at": lic.license_activated_at.isoformat() if lic.license_activated_at else None,
        "status": lic.license_status or "inactive",
        "source": lic.license_source or "",
        "filename": lic.license_filename or "",
        # 机器指纹：激活后展示绑定值，未激活时实时采集
        "machine_fingerprint": lic.license_activated_machine or _collect_machine_fingerprint(),
        "machine_hostname": _collect_hostname()
    }


class LicenseService:
    """许可管理服务类"""

    @staticmethod
    def get_machine_fingerprint(db: Session, user: User) -> Dict[str, Any]:
        """
        获取本机机器指纹（用于 .req 请求文件导出）

        Returns:
            {
                "fingerprint": "abc123...",
                "hostname": "DESKTOP-XXX",
                "platform": "Windows-10-...",
                "generated_at": "2026-08-07T10:00:00"
            }
        """
        return {
            "fingerprint": _collect_machine_fingerprint(),
            "hostname": _collect_hostname(),
            "platform": platform.platform() or "",
            "generated_at": datetime.now().isoformat()
        }

    @staticmethod
    def get_license_status(db: Session, user: User) -> Dict[str, Any]:
        """
        获取当前用户的许可状态

        状态判定逻辑：
        - license_status == 'inactive'  → 未激活
        - license_status == 'active' && expires_at < now → 自动降级为 'expired'
        - license_status == 'active' && expires_at >= now → 正常
        - license_status in ('expired', 'revoked') → 已过期/已吊销
        """
        # 自动检查过期
        lic = user.license
        if lic and lic.license_status == "active" and lic.license_expires_at:
            if lic.license_expires_at < datetime.now():
                lic.license_status = "expired"
                db.commit()
                db.refresh(user)
                logger.info(f"用户 {user.id} 许可已过期，自动降级状态")

        return _build_license_response(user)

    @staticmethod
    def activate_online(db: Session, user: User, license_key: str) -> Dict[str, Any]:
        """
        在线激活（通过 license_key 调授权服务）

        MVP 阶段：
        - 校验 license_key 格式（X-XXX-XXXX-XXXX）
        - 自动签发 30 天试用许可（P0 阶段）
        - 绑定到当前机器指纹

        P2 实施：
        - 调授权服务 POST /api/license-server/heartbeat
        - 验证签名、有效期、机器指纹

        Raises:
            ValueError: 激活失败时
        """
        cleaned = license_key.strip().replace("-", "").replace(" ", "").upper()

        # 格式校验
        if len(cleaned) < 16 or len(cleaned) > 64:
            raise ValueError("许可密钥格式无效")

        # P0 试用模式：任何符合格式的密钥都签发 30 天试用
        # P2 实装后改为调外部授权服务
        now = datetime.now()
        expires_at = datetime(now.year + 1, now.month, now.day) if "PRO" in cleaned.upper() or "PERS" in cleaned.upper() else \
                     datetime(now.year, now.month + 1, now.day) if now.month < 12 else \
                     datetime(now.year + 1, 1, now.day)

        # 简单判断计划类型
        upper = cleaned.upper()
        if "ENT" in upper or "ENTER" in upper:
            plan = "enterprise"
        elif "PRO" in upper:
            plan = "pro"
        elif "PERS" in upper:
            plan = "personal"
        else:
            plan = "trial"

        # 功能开关
        features_map = {
            "trial": ["basic"],
            "personal": ["basic", "cabinet", "market"],
            "pro": ["basic", "cabinet", "market", "hpi", "export"],
            "enterprise": ["basic", "cabinet", "market", "hpi", "export", "api", "multi_user"]
        }

        # 写库：确保 UserLicense 存在并更新字段
        lic = _ensure_license(db, user)
        lic.license_key = license_key.strip()
        lic.license_plan = plan
        lic.license_features = json.dumps(features_map.get(plan, []), ensure_ascii=False)
        lic.license_issued_at = now
        lic.license_expires_at = expires_at
        lic.license_activated_at = now
        lic.license_status = "active"
        lic.license_source = "online"
        lic.license_filename = ""
        lic.license_activated_machine = _collect_machine_fingerprint()

        db.commit()
        db.refresh(user)

        logger.info(f"用户 {user.id} 在线激活成功，plan={plan}, expires_at={expires_at}")
        return _build_license_response(user)

    @staticmethod
    def import_offline(db: Session, user: User, filename: str, content: str) -> Dict[str, Any]:
        """
        离线导入（解析 .lic 文件内容）

        MVP 阶段：
        - .lic 文件内容为 JSON 字符串
        - 解析字段：license_key / plan / features / issued_at / expires_at
        - 绑定到当前机器指纹
        - 真正的 Ed25519 签名验证在 P1 实施

        Raises:
            ValueError: 解析失败时
        """
        try:
            lic_data = json.loads(content)
        except json.JSONDecodeError as e:
            raise ValueError(f"许可文件格式错误（需为 JSON）：{str(e)}")

        # 必需字段
        required = ["license_key", "plan", "issued_at", "expires_at"]
        for field in required:
            if field not in lic_data:
                raise ValueError(f"许可文件缺少必需字段：{field}")

        # 解析时间戳
        try:
            issued_at = datetime.fromisoformat(lic_data["issued_at"].replace("Z", "+00:00")).replace(tzinfo=None)
            expires_at = datetime.fromisoformat(lic_data["expires_at"].replace("Z", "+00:00")).replace(tzinfo=None)
        except Exception as e:
            raise ValueError(f"许可时间戳解析失败：{str(e)}")

        # 校验是否过期
        now = datetime.now()
        if expires_at < now:
            raise ValueError("许可文件已过期")

        # 校验计划
        plan = lic_data["plan"]
        if plan not in PLAN_LABELS:
            raise ValueError(f"未知授权类型：{plan}")

        # 写库：确保 UserLicense 存在并更新字段
        lic = _ensure_license(db, user)
        lic.license_key = lic_data["license_key"]
        lic.license_plan = plan
        lic.license_features = json.dumps(lic_data.get("features", []), ensure_ascii=False)
        lic.license_issued_at = issued_at
        lic.license_expires_at = expires_at
        lic.license_activated_at = now
        lic.license_status = "active"
        lic.license_source = "offline"
        lic.license_filename = filename
        lic.license_activated_machine = _collect_machine_fingerprint()

        db.commit()
        db.refresh(user)

        logger.info(f"用户 {user.id} 离线导入成功，filename={filename}, plan={plan}")
        return _build_license_response(user)

    @staticmethod
    def revoke_license(db: Session, user: User) -> Dict[str, Any]:
        """
        吊销当前许可（标记为 revoked，功能立即失效）
        """
        lic = user.license
        if lic is None or lic.license_status == "inactive":
            raise ValueError("当前未激活任何许可")

        lic.license_status = "revoked"
        db.commit()
        db.refresh(user)

        logger.info(f"用户 {user.id} 已吊销当前许可")
        return _build_license_response(user)

    @staticmethod
    def delete_history(db: Session, user: User) -> Dict[str, Any]:
        """
        删除许可记录（重置为出厂默认；物理删除 UserLicense 行）
        """
        lic = user.license
        if lic is not None:
            db.delete(lic)
            db.commit()
            db.refresh(user)
            logger.info(f"用户 {user.id} 已删除许可记录 (id={lic.id})")
        return _build_license_response(user)

    @staticmethod
    def get_history(db: Session, user: User) -> Dict[str, Any]:
        """
        获取许可历史记录

        MVP 阶段：仅返回当前激活的 1 条（基于 user_licenses）
        P1 实施：新建 license_history 表，完整记录每次激活/导入
        """
        items: List[Dict[str, Any]] = []
        lic = user.license

        if lic and lic.license_status in ("active", "expired", "revoked") and lic.license_key:
            items.append({
                "id": lic.id,
                "license_key": lic.license_key,
                "plan": lic.license_plan or "trial",
                "plan_label": _plan_label(lic.license_plan or "trial"),
                "filename": lic.license_filename or "",
                "source": lic.license_source or "",
                "issued_at": lic.license_issued_at.isoformat() if lic.license_issued_at else None,
                "expires_at": lic.license_expires_at.isoformat() if lic.license_expires_at else None,
                "activated_at": lic.license_activated_at.isoformat() if lic.license_activated_at else None,
                "status": lic.license_status or "inactive",
                "is_current": lic.license_status == "active",
                "machine_fingerprint": lic.license_activated_machine or ""
            })

        return {
            "items": items,
            "total": len(items)
        }
