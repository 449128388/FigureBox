"""
wishlist_router - 愿望清单路由注册层

路由端点：
- GET    /wishlist/                     列表（分页+过滤）
- GET    /wishlist/stats                统计指标
- POST   /wishlist/                     创建愿望
- GET    /wishlist/{id}                 详情
- PUT    /wishlist/{id}                 更新
- DELETE /wishlist/{id}                 软删除
- POST   /wishlist/{id}/status          状态流转
- POST   /wishlist/{id}/move-to-library 转入手办库
- POST   /wishlist/url-fetch            URL 智能抓取（模拟）
"""
from fastapi import APIRouter

from . import wishlist, wishlist_stats, wishlist_url

router = APIRouter()

router.include_router(wishlist_stats.router, prefix="", tags=["wishlist-stats"])
router.include_router(wishlist.router, prefix="", tags=["wishlist"])
router.include_router(wishlist_url.router, prefix="", tags=["wishlist-url"])
