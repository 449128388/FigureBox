"""
资产交易服务
提供资产交易记录相关的业务逻辑，包括创建、查询、更新交易记录
支持股票式补仓功能，记录买入卖出交易
"""
from datetime import datetime
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import desc, func

from app.models.asset import AssetTransaction
from app.models.figure import Figure
from app.models.order import Order


class AssetTransactionService:
    """资产交易服务类"""

    @staticmethod
    def create_transaction_from_figure(
        db: Session,
        user_id: int,
        figure_id: int,
        price: float,
        quantity: int = 1,
        order_id: Optional[int] = None
    ) -> AssetTransaction:
        """
        从手办数据创建资产交易记录（买入类型）

        使用场景：
        - 用户创建手办时，自动创建对应的买入交易记录
        - 用于记录资产的初始成本

        Args:
            db: 数据库会话
            user_id: 用户ID
            figure_id: 手办ID
            price: 单价
            quantity: 数量，默认为1
            order_id: 关联订单ID，可选

        Returns:
            创建的交易记录对象
        """
        # 对于已取消订单(quantity=0)，total_amount应该等于price（定金金额）
        # 对于正常订单，total_amount = price * quantity
        total_amount = price if quantity == 0 else price * quantity

        transaction = AssetTransaction(
            user_id=user_id,
            figure_id=figure_id,
            order_id=order_id,
            transaction_type="buy",
            price=price,
            quantity=quantity,
            total_amount=total_amount,
            remaining_quantity=quantity,  # 初始剩余数量等于购买数量
            notes="自动创建：从订单管理数据中创建"
        )

        db.add(transaction)
        db.flush()  # 获取ID但不提交

        return transaction

    @staticmethod
    def link_order_to_existing_transaction(
        db: Session,
        user_id: int,
        figure_id: int,
        order: Order,
        quantity: int = 1
    ) -> Optional[AssetTransaction]:
        """
        将订单关联到现有的库存交易记录（补录凭证模式）

        使用场景：
        - 用户创建订单时，将订单关联到手办创建时的原始交易记录
        - 不新增交易记录，避免手办数量虚增
        - 更新原有记录的 order_id 和备注信息

        查找逻辑：
        1. 查找该手办下无订单关联的买入记录（order_id IS NULL）
        2. 如果找到，更新 order_id 并添加补录备注
        3. 如果没找到，返回 None（表示所有库存记录都已关联订单）

        Args:
            db: Session: 数据库会话
            user_id: 用户ID
            figure_id: 手办ID
            order: 订单对象
            quantity: 数量，默认为1

        Returns:
            更新的交易记录对象，如果没有可关联的记录则返回 None
        """
        # 查找该手办下无订单关联且有剩余库存的买入记录
        existing_transaction = db.query(AssetTransaction).filter(
            AssetTransaction.user_id == user_id,
            AssetTransaction.figure_id == figure_id,
            AssetTransaction.transaction_type == "buy",
            AssetTransaction.order_id.is_(None),
            AssetTransaction.remaining_quantity > 0
        ).first()

        if existing_transaction:
            # 更新现有记录，关联订单
            existing_transaction.order_id = order.id
            existing_transaction.notes = f"补录凭证：订单 #{order.id} 关联到原有库存记录"
            db.flush()
            return existing_transaction

        # 没有找到可关联的记录，返回 None
        # 这种情况可能发生在：手办创建时的记录已经关联了其他订单
        return None

    @staticmethod
    def create_sell_transaction(
        db: Session,
        user_id: int,
        figure_id: int,
        price: float,
        quantity: int,
        notes: Optional[str] = None
    ) -> Optional[AssetTransaction]:
        """
        创建卖出交易记录

        使用场景：
        - 用户卖出部分或全部手办时
        - 自动扣减剩余持仓数量

        Args:
            db: 数据库会话
            user_id: 用户ID
            figure_id: 手办ID
            price: 卖出单价
            quantity: 卖出数量
            notes: 备注

        Returns:
            创建的交易记录对象，如果持仓不足返回None
        """
        # 检查总持仓数量
        total_remaining = db.query(func.sum(AssetTransaction.remaining_quantity)).filter(
            AssetTransaction.user_id == user_id,
            AssetTransaction.figure_id == figure_id,
            AssetTransaction.transaction_type == "buy"
        ).scalar() or 0

        if total_remaining < quantity:
            raise ValueError(f"持仓不足，当前持仓：{total_remaining}，尝试卖出：{quantity}")

        # 创建卖出交易记录
        total_amount = price * quantity
        transaction = AssetTransaction(
            user_id=user_id,
            figure_id=figure_id,
            order_id=None,
            transaction_type="sell",
            price=price,
            quantity=quantity,
            total_amount=total_amount,
            remaining_quantity=0,  # 卖出记录的剩余数量为0
            notes=notes or "卖出交易"
        )
        db.add(transaction)

        # 扣减买入记录的剩余数量（先进先出）
        remaining_to_deduct = quantity
        buy_transactions = db.query(AssetTransaction).filter(
            AssetTransaction.user_id == user_id,
            AssetTransaction.figure_id == figure_id,
            AssetTransaction.transaction_type == "buy",
            AssetTransaction.remaining_quantity > 0
        ).order_by(AssetTransaction.transaction_date.asc()).all()

        for buy_tx in buy_transactions:
            if remaining_to_deduct <= 0:
                break

            deduct_amount = min(buy_tx.remaining_quantity, remaining_to_deduct)
            buy_tx.remaining_quantity -= deduct_amount
            remaining_to_deduct -= deduct_amount

        db.flush()
        return transaction

    @staticmethod
    def get_transactions_by_figure(
        db: Session,
        user_id: int,
        figure_id: int
    ) -> List[AssetTransaction]:
        """
        获取指定手办的所有交易记录

        Args:
            db: 数据库会话
            user_id: 用户ID
            figure_id: 手办ID

        Returns:
            交易记录列表，按时间倒序
        """
        return db.query(AssetTransaction).filter(
            AssetTransaction.user_id == user_id,
            AssetTransaction.figure_id == figure_id
        ).order_by(desc(AssetTransaction.transaction_date)).all()

    @staticmethod
    def get_all_transactions(
        db: Session,
        user_id: int,
        transaction_type: Optional[str] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[AssetTransaction]:
        """
        获取用户的所有交易记录

        Args:
            db: 数据库会话
            user_id: 用户ID
            transaction_type: 交易类型过滤（buy/sell）
            skip: 跳过数量
            limit: 限制数量

        Returns:
            交易记录列表
        """
        query = db.query(AssetTransaction).filter(
            AssetTransaction.user_id == user_id
        )

        if transaction_type:
            query = query.filter(AssetTransaction.transaction_type == transaction_type)

        return query.order_by(desc(AssetTransaction.transaction_date)).offset(skip).limit(limit).all()

    @staticmethod
    def calculate_average_cost(
        db: Session,
        user_id: int,
        figure_id: int
    ) -> Dict[str, Any]:
        """
        计算手办的平均成本（补仓核心算法）

        Args:
            db: 数据库会话
            user_id: 用户ID
            figure_id: 手办ID

        Returns:
            包含平均成本、总持仓、总成本的字典
        """
        # 获取所有买入记录
        buy_transactions = db.query(AssetTransaction).filter(
            AssetTransaction.user_id == user_id,
            AssetTransaction.figure_id == figure_id,
            AssetTransaction.transaction_type == "buy"
        ).all()

        total_cost = sum(tx.total_amount for tx in buy_transactions)
        total_quantity = sum(tx.quantity for tx in buy_transactions)
        total_remaining = sum(tx.remaining_quantity or 0 for tx in buy_transactions)

        average_cost = total_cost / total_quantity if total_quantity > 0 else 0

        return {
            "average_cost": round(average_cost, 2),
            "total_quantity": total_quantity,
            "total_remaining": total_remaining,
            "total_cost": round(total_cost, 2)
        }

    @staticmethod
    def calculate_profit(
        db: Session,
        user_id: int,
        figure_id: int,
        current_market_price: Optional[float] = None
    ) -> Dict[str, Any]:
        """
        计算手办的盈亏情况

        Args:
            db: 数据库会话
            user_id: 用户ID
            figure_id: 手办ID
            current_market_price: 当前市场价格，可选

        Returns:
            包含盈亏数据的字典
        """
        cost_info = AssetTransactionService.calculate_average_cost(db, user_id, figure_id)

        # 获取卖出记录
        sell_transactions = db.query(AssetTransaction).filter(
            AssetTransaction.user_id == user_id,
            AssetTransaction.figure_id == figure_id,
            AssetTransaction.transaction_type == "sell"
        ).all()

        total_sell_revenue = sum(tx.total_amount for tx in sell_transactions)
        total_sell_quantity = sum(tx.quantity for tx in sell_transactions)

        result = {
            "average_cost": cost_info["average_cost"],
            "total_cost": cost_info["total_cost"],
            "total_remaining": cost_info["total_remaining"],
            "total_sell_revenue": round(total_sell_revenue, 2),
            "total_sell_quantity": total_sell_quantity,
            "realized_profit": round(total_sell_revenue - (cost_info["average_cost"] * total_sell_quantity), 2) if total_sell_quantity > 0 else 0
        }

        # 计算未实现盈亏（基于当前市场价格）
        if current_market_price and cost_info["total_remaining"] > 0:
            unrealized_profit = (current_market_price - cost_info["average_cost"]) * cost_info["total_remaining"]
            result["current_market_price"] = current_market_price
            result["unrealized_profit"] = round(unrealized_profit, 2)
            result["total_profit"] = round(result["realized_profit"] + unrealized_profit, 2)

        return result

    @staticmethod
    def delete_transaction(
        db: Session,
        transaction_id: int,
        user_id: int
    ) -> bool:
        """
        删除交易记录

        Args:
            db: 数据库会话
            transaction_id: 交易记录ID
            user_id: 用户ID

        Returns:
            是否删除成功
        """
        transaction = db.query(AssetTransaction).filter(
            AssetTransaction.id == transaction_id,
            AssetTransaction.user_id == user_id
        ).first()

        if not transaction:
            return False

        db.delete(transaction)
        db.flush()
        return True

    @staticmethod
    def create_quantity_adjustment_transaction(
        db: Session,
        user_id: int,
        figure_id: int,
        quantity_change: int,
        price: float,
        original_quantity: int,
        new_quantity: int
    ) -> AssetTransaction:
        """
        创建数量调整冲正交易记录

        使用场景：
        - 用户在手办管理中修改手办数量时
        - 数量增加：创建买入交易（补录）
        - 数量减少：创建冲正交易（adjust类型，quantity为负数）

        Args:
            db: 数据库会话
            user_id: 用户ID
            figure_id: 手办ID
            quantity_change: 数量变化（正数表示增加，负数表示减少）
            price: 单价（使用当前手办的入手价格）
            original_quantity: 原始数量
            new_quantity: 新数量

        Returns:
            创建的交易记录对象
        """
        total_amount = price * abs(quantity_change)

        if quantity_change > 0:
            # 数量增加：创建补录买入交易
            transaction = AssetTransaction(
                user_id=user_id,
                figure_id=figure_id,
                order_id=None,
                transaction_type="buy",
                price=price,
                quantity=quantity_change,
                total_amount=total_amount,
                remaining_quantity=quantity_change,
                notes=f"数量调整补录：{original_quantity} → {new_quantity}（+{quantity_change}）"
            )
        else:
            # 数量减少：创建冲正交易
            transaction = AssetTransaction(
                user_id=user_id,
                figure_id=figure_id,
                order_id=None,
                transaction_type="adjust",
                price=price,
                quantity=quantity_change,  # 负数
                total_amount=-total_amount,  # 负数表示减少金额
                remaining_quantity=0,  # 冲正交易不增加持仓
                notes=f"数量调整冲正：{original_quantity} → {new_quantity}（{quantity_change}）"
            )

            # 【修复】扣减买入记录的剩余数量（后进先出 LIFO）
            # 冲正场景应该撤销最近补录的数量，而不是最早的原始数量
            remaining_to_deduct = abs(quantity_change)
            buy_transactions = db.query(AssetTransaction).filter(
                AssetTransaction.user_id == user_id,
                AssetTransaction.figure_id == figure_id,
                AssetTransaction.transaction_type.in_(["buy"]),
                AssetTransaction.remaining_quantity > 0
            ).order_by(AssetTransaction.transaction_date.desc()).all()  # 【修复】desc 后进先出

            for buy_tx in buy_transactions:
                if remaining_to_deduct <= 0:
                    break
                deduct_amount = min(buy_tx.remaining_quantity, remaining_to_deduct)
                buy_tx.remaining_quantity -= deduct_amount
                remaining_to_deduct -= deduct_amount

        db.add(transaction)
        db.flush()
        return transaction

    @staticmethod
    def create_price_adjustment_transaction(
        db: Session,
        user_id: int,
        figure_id: int,
        old_price: float,
        new_price: float,
        quantity: int
    ) -> AssetTransaction:
        """
        创建价格调整记录

        使用场景：
        - 用户在手办管理中修改入手价格时
        - 记录价格变更历史

        Args:
            db: 数据库会话
            user_id: 用户ID
            figure_id: 手办ID
            old_price: 原价格
            new_price: 新价格
            quantity: 手办数量

        Returns:
            创建的交易记录对象
        """
        price_diff = new_price - old_price
        total_diff = price_diff * quantity

        transaction = AssetTransaction(
            user_id=user_id,
            figure_id=figure_id,
            order_id=None,
            transaction_type="adjust",
            price=price_diff,  # 记录价格差值
            quantity=quantity,
            total_amount=total_diff,  # 记录金额差值
            remaining_quantity=None,  # 价格调整不影响持仓数量
            notes=f"价格调整：¥{old_price} → ¥{new_price}（差值：¥{price_diff}）"
        )

        db.add(transaction)
        db.flush()
        return transaction
