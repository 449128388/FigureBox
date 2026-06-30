"""
为 exchange_rate_realtime 和 exchange_rate_history 表添加备注
（兼容已存在的表，通过 ALTER TABLE 添加注释）
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import create_engine, text
from app.models.database import Base, DATABASE_URL as SQLALCHEMY_DATABASE_URL


def upgrade():
    """为已存在的汇率表添加表和字段备注"""
    engine = create_engine(SQLALCHEMY_DATABASE_URL)

    with engine.connect() as conn:
        # 检查表是否存在
        result = conn.execute(text(
            "SELECT COUNT(*) FROM information_schema.tables "
            "WHERE table_schema = DATABASE() AND table_name = 'exchange_rate_realtime'"
        ))
        if result.scalar() == 0:
            print("⚠️ exchange_rate_realtime 表不存在，跳过")
            return

        # 为表添加备注
        conn.execute(text(
            "ALTER TABLE exchange_rate_realtime COMMENT = '最新汇率缓存表'"
        ))
        print("✅ exchange_rate_realtime 表备注已添加")

        # 为字段添加备注
        conn.execute(text(
            "ALTER TABLE exchange_rate_realtime MODIFY COLUMN id INT COMMENT '记录唯一标识ID'"
        ))
        conn.execute(text(
            "ALTER TABLE exchange_rate_realtime MODIFY COLUMN currency VARCHAR(10) NOT NULL COMMENT '币种代码：CNY/USD/JPY/EUR 等'"
        ))
        conn.execute(text(
            "ALTER TABLE exchange_rate_realtime MODIFY COLUMN rate_to_cny FLOAT NOT NULL COMMENT '相对人民币的汇率（1单位本币 = ? 人民币）'"
        ))
        conn.execute(text(
            "ALTER TABLE exchange_rate_realtime MODIFY COLUMN updated_at DATETIME COMMENT '最后更新时间'"
        ))
        print("✅ exchange_rate_realtime 字段备注已添加")

        # exchange_rate_history 表备注
        conn.execute(text(
            "ALTER TABLE exchange_rate_history COMMENT = '汇率历史记录表'"
        ))
        print("✅ exchange_rate_history 表备注已添加")

        conn.execute(text(
            "ALTER TABLE exchange_rate_history MODIFY COLUMN id INT COMMENT '记录唯一标识ID'"
        ))
        conn.execute(text(
            "ALTER TABLE exchange_rate_history MODIFY COLUMN currency VARCHAR(10) NOT NULL COMMENT '币种代码'"
        ))
        conn.execute(text(
            "ALTER TABLE exchange_rate_history MODIFY COLUMN rate_to_cny FLOAT NOT NULL COMMENT '相对人民币的汇率'"
        ))
        conn.execute(text(
            "ALTER TABLE exchange_rate_history MODIFY COLUMN record_date DATETIME COMMENT '记录时间'"
        ))
        conn.execute(text(
            "ALTER TABLE exchange_rate_history MODIFY COLUMN created_at DATETIME COMMENT '创建时间'"
        ))
        print("✅ exchange_rate_history 字段备注已添加")

        conn.commit()

    print("🎉 汇率表备注迁移完成")


if __name__ == "__main__":
    upgrade()
