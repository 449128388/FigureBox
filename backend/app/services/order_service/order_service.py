"""
订单服务
提供订单相关的业务逻辑，是各子服务的统一入口，保持向后兼容

企业级架构说明：
本文件作为 Facade 模式实现，将业务逻辑拆分到以下子服务：
- OrderQueryService: 订单查询、统计（order_query_service.py）
- OrderCrudService: 订单增删改（order_crud_service.py）

新代码应优先直接使用子服务，本文件仅用于保持向后兼容。
"""
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session

from app.models.order import Order
from app.models.user import User
from app.schemas.order import OrderCreate, OrderUpdate, OrderListItem

# 导入子服务（使用相对导入）
from .order_query_service import OrderQueryService
from .order_crud_service import OrderCrudService


class OrderService:
    """
    订单服务类（Facade 模式）

    作为各子服务的统一入口，所有方法委托给相应的子服务实现
    保持向后兼容，现有调用代码无需修改
    """

    # ==========================================================================
    # 查询相关（委托给 OrderQueryService）
    # ==========================================================================
    @staticmethod
    def get_unpaid_balance(db: Session, current_user: User) -> dict:
        """获取未支付状态的尾款总额"""
        return OrderQueryService.get_unpaid_balance(db, current_user)

    @staticmethod
    def get_orders(db: Session, current_user: User) -> List[OrderListItem]:
        """获取订单列表"""
        return OrderQueryService.get_orders(db, current_user)

    @staticmethod
    def get_order_by_id(db: Session, order_id: int, current_user: User) -> Optional[Order]:
        """获取单个订单详情"""
        return OrderQueryService.get_order_by_id(db, order_id, current_user)

    @staticmethod
    def get_order_count_by_figure(db: Session, figure_id: int) -> int:
        """获取指定手办的订单数量"""
        return OrderQueryService.get_order_count_by_figure(db, figure_id)

    # ==========================================================================
    # CRUD 操作（委托给 OrderCrudService）
    # ==========================================================================
    @staticmethod
    def create_order(
        db: Session,
        order_data: OrderCreate,
        current_user: User
    ) -> Order:
        """创建订单"""
        return OrderCrudService.create_order(db, order_data, current_user)

    @staticmethod
    def update_order(
        db: Session,
        order_id: int,
        order_data: OrderUpdate,
        current_user: User
    ) -> Order:
        """更新订单"""
        return OrderCrudService.update_order(db, order_id, order_data, current_user)

    @staticmethod
    def delete_order(
        db: Session,
        order_id: int,
        current_user: User
    ) -> dict:
        """删除订单（软删除）"""
        return OrderCrudService.delete_order(db, order_id, current_user)
