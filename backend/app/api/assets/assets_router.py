"""
assets_router.py - 资产模块路由注册层

功能说明：
- 统一管理资产相关路由的注册（不含market和collector）
- 将各业务模块的路由汇总到统一的APIRouter
- 保持原有接口路径和参数不变

路由模块：
- dashboard_asset: 资产看板 (/dashboard)
- operation_price: 价格更新操作 (/figures/{id}/price-info, /figures/{id}/update-price)
- operation_position: 补仓操作 (/figures/{id}/add-position)
- operation_holding_filter: 持仓筛选 (/holdings/filter)
- settings_annual_limit: 年度限额配置 (/settings/annual-limit)

注意：
- market看板路由已独立到 app.api.market 模块
- collector看板路由已独立到 app.api.collector 模块
- records交易记录路由已独立到 app.api.records 模块

依赖：
- fastapi.APIRouter
- 各业务模块的router

创建时间: 2026-05-18
作者: FigureBox Team
"""

from fastapi import APIRouter

# 导入各业务模块路由
from . import dashboard_asset
from . import operation_price
from . import operation_position
from . import operation_holding_filter
from . import settings_annual_limit

# 创建主路由
router = APIRouter()

# 注册资产看板路由
router.include_router(
    dashboard_asset.router,
    prefix="",
    tags=["asset-dashboard"]
)

# 注册价格更新操作路由
router.include_router(
    operation_price.router,
    prefix="",
    tags=["asset-operations"]
)

# 注册补仓操作路由
router.include_router(
    operation_position.router,
    prefix="",
    tags=["asset-operations"]
)

# 注册持仓筛选路由
router.include_router(
    operation_holding_filter.router,
    prefix="",
    tags=["asset-operations"]
)

# 注册年度限额配置路由
router.include_router(
    settings_annual_limit.router,
    prefix="",
    tags=["asset-settings"]
)