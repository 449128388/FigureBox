"""
订单服务模块

提供订单相关的所有业务逻辑服务，采用 Facade 模式组织：
- OrderService: 主入口（Facade），保持向后兼容
- OrderQueryService: 订单查询、统计
- OrderCrudService: 订单增删改

使用示例：
    from app.services.order_service import OrderService
    from app.services.order_service import OrderQueryService, OrderCrudService
"""

from .order_service import OrderService
from .order_query_service import OrderQueryService
from .order_crud_service import OrderCrudService

__all__ = [
    "OrderService",
    "OrderQueryService",
    "OrderCrudService",
]
