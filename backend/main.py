from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi import Request
from app.api import auth, figures, orders, users, asset_transactions, sold_orders, upload, wishlist, home
from app.api.dashboard.trade_records import router as trade_records_router
from app.api.dashboard.market import router as market_router
from app.api.dashboard.assets import router as dashboard_assets_router
from app.api.dashboard.collector import router as dashboard_collector_router
from app.api.users import email_config_router, license_config_router
from app.api.password_reset import router as password_reset_router
from app.models.database import engine, Base
from app.models.exchange_rate import ExchangeRateRealtime, ExchangeRateHistory
from app.models.hpi import HPIDaily, HPIComponent
from app.models.hpoi_cache import HpoiScrapeCache
from app.models.license import UserLicense
from app.models.password_reset import PasswordResetCode
from app.utils.exception_handlers import register_exception_handlers
from app.utils.middleware import TokenRefreshMiddleware
from starlette.responses import Response
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 创建数据库表（如果不存在）
Base.metadata.create_all(bind=engine)

# 导入并启动定时任务调度器
from app.services.scheduler_service import start_scheduler
start_scheduler()

# 增加请求体大小限制到 300MB
app = FastAPI()

# 注册自定义异常处理器（隐藏 Pydantic 底层错误详情，只返回业务错误信息）
register_exception_handlers(app)

# 配置 CORS（必须在 TokenRefreshMiddleware 之前添加）
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 在生产环境中应该设置具体的前端地址
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["X-Refresh-Token"],  # 暴露自定义响应头
)

# 添加 Token 续期中间件（从 app/utils/middleware.py 导入）
app.add_middleware(TokenRefreshMiddleware)

# 注册路由
app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
app.include_router(password_reset_router, prefix="/api/auth", tags=["auth"])
app.include_router(users.router, prefix="/api/users", tags=["users"])
app.include_router(figures.router, prefix="/api/figures", tags=["figures"])
app.include_router(orders.router, prefix="/api/orders", tags=["orders"])
app.include_router(dashboard_assets_router, prefix="/api/assets", tags=["assets"])
app.include_router(market_router, prefix="/api/market", tags=["market"])
app.include_router(dashboard_collector_router, prefix="/api/collector", tags=["collector"])
app.include_router(asset_transactions.router, prefix="/api/asset-transactions", tags=["asset-transactions"])
app.include_router(sold_orders.router, prefix="/api/sold-orders", tags=["sold-orders"])
app.include_router(trade_records_router, prefix="/api/trade_records", tags=["trade_records"])
app.include_router(upload.router, prefix="/api", tags=["upload"])
app.include_router(wishlist.router, prefix="/api/wishlist", tags=["wishlist"])
app.include_router(email_config_router, prefix="/api", tags=["email-config"])
app.include_router(license_config_router, prefix="/api", tags=["license-config"])
app.include_router(home.router, prefix="/api/home", tags=["home"])
app.include_router(users.minio_config_router, prefix="/api", tags=["minio-config"])
app.include_router(users.timeout_config_router, prefix="/api", tags=["timeout-config"])
app.include_router(users.backup_router, prefix="/api", tags=["backup"])

@app.get("/")
def read_root():
    return {"message": "Welcome to FigureBox API"}
