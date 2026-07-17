"""
trade_filter_service.py - 交易流水筛选服务

功能说明：
- 提供交易流水的高级筛选功能
- 支持时间范围、手办、平台、状态、金额、关键词等多维度筛选
- 与 TransactionQueryService 配合实现数据查询

筛选维度：
- 时间范围：近7天/近30天/本月/上月/本年/自定义日期
- 手办名称：多选手办ID筛选
- 平台：多选平台筛选
- 订单状态：多选状态筛选
- 金额范围：最小金额到最大金额
- 关键词：模糊匹配订单号、手办名、备注等

创建时间: 2026-06-02
作者: FigureBox Team
"""

from datetime import datetime, date, timedelta
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_, func

from app.models.order import Order
from app.models.sold_order import SoldOrder
from app.models.asset import OrderTransaction
from app.models.figure import Figure


class TradeFilterService:
    """交易流水筛选服务"""

    @classmethod
    def build_time_filter(cls, time_type: str, date_range: List[str] = None) -> tuple:
        """
        构建时间筛选条件

        Args:
            time_type: 时间类型 (last7days/last30days/thisMonth/lastMonth/thisYear/custom)
            date_range: 自定义日期范围 [start_date, end_date]

        Returns:
            tuple: (start_date, end_date)
        """
        today = date.today()

        if time_type == 'last7days':
            start = today - timedelta(days=7)
            end = today
        elif time_type == 'last30days':
            start = today - timedelta(days=30)
            end = today
        elif time_type == 'thisMonth':
            start = today.replace(day=1)
            end = today
        elif time_type == 'lastMonth':
            # 上月的第一天和最后一天
            if today.month == 1:
                start = today.replace(year=today.year - 1, month=12, day=1)
                end = today.replace(year=today.year - 1, month=12, day=31)
            else:
                start = today.replace(month=today.month - 1, day=1)
                # 计算上月最后一天
                last_day = (today.replace(day=1) - timedelta(days=1)).day
                end = today.replace(month=today.month - 1, day=last_day)
        elif time_type == 'thisYear':
            start = today.replace(month=1, day=1)
            end = today
        elif time_type == 'custom' and date_range and len(date_range) == 2:
            start = datetime.strptime(date_range[0], '%Y-%m-%d').date()
            end = datetime.strptime(date_range[1], '%Y-%m-%d').date()
        else:
            # 默认近30天
            start = today - timedelta(days=30)
            end = today

        return start, end

    @classmethod
    def build_buy_query_filters(cls, db: Session, filters: Dict[str, Any]) -> List:
        """
        构建买入订单查询过滤条件

        Args:
            db: 数据库会话
            filters: 筛选参数字典

        Returns:
            List: SQLAlchemy 过滤条件列表
        """
        query_filters = []

        # 时间筛选
        if filters.get('timeType'):
            start, end = cls.build_time_filter(
                filters['timeType'],
                filters.get('dateRange', [])
            )
            query_filters.append(Order.order_date >= start)
            query_filters.append(Order.order_date <= end)

        # 手办筛选
        if filters.get('figureIds'):
            query_filters.append(Order.figure_id.in_(filters['figureIds']))

        # 平台筛选
        if filters.get('platforms'):
            query_filters.append(Order.purchase_platform.in_(filters['platforms']))

        # 状态筛选
        if filters.get('statusList'):
            # 买入订单状态映射
            status_mapping = {
                '已完成': '已完成',
                '待入库': '待入库',
                '已取消': '已取消',
                '已退款': '已退款'
            }
            mapped_statuses = [
                status_mapping.get(s, s)
                for s in filters['statusList']
                if s in status_mapping
            ]
            if mapped_statuses:
                query_filters.append(Order.status.in_(mapped_statuses))

        # 金额范围筛选
        if filters.get('minAmount') is not None:
            query_filters.append(Order.total_amount >= filters['minAmount'])
        if filters.get('maxAmount') is not None:
            query_filters.append(Order.total_amount <= filters['maxAmount'])

        # 关键词搜索
        if filters.get('keyword'):
            keyword = f"%{filters['keyword']}%"
            query_filters.append(
                or_(
                    Order.order_number.like(keyword),
                    Order.remarks.like(keyword),
                    Figure.name.like(keyword),
                    Figure.character_name.like(keyword),
                    Figure.series.like(keyword)
                )
            )

        return query_filters

    @classmethod
    def build_sell_query_filters(cls, db: Session, filters: Dict[str, Any]) -> List:
        """
        构建卖出订单查询过滤条件

        Args:
            db: 数据库会话
            filters: 筛选参数字典

        Returns:
            List: SQLAlchemy 过滤条件列表
        """
        query_filters = []

        # 时间筛选
        if filters.get('timeType'):
            start, end = cls.build_time_filter(
                filters['timeType'],
                filters.get('dateRange', [])
            )
            query_filters.append(SoldOrder.sell_date >= start)
            query_filters.append(SoldOrder.sell_date <= end)

        # 手办筛选
        if filters.get('figureIds'):
            query_filters.append(SoldOrder.figure_id.in_(filters['figureIds']))

        # 平台筛选
        if filters.get('platforms'):
            query_filters.append(SoldOrder.sell_platform.in_(filters['platforms']))

        # 状态筛选
        if filters.get('statusList'):
            # 卖出订单状态映射
            status_mapping = {
                '已完成': '已完成',
                '待发货': '待发货',
                '已取消': '已取消',
                '已退款': '已退款'
            }
            mapped_statuses = [
                status_mapping.get(s, s)
                for s in filters['statusList']
                if s in status_mapping
            ]
            if mapped_statuses:
                query_filters.append(SoldOrder.status.in_(mapped_statuses))

        # 金额范围筛选
        if filters.get('minAmount') is not None:
            query_filters.append(SoldOrder.sell_price >= filters['minAmount'])
        if filters.get('maxAmount') is not None:
            query_filters.append(SoldOrder.sell_price <= filters['maxAmount'])

        # 关键词搜索
        if filters.get('keyword'):
            keyword = f"%{filters['keyword']}%"
            query_filters.append(
                or_(
                    SoldOrder.order_number.like(keyword),
                    SoldOrder.remark.like(keyword),
                    Figure.name.like(keyword),
                    Figure.character_name.like(keyword),
                    Figure.series.like(keyword)
                )
            )

        return query_filters

    @classmethod
    def apply_filters_to_transactions(
        cls,
        transactions: List[Dict[str, Any]],
        filters: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        对交易记录列表应用筛选条件（前端筛选备用方案）

        Args:
            transactions: 交易记录列表
            filters: 筛选参数字典

        Returns:
            List[Dict]: 筛选后的交易记录列表
        """
        result = transactions

        # 时间筛选
        if filters.get('timeType') and filters['timeType'] != 'last30days':
            start, end = cls.build_time_filter(
                filters['timeType'],
                filters.get('dateRange', [])
            )
            result = [
                t for t in result
                if t.get('date') and start <= datetime.strptime(t['date'][:10], '%Y-%m-%d').date() <= end
            ]

        # 筛选类型过滤
        if filters.get('filterType') and filters['filterType'] != 'all':
            filter_type = filters['filterType']
            if filter_type == 'income':
                result = [t for t in result if t.get('card_type') == 'sell']
            elif filter_type == 'expense':
                result = [t for t in result if t.get('card_type') == 'buy']
            elif filter_type == 'fee':
                result = [t for t in result if t.get('type') == '费用']

        # 平台筛选
        if filters.get('platforms'):
            platforms = filters['platforms']
            result = [t for t in result if t.get('platform') in platforms]

        # 状态筛选
        if filters.get('statusList'):
            statuses = filters['statusList']
            # 状态映射（买入记录的状态带有表情符号前缀）
            status_mapping = {
                '已完成': ['已完成', '✅ 已完成'],
                '待发货': ['待发货'],
                '待入库': ['待入库'],
                '已取消': ['已取消', '❌ 已取消'],
                '已退款': ['已退款'],
                '已支付': ['已支付', '⏳ 已支付尾款,待发货'],
                '未支付': ['未支付', '⏳ 未支付尾款']
            }
            # 展开所有可能的状态值
            all_matching_statuses = []
            for s in statuses:
                if s in status_mapping:
                    all_matching_statuses.extend(status_mapping[s])
                else:
                    all_matching_statuses.append(s)
            result = [t for t in result if t.get('status') in all_matching_statuses]

        # 金额范围筛选
        if filters.get('minAmount') is not None:
            min_amount = filters['minAmount']
            result = [t for t in result if abs(t.get('gross_amount', 0)) >= min_amount]
        if filters.get('maxAmount') is not None:
            max_amount = filters['maxAmount']
            result = [t for t in result if abs(t.get('gross_amount', 0)) <= max_amount]

        # 关键词搜索
        if filters.get('keyword'):
            keyword = filters['keyword'].lower()
            result = [
                t for t in result
                if keyword in str(t.get('order_number', '')).lower()
                or keyword in str(t.get('figure_name', '')).lower()
                or keyword in str(t.get('remarks', '')).lower()
            ]

        # 手办筛选
        if filters.get('figureIds'):
            figure_ids = filters['figureIds']
            result = [t for t in result if t.get('figure_id') in figure_ids]

        return result
