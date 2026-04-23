"""
订单资金流水服务层 - 企业级拆分架构

核心原则：
- 只记录有真实资金流动的交易
- 严禁记录无资金流动的场景（库存调整、价格调整等）
- 资金账与库存账完全解耦

模块划分：
- transaction_create_service: 交易创建相关
- transaction_query_service: 交易查询统计相关
- transaction_delete_service: 交易删除相关

使用方式：
    from app.services.order_transaction_service import OrderTransactionService
    service = OrderTransactionService()
    service.create_buy_transaction(...)
"""

from .order_transaction_service import OrderTransactionService

__all__ = ["OrderTransactionService"]
