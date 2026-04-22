"""
手办价格服务
提供手办价格相关的业务逻辑，包括汇率转换、平均价格计算等
"""
from typing import TYPE_CHECKING, List
from sqlalchemy.orm import Session

if TYPE_CHECKING:
    from app.models.figure import Figure


class FigurePriceService:
    """手办价格服务类"""

    # 汇率配置：相对人民币的汇率
    EXCHANGE_RATES = {
        'CNY': 1.0,    # 人民币
        'JPY': 1/23,   # 日元：1人民币 = 23日元
        'USD': 7.0,    # 美元：1美元 = 7人民币
        'EUR': 8.0     # 欧元：1欧元 = 8人民币
    }

    @classmethod
    def convert_to_cny(cls, amount: float, currency: str) -> float:
        """
        将金额转换为人民币

        汇率：
        - 1人民币 = 23日元
        - 1美元 = 7人民币
        - 1欧元 = 8人民币

        Args:
            amount: 金额
            currency: 币种代码 (CNY/JPY/USD/EUR)

        Returns:
            float: 转换后的人民币金额
        """
        if not amount:
            return 0

        rate = cls.EXCHANGE_RATES.get(currency, 1.0)
        return amount * rate

    @classmethod
    def calculate_order_amount_cny(cls, deposit: float, deposit_currency: str,
                                   balance: float, balance_currency: str) -> float:
        """
        计算订单总金额（人民币）

        Args:
            deposit: 定金金额
            deposit_currency: 定金币种
            balance: 尾款金额
            balance_currency: 尾款币种

        Returns:
            float: 订单总金额（人民币）
        """
        deposit_cny = cls.convert_to_cny(deposit or 0, deposit_currency or 'CNY')
        balance_cny = cls.convert_to_cny(balance or 0, balance_currency or 'CNY')
        return deposit_cny + balance_cny

    @staticmethod
    def update_figure_average_purchase_price(db: Session, figure_id: int) -> float:
        """
        更新手办的平均入手价格

        根据关联的未软删除订单计算平均入手价格，并保存到数据库

        Args:
            db: 数据库会话
            figure_id: 手办ID

        Returns:
            float: 更新后的平均入手价格
        """
        from app.models.figure import Figure
        from app.models.order import Order

        # 获取手办
        figure = db.query(Figure).filter(Figure.id == figure_id).first()
        if not figure:
            return 0

        # 获取所有未软删除的订单
        orders = db.query(Order).filter(
            Order.figure_id == figure_id,
            Order.is_active == 1
        ).all()

        # 计算平均入手价格
        if orders:
            total_amount = 0
            for order in orders:
                total_amount += FigurePriceService.calculate_order_amount_cny(
                    order.deposit, order.deposit_currency,
                    order.balance, order.balance_currency
                )
            average_price = total_amount / len(orders)
        else:
            average_price = 0

        # 更新手办的平均入手价格
        figure.average_purchase_price = average_price
        db.commit()
        db.refresh(figure)

        return average_price

    @staticmethod
    def calculate_figure_average_purchase_price(figure: 'Figure', orders: List = None) -> float:
        """
        计算手办的平均入手价格（不保存到数据库）

        根据关联的订单计算平均入手价格，仅返回计算结果而不修改数据库

        Args:
            figure: 手办对象
            orders: 订单列表（可选，如果为None则从figure.orders获取）

        Returns:
            float: 计算后的平均入手价格
        """
        if orders is None:
            orders = figure.orders if figure.orders else []

        if not orders:
            return 0

        total_amount = 0
        total_quantity = 0

        for order in orders:
            order_amount = FigurePriceService.calculate_order_amount_cny(
                order.deposit, order.deposit_currency,
                order.balance, order.balance_currency
            )
            # 使用订单数量，如果没有则默认为1
            order_quantity = getattr(order, 'quantity', 1) or 1

            total_amount += order_amount
            total_quantity += order_quantity

        if total_quantity == 0:
            return 0

        return total_amount / total_quantity

    @staticmethod
    def calculate_orders_average_price(orders: List) -> float:
        """
        计算多个订单的平均价格

        Args:
            orders: 订单列表

        Returns:
            float: 平均价格
        """
        if not orders:
            return 0

        total_amount = 0
        for order in orders:
            total_amount += FigurePriceService.calculate_order_amount_cny(
                order.deposit, order.deposit_currency,
                order.balance, order.balance_currency
            )

        return total_amount / len(orders)
