"""
买入订单服务
提供买入订单详情查询和订单操作服务
采用企业级服务层架构
"""
from typing import Dict, Any, Optional, List
from sqlalchemy.orm import Session
from datetime import datetime

from app.models.order import Order
from app.models.figure import Figure
from app.models.asset import OrderTransaction


class BuyOrderService:
    """
    买入订单服务类

    提供以下核心功能：
    1. 获取买入订单详情
    2. 获取订单支付明细（全款/定金+尾款）
    3. 获取订单物流信息
    4. 更新订单备注
    5. 订单状态操作（确认入库、支付尾款等）
    """

    @classmethod
    def get_order_detail(cls, db: Session, user_id: int, order_id: int) -> Dict[str, Any]:
        """
        获取买入订单详情

        返回完整的订单信息，包括：
        - 订单基本信息
        - 手办信息
        - 支付明细
        - 物流信息
        - 备注

        Args:
            db: 数据库会话
            user_id: 用户ID
            order_id: 订单ID

        Returns:
            Dict: 订单详情数据
        """
        # 查询订单
        order = db.query(Order).filter(
            Order.id == order_id,
            Order.user_id == user_id,
            Order.is_active == 1
        ).first()

        if not order:
            return {"error": "订单不存在"}

        # 获取手办信息
        figure_info = cls._get_figure_info(db, order.figure_id)

        # 获取支付明细
        payment_details = cls._get_payment_details(db, user_id, order)

        # 获取物流信息
        logistics_info = cls._get_logistics_info(order)

        # 构建订单详情
        order_detail = {
            # 头部区信息
            "header": {
                "order_number": f"ORDER-{order.created_at.strftime('%Y%m%d')}-{order.id:03d}" if order.created_at else f"ORDER-{order.id:03d}",
                "figure_image": figure_info.get("image", ""),
                "figure_name": figure_info.get("name", "未知手办"),
                "figure_series": figure_info.get("series", ""),
                "quantity": 1,
                "platform": order.shop_name or "-"
            },

            # 订单信息区
            "order_info": {
                "order_id": order.id,
                "order_number": f"ORDER-{order.created_at.strftime('%Y%m%d')}-{order.id:03d}" if order.created_at else f"ORDER-{order.id:03d}",
                "order_type": cls._get_order_type(order),
                "platform": order.shop_name or "-",
                "order_time": order.created_at.strftime("%Y-%m-%d %H:%M:%S") if order.created_at else "-",
                "status": cls._format_status(order.status),
                "status_code": order.status
            },

            # 支付明细区
            "payment": payment_details,

            # 物流信息区
            "logistics": logistics_info,

            # 备注区
            "remarks": order.remarks or ""
        }

        return order_detail

    @staticmethod
    def _get_figure_info(db: Session, figure_id: Optional[int]) -> Dict[str, Any]:
        """获取手办信息"""
        if not figure_id:
            return {"name": "未知手办", "series": "", "image": ""}

        figure = db.query(Figure).filter(Figure.id == figure_id).first()
        if not figure:
            return {"name": "未知手办", "series": "", "image": ""}

        return {
            "name": figure.name or "未知手办",
            "series": figure.series or "",
            "image": figure.image_url or ""
        }

    @classmethod
    def _get_order_type(cls, order: Order) -> str:
        """
        判断订单类型

        根据定金和尾款判断：
        - 定金>0 且 尾款>0：全款预定
        - 定金>0 且 尾款=0：散货
        - 定金=0 且 尾款>0：现货
        - 其他：补仓
        """
        deposit = order.deposit or 0
        balance = order.balance or 0

        if deposit > 0 and balance > 0:
            return "全款预定"
        elif deposit > 0 and balance == 0:
            return "散货"
        elif deposit == 0 and balance > 0:
            return "现货"
        else:
            return "补仓"

    @classmethod
    def _format_status(cls, status: str) -> Dict[str, Any]:
        """
        格式化订单状态

        返回状态标签和颜色
        """
        status_map = {
            "已完成": {"label": "已入库", "color": "green", "icon": "✅"},
            "已支付": {"label": "待付尾款", "color": "orange", "icon": "⏳"},
            "未支付": {"label": "待支付", "color": "gray", "icon": "⏳"},
            "已取消": {"label": "已取消", "color": "gray", "icon": "❌"}
        }
        return status_map.get(status, {"label": status, "color": "gray", "icon": ""})

    @classmethod
    def _get_payment_details(cls, db: Session, user_id: int, order: Order) -> Dict[str, Any]:
        """
        获取支付明细

        根据订单类型返回不同的支付明细格式：
        - 全款/现货：单条支付记录
        - 预定：定金+尾款时间线
        """
        deposit = order.deposit or 0
        balance = order.balance or 0
        total_amount = deposit + balance

        # 查询关联的交易记录
        transactions = db.query(OrderTransaction).filter(
            OrderTransaction.user_id == user_id,
            OrderTransaction.order_id == order.id,
            OrderTransaction.is_active == True
        ).order_by(OrderTransaction.transaction_date.asc()).all()

        # 构建支付明细列表
        payment_items = []
        for tx in transactions:
            if tx.transaction_type in ["buy", "deposit", "balance"]:
                payment_items.append({
                    "type": cls._map_payment_type(tx.transaction_type),
                    "amount": tx.total_amount or 0,
                    "date": tx.transaction_date.strftime("%m-%d") if tx.transaction_date else "-",
                    "full_date": tx.transaction_date.strftime("%Y-%m-%d %H:%M:%S") if tx.transaction_date else "-",
                    "method": tx.payment_method or "-",
                    "status": "paid" if tx.direction == "out" else "pending",
                    "transaction_no": tx.transaction_no or f"TRX-{tx.id}"
                })

        # 如果没有交易记录，根据订单状态构建默认支付明细
        if not payment_items:
            if deposit > 0:
                payment_items.append({
                    "type": "定金",
                    "amount": deposit,
                    "date": order.created_at.strftime("%m-%d") if order.created_at else "-",
                    "full_date": order.created_at.strftime("%Y-%m-%d %H:%M:%S") if order.created_at else "-",
                    "method": "-",
                    "status": "paid" if order.status in ["已支付", "已完成"] else "pending",
                    "transaction_no": "-"
                })
            if balance > 0:
                payment_items.append({
                    "type": "尾款",
                    "amount": balance,
                    "date": order.due_date.strftime("%m-%d") if order.due_date else "-",
                    "full_date": order.due_date.strftime("%Y-%m-%d") if order.due_date else "-",
                    "method": "-",
                    "status": "paid" if order.status == "已完成" else "pending",
                    "transaction_no": "-"
                })

        return {
            "payment_type": cls._get_order_type(order),
            "total_amount": total_amount,
            "items": payment_items,
            "deposit": deposit,
            "balance": balance
        }

    @staticmethod
    def _map_payment_type(tx_type: str) -> str:
        """映射交易类型为中文"""
        type_map = {
            "buy": "全款",
            "deposit": "定金",
            "balance": "尾款"
        }
        return type_map.get(tx_type, tx_type)

    @staticmethod
    def _get_logistics_info(order: Order) -> Dict[str, Any]:
        """获取物流信息"""
        has_tracking = bool(order.tracking_number)

        return {
            "tracking_number": order.tracking_number or "",
            "logistics_company": cls._detect_logistics_company(order.tracking_number) if has_tracking else "",
            "status": "已签收" if order.status == "已完成" else ("运输中" if has_tracking else "待发货"),
            "delivery_time": "",  # 可从物流接口获取
            "has_tracking": has_tracking
        }

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
    def update_remarks(cls, db: Session, user_id: int, order_id: int, remarks: str) -> Dict[str, Any]:
        """
        更新订单备注

        Args:
            db: 数据库会话
            user_id: 用户ID
            order_id: 订单ID
            remarks: 新备注内容

        Returns:
            Dict: 更新结果
        """
        order = db.query(Order).filter(
            Order.id == order_id,
            Order.user_id == user_id,
            Order.is_active == 1
        ).first()

        if not order:
            return {"success": False, "error": "订单不存在"}

        order.remarks = remarks
        order.updated_at = datetime.now()
        db.commit()

        return {"success": True, "remarks": remarks}

    @classmethod
    def get_available_actions(cls, status: str) -> List[Dict[str, Any]]:
        """
        根据订单状态获取可用操作按钮

        Args:
            status: 订单状态

        Returns:
            List: 可用操作按钮列表
        """
        actions_map = {
            "已完成": [
                {"key": "edit_remarks", "label": "编辑备注", "type": "default"},
                {"key": "close", "label": "关闭", "type": "primary"}
            ],
            "已支付": [
                {"key": "pay_balance", "label": "支付尾款", "type": "primary"},
                {"key": "cancel_order", "label": "取消订单", "type": "danger"},
                {"key": "edit_remarks", "label": "编辑备注", "type": "default"},
                {"key": "close", "label": "关闭", "type": "default"}
            ],
            "未支付": [
                {"key": "confirm_stock", "label": "确认入库", "type": "primary"},
                {"key": "edit_remarks", "label": "编辑备注", "type": "default"},
                {"key": "close", "label": "关闭", "type": "default"}
            ],
            "运输中": [
                {"key": "confirm_receipt", "label": "确认收货/入库", "type": "primary"},
                {"key": "edit_remarks", "label": "编辑备注", "type": "default"},
                {"key": "close", "label": "关闭", "type": "default"}
            ],
            "已取消": [
                {"key": "view_refund", "label": "查看退款流水", "type": "default"},
                {"key": "close", "label": "关闭", "type": "primary"}
            ]
        }

        return actions_map.get(status, actions_map.get("未支付", []))
