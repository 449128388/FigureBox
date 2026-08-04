"""
backup_record.py - 备份历史记录 ORM 模型

功能说明：
- 记录每次备份（手动 / 自动）的元数据
- 磁盘文件本体存到 storage/backups/{user_id}/{ts}.json（持久化到宿主机 backups_data/）
- 本表只存指针 + 元数据，不存文件内容
"""
from sqlalchemy import Column, Integer, String, BigInteger, DateTime, Index, Enum
from sqlalchemy.sql import func

from app.models.database import Base


class BackupRecord(Base):
    """
    备份历史记录表

    字段说明：
    - id              主键
    - user_id         所属用户
    - filename        文件名（含 .json 后缀），用于 Content-Disposition
    - file_path       容器内磁盘绝对路径（持久化到宿主机 backups_data/）
    - size_bytes      文件大小
    - record_count    备份包含的 figures 数量
    - backup_type     备份类型：auto（自动）/ manual（手动）
    - created_at      备份创建时间（带时区）

    索引：
    - (user_id, created_at desc) 加速历史列表查询
    """
    __tablename__ = "backup_records"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True, comment="备份记录唯一标识ID")
    user_id = Column(Integer, nullable=False, comment="所属用户ID")
    filename = Column(String(255), nullable=False, comment="备份文件名（含 .json）")
    file_path = Column(String(512), nullable=False, comment="磁盘文件绝对路径（容器内）")
    size_bytes = Column(BigInteger, nullable=False, default=0, comment="文件大小（字节）")
    record_count = Column(Integer, nullable=False, default=0, comment="备份包含的 figures 数量")
    backup_type = Column(
        Enum("auto", "manual", name="backup_type_enum"),
        nullable=False,
        default="manual",
        comment="备份类型：auto=自动 / manual=手动"
    )
    created_at = Column(
        DateTime, nullable=False, server_default=func.now(), comment="备份创建时间"
    )

    __table_args__ = (
        Index("idx_user_created", "user_id", "created_at"),
    )
