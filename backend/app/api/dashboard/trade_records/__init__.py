"""
trade_records 子包入口

交易模块 API 路由聚合包（2026-08-04 从 app/api/records/trade_records.py 拆分）

子模块：
- trade_router:        统一聚合路由（5 子路由聚合）
- trade_dashboard:     大盘统计（/dashboard /monthly-stats /transactions /profit-analysis）
- trade_export:        账单导出（/export）
- trade_buy_order:     买入订单（/buy-order /buy-orders）
- trade_sell_order:    卖出订单（/sell-order）
- trade_balance:       尾款支付（/pending-balance-orders /pay-balance）

main.py 用法：
    from app.api.dashboard.trade_records import router as trade_records_router
    app.include_router(trade_records_router, prefix="/api/trade_records", tags=["trade_records"])
"""
from app.api.dashboard.trade_records.trade_router import router

__all__ = ["router"]
