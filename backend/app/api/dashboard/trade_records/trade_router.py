"""
trade_router.py - 交易模块统一聚合路由

功能说明：
- 交易模块所有子路由的聚合入口
- 集成 5 个业务子路由：大盘统计、导出、买入订单、卖出订单、尾款支付
- 挂载到 prefix="/api/trade_records"（前缀与拆分前 0 变化）
- 提供单一 router 给 main.py include_router，保证前端 0 感知

子路由文件：
- trade_dashboard.py:  大盘统计（/dashboard /monthly-stats /transactions /profit-analysis）
- trade_export.py:     账单导出（/export）
- trade_buy_order.py:  买入订单（/buy-order /buy-orders）
- trade_sell_order.py: 卖出订单（/sell-order）
- trade_balance.py:    尾款支付（/pending-balance-orders /pay-balance）

依赖：
- fastapi.APIRouter
- 当前包内 5 个子路由

创建时间: 2026-08-04（从 app/api/records/trade_records.py 拆分）
作者: FigureBox Team
"""

from fastapi import APIRouter

from app.api.dashboard.trade_records.trade_dashboard import router as dashboard_router
from app.api.dashboard.trade_records.trade_export import router as export_router
from app.api.dashboard.trade_records.trade_buy_order import router as buy_order_router
from app.api.dashboard.trade_records.trade_sell_order import router as sell_order_router
from app.api.dashboard.trade_records.trade_balance import router as balance_router

# 统一聚合路由（无 prefix，由 main.py 挂载 /api/trade_records）
router = APIRouter()

# 顺序挂载 5 个子路由（顺序与业务域内聚性对齐：聚合统计 → 文件导出 → 业务操作）
router.include_router(dashboard_router)
router.include_router(export_router)
router.include_router(buy_order_router)
router.include_router(sell_order_router)
router.include_router(balance_router)

__all__ = ["router"]
