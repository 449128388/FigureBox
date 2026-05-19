"""
collector_router.py - 收藏家看板路由注册层

功能说明：
- 统一管理收藏家看板相关路由的注册
- 将收藏家看板业务路由汇总到统一的APIRouter

路由端点：
- GET /collector/dashboard: 获取收藏家看板数据

创建时间: 2026-05-18
作者: FigureBox Team
"""

from fastapi import APIRouter

from . import dashboard

router = APIRouter()

# 注册收藏家看板路由
router.include_router(
    dashboard.router,
    prefix="",
    tags=["collector-dashboard"]
)
