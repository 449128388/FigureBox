"""
添加展示分类排除表

迁移内容：
1. 创建 cabinet_figure_exclusions 表
2. 添加 user_id + figure_id + cabinet_type 联合唯一键

表结构说明：
- cabinet_figure_exclusions：记录用户手动将手办从展示分类中排除的记录
- user_id + figure_id + cabinet_type 作为联合唯一键
- 被排除的手办在对应分类的自动统计中不再出现

执行方式：
- Docker 环境：进入容器后执行 python migrations/add_cabinet_exclusion_table.py
"""

import sys
import os

# 添加 backend 目录到路径
backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, backend_dir)

from sqlalchemy import create_engine, text, inspect
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

# 加载环境变量
load_dotenv(os.path.join(backend_dir, '.env'))

# 数据库连接字符串
DATABASE_URL = os.getenv("DATABASE_URL", "mysql+pymysql://admin:password@localhost:3306/figurebox")


def migrate():
    """执行数据库迁移"""
    print(f"连接到数据库...")
    engine = create_engine(DATABASE_URL)
    SessionLocal = sessionmaker(bind=engine)
    db = SessionLocal()

    try:
        # 检查表是否已存在
        inspector = inspect(engine)
        existing_tables = inspector.get_table_names()

        if 'cabinet_figure_exclusions' in existing_tables:
            print("⚠️ cabinet_figure_exclusions 表已存在，跳过创建")
        else:
            # 创建 cabinet_figure_exclusions 表
            print("正在创建 cabinet_figure_exclusions 表...")
            db.execute(text("""
                CREATE TABLE cabinet_figure_exclusions (
                    id BIGINT AUTO_INCREMENT PRIMARY KEY COMMENT '记录唯一标识ID',
                    user_id INT NOT NULL COMMENT '用户ID',
                    figure_id INT NOT NULL COMMENT '手办ID',
                    cabinet_type VARCHAR(32) NOT NULL COMMENT '分类标识: star,new,fix,air,dup,wait,maker',
                    source_cabinet VARCHAR(32) DEFAULT NULL COMMENT '触发移出的源分类',
                    exclude_reason VARCHAR(255) DEFAULT NULL COMMENT '移出原因（用户可选填）',
                    excluded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '移出时间',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
                    UNIQUE KEY uk_user_figure_cabinet (user_id, figure_id, cabinet_type),
                    KEY idx_user_cabinet (user_id, cabinet_type),
                    KEY idx_figure (user_id, figure_id)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='展示分类手动排除表'
            """))
            db.commit()
            print("✅ cabinet_figure_exclusions 表创建成功")

        print("🎉 迁移完成")
    except Exception as e:
        print(f"❌ 迁移失败: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == '__main__':
    migrate()
