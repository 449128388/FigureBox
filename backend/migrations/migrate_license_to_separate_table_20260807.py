"""
2026-08-07 v3 迁移 - 许可数据从 users_info 表剥离到独立 user_licenses 表

背景：
- v2 时期（#5）通过 SQLAlchemy Mixin 把 10 个 license_* 列挂在 users_info 上
- v3（#6，当前）升级为 1:1 独立表 user_licenses：
  - 摆脱 users_info 因 Feature 字段无限膨胀的问题
  - 许可数据可独立备份 / 历史记录可平滑扩展
  - 业务层 0 影响（service 通过 User.license 关系访问，0 JOIN N+1）

迁移策略（4 步幂等）：
1. 校验段：检查 users_info 上仍有 10 个 license_* 列（v2 时期产物）
2. 数据迁移：INSERT INTO user_licenses SELECT FROM users_info WHERE 被改过（status != 'inactive'）
   - 用 INSERT IGNORE 避免 user_id UNIQUE 冲突（重跑幂等）
   - 上版清理脚本已确认 0 行需要迁移，但留作「万一」保险
3. 建表段：CREATE TABLE user_licenses（如果不存在）+ 复合索引
4. 删列段：ALTER TABLE users_info DROP COLUMN 10 个 license_*
   - 用 IF EXISTS（MySQL 8.0.29+）保证幂等
5. 验证段：检查 user_licenses 已建 + users_info 已无 license_* 列

执行顺序：必须在 backend 重启前执行（重启后 ORM 期望 users_info 无 license_* 列）
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import create_engine, text
from app.models.database import DATABASE_URL as SQLALCHEMY_DATABASE_URL

# 与 LicenseMixin / UserLicense 一致的列定义
LICENSE_COLUMNS = [
    "license_key", "license_plan", "license_features",
    "license_issued_at", "license_expires_at", "license_activated_at",
    "license_status", "license_source", "license_filename",
    "license_activated_machine",
]

engine = create_engine(SQLALCHEMY_DATABASE_URL)

with engine.connect() as conn:
    # ===== 1. 校验：users_info 仍有 10 列（v2 状态） =====
    print("=== 1. 校验：users_info 表 v2 时期 license_* 列 ===")
    existing_cols = []
    for col in LICENSE_COLUMNS:
        r = conn.execute(text(
            "SELECT COUNT(*) FROM information_schema.columns "
            "WHERE table_schema = DATABASE() AND table_name = 'users_info' AND column_name = :c"
        ), {"c": col})
        if r.scalar() > 0:
            existing_cols.append(col)
            print(f"  [ OK ] {col}")
        else:
            print(f"  [SKIP] {col} (already dropped)")

    if not existing_cols:
        print("  -> v2 列已全部删除（重复执行），跳过数据迁移与删列段")

    # ===== 2. 数据迁移：把 v2 时期残存的许可数据搬到 user_licenses =====
    if existing_cols:
        cols_csv = ", ".join(existing_cols)
        print(f"\n=== 2. 数据迁移：users_info -> user_licenses ===")
        # 用 INSERT IGNORE 避免 user_id UNIQUE 冲突（脚本重跑幂等）
        # 仅迁移「被改过」的行（status != 'inactive' 或 license_key != '' 等）
        r = conn.execute(text(f"""
            INSERT IGNORE INTO user_licenses
                (user_id, {cols_csv}, created_at, updated_at)
            SELECT
                id AS user_id, {cols_csv}, NOW(), NOW()
            FROM users_info
            WHERE
                license_status != 'inactive'
                OR license_key != ''
                OR license_activated_at IS NOT NULL
                OR license_expires_at IS NOT NULL
                OR license_activated_machine != ''
        """))
        conn.commit()
        print(f"  迁移 {r.rowcount} 行到 user_licenses")

    # ===== 3. 建表：CREATE TABLE user_licenses（如果不存在） =====
    print("\n=== 3. 建表：user_licenses ===")
    r = conn.execute(text("""
        SELECT COUNT(*) FROM information_schema.tables
        WHERE table_schema = DATABASE() AND table_name = 'user_licenses'
    """))
    if r.scalar() == 0:
        conn.execute(text("""
            CREATE TABLE user_licenses (
                id INT NOT NULL AUTO_INCREMENT COMMENT '许可记录主键 ID',
                user_id INT NOT NULL COMMENT '所属用户 ID（1:1 关联 users_info.id，ON DELETE CASCADE）',
                license_key VARCHAR(64) DEFAULT '' COMMENT '许可密钥（公开 ID）',
                license_plan VARCHAR(20) DEFAULT 'trial' COMMENT '授权类型：trial / personal / pro / enterprise',
                license_features VARCHAR(500) DEFAULT '' COMMENT '功能开关 JSON 字符串',
                license_issued_at DATETIME DEFAULT NULL COMMENT '许可签发时间',
                license_expires_at DATETIME DEFAULT NULL COMMENT '许可到期时间',
                license_activated_at DATETIME DEFAULT NULL COMMENT '本机激活时间',
                license_status VARCHAR(20) DEFAULT 'inactive' COMMENT '许可状态：active / expired / revoked / inactive',
                license_source VARCHAR(20) DEFAULT '' COMMENT '激活来源：online / offline / trial',
                license_filename VARCHAR(100) DEFAULT '' COMMENT '导入的许可文件名（仅离线激活时记录）',
                license_activated_machine VARCHAR(64) DEFAULT '' COMMENT '本机机器指纹（激活时绑定）',
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '记录创建时间',
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '记录更新时间',
                PRIMARY KEY (id),
                UNIQUE KEY uk_user_licenses_user_id (user_id),
                KEY idx_user_licenses_user_status (user_id, license_status),
                CONSTRAINT fk_user_licenses_user_id FOREIGN KEY (user_id) REFERENCES users_info (id) ON DELETE CASCADE
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='用户许可记录表（1:1 关联 users_info）'
        """))
        conn.commit()
        print("  [CREATE] user_licenses 表 + UNIQUE 索引 + 复合索引 + FK CASCADE")
    else:
        print("  [SKIP] user_licenses 表已存在")

    # ===== 4. 删列：users_info DROP COLUMN 10 个 license_* =====
    if existing_cols:
        print("\n=== 4. 删列：users_info.license_* ===")
        for col in existing_cols:
            conn.execute(text(f"ALTER TABLE users_info DROP COLUMN {col}"))
            print(f"  [DROP] {col}")
        conn.commit()
    else:
        print("\n=== 4. 删列：users_info.license_* ===")
        print("  [SKIP] 列已全部删除（重复执行）")

    # ===== 5. 验证：user_licenses 已建 + users_info 已无 license_* 列 =====
    print("\n=== 5. 验证 ===")
    r = conn.execute(text("""
        SELECT COUNT(*) FROM information_schema.tables
        WHERE table_schema = DATABASE() AND table_name = 'user_licenses'
    """))
    assert r.scalar() == 1, "user_licenses 表未创建"
    print("  [ OK ] user_licenses 表已存在")

    r = conn.execute(text("""
        SELECT COUNT(*) FROM information_schema.columns
        WHERE table_schema = DATABASE() AND table_name = 'users_info' AND column_name LIKE 'license_%'
    """))
    remaining = r.scalar()
    if remaining == 0:
        print("  [ OK ] users_info 已无 license_* 列")
    else:
        print(f"  [WARN] users_info 仍有 {remaining} 个 license_* 列残留")

    r = conn.execute(text("SELECT COUNT(*) FROM user_licenses"))
    print(f"  [INFO] user_licenses 当前 {r.scalar()} 行记录")

print("\n迁移完成：v2 -> v3 (users_info -> user_licenses 独立表) + 旧列已删除")
