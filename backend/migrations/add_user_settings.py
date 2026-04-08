"""
添加用户设置表（年度手办消费上限等）
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import create_engine, Column, Integer, Float, DateTime, ForeignKey
from sqlalchemy.sql import func
from app.models.database import Base, SQLALCHEMY_DATABASE_URL

def upgrade():
    """创建user_settings表"""
    engine = create_engine(SQLALCHEMY_DATABASE_URL)
    
    # 创建表
    from sqlalchemy import Table, MetaData
    metadata = MetaData()
    
    user_settings = Table(
        'user_settings',
        metadata,
        Column('id', Integer, primary_key=True, index=True),
        Column('user_id', Integer, ForeignKey('users.id'), nullable=False, unique=True),
        Column('annual_spending_limit', Float, default=0),
        Column('updated_at', DateTime(timezone=True), server_default=func.now(), onupdate=func.now()),
    )
    
    # 创建表
    metadata.create_all(engine, tables=[user_settings])
    print("✅ user_settings表创建成功")
    
    # 创建索引
    from sqlalchemy import Index
    Index('idx_user_settings_user_id', 
          user_settings.c.user_id).create(engine)
    print("✅ 索引创建成功")

def downgrade():
    """删除user_settings表"""
    engine = create_engine(SQLALCHEMY_DATABASE_URL)
    
    from sqlalchemy import Table, MetaData
    metadata = MetaData()
    
    user_settings = Table('user_settings', metadata, autoload_with=engine)
    user_settings.drop(engine)
    print("✅ user_settings表删除成功")

if __name__ == "__main__":
    upgrade()
