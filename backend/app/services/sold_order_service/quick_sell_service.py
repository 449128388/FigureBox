"""
快速卖出服务

提供从持仓列表快速卖出的功能，简化订单创建流程
集成多模块联动：库存账、资金账、资产看板、手办状态
"""
from typing import Dict, Any
from sqlalchemy.orm import Session
from datetime import datetime

from app.models.sold_order import SoldOrder
from app.models.user import User
from app.schemas.sold_order import SoldOrderCreate
from .sold_order_crud_service import SoldOrderCrudService


class QuickSellService:
    """
    快速卖出服务类

    提供从持仓列表快速卖出的简化功能：
    1. 自动生成订单编号（QS + 时间戳）
    2. 默认使用"快速卖出"作为卖出平台
    3. 使用占位符填充非必填字段
    4. 创建时自动完成以下联动操作：
       - 创建已出售订单记录
       - 尾款管理：创建卖出订单主记录和资金流水
       - 库存账：扣减库存数量
       - 资产看板：盈亏分析数据
       - 手办聚合状态：更新库存数量和售罄状态

    所有操作在事务中执行，确保数据一致性
    """

    @staticmethod
    def _generate_order_number() -> str:
        """
        生成快速卖出订单编号
        格式：QS + 年月日时分秒 + 3位随机数
        """
        from random import randint
        now = datetime.now()
        random_suffix = randint(100, 999)
        return f"QS{now.strftime('%Y%m%d%H%M%S')}{random_suffix}"

    @staticmethod
    def create_quick_sell_order(
        db: Session,
        figure_id: int,
        figure_name: str,
        quantity: int,
        sell_price: float,
        cost_price: float,
        current_user: User
    ) -> SoldOrder:
        """
        创建快速卖出订单

        Args:
            db: 数据库会话
            figure_id: 手办ID
            figure_name: 手办名称（用于生成备注）
            quantity: 卖出数量
            sell_price: 卖出单价
            cost_price: 成本单价
            current_user: 当前用户

        Returns:
            创建的已出售订单对象

        Raises:
            ValueError: 参数校验失败
            Exception: 数据库操作失败
        """
        # 参数校验
        if not figure_id:
            raise ValueError('手办ID不能为空')
        if quantity <= 0:
            raise ValueError('卖出数量必须大于0')
        if sell_price <= 0:
            raise ValueError('卖出价格必须大于0')

        # 计算总卖出金额
        total_sell_price = sell_price * quantity
        total_cost_price = cost_price * quantity

        # 构建订单创建数据
        order_data = SoldOrderCreate(
            figure_id=figure_id,
            quantity=quantity,  # 卖出数量
            sell_price=total_sell_price,
            cost_price=total_cost_price,
            shipping_fee=0.0,  # 快速卖出默认运费为0，后续可在订单详情中修改
            platform_fee=0.0,  # 快速卖出默认平台费为0，后续可在订单详情中修改
            sell_price_currency='CNY',
            cost_price_currency='CNY',
            shipping_fee_currency='CNY',
            platform_fee_currency='CNY',
            sell_platform='快速卖出',  # 默认平台
            order_number=QuickSellService._generate_order_number(),
            buyer_phone='13800000000',  # 占位符，后续可在订单详情中修改
            buyer_address=None,
            tracking_number=None,
            shipping_date=None,
            status='已完成',  # 快速卖出默认状态为已完成
            remark=f'快速卖出 {quantity}体 {figure_name}'
        )

        # 调用标准创建服务
        return SoldOrderCrudService.create_sold_order(
            db=db,
            order_data=order_data,
            current_user=current_user
        )
