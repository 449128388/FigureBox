"""
auto_backup_scheduler.py - 自动备份调度器

功能说明：
- 每 1 小时扫描所有 auto_backup_enabled=True 的用户
- 按各自 auto_backup_frequency（daily/weekly/monthly）+ last_auto_backup_at 判断是否到期
- 到期则调 BackupService.export_backup → 落盘 → 写 backup_records → 更新 last_auto_backup_at → enforce_retain
- 单用户失败不影响其他用户
- 应用启动时立即执行一次（让首次开启自动备份的用户立即看到结果）

频率定义：
- daily   : 24 小时（86400 秒）
- weekly  : 7 天（604800 秒）
- monthly : 30 天（2592000 秒，按自然月近似）
"""
import logging
from datetime import datetime, timedelta
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from pytz import timezone
from sqlalchemy.orm import Session

from app.models.database import SessionLocal
from app.models.user import User
from app.services.user_profile_service.backup_service import BackupService
from app.services.user_profile_service.backup_service.backup_file_service import BackupFileService
from app.services.user_profile_service.backup_service.backup_record_service import BackupRecordService

logger = logging.getLogger(__name__)
BEIJING_TZ = timezone("Asia/Shanghai")

# 频率到秒数的映射
FREQUENCY_SECONDS = {
    "daily": 24 * 60 * 60,
    "weekly": 7 * 24 * 60 * 60,
    "monthly": 30 * 24 * 60 * 60,
}


class AutoBackupScheduler:
    """自动备份调度器"""

    def __init__(self):
        self._scheduler: BackgroundScheduler | None = None

    def start(self):
        """启动调度器：每 1 小时扫描一次 + 启动后立即执行一次"""
        if self._scheduler and self._scheduler.running:
            logger.warning("AutoBackupScheduler 已在运行，跳过重复启动")
            return

        self._scheduler = BackgroundScheduler(timezone=BEIJING_TZ)

        # 主任务：每 1 小时跑一次
        self._scheduler.add_job(
            func=self._check_and_run,
            trigger=IntervalTrigger(hours=1, timezone=BEIJING_TZ),
            id='auto_backup_check',
            name='自动备份扫描（每小时）',
            replace_existing=True,
            next_run_time=datetime.now(BEIJING_TZ)  # 启动时立即执行一次
        )

        self._scheduler.start()
        logger.info("自动备份调度器已启动：每 1 小时扫描一次，启动时立即执行一次")

    def stop(self):
        """停止调度器"""
        if self._scheduler and self._scheduler.running:
            self._scheduler.shutdown()
            logger.info("自动备份调度器已停止")

    def _check_and_run(self):
        """
        扫描所有启用自动备份的用户，对到期的用户执行备份

        流程：
        1. 查 auto_backup_enabled=True 的所有用户
        2. 逐用户判断 _should_run(user)
        3. 到期则 _run_for_user(user)
        4. 异常隔离：单用户失败 log error 继续
        """
        db: Session = SessionLocal()
        try:
            users = db.query(User).filter(User.auto_backup_enabled == True).all()  # noqa: E712
            logger.info(f"[自动备份] 扫描到 {len(users)} 个启用用户")

            success = 0
            failed = 0
            skipped = 0
            for user in users:
                try:
                    if not self._should_run(user):
                        skipped += 1
                        continue
                    if self._run_for_user(db, user):
                        success += 1
                    else:
                        failed += 1
                except Exception as e:
                    failed += 1
                    logger.error(f"[自动备份] 用户 {user.id} 备份失败: {e}", exc_info=True)
                    continue

            logger.info(
                f"[自动备份] 扫描完成 - 成功 {success} / 跳过 {skipped} / 失败 {failed}"
            )
        except Exception as e:
            logger.error(f"[自动备份] 扫描任务执行失败: {e}", exc_info=True)
        finally:
            db.close()

    def _should_run(self, user: User) -> bool:
        """
        判断某用户是否到期

        规则：
        - last_auto_backup_at 为 NULL → 立即执行（首次开启）
        - last_auto_backup_at 距今 ≥ frequency 间隔 → 到期
        - 否则 → 未到期
        """
        frequency = user.auto_backup_frequency or "weekly"
        interval = FREQUENCY_SECONDS.get(frequency)
        if interval is None:
            logger.warning(f"用户 {user.id} 的频率 '{frequency}' 不在白名单，跳过")
            return False

        if user.last_auto_backup_at is None:
            return True

        # DB 读出的 DateTime 可能是 offset-naive，需统一为带时区（北京时间）后再相减
        last_at = user.last_auto_backup_at
        if last_at.tzinfo is None:
            last_at = BEIJING_TZ.localize(last_at)
        elapsed = (datetime.now(BEIJING_TZ) - last_at).total_seconds()
        return elapsed >= interval

    def _run_for_user(self, db: Session, user: User) -> bool:
        """
        对单个用户执行自动备份

        完整流程：
        1. BackupService.export_backup → 拿 json_str
        2. BackupFileService.save_to_disk → 落盘 + 拿 file_path / size / count
        3. BackupRecordService.create_record(type='auto')
        4. 更新 user.last_auto_backup_at = now()
        5. BackupRecordService.enforce_retain(retain=user.auto_backup_retain)
        6. commit
        """
        logger.info(f"[自动备份] 用户 {user.id}（{user.username}）开始自动备份")

        # 1. 生成 JSON
        result = BackupService.export_backup(db)
        json_str = result["json_str"]
        filename = result["filename"]

        # 2. 落盘
        file_path, size_bytes, record_count = BackupFileService.save_to_disk(
            user_id=user.id,
            json_str=json_str
        )

        # 3. 写记录
        BackupRecordService.create_record(
            db=db,
            user_id=user.id,
            filename=filename,
            file_path=file_path,
            size_bytes=size_bytes,
            record_count=record_count,
            backup_type="auto"
        )

        # 4. 更新 last_auto_backup_at
        user.last_auto_backup_at = datetime.now(BEIJING_TZ)
        db.commit()
        db.refresh(user)

        # 5. 保留份数清理
        retain = int(user.auto_backup_retain or 0)
        deleted = BackupRecordService.enforce_retain(db, user.id, retain)

        logger.info(
            f"[自动备份] 用户 {user.id} 完成 - {record_count} 条记录, "
            f"{size_bytes/1024:.1f} KB, 清理 {deleted} 条旧备份"
        )
        return True


# 全局调度器实例
auto_backup_scheduler = AutoBackupScheduler()


def start_scheduler():
    """启动调度器（用于应用启动时调用）"""
    auto_backup_scheduler.start()


def stop_scheduler():
    """停止调度器（用于应用关闭时调用）"""
    auto_backup_scheduler.stop()
