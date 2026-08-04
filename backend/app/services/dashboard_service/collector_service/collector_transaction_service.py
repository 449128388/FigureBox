"""
collector_transaction_service.py - 收藏家模式收藏历程服务

功能说明：
- 提供藏品收藏历程（全生命周期流水）查询服务
- 时间轴事件取自 order_transactions（资金流水）
- 库存数值取自 asset_transactions（库存账）

API端点对应：
- GET /collector/figures/{figure_id}/transactions

依赖：
- OrderTransaction 模型（订单资金流水表）
- AssetTransaction 模型（资产交易表）
"""

from sqlalchemy.orm import Session
from sqlalchemy import desc, asc
from datetime import datetime

from app.models.asset import OrderTransaction, AssetTransaction


class CollectorTransactionService:
    """收藏家模式收藏历程服务类"""

    @staticmethod
    def get_figure_transactions(db: Session, user_id: int, figure_id: int) -> list:
        """
        获取手办全生命周期交易流水

        时间轴事件取自 order_transactions 记录，
        库存数值（balance）取自 asset_transactions 表的 remaining_quantity。

        Args:
            db: 数据库会话
            user_id: 用户ID
            figure_id: 手办ID

        Returns:
            list[dict]: 交易流水列表，按 transaction_date 倒序排列
        """
        # 1. 获取所有 asset_transactions（用于计算实时库存）
        asset_txs = db.query(AssetTransaction).filter(
            AssetTransaction.user_id == user_id,
            AssetTransaction.figure_id == figure_id,
            AssetTransaction.is_active == True
        ).order_by(AssetTransaction.transaction_date.asc()).all()

        # 构建 asset_transactions 的时间轴库存快照
        # 对每个资产交易，按日期累加 remaining_quantity 变化
        asset_stock_at_date = {}  # date_str -> stock
        running_stock = 0
        for at in asset_txs:
            date_key = None
            if at.transaction_date:
                if isinstance(at.transaction_date, datetime):
                    date_key = at.transaction_date.strftime("%Y-%m-%d %H:%M:%S")
                else:
                    date_key = str(at.transaction_date)
            else:
                continue

            if at.transaction_type == 'buy':
                running_stock += (at.remaining_quantity or 0)
            elif at.transaction_type == 'sell':
                running_stock -= (at.quantity or 0)
            # 记录该时间点的库存
            asset_stock_at_date[date_key] = running_stock

        # 当前总库存
        current_stock = running_stock

        # 2. 获取所有 order_transactions（用于时间轴事件）
        transactions = db.query(OrderTransaction).filter(
            OrderTransaction.user_id == user_id,
            OrderTransaction.figure_id == figure_id,
            OrderTransaction.is_active == True
        ).order_by(OrderTransaction.transaction_date.asc()).all()

        if not transactions:
            return []

        # 识别同一时间点的币种变更配对（退款+支付），合并为一条变更记录
        # 支持两种类型：
        #   1. deposit - "定金币种变更退款"+"定金币种变更支付" → 标签"定金币种"
        #   2. balance - "尾款币种变更退款"+"尾款币种变更支付" → 标签"尾款币种"
        CURRENCY_CHANGE_CONFIG = {
            'deposit': ('定金币种变更退款', '定金币种变更支付', '定金币种'),
            'balance': ('尾款币种变更退款', '尾款币种变更支付', '尾款币种'),
        }

        currency_change_pairs = {}  # (date_str, txn_type) -> {"refund": tx, "payment": tx}
        for t in transactions:
            if t.transaction_type in CURRENCY_CHANGE_CONFIG and t.notes:
                date_str = None
                if t.transaction_date:
                    if isinstance(t.transaction_date, datetime):
                        date_str = t.transaction_date.strftime("%Y-%m-%d %H:%M:%S")
                    else:
                        date_str = str(t.transaction_date)

                if date_str:
                    refund_keyword, payment_keyword, _ = CURRENCY_CHANGE_CONFIG[t.transaction_type]
                    pair_key = (date_str, t.transaction_type)
                    if pair_key not in currency_change_pairs:
                        currency_change_pairs[pair_key] = {}
                    if refund_keyword in t.notes:
                        currency_change_pairs[pair_key]['refund'] = t
                    elif payment_keyword in t.notes:
                        currency_change_pairs[pair_key]['payment'] = t

        # 收集需要跳过的交易ID（已配对的）
        cc_skip_ids = set()
        cc_merged_data = []  # list of merged dicts
        for pair_key, pair in currency_change_pairs.items():
            if 'refund' in pair and 'payment' in pair:
                date_str, txn_type = pair_key
                cc_skip_ids.add(pair['refund'].id)
                cc_skip_ids.add(pair['payment'].id)

                # 从模型字段中获取币种变更信息
                # 退款记录包含原始金额和原币种，支付记录包含新金额和新币种
                refund_tx = pair['refund']
                payment_tx = pair['payment']
                from_amount = str(refund_tx.previous_amount or refund_tx.total_amount or '')
                from_currency = refund_tx.currency or ''
                to_amount = str(payment_tx.current_amount or payment_tx.total_amount or '')
                to_currency = payment_tx.currency or ''

                _, _, type_label = CURRENCY_CHANGE_CONFIG[txn_type]

                cc_merged_data.append({
                    "date_str": date_str,
                    "refund_tx": refund_tx,
                    "payment_tx": payment_tx,
                    "from_amount": from_amount,
                    "from_currency": from_currency,
                    "to_amount": to_amount,
                    "to_currency": to_currency,
                    "type_label": type_label
                })

        # 按日期升序遍历计算库存结余
        result = []
        for t in transactions:
            # 跳过已配对的币种变更交易（定金币种/尾款币种），后续合并处理
            if t.id in cc_skip_ids:
                continue
            # 确定交易类型和标签
            if t.direction == 'out' and t.transaction_type in ('buy', 'deposit', 'balance'):
                if t.transaction_type == 'deposit':
                    # 通过 notes 区分是"定金"还是"补仓"
                    label = '补仓' if (t.notes and '补仓' in t.notes) else '定金'
                elif t.transaction_type == 'balance':
                    # 通过 notes 区分是"尾款"还是"补仓"
                    label = '补仓' if (t.notes and '补仓' in t.notes) else '尾款'
                else:
                    label = '补仓' if (t.notes and '补仓' in t.notes) else '买入'
                trans_type = 'buy'
            elif t.direction == 'in' and t.transaction_type == 'sell':
                label = '卖出'
                trans_type = 'sell'
            elif t.transaction_type == 'refund':
                label = '退款'
                trans_type = 'refund'
            elif t.transaction_type == 'fee':
                label = '手续费'
                trans_type = 'fee'
            else:
                label = t.transaction_type or '其他'
                trans_type = t.transaction_type or 'other'

            date_str = None
            if t.transaction_date:
                if isinstance(t.transaction_date, datetime):
                    date_str = t.transaction_date.strftime("%Y-%m-%d %H:%M:%S")
                else:
                    date_str = str(t.transaction_date)

            # 查找该时间点的库存（从 asset_transactions 快照中取最近的库存值）
            balance = current_stock
            if date_str and date_str in asset_stock_at_date:
                balance = asset_stock_at_date[date_str]
            elif asset_stock_at_date:
                # 取最接近的之前时间点的库存
                sorted_dates = sorted(asset_stock_at_date.keys())
                for d in reversed(sorted_dates):
                    if d <= date_str:
                        balance = asset_stock_at_date[d]
                        break

            # 为 fee 交易记录额外标识费用类型
            fee_type = None
            if trans_type == 'fee':
                if t.notes and '运费' in t.notes:
                    fee_type = 'shipping'
                elif t.notes and '平台手续费' in t.notes:
                    fee_type = 'platform'

            result.append({
                "date": date_str,
                "type": trans_type,
                "type_label": label,
                "quantity": t.quantity or 1,
                "price": t.unit_price or 0,
                "total_amount": t.total_amount or 0,
                "balance": balance,
                "fee_type": fee_type
            })

        # 合并同一日期的 fee 交易
        merged = []
        i = 0
        while i < len(result):
            if result[i]['type'] == 'fee':
                same_date_fees = []
                j = i
                while j < len(result) and result[j]['type'] == 'fee' and result[j]['date'] == result[i]['date']:
                    same_date_fees.append(result[j])
                    j += 1

                shipping_fee = 0
                platform_fee = 0
                total_fee = 0
                for fee in same_date_fees:
                    total_fee += fee['total_amount']
                    if fee['fee_type'] == 'shipping':
                        shipping_fee += fee['total_amount']
                    else:
                        platform_fee += fee['total_amount']

                merged.append({
                    "date": result[i]['date'],
                    "type": "fee",
                    "type_label": "手续费",
                    "quantity": 1,
                    "price": total_fee,
                    "total_amount": total_fee,
                    "balance": same_date_fees[-1]['balance'],
                    "fee_detail": {
                        "shipping_fee": shipping_fee,
                        "platform_fee": platform_fee,
                        "total": total_fee
                    },
                    "fee_type": None
                })
                i = j
            else:
                merged.append(result[i])
                i += 1

        # 添加币种变更合并记录（定金币种/尾款币种）
        for cc_data in cc_merged_data:
            date_str = cc_data['date_str']

            # 查找该时间点的库存
            balance = current_stock
            if date_str and date_str in asset_stock_at_date:
                balance = asset_stock_at_date[date_str]
            elif asset_stock_at_date:
                sorted_dates = sorted(asset_stock_at_date.keys())
                for d in reversed(sorted_dates):
                    if d <= date_str:
                        balance = asset_stock_at_date[d]
                        break

            merged.append({
                "date": date_str,
                "type": "currency_change",
                "type_label": cc_data['type_label'],
                "quantity": 1,
                "price": 0,
                "total_amount": 0,
                "balance": balance,
                "currency_change": {
                    "from_amount": cc_data['from_amount'],
                    "from_currency": cc_data['from_currency'],
                    "to_amount": cc_data['to_amount'],
                    "to_currency": cc_data['to_currency']
                }
            })

        # 按日期升序排序
        merged.sort(key=lambda x: x['date'] or '')

        # 按日期倒序返回（前端按时间线展示）
        merged.reverse()
        return merged
