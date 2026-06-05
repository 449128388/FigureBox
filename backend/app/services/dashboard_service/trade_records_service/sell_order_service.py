"""
卖出订单服务
提供卖出订单详情查询和订单操作服务
采用企业级服务层架构
"""
from typing import Dict, Any, Optional
from sqlalchemy.orm import Session
from datetime import datetime

from app.models.sold_order import SoldOrder
from app.models.figure import Figure


# 汇率配置：相对人民币的汇率
EXCHANGE_RATES = {
    'CNY': 1.0,    # 人民币
    'JPY': 1/23,   # 日元：1人民币 = 23日元
    'USD': 7.0,    # 美元：1美元 = 7人民币
    'EUR': 8.0     # 欧元：1欧元 = 8人民币
}


class SellOrderService:
    """
    卖出订单服务类

    提供以下核心功能：
    1. 获取卖出订单详情
    2. 获取收款明细
    3. 计算盈亏信息
    4. 获取物流信息
    5. 更新订单备注和物流
    """

    @classmethod
    def get_order_detail(cls, db: Session, user_id: int, sold_order_id: int) -> Dict[str, Any]:
        """
        获取卖出订单详情

        返回完整的订单信息，包括：
        - 头部信息（订单号）
        - 手办信息
        - 订单信息
        - 收款明细
        - 盈亏信息
        - 物流信息
        - 买家信息
        - 备注

        Args:
            db: 数据库会话
            user_id: 用户ID
            sold_order_id: 卖出订单ID

        Returns:
            Dict: 订单详情数据
        """
        # 查询卖出订单
        sold_order = db.query(SoldOrder).filter(
            SoldOrder.id == sold_order_id,
            SoldOrder.user_id == user_id,
            SoldOrder.is_active == 1
        ).first()

        if not sold_order:
            return {"error": "订单不存在"}

        # 获取手办信息
        figure_info = cls._get_figure_info(db, sold_order.figure_id)

        # 构建订单详情
        order_detail = {
            # 头部区信息
            "header": {
                "order_number": sold_order.order_number or str(sold_order.id)
            },

            # 手办信息区
            "figure": {
                "name": figure_info.get("name", "未知手办"),
                "image": figure_info.get("image", ""),
                "quantity": sold_order.quantity or 1,
                "platform": sold_order.sell_platform or "-"
            },

            # 订单信息区
            "order_info": {
                "order_id": sold_order.id,
                "order_number": sold_order.order_number or str(sold_order.id),
                "sell_platform": cls._format_platform(sold_order.sell_platform),
                "transaction_date": sold_order.created_at.strftime("%Y-%m-%d %H:%M:%S") if sold_order.created_at else "-",
                "status": "已完成"
            },

            # 收款明细区
            "payment": cls._get_payment_details(sold_order),

            # 盈亏信息区
            "profit": cls._get_profit_info(sold_order),

            # 物流信息区
            "logistics": cls._get_logistics_info(sold_order),

            # 买家信息区
            "buyer": {
                "phone": sold_order.buyer_phone or "",
                "address": sold_order.buyer_address or ""
            },

            # 备注区
            "remarks": sold_order.remark or ""
        }

        return order_detail

    @staticmethod
    def _get_figure_info(db: Session, figure_id: Optional[int]) -> Dict[str, Any]:
        """获取手办信息"""
        if not figure_id:
            return {"name": "未知手办", "image": ""}

        figure = db.query(Figure).filter(Figure.id == figure_id).first()
        if not figure:
            return {"name": "未知手办", "image": ""}

        # 从 images JSON 数组中获取第一张图片
        image_url = ""
        if figure.images and isinstance(figure.images, list) and len(figure.images) > 0:
            image_url = figure.images[0]

        return {
            "name": figure.name or "未知手办",
            "image": image_url
        }

    @staticmethod
    def _format_platform(platform: Optional[str]) -> str:
        """格式化平台名称"""
        if not platform:
            return "-"
        # 如果是闲鱼，添加鱼小铺标识
        if platform == "闲鱼":
            return "闲鱼（鱼小铺）"
        return platform

    @classmethod
    def _get_payment_details(cls, sold_order: SoldOrder) -> Dict[str, Any]:
        """
        获取收款明细

        包含：
        - 卖出价格
        - 运费
        - 平台手续费
        - 实到账金额
        """
        sell_price = sold_order.sell_price or 0
        shipping_fee = abs(sold_order.shipping_fee or 0)
        platform_fee = abs(sold_order.platform_fee or 0)

        # 计算实到账（卖出价 - 运费 - 手续费）
        net_received = sell_price - shipping_fee - platform_fee

        # 转换为人民币
        sell_price_cny = cls._to_cny(sell_price, sold_order.sell_price_currency)
        shipping_fee_cny = cls._to_cny(shipping_fee, sold_order.shipping_fee_currency)
        platform_fee_cny = cls._to_cny(platform_fee, sold_order.platform_fee_currency)
        net_received_cny = sell_price_cny - shipping_fee_cny - platform_fee_cny

        return {
            "sell_price": sell_price,
            "sell_price_currency": sold_order.sell_price_currency or "CNY",
            "shipping_fee": shipping_fee,
            "shipping_fee_currency": sold_order.shipping_fee_currency or "CNY",
            "platform_fee": platform_fee,
            "platform_fee_currency": sold_order.platform_fee_currency or "CNY",
            "net_received": round(net_received_cny, 2),
            "net_received_currency": "CNY"
        }

    @classmethod
    def _get_profit_info(cls, sold_order: SoldOrder) -> Dict[str, Any]:
        """
        获取盈亏信息

        包含：
        - 成本单价
        - 成本合计
        - 净利润
        - 利润率
        """
        sell_price = sold_order.sell_price or 0
        shipping_fee = abs(sold_order.shipping_fee or 0)
        platform_fee = abs(sold_order.platform_fee or 0)
        cost_price = sold_order.cost_price or 0
        quantity = sold_order.quantity or 1

        # 计算净到账
        net_received = sell_price - shipping_fee - platform_fee

        # 转换为人民币
        net_received_cny = cls._to_cny(net_received, sold_order.sell_price_currency)
        cost_price_cny = cls._to_cny(cost_price, sold_order.cost_price_currency)

        # 成本合计
        total_cost = cost_price_cny * quantity

        # 净利润 = 净到账 - 成本合计
        net_profit = net_received_cny - total_cost

        # 利润率 = 净利润 / 成本合计 * 100%
        profit_rate = (net_profit / total_cost * 100) if total_cost > 0 else 0

        return {
            "cost_price": cost_price,
            "cost_price_currency": sold_order.cost_price_currency or "CNY",
            "total_cost": round(total_cost, 2),
            "net_profit": round(net_profit, 2),
            "profit_rate": round(profit_rate, 1)
        }

    @classmethod
    def _get_logistics_info(cls, sold_order: SoldOrder) -> Dict[str, Any]:
        """获取物流信息"""
        has_tracking = bool(sold_order.tracking_number)

        # 优先使用数据库中的物流公司字段，如果为空再根据单号识别
        if sold_order.logistics_company:
            logistics_company = sold_order.logistics_company
        elif sold_order.tracking_number:
            logistics_company = cls._detect_logistics_company(sold_order.tracking_number)
        else:
            logistics_company = ""

        return {
            "tracking_number": sold_order.tracking_number or "",
            "logistics_company": logistics_company,
            "status": "已签收" if has_tracking else "待发货",
            "has_tracking": has_tracking
        }

    @classmethod
    def _to_cny(cls, amount: float, currency: Optional[str]) -> float:
        """将金额转换为人民币"""
        if not currency:
            currency = "CNY"
        rate = EXCHANGE_RATES.get(currency, 1.0)
        return amount * rate

    @staticmethod
    def _detect_logistics_company(tracking_number: Optional[str]) -> str:
        """根据单号识别物流公司"""
        if not tracking_number:
            return ""

        # 简单的单号规则识别
        if tracking_number.startswith("SF"):
            return "顺丰速运"
        elif tracking_number.startswith("YT"):
            return "圆通速递"
        elif tracking_number.startswith("ZT"):
            return "中通快递"
        elif tracking_number.startswith("YD"):
            return "韵达速递"
        elif tracking_number.isdigit() and len(tracking_number) == 13:
            return "EMS"
        else:
            return "其他快递"

    @classmethod
    def update_remarks(cls, db: Session, user_id: int, sold_order_id: int, remarks: str) -> Dict[str, Any]:
        """
        更新订单备注

        Args:
            db: 数据库会话
            user_id: 用户ID
            sold_order_id: 卖出订单ID
            remarks: 新备注内容

        Returns:
            Dict: 更新结果
        """
        sold_order = db.query(SoldOrder).filter(
            SoldOrder.id == sold_order_id,
            SoldOrder.user_id == user_id,
            SoldOrder.is_active == 1
        ).first()

        if not sold_order:
            return {"success": False, "error": "订单不存在"}

        sold_order.remark = remarks
        db.commit()

        return {"success": True, "remarks": remarks}

    @classmethod
    def update_logistics(cls, db: Session, user_id: int, sold_order_id: int, tracking_number: str) -> Dict[str, Any]:
        """
        更新订单物流信息

        Args:
            db: 数据库会话
            user_id: 用户ID
            sold_order_id: 卖出订单ID
            tracking_number: 快递单号

        Returns:
            Dict: 更新结果
        """
        sold_order = db.query(SoldOrder).filter(
            SoldOrder.id == sold_order_id,
            SoldOrder.user_id == user_id,
            SoldOrder.is_active == 1
        ).first()

        if not sold_order:
            return {"success": False, "error": "订单不存在"}

        # 更新物流信息
        sold_order.tracking_number = tracking_number
        sold_order.logistics_company = cls._detect_logistics_company(tracking_number)
        sold_order.updated_at = datetime.now()
        db.commit()

        return {
            "success": True,
            "tracking_number": tracking_number,
            "logistics_company": sold_order.logistics_company,
            "status": "已发货"
        }
