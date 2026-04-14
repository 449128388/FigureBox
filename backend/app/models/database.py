from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv

# 加载环境变量
# 说明：从 .env 文件加载数据库连接等配置信息
# 便于在不同环境（开发、测试、生产）使用不同配置
load_dotenv()

# 数据库连接字符串
# 格式：dialect+driver://username:password@host:port/database
# 默认使用本地 MySQL 数据库，可通过环境变量 DATABASE_URL 覆盖
DATABASE_URL = os.getenv("DATABASE_URL", "mysql+pymysql://admin:password@localhost:3306/figurebox")

# 创建数据库引擎
# 说明：引擎是 SQLAlchemy 与数据库交互的核心组件
# 负责管理连接池、执行 SQL 语句等
engine = create_engine(DATABASE_URL)

# 创建会话工厂
# 说明：SessionLocal 用于创建数据库会话实例
# - autocommit=False: 不自动提交，需要手动调用 commit()
# - autoflush=False: 不自动刷新，需要手动调用 flush()
# - bind=engine: 绑定到上面创建的引擎
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 创建基类
# 说明：所有模型类都需要继承这个 Base 类
# Base 类提供了 ORM 功能，包括表映射、字段定义等
Base = declarative_base()


# 依赖项函数
# 说明：用于 FastAPI 的依赖注入系统
# 在路由函数中通过 Depends(get_db) 获取数据库会话
# 使用 try-finally 确保会话在使用后正确关闭
def get_db():
    """
    获取数据库会话的生成器函数
    
    使用方式：
    - 在 FastAPI 路由中：@router.get("/") def get_items(db: Session = Depends(get_db))
    - 自动管理会话生命周期，确保连接正确释放
    
    注意事项：
    - 不要在函数内部捕获所有异常，让 FastAPI 的异常处理机制正常工作
    - 会话会在请求结束后自动关闭
    """
    db = SessionLocal()  # 创建新的会话实例
    try:
        yield db  # 返回会话供路由函数使用
    finally:
        db.close()  # 确保会话被关闭，释放数据库连接
