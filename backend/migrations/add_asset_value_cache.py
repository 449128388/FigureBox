"""
添加资产市值缓存表（用于计算日涨跌）
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import create_engine, Column, Integer, Float, Date, DateTime, ForeignKey
from sqlalchemy.sql import func
from app.models.database import Base, SQLALCHEMY_DATABASE_URL

def upgrade():
    """创建asset_value_cache表"""
    engine = create_engine(SQLALCHEMY_DATABASE_URL)
    
    # 创建表
    from sqlalchemy import Table, MetaData
    metadata = MetaData()
    
    asset_value_cache = Table(
        'asset_value_cache',
        metadata,
        Column('id', Integer, primary_key=True, index=True),
        Column('user_id', Integer, ForeignKey('users.id'), nullable=False),
        Column('total_value', Float, nullable=False),
        Column('cache_date', Date, nullable=False),
        Column('created_at', DateTime(timezone=True), server_default=func.now()),
    )
    
    # 创建表
    metadata.create_all(engine, tables=[asset_value_cache])
    print("✅ asset_value_cache表创建成功")
    
    # 创建索引
    from sqlalchemy import Index
    Index('idx_asset_value_cache_user_date', 
          asset_value_cache.c.user_id, 
          asset_value_cache.c.cache_date).create(engine)
    print("✅ 索引创建成功")

def downgrade():
    """删除asset_value_cache表"""
    engine = create_engine(SQLALCHEMY_DATABASE_URL)
    
    from sqlalchemy import Table, MetaData
    metadata = MetaData()
    
    asset_value_cache = Table('asset_value_cache', metadata, autoload_with=engine)
    asset_value_cache.drop(engine)
    print("✅ asset_value_cache表删除成功")

if __name__ == "__main__":
    upgrade()
