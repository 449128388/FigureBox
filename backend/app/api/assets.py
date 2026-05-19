"""
assets.py - 资产相关API路由（重构后入口文件）

功能说明：
- 资产模块路由入口，统一导出所有资产相关API
- 原单文件已按企业级规范拆分为多个职责单一的模块
- 具体实现已迁移至 app/api/assets/ 目录下各子模块

模块拆分说明：
- assets_router.py: 路由注册层，统一管理所有资产路由
- dashboard_asset.py: 资产看板业务（/dashboard）
- dashboard_collector.py: 收藏家看板业务（/collector/dashboard）
- dashboard_market.py: 行情看板业务（/market/dashboard）
- operation_price.py: 价格更新操作
- operation_position.py: 补仓操作
- operation_holding_filter.py: 持仓筛选
- settings_annual_limit.py: 年度限额配置
- assets_common.py: 公共服务层

重构时间: 2026-05-18
作者: FigureBox Team
"""

# 从新的模块包导入路由
from app.api.assets import router

# 为了保持向后兼容，导出router
__all__ = ["router"]
