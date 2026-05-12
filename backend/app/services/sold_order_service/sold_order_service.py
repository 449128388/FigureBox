"""
已出售订单服务

提供已出售订单相关的业务逻辑，是各子服务的统一入口，保持向后兼容

企业级架构说明：
本文件作为 Facade 模式实现，将业务逻辑拆分到以下子服务：
- SoldOrderQueryService: 订单查询、统计（sold_order_query_service.py）
- SoldOrderCrudService: 订单增删改（sold_order_crud_service.py）

新代码应优先直接使用子服务，本文件仅用于保持向后兼容。
"""
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session

from app.models.sold_order import SoldOrder
from app.models.user import User
from app.schemas.sold_order import SoldOrderCreate, SoldOrderUpdate, SoldOrderListItem, SoldOrderStatistics

# 导入子服务（使用相对导入）
from .sold_order_query_service import SoldOrderQueryService
from .sold_order_crud_service import SoldOrderCrudService


class SoldOrderService:
    """
    已出售订单服务类（Facade 模式）

    作为各子服务的统一入口，所有方法委托给相应的子服务实现
    保持向后兼容，现有调用代码无需修改
    """

    # ==========================================================================
    # 查询相关（委托给 SoldOrderQueryService）
    # ==========================================================================
    @staticmethod
    def get_sold_orders(db: Session, current_user: User) -> List[SoldOrderListItem]:
        """获取已出售订单列表"""
        return SoldOrderQueryService.get_sold_orders(db, current_user)

    @staticmethod
    def get_sold_order_by_id(db: Session, order_id: int, current_user: User) -> Optional[SoldOrder]:
        """获取单个已出售订单详情"""
        return SoldOrderQueryService.get_sold_order_by_id(db, order_id, current_user)

    @staticmethod
    def get_sold_order_statistics(db: Session, current_user: User) -> SoldOrderStatistics:
        """获取已出售订单统计信息"""
        return SoldOrderQueryService.get_sold_order_statistics(db, current_user)

    # ==========================================================================
    # CRUD 操作（委托给 SoldOrderCrudService）
    # ==========================================================================
    @staticmethod
    def create_sold_order(
        db: Session,
        order_data: SoldOrderCreate,
        current_user: User
    ) -> SoldOrder:
        """创建已出售订单"""
        return SoldOrderCrudService.create_sold_order(db, order_data, current_user)

    @staticmethod
    def update_sold_order(
        db: Session,
        order_id: int,
        order_data: SoldOrderUpdate,
        current_user: User
    ) -> SoldOrder:
        """更新已出售订单"""
        return SoldOrderCrudService.update_sold_order(db, order_id, order_data, current_user)

    @staticmethod
    def delete_sold_order(
        db: Session,
        order_id: int,
        current_user: User
    ) -> dict:
        """删除已出售订单（软删除）"""
        return SoldOrderCrudService.delete_sold_order(db, order_id, current_user)

    @staticmethod
    def batch_delete_sold_orders(
        db: Session,
        order_ids: list[int],
        current_user: User
    ) -> dict:
        """批量删除已出售订单（软删除）"""
        return SoldOrderCrudService.batch_delete_sold_orders(db, order_ids, current_user)