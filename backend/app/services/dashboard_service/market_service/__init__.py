"""
market_service 模块 - 行情看板服务层

功能说明：
- 提供行情看板相关的业务逻辑服务
- 包括塑料小人指数(HPI)、市场涨跌统计、板块分析等

创建时间: 2026-05-18
作者: FigureBox Team
"""

from .hpi_service import HPIService

__all__ = ["HPIService"]
