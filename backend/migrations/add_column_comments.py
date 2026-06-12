
"""
数据库迁移脚本：为所有现有表字段添加 COMMENT 注释

从 SQLAlchemy 模型定义中读取 comment 参数，使用 INFORMATION_SCHEMA 获取
数据库现有字段类型，通过 ALTER TABLE MODIFY COLUMN 安全添加注释。
不会改变字段的现有类型、默认值、自增等属性。

执行方式：
  docker exec figurebox-backend-1 python migrations/add_column_comments.py
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import text, inspect
from app.models.database import engine, Base

# 导入所有模型，确保 Base.metadata 包含所有表
from app.models.user import User
from app.models.figure import Figure
from app.models.order import Order
from app.models.sold_order import SoldOrder
from app.models.tag import Tag
from app.models.asset import (
    AssetPriceHistory, AssetAlert, AssetTransaction,
    StockIndexCache, StockIndexHistory, AssetValueCache,
    UserSettings, OrderTransaction, PlasticIndexHistory
)
from app.models.user_asset_snapshot import UserAssetSnapshot
from app.models.holding_snapshot import HoldingSnapshot, HoldingSnapshotSummary


# 获取数据库名称
DATABASE_NAME = os.getenv("MYSQL_DATABASE", "figurebox")


def add_column_comments():
    """为所有表字段添加注释"""
    inspector = inspect(engine)

    # 获取所有已存在的表
    existing_tables = set(inspector.get_table_names())

    # 先查询 INFORMATION_SCHEMA 获取字段的完整定义信息
    with engine.connect() as connection:
        # 获取所有字段的详细信息（类型、是否可为空、默认值、是否自增、字符集等）
        schema_sql = text("""
            SELECT TABLE_NAME, COLUMN_NAME, COLUMN_TYPE,
                   IS_NULLABLE, COLUMN_DEFAULT, EXTRA,
                   COLUMN_COMMENT, CHARACTER_SET_NAME,
                   COLLATION_NAME
            FROM INFORMATION_SCHEMA.COLUMNS
            WHERE TABLE_SCHEMA = :db_name
        """)
        result = connection.execute(schema_sql, {"db_name": DATABASE_NAME})
        db_columns = {}
        for row in result:
            table = row[0]
            col = row[1]
            if table not in db_columns:
                db_columns[table] = {}
            db_columns[table][col] = {
                "COLUMN_TYPE": row[2],
                "IS_NULLABLE": row[3],
                "COLUMN_DEFAULT": row[4],
                "EXTRA": row[5] or "",
                "COLUMN_COMMENT": row[6] or "",
                "CHARACTER_SET_NAME": row[7],
                "COLLATION_NAME": row[8],
            }

    total_updated = 0
    total_skipped = 0
    total_errors = []

    metadata = Base.metadata

    with engine.connect() as connection:
        for table_name, table in metadata.tables.items():
            if table_name not in existing_tables:
                print(f"  - 跳过 {table_name}（表不存在）")
                continue

            print(f"\n{'='*50}")
            print(f"表: {table_name}")

            table_db_cols = db_columns.get(table_name, {})

            for column in table.columns:
                col_name = column.name

                if col_name not in table_db_cols:
                    print(f"  - 跳过 {col_name}（数据库中不存在）")
                    continue

                comment = column.comment
                if not comment:
                    continue

                db_col = table_db_cols[col_name]
                existing_comment = db_col["COLUMN_COMMENT"]

                # 如果注释已存在且相同，跳过
                if existing_comment == comment:
                    total_skipped += 1
                    continue

                # 转义注释中的单引号
                safe_comment = comment.replace("'", "\\'")

                # 从数据库获取完整的列类型和属性
                col_type = db_col["COLUMN_TYPE"]
                nullable = "NULL" if db_col["IS_NULLABLE"] == "YES" else "NOT NULL"
                extra = db_col["EXTRA"]

                # 需要过滤掉 MySQL 内部标记，只保留对 MODIFY COLUMN 有效的部分
                # - DEFAULT_GENERATED: 内部标记，不能出现在 MODIFY COLUMN 中
                # - on update CURRENT_TIMESTAMP: 需要保留
                has_default_generated = "DEFAULT_GENERATED" in extra.upper()
                valid_extras = []
                for part in extra.split():
                    part = part.strip()
                    if part and part.upper() != "DEFAULT_GENERATED":
                        valid_extras.append(part)
                extra_str = f" {' '.join(valid_extras)}" if valid_extras else ""

                # 处理默认值
                default_str = ""
                if has_default_generated:
                    # DEFAULT_GENERATED 表示默认值由 MySQL 自动生成（如 CURRENT_TIMESTAMP）
                    # 不指定 DEFAULT，MySQL 会保留现有默认值定义
                    default_str = ""
                elif db_col["COLUMN_DEFAULT"] is not None:
                    default_val = db_col["COLUMN_DEFAULT"]
                    if isinstance(default_val, str):
                        default_str = f" DEFAULT '{default_val}'"
                    else:
                        default_str = f" DEFAULT {default_val}"

                # 拼接字符集信息（仅 varchar/char/text 类型需要）
                charset_str = ""
                if db_col["CHARACTER_SET_NAME"] and any(t in col_type.upper() for t in ["VARCHAR", "CHAR", "TEXT"]):
                    charset_str = f" CHARACTER SET {db_col['CHARACTER_SET_NAME']} COLLATE {db_col['COLLATION_NAME']}"

                sql = (
                    f"ALTER TABLE {table_name} "
                    f"MODIFY COLUMN {col_name} {col_type}{charset_str} "
                    f"{nullable}{default_str}{extra_str} "
                    f"COMMENT '{safe_comment}'"
                )

                try:
                    connection.execute(text(sql))
                    print(f"  ✅ {col_name}")
                    total_updated += 1
                except Exception as e:
                    err_msg = f"  ❌ {col_name}: {e}"
                    print(err_msg)
                    total_errors.append(err_msg)

        connection.commit()

    print(f"\n{'='*50}")
    print(f"操作完成！")
    print(f"  已更新注释: {total_updated} 个字段")
    print(f"  已跳过:     {total_skipped} 个字段（注释已存在）")
    if total_errors:
        print(f"  失败:       {len(total_errors)} 个字段")
        for err in total_errors:
            print(f"    {err}")
    else:
        print(f"  失败:       0")


if __name__ == "__main__":
    print("=" * 50)
    print("开始为数据库表字段添加 COMMENT 注释")
    print("=" * 50)

    add_column_comments()
