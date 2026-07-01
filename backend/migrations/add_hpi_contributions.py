"""
HPI 走势表添加 in_cabinet_value 和 sold_value 字段
- 在柜贡献: 当前在柜手办按权重加权的当前市值贡献
- 已出贡献: 已出手办按权重加权的当前市值贡献
- 走势图: 展示两个拆分曲线（绿实线+灰虚线），Y轴 0~1000
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import create_engine, text
from app.models.database import DATABASE_URL as SQLALCHEMY_DATABASE_URL


def upgrade():
    engine = create_engine(SQLALCHEMY_DATABASE_URL)

    with engine.connect() as conn:
        # 检查 hpi_daily 表是否已有 in_cabinet_value 字段
        result = conn.execute(text("""
            SELECT COUNT(*) FROM information_schema.COLUMNS
            WHERE table_schema = DATABASE()
              AND table_name = 'hpi_daily'
              AND column_name = 'in_cabinet_value'
        """)).scalar()

        if result == 0:
            print("→ 添加 hpi_daily.in_cabinet_value 字段")
            conn.execute(text("""
                ALTER TABLE hpi_daily
                ADD COLUMN in_cabinet_value FLOAT DEFAULT 0
                COMMENT '在柜手办加权市值贡献(走势图绿色实线)'
                AFTER sold_down_count
            """))
        else:
            print("✓ hpi_daily.in_cabinet_value 已存在")

        result = conn.execute(text("""
            SELECT COUNT(*) FROM information_schema.COLUMNS
            WHERE table_schema = DATABASE()
              AND table_name = 'hpi_daily'
              AND column_name = 'sold_value'
        """)).scalar()

        if result == 0:
            print("→ 添加 hpi_daily.sold_value 字段")
            conn.execute(text("""
                ALTER TABLE hpi_daily
                ADD COLUMN sold_value FLOAT DEFAULT 0
                COMMENT '已出手办加权市值贡献(走势图灰色虚线)'
                AFTER in_cabinet_value
            """))
        else:
            print("✓ hpi_daily.sold_value 已存在")

        conn.commit()
        print("✅ hpi_daily 拆分贡献字段迁移完成")


if __name__ == "__main__":
    upgrade()
