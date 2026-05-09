"""
补仓服务
提供补仓相关的业务逻辑，包括创建订单、更新库存、计算新的平均成本等
采用企业级服务层架构
"""
from datetime import datetime, date
from typing import Dict, Any
from sqlalchemy.orm import Session

from app.models.figure import Figure
from app.models.order import Order
from app.models.asset import AssetTransaction, OrderTransaction, AssetValueCache
from app.models.user import User


class AddPositionService:
    """补仓服务类"""

    @classmethod
    def add_position(
        cls,
        db: Session,
        user_id: int,
        figure_id: int,
        quantity: int,
        price: float
    ) -> Dict[str, Any]:
        """
        执行补仓操作

        业务流程:
        1. 创建已完成状态的订单（补仓视同已完成购买）
        2. 创建asset_transactions记录（买入）
        3. 创建order_transactions记录（资金流出）
        4. 更新手办数量和平均入手价格（加权平均）
        5. 更新日涨跌缓存（新买入部分按买入价=市值处理，贡献0%波动）

        Args:
            db: 数据库会话
            user_id: 用户ID
            figure_id: 手办ID
            quantity: 补仓数量
            price: 补仓单价

        Returns:
            Dict包含补仓操作结果
        """
        # 获取手办信息
        figure = db.query(Figure).filter(Figure.id == figure_id).first()
        if not figure:
            raise ValueError(f"手办不存在: {figure_id}")

        # 获取当前库存和成本
        current_quantity = figure.quantity or 1
        current_cost_price = figure.average_purchase_price or 0

        # 计算新的加权平均成本价
        # 新成本价 = (原成本 × 原数量 + 补仓价格 × 补仓数量) / (原数量 + 补仓数量)
        total_cost = (current_cost_price * current_quantity) + (price * quantity)
        new_quantity = current_quantity + quantity
        new_cost_price = total_cost / new_quantity if new_quantity > 0 else 0

        # 1. 创建已完成状态的订单（根据数量创建多个订单，每体一个订单）
        orders = cls._create_orders(db, user_id, figure_id, quantity, price)
        order_ids = [order.id for order in orders]

        # 2. 创建asset_transactions记录
        asset_transaction = cls._create_asset_transaction(
            db, user_id, figure_id, order_ids[0] if order_ids else None, quantity, price
        )

        # 3. 创建order_transactions记录
        order_transaction = cls._create_order_transaction(
            db, user_id, figure_id, order_ids[0] if order_ids else None, quantity, price
        )

        # 4. 更新手办信息
        figure.quantity = new_quantity
        figure.average_purchase_price = new_cost_price

        # 更新手办当前市值（市场价 × 数量）
        current_market_price = figure.market_price or figure.price or price
        figure.current_value = current_market_price * new_quantity

        # 5. 更新日涨跌缓存（新买入部分按买入价=市值处理）
        cls._update_daily_cache_for_add_position(db, user_id, quantity, price)

        db.commit()

        return {
            "figure_id": figure_id,
            "figure_name": figure.name,
            "order_ids": order_ids,
            "added_quantity": quantity,
            "add_price": price,
            "previous_quantity": current_quantity,
            "new_quantity": new_quantity,
            "previous_cost_price": current_cost_price,
            "new_cost_price": new_cost_price,
            "asset_transaction_id": asset_transaction.id,
            "order_transaction_id": order_transaction.id
        }

    @staticmethod
    def _create_orders(
        db: Session,
        user_id: int,
        figure_id: int,
        quantity: int,
        price: float
    ) -> list[Order]:
        """
        创建已完成状态的订单（补仓视同已完成购买）

        补仓订单特点:
        - 状态为"已完成"
        - 每体手办创建一个独立订单
        - 定金=单价，尾款=0（视为全款已付）
        - 币种默认为CNY
        - 备注中记录补仓详情
        """
        now = datetime.now()
        orders = []

        for i in range(quantity):
            # 格式化备注信息: yyyy-mm-dd hh:mm 花费多少补仓价格 补仓购入
            remarks = f"{now.strftime('%Y-%m-%d %H:%M')} 花费¥{price} 补仓购入"

            order = Order(
                user_id=user_id,
                figure_id=figure_id,
                deposit=price,  # 定金=单价（每体一个订单）
                deposit_currency="CNY",
                balance=0,  # 尾款=0
                balance_currency="CNY",
                status="已完成",  # 补仓视同已完成购买
                shop_name=None,  # 补仓订单不填充购买店铺
                shop_contact="",
                tracking_number="",
                remarks=remarks  # 在备注中记录补仓详情
            )
            db.add(order)
            orders.append(order)

        db.flush()  # 获取所有order.id

        return orders

    @staticmethod
    def _create_asset_transaction(
        db: Session,
        user_id: int,
        figure_id: int,
        order_id: int,
        quantity: int,
        price: float
    ) -> AssetTransaction:
        """
        创建asset_transactions记录（买入）
        """
        total_amount = price * quantity

        transaction = AssetTransaction(
            user_id=user_id,
            figure_id=figure_id,
            order_id=order_id,
            transaction_type="buy",
            price=price,
            quantity=quantity,
            total_amount=total_amount,
            remaining_quantity=quantity,
            notes=f"补仓买入: {quantity}体，补仓价格: ¥{price}/体"
        )
        db.add(transaction)
        db.flush()

        return transaction

    @staticmethod
    def _create_order_transaction(
        db: Session,
        user_id: int,
        figure_id: int,
        order_id: int,
        quantity: int,
        price: float
    ) -> OrderTransaction:
        """
        创建order_transactions记录（资金流出）
        """
        total_amount = price * quantity

        transaction = OrderTransaction(
            user_id=user_id,
            figure_id=figure_id,
            order_id=order_id,
            transaction_type="buy",
            direction="out",
            quantity=quantity,
            unit_price=price,
            total_amount=total_amount,
            currency="CNY",
            platform="补仓",
            transaction_date=datetime.now(),
            notes=f"补仓买入: {quantity}体 @ ¥{price}/体，总价¥{total_amount}"
        )
        db.add(transaction)
        db.flush()

        return transaction

    @staticmethod
    def _update_daily_cache_for_add_position(
        db: Session,
        user_id: int,
        quantity: int,
        price: float
    ) -> None:
        """
        更新日涨跌缓存（新买入部分按买入价=市值处理，贡献0%波动）

        市值法处理逻辑:
        - 新买入部分按买入价计入今日市值
        - 这样当日涨跌 = (原市值 + 新买入市值) - 昨日市值
        - 由于新买入市值 = 买入价 × 数量，这部分对涨跌贡献为0
        - 只有原有持仓部分产生涨跌波动
        """
        today = date.today()

        # 查询今日缓存
        today_cache = db.query(AssetValueCache).filter(
            AssetValueCache.user_id == user_id,
            AssetValueCache.cache_date == today
        ).first()

        if today_cache:
            # 更新今日缓存：增加新买入部分的市值
            # 新买入部分按买入价计入市值，当日涨跌贡献为0
            added_value = price * quantity
            today_cache.total_value += added_value
        # 如果没有今日缓存，不需要创建（下次查询时会自动创建）
