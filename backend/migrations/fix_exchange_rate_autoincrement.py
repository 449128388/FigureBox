"""
修复 exchange_rate_realtime 和 exchange_rate_history 表 id 字段缺少 AUTO_INCREMENT

根因：迁移脚本使用 Table() 定义时未指定 autoincrement=True，导致
      MySQL 中 id 列为 int NOT NULL 而非 int NOT NULL AUTO_INCREMENT
      → INSERT 时报错 "Field 'id' doesn't have a default value"
      → 汇率写入失败 → 数据库连接报错 → 502 Bad Gateway
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import create_engine, text
from app.models.database import DATABASE_URL as SQLALCHEMY_DATABASE_URL


def upgrade():
    """为 exchange_rate 表的 id 字段添加 AUTO_INCREMENT"""
    engine = create_engine(SQLALCHEMY_DATABASE_URL)

    with engine.connect() as conn:
        # 检查 exchange_rate_realtime 表是否存在
        result = conn.execute(text(
            "SELECT COUNT(*) FROM information_schema.tables "
            "WHERE table_schema = DATABASE() AND table_name = 'exchange_rate_realtime'"
        ))
        if result.scalar() > 0:
            # 检查 id 是否已有 AUTO_INCREMENT
            result = conn.execute(text(
                "SELECT COUNT(*) FROM information_schema.columns "
                "WHERE table_schema = DATABASE() AND table_name = 'exchange_rate_realtime' "
                "AND column_name = 'id' AND extra LIKE '%auto_increment%'"
            ))
            if result.scalar() == 0:
                conn.execute(text(
                    "ALTER TABLE exchange_rate_realtime MODIFY COLUMN id INT NOT NULL AUTO_INCREMENT"
                ))
                print("✅ exchange_rate_realtime.id 已添加 AUTO_INCREMENT")
            else:
                print("ℹ️ exchange_rate_realtime.id 已有 AUTO_INCREMENT，跳过")
        else:
            print("ℹ️ exchange_rate_realtime 表不存在，跳过")

        # 检查 exchange_rate_history 表
        result = conn.execute(text(
            "SELECT COUNT(*) FROM information_schema.tables "
            "WHERE table_schema = DATABASE() AND table_name = 'exchange_rate_history'"
        ))
        if result.scalar() > 0:
            result = conn.execute(text(
                "SELECT COUNT(*) FROM information_schema.columns "
                "WHERE table_schema = DATABASE() AND table_name = 'exchange_rate_history' "
                "AND column_name = 'id' AND extra LIKE '%auto_increment%'"
            ))
            if result.scalar() == 0:
                conn.execute(text(
                    "ALTER TABLE exchange_rate_history MODIFY COLUMN id INT NOT NULL AUTO_INCREMENT"
                ))
                print("✅ exchange_rate_history.id 已添加 AUTO_INCREMENT")
            else:
                print("ℹ️ exchange_rate_history.id 已有 AUTO_INCREMENT，跳过")
        else:
            print("ℹ️ exchange_rate_history 表不存在，跳过")

        conn.commit()

    print("✅ 汇率表 AUTO_INCREMENT 修复完成")


if __name__ == "__main__":
    upgrade()
