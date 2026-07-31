"""
账单导出服务
提供交易账单导出功能，支持Excel和CSV格式
采用企业级服务层架构
"""
import io
import csv
from typing import List, Dict, Any, Optional
from datetime import date, datetime
from calendar import monthrange
from sqlalchemy.orm import Session
from sqlalchemy import case

from app.models.asset import OrderTransaction
from app.models.sold_order import SoldOrder
from app.models.order import Order
from app.models.figure import Figure


class BillExportService:
    """
    账单导出服务类

    提供以下核心功能：
    1. 交易数据查询：根据时间范围获取交易记录
    2. 数据格式化：将交易记录格式化为导出字段
    3. 文件生成：生成Excel或CSV格式的账单文件
    """

    @classmethod
    def export_bill(
        cls,
        db: Session,
        user_id: int,
        export_range: str,
        year: Optional[int] = None,
        month: Optional[int] = None,
        file_format: str = "xlsx"
    ) -> bytes:
        """
        导出账单

        Args:
            db: 数据库会话
            user_id: 用户ID
            export_range: 导出范围 ('current' 当前月份, 'all' 全部历史)
            year: 年份（当export_range为'current'时必填）
            month: 月份（当export_range为'current'时必填）
            file_format: 文件格式 ('xlsx' 或 'csv')

        Returns:
            bytes: 文件内容
        """
        # 获取交易数据
        transactions = cls._get_transactions(db, user_id, export_range, year, month)

        # 格式化数据
        formatted_data = cls._format_transactions(transactions)

        # 生成文件
        if file_format == "xlsx":
            return cls._generate_excel(formatted_data)
        else:
            return cls._generate_csv(formatted_data)

    @classmethod
    def _get_transactions(
        cls,
        db: Session,
        user_id: int,
        export_range: str,
        year: Optional[int] = None,
        month: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        获取交易记录

        从OrderTransaction和SoldOrder获取数据
        """
        records = []

        # 构建时间过滤条件
        start_date = None
        end_date = None
        if export_range == "current" and year and month:
            start_date = date(year, month, 1)
            _, last_day = monthrange(year, month)
            end_date = date(year, month, last_day)

        # 获取OrderTransaction交易记录
        buy_query = db.query(OrderTransaction).filter(
            OrderTransaction.user_id == user_id,
            OrderTransaction.is_active == True
        )

        if start_date and end_date:
            # 按交易类型分流：
            #   deposit → Order.payment_time
            #   balance → Order.balance_payment_time
            #   fee     → SoldOrder.sell_date（手续费随售出，归到售出日）
            #   其他    → ot.transaction_date
            # sell 行不进 SQL 过滤（Python 层跳过，统一由 SoldOrder 循环提供"卖出"行）
            effective_date = case(
                (OrderTransaction.transaction_type == "deposit", Order.payment_time),
                (OrderTransaction.transaction_type == "balance", Order.balance_payment_time),
                (OrderTransaction.transaction_type == "fee", SoldOrder.sell_date),
                else_=OrderTransaction.transaction_date,
            )
            buy_query = buy_query.join(
                Order, OrderTransaction.order_id == Order.id, isouter=True
            ).join(
                SoldOrder, OrderTransaction.sold_order_id == SoldOrder.id, isouter=True
            ).filter(
                effective_date >= start_date,
                effective_date <= end_date,
            )

        buy_records = buy_query.order_by(OrderTransaction.transaction_date.desc()).all()

        for ot in buy_records:
            # sell 类型由 SoldOrder 自身提供「卖出」行，避免重复
            if ot.transaction_type == "sell":
                continue

            figure = None
            if ot.figure_id:
                figure = db.query(Figure).filter(Figure.id == ot.figure_id).first()

            # 关联订单：用于按定金/尾款类型取对应的支付时间
            order = None
            if ot.order_id:
                order = db.query(Order).filter(Order.id == ot.order_id).first()

            transaction_type_map = {
                "buy": "买入",
                "refund": "退款",
                "deposit": "定金",
                "balance": "尾款",
                "fee": "手续费",
                "cancel": "已取消"
            }

            # 获取订单编号：优先使用 display_order_number，其次使用 order_id/sold_order_id
            order_id = ""
            if ot.order_id:
                if order and order.display_order_number:
                    order_id = order.display_order_number
                else:
                    order_id = f"ORD-{ot.order_id:06d}"
            elif ot.sold_order_id:
                sold_order = db.query(SoldOrder).filter(SoldOrder.id == ot.sold_order_id).first()
                if sold_order and sold_order.display_order_number:
                    order_id = sold_order.display_order_number
                else:
                    order_id = f"SLD-{ot.sold_order_id:06d}"

            # 获取成本价和盈亏：对于 sell/fee 类型，从关联的 SoldOrder 获取
            cost_price = None
            profit = None
            sold_order = None
            if ot.sold_order_id:
                sold_order = db.query(SoldOrder).filter(SoldOrder.id == ot.sold_order_id).first()
                if sold_order:
                    cost_price = sold_order.cost_price
                    profit = sold_order.net_profit

            # 交易日期口径：
            #   deposit → Order.payment_time
            #   balance → Order.balance_payment_time
            #   fee     → SoldOrder.sell_date（手续费随售出，归到售出日）
            #   其他    → ot.transaction_date
            if ot.transaction_type == "deposit" and order and order.payment_time:
                display_date = order.payment_time
            elif ot.transaction_type == "balance" and order and order.balance_payment_time:
                display_date = order.balance_payment_time
            elif ot.transaction_type == "fee" and sold_order and sold_order.sell_date:
                display_date = sold_order.sell_date
            else:
                display_date = ot.transaction_date

            records.append({
                "transaction_date": display_date,
                "transaction_type": transaction_type_map.get(ot.transaction_type, ot.transaction_type),
                "order_id": order_id,
                "figure_name": figure.name if figure else "",
                "manufacturer": figure.manufacturer if figure else "",
                "original_art": figure.original_art if figure else "",
                "purchase_type": figure.purchase_type if figure else "",
                "quantity": ot.quantity or 1,
                "unit_price": ot.unit_price,
                "total_amount": ot.total_amount,
                "cost_price": cost_price,
                "profit": profit,
                "platform": ot.platform or "",
                "notes": ot.notes or ""
            })

        # 获取SoldOrder卖出记录
        sell_query = db.query(SoldOrder).filter(
            SoldOrder.user_id == user_id,
            SoldOrder.is_active == True
        )

        if start_date and end_date:
            sell_query = sell_query.filter(
                SoldOrder.sell_date >= start_date,
                SoldOrder.sell_date <= end_date
            )

        sell_records = sell_query.order_by(SoldOrder.sell_date.desc()).all()

        for so in sell_records:
            figure = None
            if so.figure_id:
                figure = db.query(Figure).filter(Figure.id == so.figure_id).first()

            total_amount = so.sell_price * (so.quantity or 1)

            records.append({
                "transaction_date": so.sell_date or so.created_at,
                "transaction_type": "卖出",
                "order_id": so.order_number or so.display_order_number or f"SLD-{so.id:06d}",
                "figure_name": figure.name if figure else "",
                "manufacturer": figure.manufacturer if figure else "",
                "original_art": figure.original_art if figure else "",
                "purchase_type": figure.purchase_type if figure else "",
                "quantity": so.quantity or 1,
                "unit_price": so.sell_price,
                "total_amount": total_amount,
                "cost_price": so.cost_price,
                "profit": so.net_profit,
                "platform": so.sell_platform or "",
                "notes": so.remark or ""
            })

        # 按日期排序
        records.sort(key=lambda x: x["transaction_date"] or date.min, reverse=True)

        return records

    @classmethod
    def _format_transactions(
        cls,
        transactions: List[Dict[str, Any]]
    ) -> List[List[Any]]:
        """
        格式化交易记录为导出格式
        """
        headers = [
            "交易日期",
            "交易类型",
            "订单编号",
            "手办名称",
            "制造商",
            "原画作者",
            "入手形式",
            "数量",
            "单价",
            "成交金额",
            "成本价",
            "盈亏（卖出时）",
            "卖出平台",
            "备注"
        ]

        data = [headers]

        for t in transactions:
            row = [
                t["transaction_date"].strftime("%Y/%m/%d %H:%M") if t["transaction_date"] else "",
                t["transaction_type"],
                t["order_id"],
                t["figure_name"],
                t["manufacturer"],
                t["original_art"],
                t["purchase_type"],
                t["quantity"],
                f"￥{t['unit_price']:.2f}" if t["unit_price"] else "",
                f"￥{t['total_amount']:.2f}" if t["total_amount"] else "",
                f"￥{t['cost_price']:.2f}" if t["cost_price"] else "",
                f"￥{t['profit']:.2f}" if t["profit"] is not None else "",
                t["platform"],
                t["notes"]
            ]
            data.append(row)

        return data

    @classmethod
    def _generate_excel(cls, data: List[List[Any]]) -> bytes:
        """
        生成Excel文件

        使用openpyxl库生成.xlsx文件
        """
        try:
            from openpyxl import Workbook
            from openpyxl.styles import Font, Alignment

            wb = Workbook()
            ws = wb.active
            ws.title = "交易账单"

            for row_idx, row_data in enumerate(data, 1):
                for col_idx, value in enumerate(row_data, 1):
                    cell = ws.cell(row=row_idx, column=col_idx, value=value)
                    if row_idx == 1:
                        cell.font = Font(bold=True)
                        cell.alignment = Alignment(horizontal="center", vertical="center")

            output = io.BytesIO()
            wb.save(output)
            output.seek(0)
            return output.getvalue()

        except ImportError:
            return cls._generate_csv(data)

    @classmethod
    def _generate_csv(cls, data: List[List[Any]]) -> bytes:
        """
        生成CSV文件
        """
        output = io.StringIO()
        writer = csv.writer(output)

        for row in data:
            writer.writerow(row)

        # 添加BOM以支持中文
        return "\ufeff".encode("utf-8") + output.getvalue().encode("utf-8")
