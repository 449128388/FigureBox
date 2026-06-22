"""
collector_transaction_service.py - 收藏家模式收藏历程服务

功能说明：
- 提供藏品收藏历程（全生命周期流水）查询服务
- 汇总某个手办下的所有交易记录（资金流水）

API端点对应：
- GET /collector/figures/{figure_id}/transactions

依赖：
- OrderTransaction 模型（订单资金流水表）
- Figure 模型
"""

from sqlalchemy.orm import Session
from sqlalchemy import desc, asc
from datetime import datetime

from app.models.asset import OrderTransaction


class CollectorTransactionService:
    """收藏家模式收藏历程服务类"""

    @staticmethod
    def get_figure_transactions(db: Session, user_id: int, figure_id: int) -> list:
        """
        获取手办全生命周期交易流水

        查询该 figure_id 下所有 order_transactions 记录，
        按 transaction_date 升序排列，计算累计库存结余。

        Args:
            db: 数据库会话
            user_id: 用户ID
            figure_id: 手办ID

        Returns:
            list[dict]: 交易流水列表，按 transaction_date 倒序排列
            每项包含：
            - date: 交易日期
            - type: 交易类型（buy=买入, sell=卖出, refund=退款, fee=手续费）
            - type_label: 交易类型中文标签
            - quantity: 交易数量
            - price: 单价
            - total_amount: 总金额
            - balance: 当日交易后的库存结余
            - fee_detail: （仅 fee 合并后）运费、平台手续费明细
        """
        # 查询所有交易记录，按日期升序
        transactions = db.query(OrderTransaction).filter(
            OrderTransaction.user_id == user_id,
            OrderTransaction.figure_id == figure_id,
            OrderTransaction.is_active == True
        ).order_by(OrderTransaction.transaction_date.asc()).all()

        if not transactions:
            return []

        # 按日期升序遍历计算库存结余
        running_balance = 0
        result = []
        for t in transactions:
            # 确定交易类型和标签
            if t.direction == 'out' and t.transaction_type in ('buy', 'deposit', 'balance'):
                # 买入类交易：库存增加
                running_balance += (t.quantity or 0)
                # 按 transaction_type 细分：deposit→定金，balance→尾款
                if t.transaction_type == 'deposit':
                    label = '定金'
                elif t.transaction_type == 'balance':
                    label = '尾款'
                else:
                    # buy 类型时通过 notes 判断是否补仓
                    is_replenish = t.notes and '补仓' in t.notes
                    label = '补仓' if is_replenish else '买入'
                trans_type = 'buy'
            elif t.direction == 'in' and t.transaction_type == 'sell':
                # 卖出：库存减少
                running_balance -= (t.quantity or 0)
                label = '卖出'
                trans_type = 'sell'
            elif t.transaction_type == 'refund':
                # 退款：库存不变（款项退回）
                label = '退款'
                trans_type = 'refund'
            elif t.transaction_type == 'fee':
                # 手续费：库存不变，按 notes 区分运费/平台手续费
                label = '手续费'
                trans_type = 'fee'
            else:
                label = t.transaction_type or '其他'
                trans_type = t.transaction_type or 'other'

            date_str = None
            if t.transaction_date:
                if isinstance(t.transaction_date, datetime):
                    date_str = t.transaction_date.strftime("%Y-%m-%d")
                else:
                    date_str = str(t.transaction_date)

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
                "balance": running_balance,
                "fee_type": fee_type
            })

        # 合并同一日期的 fee 交易
        merged = []
        i = 0
        while i < len(result):
            if result[i]['type'] == 'fee':
                # 收集同一日期的所有 fee 记录
                same_date_fees = []
                j = i
                while j < len(result) and result[j]['type'] == 'fee' and result[j]['date'] == result[i]['date']:
                    same_date_fees.append(result[j])
                    j += 1

                # 合并这些 fee 记录
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

        # 按日期倒序返回（前端按时间线展示）
        merged.reverse()
        return merged
