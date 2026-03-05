from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi import Request
from app.api import auth, figures, orders, users
from app.models.database import engine, Base

# 删除所有表
Base.metadata.drop_all(bind=engine)
# 创建数据库表
Base.metadata.create_all(bind=engine)

# 增加请求体大小限制到300MB
app = FastAPI()

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 在生产环境中应该设置具体的前端地址
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
app.include_router(users.router, prefix="/api/users", tags=["users"])
app.include_router(figures.router, prefix="/api/figures", tags=["figures"])
app.include_router(orders.router, prefix="/api/orders", tags=["orders"])

@app.get("/")
def read_root():
    return {"message": "Welcome to FigureBox API"}