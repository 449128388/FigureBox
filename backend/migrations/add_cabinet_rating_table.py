"""
添加收藏柜喜爱度评分表

迁移内容：
1. 创建 cabinet_ratings 表
2. 添加 user_id + figure_id + cabinet_type 联合唯一键
3. 添加复合索引

表结构说明：
- cabinet_ratings：用户在手办在每个收藏柜中的喜爱度评分
- user_id + figure_id + cabinet_type 作为联合唯一键
- rating 1-5 星

联合唯一键说明：
- 同一个用户、同一个手办、在同一个收藏柜中只能有一个评分
- 不同收藏柜中可以对同一个手办设置不同评分

执行方式：
- 开发环境：python backend/migrations/add_cabinet_rating_table.py
- Docker 环境：进入容器后执行 python migrations/add_cabinet_rating_table.py
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

        if 'cabinet_ratings' in existing_tables:
            print("⚠️ cabinet_ratings 表已存在，跳过创建")
        else:
            # 创建 cabinet_ratings 表
            print("正在创建 cabinet_ratings 表...")
            db.execute(text("""
                CREATE TABLE cabinet_ratings (
                    id INT AUTO_INCREMENT PRIMARY KEY COMMENT '评分唯一标识ID',
                    user_id INT NOT NULL COMMENT '用户ID',
                    figure_id INT NOT NULL COMMENT '手办ID',
                    cabinet_type VARCHAR(20) NOT NULL COMMENT '收藏柜分类类型: star/new/fix/out/air/dup/wait/role',
                    rating INT NOT NULL DEFAULT 0 COMMENT '喜爱度评分: 0=未评分, 1-5=星级评分',
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
                    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
                    UNIQUE KEY uq_user_figure_cabinet_rating (user_id, figure_id, cabinet_type),
                    INDEX idx_cabinet_ratings_user_figure (user_id, figure_id),
                    CONSTRAINT fk_cabinet_ratings_user FOREIGN KEY (user_id) REFERENCES users(id),
                    CONSTRAINT fk_cabinet_ratings_figure FOREIGN KEY (figure_id) REFERENCES figures(id)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='收藏柜喜爱度评分表'
            """))
            db.commit()
            print("✅ cabinet_ratings 表创建成功")

        print("🎉 迁移完成")
    except Exception as e:
        print(f"❌ 迁移失败: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == '__main__':
    migrate()
