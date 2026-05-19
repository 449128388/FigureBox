"""
collector 模块 - 收藏家看板API路由包

功能说明：
- 提供收藏家模式看板相关的所有API路由
- 包括收藏统计、高价值藏品、标签云、动态流等

创建时间: 2026-05-18
作者: FigureBox Team
"""

from .collector_router import router

__all__ = ["router"]
