from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi import Request
from app.api import auth, figures, orders, users, assets, asset_transactions
from app.models.database import engine, Base
from app.utils.jwt import verify_token, create_access_token
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 创建数据库表（如果不存在）
Base.metadata.create_all(bind=engine)

# 增加请求体大小限制到 300MB
app = FastAPI()

# 配置 CORS（必须在 TokenRefreshMiddleware 之前添加）
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 在生产环境中应该设置具体的前端地址
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["X-Refresh-Token"],  # 暴露自定义响应头
)

# Token 自动续期中间件
class TokenRefreshMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # 打印请求头信息用于调试
        logger.info(f"请求路径: {request.url.path}")
        logger.info(f"所有请求头: {dict(request.headers)}")
        logger.info(f"Authorization头: {request.headers.get('Authorization')}")
        
        response = await call_next(request)
        
        # 获取请求中的 token
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            token = auth_header[7:]  # 去掉 "Bearer " 前缀
            user_id, should_refresh = verify_token(token)
            
            # 只有当需要续期时才续期
            if user_id and should_refresh:
                new_token = create_access_token({"sub": user_id})
                response.headers["X-Refresh-Token"] = new_token
        
        return response

# 添加 Token 续期中间件
app.add_middleware(TokenRefreshMiddleware)

# 注册路由
app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
app.include_router(users.router, prefix="/api/users", tags=["users"])
app.include_router(figures.router, prefix="/api/figures", tags=["figures"])
app.include_router(orders.router, prefix="/api/orders", tags=["orders"])
app.include_router(assets.router, prefix="/api/assets", tags=["assets"])
app.include_router(asset_transactions.router, prefix="/api/asset-transactions", tags=["asset-transactions"])

@app.get("/")
def read_root():
    return {"message": "Welcome to FigureBox API"}