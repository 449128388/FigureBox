"""
补仓服务
提供补仓相关的业务逻辑，包括创建订单、更新库存、计算加权平均成本等
采用企业级服务层架构
"""
from datetime import date, datetime
from typing import Dict, Any, Tuple

from sqlalchemy.orm import Session

from app.models.figure import Figure
from app.models.order import Order
from app.models.transaction import OrderTransaction, AssetTransaction
from app.models.asset import AssetValueCache


class AddPositionService:
    """补仓服务类"""

    @classmethod
    def add_position(
        cls,
        db: Session,
        figure_id: int,
        user_id: int,
        quantity: int,
        price: float
    ) -> Dict[str, Any]:
        """
        执行补仓操作

        流程:
        1. 获取手办信息
        2. 计算新的加权平均成本
        3. 创建已完成的订单
        4. 创建 order_transactions 记录
        5. 创建 asset_transactions 记录
        6. 更新手办数量和平均入手价格
        7. 更新市值缓存（用于日涨跌计算）

        Args:
            db: 数据库会话
            figure_id: 手办ID
            user_id: 用户ID
            quantity: 补仓数量
            price: 补仓单价

        Returns:
            Dict包含补仓结果信息
        """
        # 1. 获取手办信息
        figure = db.query(Figure).filter(Figure.id == figure_id).first()
        if not figure:
            raise ValueError(f"手办不存在: {figure_id}")

        # 2. 计算加权平均成本
        current_quantity = figure.quantity or 1
        current_avg_price = figure.average_purchase_price or 0
        total_cost = current_avg_price * current_quantity
        add_cost = price * quantity
        new_quantity = current_quantity + quantity
        new_avg_price = (total_cost + add_cost) / new_quantity if new_quantity > 0 else 0

        # 3. 创建已完成的订单
        order = cls._create_order(db, figure_id, user_id, quantity, price)

        # 4. 创建 order_transactions 记录
        cls._create_order_transaction(db, order.id, figure_id, quantity, price, user_id)

        # 5. 创建 asset_transactions 记录
        cls._create_asset_transaction(db, figure_id, order.id, quantity, price, user_id)

        # 6. 更新手办数量和平均入手价格
        old_quantity = figure.quantity or 1
        old_avg_price = figure.average_purchase_price or 0
        figure.quantity = new_quantity
        figure.average_purchase_price = new_avg_price
        figure.current_value = (figure.market_price or figure.price or 0) * new_quantity

        # 7. 更新市值缓存（新买入部分当日不计入涨跌）
        # 原理：将新买入部分的成本直接加到今日缓存中
        # 这样日涨跌计算时，新买入部分贡献为0
        cls._update_cache_for_add_position(db, user_id, price * quantity)

        # 提交所有更改
        db.commit()
        db.refresh(figure)
        db.refresh(order)

        return {
            "figure_id": figure_id,
            "figure_name": figure.name,
            "old_quantity": old_quantity,
            "new_quantity": new_quantity,
            "old_avg_price": old_avg_price,
            "new_avg_price": new_avg_price,
            "add_quantity": quantity,
            "add_price": price,
            "order_id": order.id,
            "total_cost": total_cost + add_cost
        }

    @staticmethod
    def _create_order(
        db: Session,
        figure_id: int,
        user_id: int,
        quantity: int,
        price: float
    ) -> Order:
        """
        创建已完成的补仓订单
        """
        total_amount = price * quantity

        order = Order(
            figure_id=figure_id,
            user_id=user_id,
            deposit=0,  # 补仓订单没有定金
            deposit_currency="CNY",
            balance=total_amount,  # 全额作为尾款
            balance_currency="CNY",
            quantity=quantity,
            total_amount=total_amount,
            status="已完成",  # 直接标记为已完成
            shop_name="补仓",
            shop_contact="",
            tracking_number="",
            order_number=f"BC{datetime.now().strftime('%Y%m%d%H%M%S')}",  # 补仓订单号
            order_date=date.today(),
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        db.add(order)
        db.flush()  # 获取order.id

        return order

    @staticmethod
    def _create_order_transaction(
        db: Session,
        order_id: int,
        figure_id: int,
        quantity: int,
        price: float,
        user_id: int
    ) -> None:
        """
        创建订单交易记录（order_transactions）
        """
        total_amount = price * quantity

        transaction = OrderTransaction(
            order_id=order_id,
            figure_id=figure_id,
            transaction_type="补仓",
            quantity=quantity,
            unit_price=price,
            total_amount=total_amount,
            currency="CNY",
            notes=f"补仓买入: {quantity}体 @ ¥{price}/体",
            user_id=user_id,
            created_at=datetime.now()
        )
        db.add(transaction)

    @staticmethod
    def _create_asset_transaction(
        db: Session,
        figure_id: int,
        order_id: int,
        quantity: int,
        price: float,
        user_id: int
    ) -> None:
        """
        创建资产交易记录（asset_transactions）
        """
        total_amount = price * quantity

        transaction = AssetTransaction(
            figure_id=figure_id,
            order_id=order_id,
            transaction_type="补仓",
            quantity=quantity,
            unit_price=price,
            total_amount=total_amount,
            price=price,  # 成本价
            notes=f"补仓买入: 增加{quantity}体库存，成本¥{price}/体",
            user_id=user_id,
            transaction_date=date.today(),
            created_at=datetime.now()
        )
        db.add(transaction)

    @staticmethod
    def _update_cache_for_add_position(
        db: Session,
        user_id: int,
        add_cost: float
    ) -> None:
        """
        更新市值缓存以处理补仓的日涨跌计算

        原理：
        - 新买入部分当日不计入涨跌
        - 将新买入的成本直接加到今日缓存中
        - 这样日涨跌计算时：今日总资产 - 昨日缓存 - 新买入成本 = 原有资产涨跌

        Args:
            db: 数据库会话
            user_id: 用户ID
            add_cost: 新买入的成本金额
        """
        today = date.today()
        today_cache = db.query(AssetValueCache).filter(
            AssetValueCache.user_id == user_id,
            AssetValueCache.cache_date == today
        ).first()

        if today_cache:
            # 更新今日缓存：加上新买入的成本
            # 这样日涨跌 = (原资产价值 + 新买入成本) - (昨日缓存 + 新买入成本) = 原资产价值 - 昨日缓存
            today_cache.total_value += add_cost
        else:
            # 如果没有今日缓存，创建一个包含新买入成本的缓存
            # 这种情况通常发生在首次补仓时
            today_cache = AssetValueCache(
                user_id=user_id,
                total_value=add_cost,
                cache_date=today
            )
            db.add(today_cache)
