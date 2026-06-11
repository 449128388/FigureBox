"""
买入订单服务
提供买入订单详情查询和订单操作服务
采用企业级服务层架构
"""
from typing import Dict, Any, Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime

from app.models.order import Order
from app.models.figure import Figure
from app.models.asset import OrderTransaction, AssetTransaction
from app.services.asset_transaction_service import AssetTransactionService
from app.services.figure_service import FigureService
from app.services.figure_service.figure_price_service import FigurePriceService
from app.services.order_service.order_number_service import OrderNumberService


# 汇率配置：相对人民币的汇率
EXCHANGE_RATES = {
    'CNY': 1.0,    # 人民币
    'JPY': 1/23,   # 日元：1人民币 = 23日元
    'USD': 7.0,    # 美元：1美元 = 7人民币
    'EUR': 8.0     # 欧元：1欧元 = 8人民币
}


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

        # 获取展示订单编号（只使用数据库中的）
        display_order_number = order.display_order_number or "-"

        # 构建订单详情
        order_detail = {
            # 头部区信息
            "header": {
                "order_number": display_order_number,
                "figure_image": figure_info.get("image", ""),
                "figure_name": figure_info.get("name", "未知手办"),
                "figure_series": figure_info.get("series", ""),
                "quantity": 1,
                "platform": order.shop_name or "-"
            },

            # 订单信息区
            "order_info": {
                "order_id": order.id,
                "order_number": display_order_number,
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

        # 从 images JSON 数组中获取第一张图片
        image_url = ""
        if figure.images and isinstance(figure.images, list) and len(figure.images) > 0:
            image_url = figure.images[0]

        return {
            "name": figure.name or "未知手办",
            "series": figure.work or "",
            "image": image_url
        }

    @classmethod
    def _get_order_type(cls, order: Order) -> Dict[str, str]:
        """
        获取订单类型

        直接从订单的 order_type 字段获取，并映射对应的颜色

        订单类型颜色映射：
        - 定金预定: 蓝色 #1890FF
        - 全款预定: 紫色 #722ED1
        - 现货: 青色 #13C2C2
        - 补仓: 橙色 #FA8C16
        - 已取消: 灰色 #8C8C8C
        """
        # 订单类型颜色映射
        type_colors = {
            "定金预定": "#1890FF",  # 蓝色
            "全款预定": "#722ED1",  # 紫色
            "现货": "#13C2C2",      # 青色
            "补仓": "#FA8C16",      # 橙色
            "已取消": "#8C8C8C"     # 灰色
        }

        # 直接使用数据库中的 order_type 字段
        order_type = order.order_type or "定金预定"

        # 如果订单已取消，显示为已取消
        if order.status == "已取消":
            return {"name": "已取消", "color": type_colors["已取消"]}

        return {"name": order_type, "color": type_colors.get(order_type, "#1890FF")}

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
        - 补仓：只展示全款，不展示定金和尾款

        币种处理：
        - 每笔支付明细携带原始币种信息（currency）
        - 同一币种的金额汇总到 total_by_currency
        """
        deposit = order.deposit or 0
        balance = order.balance or 0
        total_amount = deposit + balance

        # 获取订单类型
        order_type_info = cls._get_order_type(order)
        order_type_name = order_type_info["name"]
        # 补仓订单只展示全款，不需要定金和尾款
        is_replenish = order_type_name == "补仓"

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
                # 如果订单有尾款（预定类型）且不是补仓订单，交易类型是"buy"时拆分为定金+尾款
                if tx.transaction_type == "buy" and balance > 0 and not is_replenish:
                    # 添加定金记录
                    payment_items.append({
                        "type": "定金",
                        "amount": deposit,
                        "currency": order.deposit_currency or tx.currency or "CNY",
                        "date": tx.transaction_date.strftime("%Y-%m-%d") if tx.transaction_date else "-",
                        "full_date": tx.transaction_date.strftime("%Y-%m-%d %H:%M:%S") if tx.transaction_date else "-",
                        "method": tx.payment_method or "-",
                        "status": "paid" if tx.direction == "out" else "pending",
                        "transaction_no": tx.order_id or f"TRX-{tx.id}"
                    })
                    # 添加尾款记录
                    payment_items.append({
                        "type": "尾款",
                        "amount": balance,
                        "currency": order.balance_currency or tx.currency or "CNY",
                        "date": tx.transaction_date.strftime("%Y-%m-%d") if tx.transaction_date else "-",
                        "full_date": tx.transaction_date.strftime("%Y-%m-%d %H:%M:%S") if tx.transaction_date else "-",
                        "method": tx.payment_method or "-",
                        "status": "paid" if tx.direction == "out" else "pending",
                        "transaction_no": tx.order_id or f"TRX-{tx.id}"
                    })
                else:
                    payment_items.append({
                        "type": cls._map_payment_type(tx.transaction_type),
                        "amount": tx.total_amount or 0,
                        "currency": tx.currency or "CNY",
                        "date": tx.transaction_date.strftime("%Y-%m-%d") if tx.transaction_date else "-",
                        "full_date": tx.transaction_date.strftime("%Y-%m-%d %H:%M:%S") if tx.transaction_date else "-",
                        "method": tx.payment_method or "-",
                        "status": "paid" if tx.direction == "out" else "pending",
                        "transaction_no": tx.order_id or f"TRX-{tx.id}"
                    })

        # 非补仓订单：确保定金和尾款条目都存在（已取消订单等场景）
        if not is_replenish:
            existing_types = {item["type"] for item in payment_items}
            if "定金" not in existing_types:
                payment_items.append({
                    "type": "定金",
                    "amount": deposit,
                    "amount_display": "--" if deposit == 0 else None,
                    "currency": order.deposit_currency or "CNY",
                    "date": order.created_at.strftime("%Y-%m-%d") if order.created_at else "-",
                    "full_date": order.created_at.strftime("%Y-%m-%d %H:%M:%S") if order.created_at else "-",
                    "method": "-",
                    "status": "paid" if order.status in ["已支付", "已完成"] else "pending",
                    "transaction_no": "-"
                })
            if "尾款" not in existing_types:
                payment_items.append({
                    "type": "尾款",
                    "amount": balance,
                    "amount_display": "--" if balance == 0 else None,
                    "currency": order.balance_currency or "CNY",
                    "date": order.due_date.strftime("%Y-%m-%d") if order.due_date else "-",
                    "full_date": order.due_date.strftime("%Y-%m-%d") if order.due_date else "-",
                    "method": "-",
                    "status": "paid" if order.status == "已完成" else "pending",
                    "transaction_no": "-"
                })

            # 已取消订单的状态修正：定金已支付，尾款已取消
            if order.status == "已取消":
                for item in payment_items:
                    if item["type"] == "定金":
                        item["status"] = "paid"
                    elif item["type"] == "尾款":
                        item["status"] = "cancelled"

            # 固定排序：定金始终排在尾款前面
            type_order = {"定金": 0, "全款": 1, "尾款": 2}
            payment_items.sort(key=lambda x: type_order.get(x["type"], 99))

        # 按币种汇总实付金额（只统计已支付的条目）
        total_by_currency = {}
        for item in payment_items:
            if item["status"] != "paid":
                continue
            curr = item["currency"]
            total_by_currency[curr] = total_by_currency.get(curr, 0) + item["amount"]

        # 按汇率换算为人民币总金额
        total_amount_cny = 0
        for curr, amount in total_by_currency.items():
            rate = EXCHANGE_RATES.get(curr, 1.0)
            total_amount_cny += amount * rate

        return {
            "payment_type": order_type_name,
            "total_amount": total_amount,
            "total_amount_cny": round(total_amount_cny, 2),
            "total_by_currency": total_by_currency,
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

    @classmethod
    def _get_logistics_info(cls, order: Order) -> Dict[str, Any]:
        """获取物流信息"""
        has_tracking = bool(order.tracking_number)

        # 优先使用数据库中的物流公司字段，如果为空则根据单号识别
        if order.logistics_company:
            logistics_company = order.logistics_company
        elif has_tracking:
            logistics_company = cls._detect_logistics_company(order.tracking_number)
        else:
            logistics_company = ""

        return {
            "tracking_number": order.tracking_number or "",
            "logistics_company": logistics_company,
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
    def update_logistics(cls, db: Session, user_id: int, order_id: int, tracking_number: str) -> Dict[str, Any]:
        """
        更新订单物流信息

        Args:
            db: 数据库会话
            user_id: 用户ID
            order_id: 订单ID
            tracking_number: 快递单号

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

        # 更新物流信息
        order.tracking_number = tracking_number
        order.logistics_company = cls._detect_logistics_company(tracking_number)
        order.shipping_status = "已发货"
        order.updated_at = datetime.now()
        db.commit()

        return {
            "success": True,
            "tracking_number": tracking_number,
            "logistics_company": order.logistics_company,
            "status": "已发货"
        }

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
                {"key": "close", "label": "关闭", "type": "default"}
            ],
            "已支付": [
                {"key": "pay_balance", "label": "支付尾款", "type": "primary"},
                {"key": "cancel_order", "label": "取消订单", "type": "danger"},
                {"key": "edit_remarks", "label": "编辑备注", "type": "default"},
                {"key": "close", "label": "关闭", "type": "default"}
            ],
            "未支付": [
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

    @classmethod
    def create_buy_order(cls, db: Session, user_id: int, order_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        创建新的买入订单

        支持四种业务类型：
        - 预定：定金+尾款模式，创建后进入尾款到期提醒模块
        - 全款预定：定金+尾款模式（一次性付清），创建后进入尾款到期提醒模块
        - 现货：一次性付清，创建后立即触发入库
        - 补仓：一次性付清，平台自动设置为"补仓"

        Args:
            db: 数据库会话
            user_id: 用户ID
            order_data: 订单数据
                - figure_id: 手办ID
                - quantity: 数量
                - platform: 购买平台
                - order_type: 订单类型（预定/全款预定/现货/补仓）
                - deposit: 定金（预定/全款预定时）
                - balance: 尾款（预定/全款预定时）
                - due_date: 出荷日期（预定/全款预定时）
                - total_amount: 实付金额（现货/补仓时）
                - tracking_number: 快递单号（可选）
                - logistics_company: 物流公司（可选）
                - remarks: 备注（可选）

        Returns:
            Dict: 创建结果
        """
        from app.models.order import Order
        from app.models.asset import OrderTransaction
        from datetime import datetime, date

        try:
            # 提取订单数据
            figure_id = order_data.get('figure_id')
            quantity = order_data.get('quantity', 1)
            platform = order_data.get('platform', '')
            order_type = order_data.get('order_type', '预定')
            tracking_number = order_data.get('tracking_number', '')
            logistics_company = order_data.get('logistics_company', '')
            remarks = order_data.get('remarks', '')

            # 验证必填字段
            if not figure_id:
                return {"success": False, "error": "请选择手办"}

            # 验证数量
            if quantity <= 0:
                return {"success": False, "error": "数量必须大于0"}

            # 根据订单类型处理金额和状态
            if order_type in ['预定', '全款预定']:
                deposit = order_data.get('deposit', 0)
                balance = order_data.get('balance', 0)
                due_date = order_data.get('due_date')

                if deposit <= 0:
                    return {"success": False, "error": "定金必须大于0"}
                if due_date:
                    due_date = datetime.strptime(due_date, '%Y-%m-%d').date()

                # 映射订单类型：预定->定金预定，全款预定->全款预定
                db_order_type = '全款预定' if order_type == '全款预定' else '定金预定'

                # 创建订单
                new_order = Order(
                    user_id=user_id,
                    figure_id=figure_id,
                    deposit=deposit,
                    deposit_currency='CNY',
                    balance=balance,
                    balance_currency='CNY',
                    due_date=due_date,
                    status='已支付' if order_type == '全款预定' else '未支付',
                    order_type=db_order_type,  # 设置订单类型
                    shop_name=platform,
                    tracking_number=tracking_number,
                    logistics_company=logistics_company,
                    remarks=remarks,
                    is_active=1,
                    created_at=datetime.now(),
                    updated_at=datetime.now()
                )
            else:  # 现货/补仓
                total_amount = order_data.get('total_amount', 0)
                if total_amount <= 0:
                    return {"success": False, "error": "实付金额必须大于0"}

                # 补仓特殊处理：自动设置平台和备注
                if order_type == '补仓':
                    platform = '补仓'
                    if not remarks:
                        now = datetime.now()
                        remarks = f"{now.strftime('%Y-%m-%d %H:%M')} 花费¥{total_amount} 补仓购入"

                # 创建订单（现货/补仓一次性付清，deposit=总金额，balance=0）
                # 映射订单类型：现货->现货，补仓->补仓
                db_order_type = '现货' if order_type == '现货' else '补仓'
                new_order = Order(
                    user_id=user_id,
                    figure_id=figure_id,
                    deposit=total_amount,
                    deposit_currency='CNY',
                    balance=0,
                    balance_currency='CNY',
                    due_date=None,
                    status='已完成',  # 现货/补仓直接标记为已完成
                    order_type=db_order_type,  # 设置订单类型
                    shop_name=platform,
                    tracking_number=tracking_number,
                    logistics_company=logistics_company,
                    remarks=remarks,
                    is_active=1,
                    created_at=datetime.now(),
                    updated_at=datetime.now()
                )

            # 保存订单
            db.add(new_order)
            db.flush()  # 获取订单ID

            # 生成展示订单编号
            OrderNumberService.update_order_display_number(db, new_order)

            # 创建交易记录
            if order_type in ['预定', '全款预定']:
                # 预定类型：创建定金交易记录
                deposit_tx = OrderTransaction(
                    user_id=user_id,
                    figure_id=figure_id,
                    order_id=new_order.id,
                    transaction_type='deposit',
                    unit_price=deposit,
                    total_amount=deposit,
                    currency='CNY',
                    direction='out',
                    transaction_date=datetime.now(),
                    is_active=True,
                    created_at=datetime.now()
                )
                db.add(deposit_tx)

                # 如果是全款预定，同时创建尾款交易记录
                if order_type == '全款预定' and balance > 0:
                    balance_tx = OrderTransaction(
                        user_id=user_id,
                        figure_id=figure_id,
                        order_id=new_order.id,
                        transaction_type='balance',
                        unit_price=balance,
                        total_amount=balance,
                        currency='CNY',
                        direction='out',
                        transaction_date=datetime.now(),
                        is_active=True,
                        created_at=datetime.now()
                    )
                    db.add(balance_tx)
            else:
                # 现货/补仓：创建一次性支付交易记录
                buy_tx = OrderTransaction(
                    user_id=user_id,
                    figure_id=figure_id,
                    order_id=new_order.id,
                    transaction_type='buy',
                    unit_price=total_amount,
                    total_amount=total_amount,
                    currency='CNY',
                    direction='out',
                    transaction_date=datetime.now(),
                    is_active=True,
                    created_at=datetime.now()
                )
                db.add(buy_tx)

            # 对于已完成的订单（现货/补仓），创建资产交易记录和更新手办平均价格
            if new_order.status == '已完成':
                try:
                    # 计算订单总金额
                    total_price = FigurePriceService.calculate_order_amount_cny(
                        deposit=new_order.deposit,
                        deposit_currency=new_order.deposit_currency,
                        balance=new_order.balance,
                        balance_currency=new_order.balance_currency
                    )

                    # 1. 创建资产交易记录（库存账）
                    AssetTransactionService.create_transaction_from_figure(
                        db=db,
                        user_id=user_id,
                        figure_id=figure_id,
                        price=total_price,
                        quantity=1,
                        order_id=new_order.id
                    )

                    # 2. 更新手办平均入手价格
                    FigureService.update_figure_average_purchase_price(db, figure_id)

                    # 3. 更新手办持有数量（从库存账重新计算）
                    current_inventory = db.query(func.sum(AssetTransaction.remaining_quantity)).filter(
                        AssetTransaction.user_id == user_id,
                        AssetTransaction.figure_id == figure_id,
                        AssetTransaction.transaction_type == "buy",
                        AssetTransaction.is_active == True
                    ).scalar() or 0

                    figure = db.query(Figure).filter(Figure.id == figure_id).first()
                    if figure:
                        figure.quantity = int(current_inventory)

                except Exception as e:
                    # 如果创建交易记录失败，不影响订单创建
                    print(f"创建资产交易记录失败: {e}")

            db.commit()

            return {
                "success": True,
                "order_id": new_order.id,
                "message": "订单创建成功"
            }

        except Exception as e:
            db.rollback()
            return {"success": False, "error": f"创建订单失败: {str(e)}"}
