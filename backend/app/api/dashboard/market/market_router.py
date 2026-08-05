"""
market_router.py - 行情看板路由注册层

功能说明：
- 统一管理行情看板相关路由的注册
- 将行情看板业务路由汇总到统一的APIRouter

路由端点：
- GET /market/dashboard: 获取行情看板数据

创建时间: 2026-05-18
作者: FigureBox Team
"""

from fastapi import APIRouter

from . import dashboard

router = APIRouter()

# 注册行情看板路由
router.include_router(
    dashboard.router,
    prefix="",
    tags=["market-dashboard"]
)
