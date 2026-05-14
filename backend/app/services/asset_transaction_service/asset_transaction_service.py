"""
资产交易服务（主入口）
提供资产交易记录相关的业务逻辑，包括创建、查询、更新交易记录
支持股票式补仓功能，记录买入卖出交易

注意：此文件为兼容性入口，实际业务逻辑已拆分到子服务中
"""
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session

from .asset_transaction_create_service import AssetTransactionCreateService
from .asset_transaction_query_service import AssetTransactionQueryService
from .asset_transaction_change_service import AssetTransactionChangeService
from .asset_transaction_delete_service import AssetTransactionDeleteService


class AssetTransactionService:
    """资产交易服务类（主入口）"""

    # ========== 创建交易记录 ==========

    @staticmethod
    def create_transaction_from_figure(
        db: Session,
        user_id: int,
        figure_id: int,
        price: float,
        quantity: int = 1,
        order_id: Optional[int] = None
    ):
        return AssetTransactionCreateService.create_transaction_from_figure(
            db, user_id, figure_id, price, quantity, order_id
        )

    @staticmethod
    def link_order_to_existing_transaction(
        db: Session,
        user_id: int,
        figure_id: int,
        order,
        quantity: int = 1
    ):
        return AssetTransactionCreateService.link_order_to_existing_transaction(
            db, user_id, figure_id, order, quantity
        )

    @staticmethod
    def create_sell_transaction(
        db: Session,
        user_id: int,
        figure_id: int,
        price: float,
        quantity: int,
        notes: Optional[str] = None
    ):
        return AssetTransactionCreateService.create_sell_transaction(
            db, user_id, figure_id, price, quantity, notes
        )

    @staticmethod
    def create_buy_transaction_from_order(
        db: Session,
        user_id: int,
        figure_id: int,
        order,
        quantity: int = 1
    ):
        return AssetTransactionCreateService.create_buy_transaction_from_order(
            db, user_id, figure_id, order, quantity
        )

    @staticmethod
    def create_quantity_adjustment_transaction(
        db: Session,
        user_id: int,
        figure_id: int,
        quantity_change: int,
        price: float,
        original_quantity: int,
        new_quantity: int
    ):
        return AssetTransactionCreateService.create_quantity_adjustment_transaction(
            db, user_id, figure_id, quantity_change, price, original_quantity, new_quantity
        )

    @staticmethod
    def create_price_adjustment_transaction(
        db: Session,
        user_id: int,
        figure_id: int,
        old_price: float,
        new_price: float,
        quantity: int
    ):
        return AssetTransactionCreateService.create_price_adjustment_transaction(
            db, user_id, figure_id, old_price, new_price, quantity
        )

    # ========== 查询交易记录 ==========

    @staticmethod
    def get_transactions_by_figure(
        db: Session,
        user_id: int,
        figure_id: int
    ) -> List:
        return AssetTransactionQueryService.get_transactions_by_figure(db, user_id, figure_id)

    @staticmethod
    def get_all_transactions(
        db: Session,
        user_id: int,
        transaction_type: Optional[str] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List:
        return AssetTransactionQueryService.get_all_transactions(
            db, user_id, transaction_type, skip, limit
        )

    @staticmethod
    def calculate_average_cost(
        db: Session,
        user_id: int,
        figure_id: int
    ) -> Dict[str, Any]:
        return AssetTransactionQueryService.calculate_average_cost(db, user_id, figure_id)

    @staticmethod
    def calculate_profit(
        db: Session,
        user_id: int,
        figure_id: int,
        current_market_price: Optional[float] = None
    ) -> Dict[str, Any]:
        return AssetTransactionQueryService.calculate_profit(
            db, user_id, figure_id, current_market_price
        )

    # ========== 删除交易记录 ==========

    @staticmethod
    def delete_transaction(
        db: Session,
        transaction_id: int,
        user_id: int
    ) -> bool:
        return AssetTransactionDeleteService.delete_transaction(db, transaction_id, user_id)
