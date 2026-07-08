"""
wishlist_service - 愿望清单服务包

服务模块说明：
- wishlist_query_service：列表/详情查询
- wishlist_crud_service：创建/更新/删除
- wishlist_stats_service：统计指标
- wishlist_url_fetch_service：URL 智能抓取（模拟）

数据兼容：
- 复用现有 figures 表，通过 purchase_type='wishlist' 标识
- 状态字段（wish/released/purchased/cancelled）保存在 tag 备注或 description 字段
"""
from .wishlist_query_service import WishlistQueryService
from .wishlist_crud_service import WishlistCrudService
from .wishlist_stats_service import WishlistStatsService
from .wishlist_url_fetch_service import WishlistUrlFetchService

__all__ = [
    "WishlistQueryService",
    "WishlistCrudService",
    "WishlistStatsService",
    "WishlistUrlFetchService",
]
