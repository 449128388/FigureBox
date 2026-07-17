"""
交易流水查询服务
提供交易流水记录的查询和组装，支持订单聚合展示
采用企业级服务层架构
"""
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from collections import defaultdict

from app.models.figure import Figure
from app.models.asset import OrderTransaction
from app.models.sold_order import SoldOrder
from app.models.order import Order
from app.services.exchange_rate_service import ExchangeRateService


class TransactionQueryService:
    """
    交易流水查询服务类

    提供以下核心功能：
    1. 买入交易查询：从OrderTransaction获取资金流水，按order_id聚合
    2. 卖出交易查询：从SoldOrder获取卖出记录，按sold_order_id聚合
    3. 交易记录组装：统一格式返回聚合后的交易流水
    4. 筛选功能：支持按类型筛选（全部/收入/支出/费用）
    """

    @classmethod
    def get_transactions(cls, db: Session, user_id: int, filter_type: str = "all") -> List[Dict[str, Any]]:
        """
        获取聚合后的交易流水记录

        聚合规则：
        1. 卖出订单：按 sold_order_id 聚合，sell + 所有 fee 折叠为一组
        2. 买入订单：按 order_id 聚合，buy + 所有 fee（如有）折叠为一组
        3. 独立流水：无订单关联的纯费用/退款，保持单行展示

        筛选规则：
        - all: 展示所有聚合卡片
        - income: 只展示卖出聚合卡片
        - expense: 只展示买入聚合卡片
        - fee: 展示独立的费用流水（无订单关联的）

        排序规则：
        - 默认按聚合主流水时间倒序（即 sell/buy 的时间）
        - 费用明细内部按时间正序排列

        Args:
            db: 数据库会话
            user_id: 用户ID
            filter_type: 筛选类型 (all/income/expense/fee)

        Returns:
            List[Dict]: 聚合后的交易记录列表，按时间倒序排列
        """
        records = []

        # 根据筛选类型获取对应记录
        if filter_type in ["all", "income"]:
            # 获取聚合后的卖出交易记录
            sell_records = cls._get_aggregated_sell_records(db, user_id)
            records.extend(sell_records)

        if filter_type in ["all", "expense"]:
            # 获取聚合后的买入交易记录（过滤掉 transaction_type 为 fee 的数据）
            buy_records = cls._get_aggregated_buy_records(db, user_id)
            records.extend(buy_records)

        if filter_type == "fee":
            # 获取独立的费用流水
            fee_records = cls._get_independent_fee_records(db, user_id)
            records.extend(fee_records)

        # 按时间排序（倒序）
        records.sort(key=lambda x: x.get("date", ""), reverse=True)

        return records

    @staticmethod
    def _get_aggregated_sell_records(db: Session, user_id: int) -> List[Dict[str, Any]]:
        """
        获取聚合后的卖出交易记录

        聚合逻辑：
        - 按 sold_order_id 分组
        - 每组包含：卖出毛收入、运费、平台手续费
        - 计算净到账、净利润、利润率
        - 费用明细按时间正序排列

        卡片展示结构：
        ┌─────────────────────────────────────────────────────────┐
        │  05-28 11:17                              +¥3,200  🔴   │
        │  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━  │
        │  【卖出】桐宫美月 写实版  ×1体                           │
        │  平台: 闲鱼（鱼小铺）    状态: ✅ 成功                  │
        │                                                         │
        │  ▼ 费用明细                        实到账: +¥3,168.8   │
        │    ├─ 运费                          -¥25.6  🟢          │
        │    └─ 平台手续费                    -¥5.6   🟢          │
        │                                                         │
        │  净利润: +¥643.8  |  利润率: +25.3%                     │
        │  [查看订单]  [物流信息]  [评价]                          │
        └─────────────────────────────────────────────────────────┘

        Args:
            db: 数据库会话
            user_id: 用户ID

        Returns:
            List[Dict]: 聚合后的卖出交易记录列表
        """
        records = []

        # 查询所有未删除的卖出订单（不限定状态，由前端筛选处理）
        sold_orders = db.query(SoldOrder).filter(
            SoldOrder.user_id == user_id,
            SoldOrder.is_active == 1
        ).order_by(SoldOrder.created_at.desc()).limit(50).all()

        for so in sold_orders:
            figure_name = ""
            figure_id = None
            if so.figure_id:
                figure = db.query(Figure).filter(Figure.id == so.figure_id).first()
                if figure:
                    figure_name = figure.name
                    figure_id = figure.id

            # 计算各项金额
            gross_income = so.sell_price or 0  # 毛收入（卖出价格）
            shipping_fee = abs(so.shipping_fee or 0)  # 运费（转为正数显示）
            platform_fee = abs(so.platform_fee or 0)  # 平台手续费
            cost_price = so.cost_price or 0  # 成本价

            # 净到账 = 毛收入 - 运费 - 平台手续费
            net_received = gross_income - shipping_fee - platform_fee

            # 净利润 = 净到账 - 成本价
            net_profit = net_received - cost_price

            # 利润率 = 净利润 / 成本价 * 100%
            profit_rate = (net_profit / cost_price * 100) if cost_price > 0 else 0

            # 构建费用明细列表（按时间正序排列）
            fee_details = []
            # 首先添加卖出价（收入项）
            fee_details.append({
                "name": "卖出价",
                "amount": gross_income,  # 正数表示收入
                "color": "red",  # 红色表示收入
                "sort_order": 0  # 排在最前面
            })
            if shipping_fee > 0:
                fee_details.append({
                    "name": "运费",
                    "amount": -shipping_fee,  # 负号表示支出
                    "color": "green",  # 绿色表示支出
                    "sort_order": 1  # 用于排序
                })
            if platform_fee > 0:
                fee_details.append({
                    "name": "平台手续费",
                    "amount": -platform_fee,
                    "color": "green",
                    "sort_order": 2
                })

            # 费用明细按时间正序排列（这里用sort_order模拟）
            fee_details.sort(key=lambda x: x.get("sort_order", 0))

            records.append({
                "id": so.id,
                "date": so.created_at.strftime("%Y-%m-%d %H:%M:%S") if so.created_at else "",
                "type": "sell",  # 交易类型：sell/buy/independent/fee
                "card_type": "sell",  # 卡片类型，用于前端区分样式
                "order_number": so.order_number or str(so.id),
                "filter_category": "income",  # 用于筛选：income/expense/fee

                # 金额信息
                "gross_amount": gross_income,  # 毛收入（右上角显示）
                "net_received": round(net_received, 2),  # 净到账
                "net_profit": round(net_profit, 2),  # 净利润
                "profit_rate": round(profit_rate, 2),  # 利润率

                # 费用明细（可折叠，已按时间正序排列）
                "fee_details": fee_details,
                "total_fees": round(shipping_fee + platform_fee, 2),  # 总费用

                # 商品信息
                "title": f"【卖出】{figure_name}",
                "figure_name": figure_name,
                "figure_id": figure_id,
                "quantity": so.quantity or 1,

                # 交易信息
                "platform": so.sell_platform or "",
                "status": {
                    "已完成": "✅ 已完成",
                    "待发货": "⏳ 待发货",
                    "已取消": "❌ 已取消",
                    "已退款": "↩️ 已退款"
                }.get(so.status, so.status) or "⏳ 待发货",
                "buyer": "",  # 可扩展买家信息

                # 操作按钮
                "actions": ["查看订单"]
            })

        return records

    @staticmethod
    def _get_aggregated_buy_records(db: Session, user_id: int) -> List[Dict[str, Any]]:
        """
        获取聚合后的买入交易记录

        数据来源：
        - 从 orders 表获取买入订单数据
        - 关联 figures 表获取手办名称
        - 关联 OrderTransaction 获取相关费用明细

        聚合逻辑：
        - 每个订单独立展示
        - 计算总支出金额（定金 + 尾款）
        - 关联查询该订单的费用明细
        - 买入订单不计算净利润（净利润在卖出时计算）

        卡片展示结构：
        ┌─────────────────────────────────────────────────────────┐
        │  05-27 11:11                              -¥800   🟢    │
        │  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━  │
        │  【买入】蜜姬  ×1体                                     │
        │  平台: 补仓    状态: ✅ 成功                            │
        │  订单号: 10                                             │
        │                                                         │
        │  [查看订单]                                             │
        └─────────────────────────────────────────────────────────┘

        Args:
            db: 数据库会话
            user_id: 用户ID

        Returns:
            List[Dict]: 聚合后的买入交易记录列表
        """
        records = []

        # 从 orders 表查询买入订单
        # 排序规则：先按创建时间降序，时间相同时按订单号降序
        orders = db.query(Order).filter(
            Order.user_id == user_id,
            Order.is_active == 1
        ).order_by(Order.created_at.desc(), Order.id.desc()).limit(50).all()

        for order in orders:
            if not order:
                continue

            # 获取手办名称和ID
            figure_name = ""
            figure_id = None
            if order.figure_id:
                figure = db.query(Figure).filter(Figure.id == order.figure_id).first()
                if figure:
                    figure_name = figure.name
                    figure_id = figure.id

            # 计算总支出金额（定金 + 尾款，按汇率换算为人民币，只统计已支付部分）
            deposit = order.deposit or 0
            balance = order.balance or 0
            deposit_currency = order.deposit_currency or "CNY"
            balance_currency = order.balance_currency or "CNY"
            deposit_rate = ExchangeRateService.get_rate(db, deposit_currency)
            balance_rate = ExchangeRateService.get_rate(db, balance_currency)

            # 查询该订单的支付交易记录，判断定金是否已支付
            deposit_paid_txn = db.query(OrderTransaction).filter(
                OrderTransaction.user_id == user_id,
                OrderTransaction.order_id == order.id,
                OrderTransaction.is_active == True,
                OrderTransaction.transaction_type.in_(["deposit", "buy"]),
                OrderTransaction.direction == "out"
            ).first()
            deposit_paid = deposit_paid_txn is not None

            # 查询该订单的尾款交易记录，判断尾款是否已支付
            balance_paid_txn = db.query(OrderTransaction).filter(
                OrderTransaction.user_id == user_id,
                OrderTransaction.order_id == order.id,
                OrderTransaction.is_active == True,
                OrderTransaction.transaction_type == "balance",
                OrderTransaction.direction == "out"
            ).first()
            balance_paid = balance_paid_txn is not None

            # 根据订单状态和交易记录确定已支付的金额：
            # 已完成 → 定金+尾款均已支付
            # 已支付或存在定金交易 → 仅定金已支付
            # 未支付且无交易记录 → 均未支付
            # 已取消 → 仅定金已支付
            paid_deposit = deposit * deposit_rate if (
                order.status in ["已完成", "已支付", "已取消"] or deposit_paid
            ) else 0
            paid_balance = balance * balance_rate if (
                order.status == "已完成" or balance_paid
            ) else 0
            total_amount = round(paid_deposit + paid_balance, 2)

            # 查询该订单关联的费用明细（从 OrderTransaction 表）
            fee_transactions = db.query(OrderTransaction).filter(
                OrderTransaction.user_id == user_id,
                OrderTransaction.order_id == order.id,
                OrderTransaction.is_active == True,
                OrderTransaction.transaction_type == "fee"
            ).order_by(OrderTransaction.transaction_date.asc()).all()

            # 构建费用明细（按时间正序排列）
            fee_details = []
            for fee_tx in fee_transactions:
                fee_details.append({
                    "name": fee_tx.description or "费用",
                    "amount": -(fee_tx.total_amount or 0),
                    "color": "green"
                })

            # 订单时间（优先使用支付时间，降级到创建时间）
            order_date = ""
            payment_source = order.payment_time or order.created_at
            if payment_source:
                order_date = payment_source.strftime("%Y-%m-%d %H:%M:%S")

            # 订单状态映射
            status_map = {
                "已完成": "✅ 已完成",
                "已支付": "⏳ 已支付尾款,待发货",
                "未支付": "⏳ 未支付尾款",
                "已取消": "❌ 已取消"
            }
            order_status = status_map.get(order.status, order.status) or "-"

            # 出荷日期格式化
            due_date = ""
            if order.due_date:
                due_date = order.due_date.strftime("%Y-%m-%d")

            records.append({
                "id": order.id,
                "date": order_date,
                "type": "buy",
                "card_type": "buy",  # 买入卡片样式
                "order_number": order.order_number or "",
                "display_order_number": order.display_order_number,
                "filter_category": "expense",  # 用于筛选：income/expense/fee

                # 金额信息
                "gross_amount": -total_amount,  # 支出金额（右上角显示，负号表示支出）
                "net_received": None,  # 买入无净到账概念
                "net_profit": None,  # 买入无净利润概念
                "profit_rate": None,

                # 费用明细（已按时间正序排列）
                "fee_details": fee_details,
                "total_fees": sum(fee["amount"] for fee in fee_details),

                # 商品信息
                "title": f"【买入】{figure_name}",
                "figure_name": figure_name,
                "figure_id": figure_id,
                "quantity": 1,  # 买入订单默认1体

                # 交易信息
                "platform": order.shop_name or "",
                "status": order_status,
                "payment_method": "",
                "due_date": due_date,  # 出荷日期

                # 备注信息（有数据时展示，无数据时不展示）
                "remarks": order.remarks or "",

                # 操作按钮
                "actions": ["查看订单"]
            })

        return records

    @staticmethod
    def _get_independent_fee_records(db: Session, user_id: int) -> List[Dict[str, Any]]:
        """
        获取独立的费用流水记录

        筛选逻辑：
        - 只获取 transaction_type 为 fee 的数据
        - 无订单关联的纯费用/退款
        - 保持单行展示

        Args:
            db: 数据库会话
            user_id: 用户ID

        Returns:
            List[Dict]: 独立的费用流水记录列表
        """
        records = []

        # 查询独立的费用记录（transaction_type 为 fee 且无 order_id）
        fee_transactions = db.query(OrderTransaction).filter(
            OrderTransaction.user_id == user_id,
            OrderTransaction.is_active == True,
            OrderTransaction.transaction_type == "fee",  # 只查询 fee 类型
            OrderTransaction.order_id.is_(None)  # 无订单关联
        ).order_by(OrderTransaction.transaction_date.desc()).limit(50).all()

        for tx in fee_transactions:
            # 获取手办名称
            figure_name = ""
            if tx.figure_id:
                figure = db.query(Figure).filter(Figure.id == tx.figure_id).first()
                if figure:
                    figure_name = figure.name

            # 费用金额
            fee_amount = tx.total_amount or 0

            records.append({
                "id": tx.id,
                "date": tx.transaction_date.strftime("%m-%d %H:%M:%S") if tx.transaction_date else "",
                "type": "fee",  # 独立费用类型
                "card_type": "fee",  # 费用卡片样式
                "order_number": "",
                "filter_category": "fee",  # 用于筛选：income/expense/fee

                # 金额信息
                "gross_amount": -abs(fee_amount),  # 费用为支出，显示负数
                "net_received": None,
                "net_profit": None,
                "profit_rate": None,

                # 费用明细（独立费用无明细）
                "fee_details": [],
                "total_fees": -abs(fee_amount),

                # 商品信息
                "title": f"【费用】{figure_name}" if figure_name else "【费用】其他费用",
                "figure_name": figure_name,
                "quantity": tx.quantity or 1,

                # 交易信息
                "platform": tx.platform or "",
                "status": "✅ 成功",
                "payment_method": tx.payment_method or "",

                # 操作按钮
                "actions": ["查看详情"]
            })

        return records
