"""
已出售订单CRUD服务

提供已出售订单的创建、更新、删除功能
集成多模块联动：库存账、资金账、资产看板、手办状态
"""
from typing import Dict, Any
from sqlalchemy.orm import Session
from datetime import datetime

from app.models.sold_order import SoldOrder
from app.models.user import User
from app.schemas.sold_order import SoldOrderCreate, SoldOrderUpdate
from .currency_service import CurrencyService
from app.services.sold_order_service.sold_order_transaction_service import SoldOrderTransactionService
from app.services.sold_order_service.sold_order_inventory_service import SoldOrderInventoryService
from app.services.sold_order_service.sold_order_figure_service import SoldOrderFigureService


class SoldOrderCrudService:
    """
    已出售订单CRUD服务类

    提供订单的创建、更新、删除（软删除）功能
    支持多币种自动转换为人民币计算盈亏
    集成多模块联动：
    - 尾款管理（OrderTransaction）：创建卖出订单主记录和资金流水
    - 库存账（AssetTransaction）：扣减库存数量
    - 资产看板：盈亏分析数据
    - 手办聚合状态：更新库存数量和售罄状态
    """

    @staticmethod
    def _calculate_profit(
        sell_price: float,
        cost_price: float,
        shipping_fee: float,
        platform_fee: float
    ) -> Dict[str, float]:
        """
        计算净利润和利润率（所有金额应为人民币）

        净利润 = 卖出价 - 成本价 - 运费 - 手续费
        利润率 = 净利润 / 成本价 * 100

        Args:
            sell_price: 卖出价格（人民币）
            cost_price: 成本价格（人民币）
            shipping_fee: 运费（人民币，支出）
            platform_fee: 平台手续费（人民币，支出）

        Returns:
            包含净利润和利润率的字典
        """
        net_profit = sell_price - cost_price - shipping_fee - platform_fee
        profit_rate = (net_profit / cost_price) * 100 if cost_price != 0 else 0

        return {
            'net_profit': round(net_profit, 2),
            'profit_rate': round(profit_rate, 2)
        }

    @staticmethod
    def _calculate_profit_with_currency(
        sell_price: float,
        sell_price_currency: str,
        cost_price: float,
        cost_price_currency: str,
        shipping_fee: float,
        shipping_fee_currency: str,
        platform_fee: float,
        platform_fee_currency: str
    ) -> Dict[str, float]:
        """
        计算净利润和利润率（支持多币种自动转换为人民币）

        Args:
            sell_price: 卖出价格
            sell_price_currency: 卖出价格币种
            cost_price: 成本价格
            cost_price_currency: 成本价格币种
            shipping_fee: 运费
            shipping_fee_currency: 运费币种
            platform_fee: 平台手续费
            platform_fee_currency: 平台手续费币种

        Returns:
            包含净利润和利润率的字典（金额统一为人民币）
        """
        # 使用币种服务将所有金额转换为人民币
        profit_data = CurrencyService.calculate_profit_in_cny(
            sell_price=sell_price,
            sell_price_currency=sell_price_currency or 'CNY',
            cost_price=cost_price,
            cost_price_currency=cost_price_currency or 'CNY',
            shipping_fee=shipping_fee or 0,
            shipping_fee_currency=shipping_fee_currency or 'CNY',
            platform_fee=platform_fee or 0,
            platform_fee_currency=platform_fee_currency or 'CNY'
        )

        return {
            'net_profit': profit_data['net_profit'],
            'profit_rate': profit_data['profit_rate']
        }

    @staticmethod
    def create_sold_order(
        db: Session,
        order_data: SoldOrderCreate,
        current_user: User
    ) -> SoldOrder:
        """
        创建已出售订单

        创建时自动完成以下联动操作：
        1. 创建已出售订单记录
        2. 尾款管理：创建卖出订单主记录（类型标记为 sell）
        3. 资金账：创建3笔资金流水（收入-卖出价、支出-运费、支出-手续费）
        4. 库存账：扣减库存数量（trans_type='sell'）
        5. 资产看板：盈亏分析数据（通过净利润字段）
        6. 手办聚合状态：更新当前库存数量、售罄状态

        所有操作在事务中执行，确保数据一致性
        """
        try:
            # 计算净利润和利润率（自动转换多币种为人民币）
            profit_data = SoldOrderCrudService._calculate_profit_with_currency(
                sell_price=order_data.sell_price,
                sell_price_currency=order_data.sell_price_currency,
                cost_price=order_data.cost_price,
                cost_price_currency=order_data.cost_price_currency,
                shipping_fee=order_data.shipping_fee or 0,
                shipping_fee_currency=order_data.shipping_fee_currency,
                platform_fee=order_data.platform_fee or 0,
                platform_fee_currency=order_data.platform_fee_currency
            )

            # 1. 创建已出售订单记录
            new_order = SoldOrder(
                user_id=current_user.id,
                figure_id=order_data.figure_id,
                quantity=order_data.quantity or 1,  # 卖出数量
                sell_price=order_data.sell_price,
                cost_price=order_data.cost_price,
                shipping_fee=order_data.shipping_fee or 0,
                platform_fee=order_data.platform_fee or 0,
                sell_price_currency=order_data.sell_price_currency or 'CNY',
                cost_price_currency=order_data.cost_price_currency or 'CNY',
                shipping_fee_currency=order_data.shipping_fee_currency or 'CNY',
                platform_fee_currency=order_data.platform_fee_currency or 'CNY',
                net_profit=profit_data['net_profit'],
                profit_rate=profit_data['profit_rate'],
                sell_platform=order_data.sell_platform,
                order_number=order_data.order_number,
                buyer_phone=order_data.buyer_phone,
                buyer_address=order_data.buyer_address,
                tracking_number=order_data.tracking_number,
                logistics_company=order_data.logistics_company,
                shipping_date=order_data.shipping_date,
                status=order_data.status or "待发货",
                remark=order_data.remark
            )

            db.add(new_order)
            db.flush()  # 获取订单ID，但不提交

            # 设置 updated_at 等于 created_at
            new_order.updated_at = new_order.created_at

            # 2. 尾款管理：创建卖出订单主记录和资金流水（3笔）
            SoldOrderTransactionService.create_all_sold_order_transactions(
                db, new_order, current_user.id
            )

            # 3. 库存账：扣减库存数量
            SoldOrderInventoryService.deduct_inventory(
                db, new_order, current_user.id
            )

            # 4. 手办聚合状态：更新库存数量和售罄状态
            SoldOrderFigureService.update_figure_status(
                db, new_order, current_user.id
            )

            # 提交所有变更
            db.commit()
            db.refresh(new_order)

            return new_order

        except Exception as e:
            db.rollback()
            raise e

    @staticmethod
    def update_sold_order(
        db: Session,
        order_id: int,
        order_data: SoldOrderUpdate,
        current_user: User
    ) -> SoldOrder:
        """
        更新已出售订单
        
        更新时自动重新计算净利润和利润率
        """
        order = db.query(SoldOrder).filter(
            SoldOrder.id == order_id,
            SoldOrder.user_id == current_user.id,
            SoldOrder.is_active == 1
        ).first()

        if not order:
            raise ValueError("订单不存在或已被删除")

        # 记录原数量（用于数量变更处理）
        old_quantity = order.quantity or 1

        # 更新基本字段
        if order_data.figure_id is not None:
            order.figure_id = order_data.figure_id
        if order_data.sell_price is not None:
            order.sell_price = order_data.sell_price
        if order_data.cost_price is not None:
            order.cost_price = order_data.cost_price
        if order_data.shipping_fee is not None:
            order.shipping_fee = order_data.shipping_fee
        if order_data.platform_fee is not None:
            order.platform_fee = order_data.platform_fee
        if order_data.sell_price_currency is not None:
            order.sell_price_currency = order_data.sell_price_currency
        if order_data.cost_price_currency is not None:
            order.cost_price_currency = order_data.cost_price_currency
        if order_data.shipping_fee_currency is not None:
            order.shipping_fee_currency = order_data.shipping_fee_currency
        if order_data.platform_fee_currency is not None:
            order.platform_fee_currency = order_data.platform_fee_currency
        if order_data.sell_platform is not None:
            order.sell_platform = order_data.sell_platform
        if order_data.order_number is not None:
            order.order_number = order_data.order_number
        if order_data.buyer_phone is not None:
            order.buyer_phone = order_data.buyer_phone
        if order_data.buyer_address is not None:
            order.buyer_address = order_data.buyer_address
        if order_data.tracking_number is not None:
            order.tracking_number = order_data.tracking_number
        if order_data.logistics_company is not None:
            order.logistics_company = order_data.logistics_company
        if order_data.shipping_date is not None:
            order.shipping_date = order_data.shipping_date

        # 处理状态变更（特别是退款/纠纷状态）
        old_status = order.status
        if order_data.status is not None:
            order.status = order_data.status

        # 如果状态从其他状态变为"退款/纠纷"，执行库存回撤
        if order_data.status == "退款/纠纷" and old_status != "退款/纠纷":
            # 执行库存回撤（FIFO原则：撤销最后卖出的记录）
            inventory_return_result = SoldOrderInventoryService.return_inventory_for_dispute(
                db, order, current_user.id
            )
            if inventory_return_result.get("error"):
                db.rollback()
                raise ValueError(inventory_return_result["error"])

        # 如果状态从"退款/纠纷"变为"已完成"/"已发货"/"待发货"，执行正常订单创建流程
        if old_status == "退款/纠纷" and order_data.status in ["已完成", "已发货", "待发货"]:
            # 1. 尾款管理：创建卖出订单主记录和资金流水（3笔）
            SoldOrderTransactionService.create_all_sold_order_transactions(
                db, order, current_user.id
            )

            # 2. 库存账：扣减库存数量
            SoldOrderInventoryService.deduct_inventory(
                db, order, current_user.id
            )

            # 3. 手办聚合状态：更新库存数量和售罄状态
            SoldOrderFigureService.update_figure_status(
                db, order, current_user.id
            )

        if order_data.remark is not None:
            order.remark = order_data.remark

        # 标记是否涉及金额字段变更
        amount_fields_changed = (order_data.sell_price is not None or
                                  order_data.shipping_fee is not None or
                                  order_data.platform_fee is not None or
                                  order_data.sell_price_currency is not None or
                                  order_data.shipping_fee_currency is not None or
                                  order_data.platform_fee_currency is not None)

        # 如果涉及金额的字段有变化，重新计算净利润和利润率（支持多币种）
        if amount_fields_changed or order_data.cost_price is not None or order_data.cost_price_currency is not None:
            profit_data = SoldOrderCrudService._calculate_profit_with_currency(
                sell_price=order.sell_price,
                sell_price_currency=order.sell_price_currency,
                cost_price=order.cost_price,
                cost_price_currency=order.cost_price_currency,
                shipping_fee=order.shipping_fee,
                shipping_fee_currency=order.shipping_fee_currency,
                platform_fee=order.platform_fee,
                platform_fee_currency=order.platform_fee_currency
            )
            order.net_profit = profit_data['net_profit']
            order.profit_rate = profit_data['profit_rate']

        # 如果涉及卖出价、运费、手续费变更，更新 order_transactions 记录
        if amount_fields_changed:
            SoldOrderTransactionService.update_sold_order_transactions(
                db, order, current_user.id
            )

        # 如果涉及数量变更，更新库存和交易记录
        if order_data.quantity is not None and order_data.quantity != old_quantity:
            new_quantity = order_data.quantity

            # 1. 更新 asset_transactions（库存账）
            inventory_result = SoldOrderInventoryService.update_quantity_on_sold_order_change(
                db, order, current_user.id, old_quantity, new_quantity
            )

            if inventory_result.get("error"):
                db.rollback()
                raise ValueError(inventory_result["error"])

            # 2. 更新 order_transactions（资金账）
            transaction_result = SoldOrderTransactionService.update_sell_transaction_quantity(
                db, order, current_user.id, new_quantity
            )

            if transaction_result.get("error"):
                db.rollback()
                raise ValueError(transaction_result["error"])

            # 更新订单数量
            order.quantity = new_quantity

        # 更新更新时间
        order.updated_at = datetime.now()

        db.commit()
        db.refresh(order)

        return order

    @staticmethod
    def delete_sold_order(
        db: Session,
        order_id: int,
        current_user: User
    ) -> Dict[str, Any]:
        """
        软删除已出售订单

        删除时联动处理：
        1. 软删除已出售订单记录
        2. 恢复库存数量
        3. 恢复手办聚合状态
        4. 相关资金流水记录保持，但标记为无效（通过订单ID关联）
        """
        try:
            order = db.query(SoldOrder).filter(
                SoldOrder.id == order_id,
                SoldOrder.user_id == current_user.id,
                SoldOrder.is_active == 1
            ).first()

            if not order:
                raise ValueError("订单不存在或已被删除")

            # 1. 软删除已出售订单记录
            order.is_active = 0
            order.deleted_at = datetime.now()

            # 2. 恢复库存数量
            SoldOrderInventoryService.restore_inventory(
                db, order, current_user.id
            )

            # 3. 恢复手办聚合状态
            SoldOrderFigureService.restore_figure_status(
                db, order, current_user.id
            )

            db.commit()

            return {"message": "订单删除成功", "order_id": order_id}

        except Exception as e:
            db.rollback()
            raise e

    @staticmethod
    def batch_delete_sold_orders(
        db: Session,
        order_ids: list[int],
        current_user: User
    ) -> Dict[str, Any]:
        """
        批量软删除已出售订单
        
        不物理删除订单记录，仅标记 is_active=False 和 deleted_at
        """
        success_count = 0
        failed_count = 0
        errors = []

        for order_id in order_ids:
            try:
                order = db.query(SoldOrder).filter(
                    SoldOrder.id == order_id,
                    SoldOrder.user_id == current_user.id,
                    SoldOrder.is_active == 1
                ).first()

                if order:
                    order.is_active = 0
                    order.deleted_at = datetime.now()
                    success_count += 1
                else:
                    failed_count += 1
                    errors.append(f"订单ID {order_id} 不存在或已被删除")
            except Exception as e:
                failed_count += 1
                errors.append(f"订单ID {order_id} 删除失败: {str(e)}")

        db.commit()

        return {
            "success_count": success_count,
            "failed_count": failed_count,
            "errors": errors
        }