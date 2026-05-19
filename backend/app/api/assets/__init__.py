"""
assets 模块 - 资产相关API路由包

功能说明：
- 统一管理资产相关的所有API路由
- 包括资产看板、收藏家看板、行情看板、操作接口等

模块划分：
- assets_router.py: 路由注册层，统一管理所有资产路由
- dashboard_asset.py: 资产看板业务
- dashboard_collector.py: 收藏家看板业务
- dashboard_market.py: 行情看板业务
- operation_price.py: 价格更新操作
- operation_position.py: 补仓操作
- operation_holding_filter.py: 持仓筛选
- settings_annual_limit.py: 年度限额配置

创建时间: 2026-05-18
作者: FigureBox Team
"""

from .assets_router import router

__all__ = ["router"]
