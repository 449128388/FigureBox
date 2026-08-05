"""
market 模块 - 行情看板API路由包

功能说明：
- 提供行情看板相关的所有API路由
- 包括塑料小人指数、K线技术指标、板块排行等

创建时间: 2026-05-18
作者: FigureBox Team
"""

from .market_router import router

__all__ = ["router"]
