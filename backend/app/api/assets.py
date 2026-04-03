from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from datetime import datetime, timedelta, date
from typing import List, Optional
import requests
import random
import time
import re

from app.models.database import get_db
from app.models.asset import AssetPriceHistory, AssetAlert, AssetTransaction, StockIndexCache
from app.models.figure import Figure
from app.models.order import Order
from app.schemas.asset import (
    AssetSummary, AssetDetail, AssetKlineData, AssetRanking, AssetAdvice,
    AssetDashboard, AssetPriceHistoryCreate, AssetPriceHistory as AssetPriceHistorySchema,
    AssetAlertCreate, AssetAlert as AssetAlertSchema,
    AssetTransactionCreate, AssetTransaction as AssetTransactionSchema
)
from app.api.users import get_current_user
from app.models.user import User

router = APIRouter()

@router.get("/dashboard")
def get_asset_dashboard(
    time_range: str = Query("1m", description="时间范围: 1m, 3m, 1y, all"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取资产看板数据"""
    # 计算时间范围
    if time_range == "1m":
        start_date = datetime.now() - timedelta(days=30)
    elif time_range == "3m":
        start_date = datetime.now() - timedelta(days=90)
    elif time_range == "1y":
        start_date = datetime.now() - timedelta(days=365)
    else:  # all
        start_date = datetime(2000, 1, 1)
    
    # 获取所有手办
    figures = db.query(Figure).all()
    
    # 计算总资产和成本
    total_assets = sum(fig.current_value or 0 for fig in figures)
    total_cost = sum(fig.purchase_price or 0 for fig in figures)
    
    # 计算日涨跌（模拟数据，实际应该从价格历史计算）
    daily_change = 2300
    daily_change_percentage = 1.82
    
    # 塑料指数（手办总价值指数）
    plastic_index = 2847

    # 获取上证指数（带缓存机制）
    sh_index_data = get_cached_sh_index(db)
    sh_index = sh_index_data["current_value"]
    sh_change_percentage = sh_index_data["change_percentage"]

    # 跑赢大盘百分比（根据塑料指数和上证指数计算）
    outperform_percentage = 68
    
    # 仓位状态
    position = "满仓"
    
    # 本月入手数量
    monthly_purchases = 3
    
    # 构建资产摘要
    summary = {
        "total_assets": total_assets or 128500,
        "daily_change": daily_change,
        "daily_change_percentage": daily_change_percentage,
        "plastic_index": plastic_index,
        "sh_index": sh_index,
        "outperform_percentage": outperform_percentage,
        "position": position,
        "monthly_purchases": monthly_purchases
    }
    
    # 构建盈亏分析数据
    profit = {
        "floating": 23400,
        "realized": 8200,
        "total_rate": 24.6
    }
    
    # 构建K线数据（模拟数据）
    kline_data = []
    for i in range(30):
        kline_data.append({
            "date": datetime.now() - timedelta(days=30 - i),
            "value": 2500 + i * 10 + (i % 5)
        })
    
    # 构建涨跌排行（模拟数据）
    rankings = [
        {"figure_id": 1, "figure_name": "初音韶华", "change_percentage": 15, "trend": "up"},
        {"figure_id": 2, "figure_name": "蕾姆婚纱", "change_percentage": 8, "trend": "up"},
        {"figure_id": 3, "figure_name": "Saber", "change_percentage": -12, "trend": "down"}
    ]
    
    # 构建操作建议（模拟数据）
    advice = [
        {"figure_name": "Saber", "advice": "Saber跌幅超10%,建议持有或止损"}
    ]
    
    # 构建持仓明细
    holdings = []
    if not figures:
        # 模拟数据
        holdings = [
            {
                "figure_id": 1,
                "figure_name": "初音未来 韶华 Ver.",
                "stock": 1,
                "status": "收藏中",
                "cost_price": 800,
                "current_price": 2000,
                "profit": 1200,
                "profit_percentage": 150,
                "purchase_date": "2024-01",
                "holding_days": 420,
                "market_share": 15.6
            },
            {
                "figure_id": 2,
                "figure_name": "Saber 礼服 Ver.",
                "stock": 1,
                "status": "补款中(待付¥600)",
                "cost_price": 200,
                "current_price": 1200,
                "profit": 400,
                "profit_percentage": 200,
                "purchase_date": "2026-03",
                "holding_days": 15,
                "market_share": 9.3
            },
            {
                "figure_id": 3,
                "figure_name": "蕾姆 婚纱 Ver.",
                "stock": 0,
                "status": "已转卖",
                "cost_price": 1200,
                "current_price": 1000,
                "profit": -200,
                "profit_percentage": -17,
                "purchase_date": "2025-06",
                "holding_days": 180,
                "market_share": 0
            }
        ]
    else:
        for fig in figures:
            cost_price = fig.purchase_price or 0
            current_price = fig.current_value or 0
            profit = current_price - cost_price
            profit_percentage = (profit / cost_price * 100) if cost_price > 0 else 0
            
            # 确定状态
            if profit_percentage < -10:
                status = "破位"
            else:
                status = "正常"
            
            holdings.append({
                "figure_id": fig.id,
                "figure_name": fig.name,
                "stock": 1,
                "status": status,
                "cost_price": cost_price,
                "current_price": current_price,
                "profit": profit,
                "profit_percentage": profit_percentage,
                "purchase_date": "2024-01",
                "holding_days": 365,
                "market_share": 10.0
            })
    
    # 返回数据
    return {
        "summary": summary,
        "profit": profit,
        "kline_data": kline_data,
        "rankings": rankings,
        "advice": advice,
        "holdings": holdings
    }

@router.post("/price-history", response_model=AssetPriceHistorySchema)
def create_price_history(
    price_history: AssetPriceHistoryCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """创建价格历史记录"""
    db_price_history = AssetPriceHistory(**price_history.model_dump())
    db.add(db_price_history)
    db.commit()
    db.refresh(db_price_history)
    
    # 更新手办的当前估值
    figure = db.query(Figure).filter(Figure.id == price_history.figure_id).first()
    if figure:
        figure.current_value = price_history.current_price
        db.commit()
    
    return db_price_history

@router.get("/price-history/{figure_id}", response_model=List[AssetPriceHistorySchema])
def get_price_history(
    figure_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取手办的价格历史"""
    return db.query(AssetPriceHistory).filter(
        AssetPriceHistory.figure_id == figure_id
    ).order_by(desc(AssetPriceHistory.date)).all()

@router.post("/alerts", response_model=AssetAlertSchema)
def create_alert(
    alert: AssetAlertCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """创建资产预警"""
    db_alert = AssetAlert(
        user_id=current_user.id,
        **alert.model_dump()
    )
    db.add(db_alert)
    db.commit()
    db.refresh(db_alert)
    return db_alert

@router.get("/alerts", response_model=List[AssetAlertSchema])
def get_alerts(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取用户的资产预警"""
    return db.query(AssetAlert).filter(
        AssetAlert.user_id == current_user.id
    ).all()

@router.post("/transactions", response_model=AssetTransactionSchema)
def create_transaction(
    transaction: AssetTransactionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """创建资产交易记录"""
    db_transaction = AssetTransaction(
        user_id=current_user.id,
        **transaction.model_dump()
    )
    db.add(db_transaction)
    db.commit()
    db.refresh(db_transaction)
    return db_transaction

@router.get("/transactions", response_model=List[AssetTransactionSchema])
def get_transactions(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取用户的资产交易记录"""
    return db.query(AssetTransaction).filter(
        AssetTransaction.user_id == current_user.id
    ).order_by(desc(AssetTransaction.transaction_date)).all()

@router.get("/collector/dashboard")
def get_collector_dashboard(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取收藏家模式的看板数据"""
    # 获取所有手办
    figures = db.query(Figure).all()
    
    # 计算总投入、现估值和回血额
    total_investment = sum(fig.purchase_price or 0 for fig in figures)
    total_valuation = sum(fig.current_value or 0 for fig in figures)
    
    # 计算回血额（已卖出的手办的利润）
    sold_transactions = db.query(AssetTransaction).filter(
        AssetTransaction.user_id == current_user.id,
        AssetTransaction.transaction_type == "sell"
    ).all()
    blood_money = sum(t.price for t in sold_transactions)
    
    # 构建高价值藏品数据（模拟数据）
    valuable_items = [
        {
            "id": 1,
            "name": "初音韶华",
            "image": "https://example.com/figure1.jpg",
            "profit": 1200,
            "status": "海景房"
        },
        {
            "id": 2,
            "name": "蕾姆婚纱",
            "image": "https://example.com/figure2.jpg",
            "profit": 800,
            "status": "小赚"
        },
        {
            "id": 3,
            "name": "Saber",
            "image": "https://example.com/figure3.jpg",
            "profit": -200,
            "status": "破发"
        },
        {
            "id": 4,
            "name": "艾米莉亚",
            "image": "https://example.com/figure4.jpg",
            "status": "已转卖",
            "sold_profit": 500
        }
    ]
    
    # 构建标签云数据
    tags = [
        {"name": "海景房", "count": 3},
        {"name": "破发区", "count": 5},
        {"name": "待补款", "count": 2},
        {"name": "已出坑", "count": 8}
    ]
    
    # 构建动态流数据
    activities = [
        {
            "date": "2026-03-15",
            "content": "入手初音韶华 180天，估值上涨150%",
            "actions": ["生成分享卡片", "查看详情"]
        },
        {
            "date": "2026-02-20",
            "content": "蕾姆婚纱补款完成，等待发货",
            "actions": ["查看详情"]
        }
    ]
    
    return {
        "summary": {
            "total_investment": total_investment,
            "total_valuation": total_valuation,
            "blood_money": blood_money
        },
        "valuable_items": valuable_items,
        "tags": tags,
        "activities": activities
    }

@router.get("/trade/dashboard")
def get_trade_dashboard(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取交易管理页面数据"""
    # 计算本月开始日期
    now = datetime.now()
    month_start = datetime(now.year, now.month, 1)
    year_start = datetime(now.year, 1, 1)
    
    # 获取本月交易数据
    monthly_transactions = db.query(AssetTransaction).filter(
        AssetTransaction.user_id == current_user.id,
        AssetTransaction.transaction_date >= month_start
    ).all()
    
    # 计算本月交易统计
    buy_count = 0
    buy_amount = 0
    sell_count = 0
    sell_amount = 0
    
    for t in monthly_transactions:
        if t.transaction_type == "buy":
            buy_count += 1
            buy_amount += t.price
        elif t.transaction_type == "sell":
            sell_count += 1
            sell_amount += t.price
    
    net_cashflow = sell_amount - buy_amount
    
    # 获取交易流水（最近10条）
    transactions = db.query(AssetTransaction).filter(
        AssetTransaction.user_id == current_user.id
    ).order_by(desc(AssetTransaction.transaction_date)).limit(10).all()
    
    # 构建交易流水数据
    transaction_list = []
    for t in transactions:
        # 根据交易类型构建标题
        if t.transaction_type == "buy":
            title = f"买入: {t.notes}"
        elif t.transaction_type == "sell":
            title = f"卖出: {t.notes}"
        elif t.transaction_type == "payment":
            title = f"补款: {t.notes}"
        elif t.transaction_type == "shipping":
            title = f"运费: {t.notes}"
        elif t.transaction_type == "refund":
            title = f"退款: {t.notes}"
        else:
            title = t.notes
        
        # 构建交易记录
        transaction_item = {
            "id": t.id,
            "date": t.transaction_date.strftime("%m-%d %H:%M"),
            "amount": t.price if t.transaction_type == "sell" else -t.price,
            "title": title,
            "status": "✅ 成功" if t.status == "completed" else "⏳ 处理中",
            "actions": ["查看详情"]
        }
        
        # 根据交易类型添加额外信息
        if t.transaction_type == "buy":
            transaction_item["order_id"] = f"ORD{t.id:09d}"
            transaction_item["payment_method"] = "支付宝"
            transaction_item["merchant"] = "AmiAmi"
            transaction_item["actions"] = ["查看订单", "申请售后", "下载电子发票"]
        elif t.transaction_type == "sell":
            transaction_item["buyer"] = "闲鱼用户_xxx"
            transaction_item["platform"] = "闲鱼"
            transaction_item["fee"] = t.price * 0.006  # 模拟手续费
            transaction_item["net_profit"] = t.price - transaction_item["fee"]
            transaction_item["actions"] = ["查看买家信息", "物流信息", "评价"]
        elif t.transaction_type == "payment":
            transaction_item["order_id"] = f"ORD{t.id:09d}"
            transaction_item["payment_method"] = "支付宝"
            transaction_item["merchant"] = "AmiAmi"
        
        transaction_list.append(transaction_item)
    
    # 计算本年盈亏分析
    yearly_transactions = db.query(AssetTransaction).filter(
        AssetTransaction.user_id == current_user.id,
        AssetTransaction.transaction_date >= year_start
    ).all()
    
    yearly_profit = 0
    win_count = 0
    loss_count = 0
    profits = []
    
    for t in yearly_transactions:
        if t.transaction_type == "sell":
            # 查找对应的买入记录
            buy_transaction = db.query(AssetTransaction).filter(
                AssetTransaction.user_id == current_user.id,
                AssetTransaction.transaction_type == "buy",
                AssetTransaction.notes == t.notes
            ).first()
            
            if buy_transaction:
                profit = t.price - buy_transaction.price
                yearly_profit += profit
                profits.append(profit)
                if profit > 0:
                    win_count += 1
                elif profit < 0:
                    loss_count += 1
    
    # 计算胜率和平均盈亏
    total_trades = win_count + loss_count
    win_rate = (win_count / total_trades * 100) if total_trades > 0 else 0
    avg_profit = (sum(p for p in profits if p > 0) / win_count) if win_count > 0 else 0
    avg_loss = (abs(sum(p for p in profits if p < 0)) / loss_count) if loss_count > 0 else 0
    
    # 计算最大盈利和最大亏损
    max_profit = max(profits) if profits else 0
    max_loss = abs(min(profits)) if profits else 0
    max_profit_item = "初音韶华" if max_profit > 0 else ""
    max_loss_item = "蕾姆" if max_loss > 0 else ""
    
    # 构建盈亏分析数据
    profit_analysis = {
        "yearly_profit": yearly_profit,
        "win_rate": round(win_rate, 1),
        "win_count": win_count,
        "loss_count": loss_count,
        "avg_profit": round(avg_profit, 2),
        "avg_loss": round(avg_loss, 2),
        "max_profit": round(max_profit, 2),
        "max_profit_item": max_profit_item,
        "max_loss": round(max_loss, 2),
        "max_loss_item": max_loss_item
    }
    
    # 如果没有交易数据，返回模拟数据
    if not monthly_transactions and not yearly_transactions:
        return {
            "monthly_stats": {
                "buy_count": 3,
                "buy_amount": 5600,
                "sell_count": 2,
                "sell_amount": 2400,
                "net_cashflow": -3200
            },
            "transactions": [
                {
                    "id": 1,
                    "date": "04-02 14:30",
                    "amount": -800,
                    "title": "买入: 初音未来 韶华 Ver. (尾款支付)",
                    "order_id": "ORD20260402001",
                    "status": "✅ 成功",
                    "payment_method": "支付宝",
                    "merchant": "AmiAmi",
                    "actions": ["查看订单", "申请售后", "下载电子发票"]
                },
                {
                    "id": 2,
                    "date": "03-28 10:15",
                    "amount": 1200,
                    "title": "卖出: 蕾姆 婚纱 Ver.",
                    "buyer": "闲鱼用户_xxx",
                    "platform": "闲鱼",
                    "status": "✅ 已到账",
                    "fee": 7.2,
                    "net_profit": 292.8,
                    "actions": ["查看买家信息", "物流信息", "评价"]
                },
                {
                    "id": 3,
                    "date": "03-20 09:00",
                    "amount": -200,
                    "title": "定金: Saber 礼服 Ver. (预定锁定)",
                    "status": "⏳ 持有中",
                    "estimated_payment": "2026-06",
                    "actions": ["补款提醒设置", "转让定金", "放弃定金"]
                }
            ],
            "profit_analysis": {
                "yearly_profit": 3400,
                "win_rate": 66.7,
                "win_count": 4,
                "loss_count": 2,
                "avg_profit": 850,
                "avg_loss": 200,
                "max_profit": 1200,
                "max_profit_item": "初音韶华",
                "max_loss": 200,
                "max_loss_item": "蕾姆"
            }
        }
    
    return {
        "monthly_stats": {
            "buy_count": buy_count,
            "buy_amount": buy_amount,
            "sell_count": sell_count,
            "sell_amount": sell_amount,
            "net_cashflow": net_cashflow
        },
        "transactions": transaction_list,
        "profit_analysis": profit_analysis
    }

@router.get("/market/dashboard")
def get_market_dashboard(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取行情页面数据"""
    # 模拟塑料小人指数数据
    index_data = {
        "value": 2847.35,
        "change": 45.20,
        "change_percentage": 1.61,
        "volume": 230000000,
        "up_count": 1230,
        "flat_count": 45,
        "down_count": 320,
        "limit_up": "初音、蕾姆、狂三",
        "limit_down": "无"
    }
    
    # 模拟K线图数据
    kline_data = {
        "macd": "金叉",
        "rsi": 68
    }
    
    # 模拟板块涨幅排行数据
    sectors_data = [
        {
            "name": "初音未来概念",
            "change": 8.5,
            "stocks": "初音韶华、赛车音、雪未来"
        },
        {
            "name": "FGO系列",
            "change": 5.2,
            "stocks": "摩根、妖兰、提亚马特"
        },
        {
            "name": "碧蓝航线",
            "change": 3.1,
            "stocks": "信浓、柴郡、埃吉尔"
        },
        {
            "name": "原神系列",
            "change": -2.3,
            "stocks": "雷神、神子(高位回调)"
        }
    ]
    
    # 模拟我的自选股数据
    watchlist_data = [
        {
            "name": "初音韶华",
            "current_price": 2000,
            "change": 15,
            "target_price": 2500,
            "target_distance": "还差25%"
        },
        {
            "name": "蕾姆婚纱",
            "current_price": 1200,
            "change": -5,
            "target_price": 1500,
            "target_distance": "还需上涨30%"
        },
        {
            "name": "(观望中)",
            "current_price": 800,
            "change": 0,
            "target_price": 600,
            "target_distance": "等破发入手"
        }
    ]
    
    # 模拟智能投研数据
    research_data = {
        "rating": "GSC 初音韶华 买入",
        "target_price": "¥2,800 (+40%)",
        "stop_loss": "¥1,600 (-20%)",
        "institution": "Hpoi研究院",
        "date": "2026-04-01",
        "reason": "再版停产公告+海景房属性+即将出荷"
    }
    
    # 返回数据
    return {
        "index": index_data,
        "kline": kline_data,
        "sectors": sectors_data,
        "watchlist": watchlist_data,
        "research": research_data
    }


def get_sh_index_from_qq():
    """从腾讯财经获取上证指数数据"""
    url = "https://qt.gtimg.cn/q=sh000001"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36 QQBrowser/12.0',
        'Referer': 'https://stock.finance.qq.com/',
        'Accept': '*/*',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'zh-CN,zh;q=0.9',
        'Connection': 'keep-alive'
    }
    
    try:
        # 随机延时3-8秒
        delay = random.uniform(3, 8)
        time.sleep(delay)
        
        response = requests.get(url, headers=headers, timeout=30)
        response.encoding = 'gbk'
        
        if response.status_code == 200:
            # 解析返回的数据
            # 格式: v_sh000001="1~上证指数~000001~3880.10~3919.29~3927.59..."
            content = response.text
            match = re.search(r'v_sh000001="([^"]+)"', content)
            
            if match:
                data_parts = match.group(1).split('~')
                if len(data_parts) >= 6:
                    # data_parts[3] = 当前价格
                    # data_parts[4] = 昨日收盘价
                    # data_parts[5] = 今日开盘价
                    current_value = float(data_parts[3])
                    prev_close = float(data_parts[4])
                    change_value = current_value - prev_close
                    change_percentage = (change_value / prev_close) * 100 if prev_close > 0 else 0
                    
                    return {
                        "index_code": "sh000001",
                        "index_name": "上证指数",
                        "current_value": current_value,
                        "change_value": round(change_value, 2),
                        "change_percentage": round(change_percentage, 2)
                    }
        
        return None
    except Exception as e:
        print(f"获取上证指数失败: {e}")
        return None


def get_cached_sh_index(db: Session):
    """获取缓存的上证指数数据，必要时从腾讯财经获取"""
    today = date.today()
    cache_key = "sh000001"
    
    # 查询缓存
    cache_record = db.query(StockIndexCache).filter(
        StockIndexCache.index_code == cache_key
    ).first()
    
    # 检查是否需要从接口获取新数据
    need_fetch = False
    
    if not cache_record:
        # 没有缓存记录，需要获取
        need_fetch = True
    elif cache_record.request_date != today:
        # 日期变了，重置请求计数并获取
        need_fetch = True
    elif cache_record.request_count >= 6:
        # 当日请求次数已达上限，使用缓存数据
        need_fetch = False
    else:
        # 检查缓存时间是否超过3小时
        cache_age = datetime.now() - cache_record.updated_at
        if cache_age.total_seconds() > 3 * 3600:  # 3小时
            need_fetch = True
        else:
            # 缓存未过期，使用缓存数据
            need_fetch = False
    
    if need_fetch and (not cache_record or cache_record.request_count < 6):
        # 从腾讯财经获取数据
        index_data = get_sh_index_from_qq()
        
        if index_data:
            if cache_record:
                # 更新缓存记录
                cache_record.current_value = index_data["current_value"]
                cache_record.change_value = index_data["change_value"]
                cache_record.change_percentage = index_data["change_percentage"]
                cache_record.updated_at = datetime.now()
                cache_record.request_count += 1
                cache_record.request_date = today
            else:
                # 创建新的缓存记录
                cache_record = StockIndexCache(
                    index_code=index_data["index_code"],
                    index_name=index_data["index_name"],
                    current_value=index_data["current_value"],
                    change_value=index_data["change_value"],
                    change_percentage=index_data["change_percentage"],
                    request_count=1,
                    request_date=today
                )
                db.add(cache_record)
            
            db.commit()
            return index_data
    
    # 返回缓存数据
    if cache_record:
        return {
            "index_code": cache_record.index_code,
            "index_name": cache_record.index_name,
            "current_value": cache_record.current_value,
            "change_value": cache_record.change_value,
            "change_percentage": cache_record.change_percentage
        }
    
    # 如果没有缓存且获取失败，返回默认值
    return {
        "index_code": "sh000001",
        "index_name": "上证指数",
        "current_value": 3200,
        "change_value": 0,
        "change_percentage": 0
    }
