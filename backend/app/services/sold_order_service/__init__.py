"""
已出售订单服务模块

本模块提供已出售订单相关的业务逻辑，采用企业级服务层架构：
- SoldOrderQueryService: 订单查询、统计
- SoldOrderCrudService: 订单增删改
- SoldOrderService: 统一入口（Facade模式）

新代码应优先直接使用子服务，SoldOrderService 仅用于保持向后兼容。
"""

from .sold_order_service import SoldOrderService
from .sold_order_query_service import SoldOrderQueryService
from .sold_order_crud_service import SoldOrderCrudService

__all__ = ["SoldOrderService", "SoldOrderQueryService", "SoldOrderCrudService"]