"""
records 模块 - 交易记录相关API路由包

功能说明：
- 统一管理交易记录相关的所有API路由
- 包括交易流水、月度统计、盈亏分析等

模块划分：
- trade_records.py: 交易记录业务

创建时间: 2026-05-18
作者: FigureBox Team
"""

from .trade_records import router

__all__ = ["router"]
