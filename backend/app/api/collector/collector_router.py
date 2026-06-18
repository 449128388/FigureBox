"""
collector_router.py - 收藏家看板路由注册层

功能说明：
- 统一管理收藏家看板相关路由的注册
- 将收藏家看板业务路由汇总到统一的APIRouter

路由端点：
- GET /collector/dashboard: 获取收藏家看板数据（已废弃，保留兼容）
- GET /collector/summary: 获取顶部概览+三指标卡片
- GET /collector/cabinets: 获取我的收藏柜（高价值藏品）
- GET /collector/tags: 获取标签云
- GET /collector/timeline: 获取收藏历程（动态流）

创建时间: 2026-05-18
作者: FigureBox Team
"""

from fastapi import APIRouter

from . import dashboard, summary, cabinets, tags, timeline, ratings, transactions

router = APIRouter()

# 注册收藏家看板路由
router.include_router(
    dashboard.router,
    prefix="",
    tags=["collector-dashboard"]
)

# 注册拆分后的独立接口
router.include_router(
    summary.router,
    prefix="",
    tags=["collector-summary"]
)

router.include_router(
    cabinets.router,
    prefix="",
    tags=["collector-cabinets"]
)

router.include_router(
    tags.router,
    prefix="",
    tags=["collector-tags"]
)

router.include_router(
    timeline.router,
    prefix="",
    tags=["collector-timeline"]
)

router.include_router(
    ratings.router,
    prefix="",
    tags=["collector-ratings"]
)

router.include_router(
    transactions.router,
    prefix="",
    tags=["collector-transactions"]
)
