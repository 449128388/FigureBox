"""
添加汇率缓存表和历史表
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import create_engine, Column, Integer, Float, String, DateTime, TIMESTAMP, Index, text, func
from app.models.database import Base, DATABASE_URL as SQLALCHEMY_DATABASE_URL


def upgrade():
    """创建 exchange_rate_realtime 和 exchange_rate_history 表"""
    engine = create_engine(SQLALCHEMY_DATABASE_URL)

    from sqlalchemy import Table, MetaData
    metadata = MetaData()

    # 最新汇率缓存表
    realtime_table = Table(
        'exchange_rate_realtime',
        metadata,
        Column('id', Integer, primary_key=True, index=True, comment='记录唯一标识ID'),
        Column('currency', String(10), nullable=False, unique=True, comment='币种代码：CNY/USD/JPY/EUR 等'),
        Column('rate_to_cny', Float, nullable=False, comment='相对人民币的汇率（1单位本币 = ? 人民币）'),
        Column('updated_at', DateTime(timezone=True), server_default=text("CURRENT_TIMESTAMP"), onupdate=func.now(), comment='最后更新时间'),
        mysql_engine='InnoDB',
        mysql_charset='utf8mb4',
        mysql_comment='最新汇率缓存表'
    )

    # 汇率历史记录表
    history_table = Table(
        'exchange_rate_history',
        metadata,
        Column('id', Integer, primary_key=True, index=True, comment='记录唯一标识ID'),
        Column('currency', String(10), nullable=False, comment='币种代码'),
        Column('rate_to_cny', Float, nullable=False, comment='相对人民币的汇率'),
        Column('record_date', DateTime(timezone=True), server_default=text("CURRENT_TIMESTAMP"), comment='记录时间'),
        Column('created_at', DateTime(timezone=True), server_default=text("CURRENT_TIMESTAMP"), comment='创建时间'),
        mysql_engine='InnoDB',
        mysql_charset='utf8mb4',
        mysql_comment='汇率历史记录表'
    )

    # 创建表
    metadata.create_all(engine, tables=[realtime_table, history_table])
    print("✅ exchange_rate_realtime 和 exchange_rate_history 表创建成功")

    # 创建索引（忽略已存在的索引错误）
    try:
        from sqlalchemy import Index as SqlIndex
        SqlIndex('idx_realtime_currency', realtime_table.c.currency).create(engine)
        SqlIndex('idx_history_currency_date', history_table.c.currency, history_table.c.record_date).create(engine)
        print("✅ 索引创建成功")
    except Exception as e:
        if "Duplicate key name" in str(e):
            print("ℹ️ 索引已存在，跳过创建")
        else:
            print(f"⚠️ 索引创建异常（非致命）: {e}")


def downgrade():
    """删除汇率表"""
    engine = create_engine(SQLALCHEMY_DATABASE_URL)

    from sqlalchemy import Table, MetaData
    metadata = MetaData()

    realtime_table = Table('exchange_rate_realtime', metadata, autoload_with=engine)
    realtime_table.drop(engine)

    history_table = Table('exchange_rate_history', metadata, autoload_with=engine)
    history_table.drop(engine)

    print("✅ exchange_rate_realtime 和 exchange_rate_history 表删除成功")


if __name__ == "__main__":
    upgrade()
