"""
operation_trade_records.py - 交易记录接口

功能说明：
- 提供交易记录相关的API端点
- 获取交易流水、月度统计、盈亏分析
- 支持按类型、年份、月份筛选

API端点：
- GET /trade/records: 获取交易记录数据

依赖：
- fastapi.APIRouter
- sqlalchemy.orm.Session
- app.services.asset_transaction_service

创建时间: 2026-05-18
作者: FigureBox Team
"""

from datetime import datetime, date, timedelta
from typing import Optional, Dict, Any, List
from fastapi import APIRouter, Depends, Request, Response
from sqlalchemy.orm import Session
from sqlalchemy import func, extract

from app.models.database import get_db
from app.models.user import User
from app.models.figure import Figure
from app.models.asset_transaction import AssetTransaction
from app.models.order_finance import OrderTransaction
from app.models.order import Order
from app.models.sold_order import SoldOrder
from app.api.users import get_current_user

router = APIRouter()


@router.get("/trade/records")
async def get_trade_records(
    request: Request,
    response: Response,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    获取交易记录数据

    返回交易流水、月度统计、盈亏分析等数据
    """
    user_id = current_user.id
    today = date.today()
    current_month_start = today.replace(day=1)
    current_year = today.year

    # 获取本月交易统计
    monthly_stats = _get_monthly_stats(db, user_id, current_month_start, today)

    # 获取交易流水
    transactions = _get_transactions(db, user_id)

    # 获取盈亏分析
    profit_analysis = _get_profit_analysis(db, user_id, current_year)

    return {
        "monthly_stats": monthly_stats,
        "transactions": transactions,
        "profit_analysis": profit_analysis
    }


def _get_monthly_stats(db: Session, user_id: int, month_start: date, month_end: date) -> Dict[str, Any]:
    """
    获取月度交易统计

    Args:
        db: 数据库会话
        user_id: 用户ID
        month_start: 月份开始日期
        month_end: 月份结束日期

    Returns:
        Dict: 月度统计
    """
    # 本月买入统计（通过OrderTransaction）
    buy_stats = db.query(
        func.count(OrderTransaction.id).label('count'),
        func.coalesce(func.sum(OrderTransaction.total_amount), 0).label('amount')
    ).filter(
        OrderTransaction.user_id == user_id,
        OrderTransaction.direction == "out",
        OrderTransaction.is_active == True,
        func.date(OrderTransaction.transaction_date) >= month_start,
        func.date(OrderTransaction.transaction_date) <= month_end
    ).first()

    # 本月卖出统计（通过SoldOrder）
    sell_stats = db.query(
        func.count(SoldOrder.id).label('count'),
        func.coalesce(func.sum(SoldOrder.sell_price), 0).label('amount')
    ).filter(
        SoldOrder.user_id == user_id,
        SoldOrder.is_active == 1,
        SoldOrder.status == "已完成",
        func.date(SoldOrder.created_at) >= month_start,
        func.date(SoldOrder.created_at) <= month_end
    ).first()

    buy_count = buy_stats.count if buy_stats else 0
    buy_amount = buy_stats.amount if buy_stats else 0
    sell_count = sell_stats.count if sell_stats else 0
    sell_amount = sell_stats.amount if sell_stats else 0
    net_cashflow = sell_amount - buy_amount

    return {
        "buy_count": buy_count,
        "buy_amount": round(buy_amount, 2),
        "sell_count": sell_count,
        "sell_amount": round(sell_amount, 2),
        "net_cashflow": round(net_cashflow, 2)
    }


def _get_transactions(db: Session, user_id: int) -> List[Dict[str, Any]]:
    """
    获取交易流水记录

    Args:
        db: 数据库会话
        user_id: 用户ID

    Returns:
        List[Dict]: 交易记录列表
    """
    records = []

    # 从OrderTransaction获取资金流水（买入）
    order_transactions = db.query(OrderTransaction).filter(
        OrderTransaction.user_id == user_id,
        OrderTransaction.is_active == True
    ).order_by(OrderTransaction.transaction_date.desc()).limit(50).all()

    for ot in order_transactions:
        figure_name = ""
        if ot.figure_id:
            figure = db.query(Figure).filter(Figure.id == ot.figure_id).first()
            if figure:
                figure_name = figure.name

        direction_text = "支出" if ot.direction == "out" else "收入"
        amount = -ot.total_amount if ot.direction == "out" else ot.total_amount

        records.append({
            "id": ot.id,
            "date": ot.transaction_date.strftime("%m-%d %H:%M:%S") if ot.transaction_date else "",
            "amount": -ot.total_amount if ot.direction == "out" else ot.total_amount,
            "title": f"{ot.transaction_type}: {figure_name} ({direction_text})",
            "order_id": str(ot.order_id) if ot.order_id else "",
            "status": "✅ 成功",
            "payment_method": ot.payment_method or "",
            "merchant": ot.platform or "",
            "platform": ot.platform or "",
            "fee": 0,
            "net_profit": 0,
            "actions": ["查看订单"]
        })

    # 从SoldOrder获取卖出记录
    sold_orders = db.query(SoldOrder).filter(
        SoldOrder.user_id == user_id,
        SoldOrder.is_active == 1,
        SoldOrder.status == "已完成"
    ).order_by(SoldOrder.created_at.desc()).limit(50).all()

    for so in sold_orders:
        figure_name = ""
        if so.figure_id:
            figure = db.query(Figure).filter(Figure.id == so.figure_id).first()
            if figure:
                figure_name = figure.name

        net_profit = so.net_profit or (so.sell_price - so.cost_price - abs(so.shipping_fee or 0) - abs(so.platform_fee or 0))

        records.append({
            "id": so.id + 10000,
            "date": so.created_at.strftime("%m-%d %H:%M:%S") if so.created_at else "",
            "amount": so.sell_price,
            "title": f"卖出: {figure_name}",
            "order_id": so.order_number or "",
            "status": "✅ 已到账",
            "buyer": "",
            "platform": so.sell_platform or "",
            "fee": abs(so.platform_fee or 0),
            "net_profit": round(net_profit, 2),
            "actions": ["查看买家信息", "物流信息", "评价"]
        })

    # 按时间排序
    records.sort(key=lambda x: x.get("date", ""), reverse=True)

    return records


def _get_profit_analysis(db: Session, user_id: int, current_year: int) -> Dict[str, Any]:
    """
    获取盈亏分析数据

    Args:
        db: 数据库会话
        user_id: 用户ID
        current_year: 当前年份

    Returns:
        Dict: 盈亏分析数据
    """
    # 获取所有卖出记录
    sold_orders = db.query(SoldOrder).filter(
        SoldOrder.user_id == user_id,
        SoldOrder.is_active == 1,
        SoldOrder.status == "已完成"
    ).all()

    # 计算年度总利润
    yearly_profit = sum(
        (so.net_profit or (so.sell_price - so.cost_price - abs(so.shipping_fee or 0) - abs(so.platform_fee or 0)))
        for so in sold_orders
    )

    # 计算胜率
    win_count = 0
    loss_count = 0
    total_win = 0
    total_loss = 0
    max_profit = 0
    max_loss = 0
    max_profit_item = ""
    max_loss_item = ""

    for so in sold_orders:
        profit = so.net_profit or (so.sell_price - so.cost_price - abs(so.shipping_fee or 0) - abs(so.platform_fee or 0))

        figure_name = ""
        if so.figure_id:
            figure = db.query(Figure).filter(Figure.id == so.figure_id).first()
            if figure:
                figure_name = figure.name

        if profit > 0:
            win_count += 1
            total_win += profit
            if profit > max_profit:
                max_profit = profit
                max_profit_item = figure_name
        else:
            loss_count += 1
            total_loss += abs(profit)
            if abs(profit) > max_loss:
                max_loss = abs(profit)
                max_loss_item = figure_name

    total_trades = win_count + loss_count
    win_rate = round((win_count / total_trades) * 100, 1) if total_trades > 0 else 0

    return {
        "yearly_profit": round(yearly_profit, 2),
        "win_rate": win_rate,
        "win_count": win_count,
        "loss_count": loss_count,
        "avg_profit": round(total_win / win_count, 2) if win_count > 0 else 0,
        "avg_loss": round(total_loss / loss_count, 2) if loss_count > 0 else 0,
        "max_profit": round(max_profit, 2),
        "max_profit_item": max_profit_item,
        "max_loss": round(max_loss, 2),
        "max_loss_item": max_loss_item
    }
