"""
订单查询服务
提供订单查询相关的业务逻辑，包括列表查询、统计等
"""
from datetime import date
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.models.order import Order
from app.models.figure import Figure
from app.models.user import User
from app.schemas.order import OrderListItem
from app.services.figure_service.figure_price_service import FigurePriceService


class OrderQueryService:
    """订单查询服务类"""

    @staticmethod
    def get_unpaid_balance(db: Session, current_user: User) -> dict:
        """
        获取未支付状态的尾款总额（统一转换为人民币）

        Args:
            db: 数据库会话
            current_user: 当前用户

        Returns:
            dict: {"total_unpaid_balance": float}
        """
        # 获取所有未支付订单
        if current_user.is_admin:
            unpaid_orders = db.query(Order).filter(
                Order.status == "未支付",
                Order.is_active == 1
            ).all()
        else:
            unpaid_orders = db.query(Order).filter(
                Order.status == "未支付",
                Order.user_id == current_user.id,
                Order.is_active == 1
            ).all()

        # 将所有尾款按币种转换为人民币后求和
        total_balance_cny = 0.0
        for order in unpaid_orders:
            balance_cny = FigurePriceService.convert_to_cny(
                order.balance or 0,
                order.balance_currency or 'CNY'
            )
            total_balance_cny += balance_cny

        return {"total_unpaid_balance": total_balance_cny}

    @staticmethod
    def _build_base_query(
        db: Session,
        current_user: User,
        figure_name: Optional[str] = None,
        due_date_start: Optional[date] = None,
        due_date_end: Optional[date] = None,
        figure_id: Optional[int] = None
    ):
        """
        构建订单基础查询（2026-08-06 重构：get_orders 与 get_status_counts 共享过滤条件）

        Returns:
            SQLAlchemy Query 对象
        """
        query = db.query(Order).join(Figure).filter(Order.is_active == 1)

        # 非管理员只能查看自己的订单
        if not current_user.is_admin:
            query = query.filter(Order.user_id == current_user.id)

        # 按手办ID精确过滤（手办详情页使用）
        if figure_id is not None:
            query = query.filter(Order.figure_id == figure_id)

        # 按手办名称模糊搜索
        if figure_name:
            query = query.filter(Figure.name.ilike(f"%{figure_name}%"))

        # 按出荷日期范围筛选
        if due_date_start:
            query = query.filter(Order.due_date >= due_date_start)
        if due_date_end:
            query = query.filter(Order.due_date <= due_date_end)

        return query

    @staticmethod
    def _to_list_item(order) -> OrderListItem:
        """Order ORM → OrderListItem 转换（2026-08-06 抽离：get_orders 与 get_orders_page 共享）"""
        return OrderListItem(
            id=order.id,
            user_id=order.user_id,
            figure_id=order.figure_id,
            figure_name=order.figure.name,
            figure_image=order.figure.images[0] if order.figure.images else None,
            deposit=order.deposit,
            deposit_currency=order.deposit_currency,
            balance=order.balance,
            balance_currency=order.balance_currency,
            due_date=order.due_date,
            order_type=order.order_type,
            status=order.status,
            shop_name=order.shop_name,
            shop_contact=order.shop_contact,
            tracking_number=order.tracking_number,
            logistics_company=order.logistics_company,
            order_number=order.order_number,
            payment_method=order.payment_method,
            payment_time=order.payment_time,
            balance_payment_method=order.balance_payment_method,
            balance_payment_time=order.balance_payment_time,
            remarks=order.remarks,
            created_at=order.created_at,
            updated_at=order.updated_at
        )

    @staticmethod
    def get_orders(
        db: Session,
        current_user: User,
        figure_name: Optional[str] = None,
        due_date_start: Optional[date] = None,
        due_date_end: Optional[date] = None,
        figure_id: Optional[int] = None
    ) -> List[OrderListItem]:
        """
        获取订单列表（无分页，兼容手办详情页等需要全量返回的场景）

        Args:
            db: 数据库会话
            current_user: 当前用户
            figure_name: 手办名称模糊搜索
            due_date_start: 出荷日期开始
            due_date_end: 出荷日期结束
            figure_id: 手办ID精确过滤（用于手办详情页只取关联订单，避免拉全量数据）

        Returns:
            List[OrderListItem]: 订单列表
        """
        query = OrderQueryService._build_base_query(
            db, current_user, figure_name, due_date_start, due_date_end, figure_id
        )
        orders = query.all()
        return [OrderQueryService._to_list_item(order) for order in orders]

    @staticmethod
    def get_orders_page(
        db: Session,
        current_user: User,
        figure_name: Optional[str] = None,
        due_date_start: Optional[date] = None,
        due_date_end: Optional[date] = None,
        figure_id: Optional[int] = None,
        status: Optional[str] = None,
        skip: int = 0,
        limit: int = 10
    ) -> Dict[str, Any]:
        """
        获取订单分页列表 + 各状态计数（2026-08-06 新增：尾款管理翻页走服务端）

        Args:
            db: 数据库会话
            current_user: 当前用户
            figure_name: 手办名称模糊搜索
            due_date_start: 出荷日期开始
            due_date_end: 出荷日期结束
            figure_id: 手办ID精确过滤
            status: 订单状态过滤（'未支付' / '已支付' / '已取消' / '已完成' / None 表示不过滤）
            skip: 跳过的记录数
            limit: 返回的最大记录数

        Returns:
            Dict[str, Any]: {
                'items': List[OrderListItem],   # 当前页订单
                'total': int,                   # 符合当前过滤条件的总数
                'status_counts': Dict[str, int] # 各状态计数（应用 figure_name/due_date 过滤但不应用 status 过滤）
            }
        """
        # 构建基础查询（应用 figure_name / due_date / figure_id 过滤，不应用 status 过滤）
        base_query = OrderQueryService._build_base_query(
            db, current_user, figure_name, due_date_start, due_date_end, figure_id
        )

        # 计算各状态计数（在应用 status 过滤之前）
        status_counts_rows = base_query.with_entities(
            Order.status, func.count(Order.id)
        ).group_by(Order.status).all()
        status_counts = {row[0]: row[1] for row in status_counts_rows}
        # 补齐所有状态（前端 Tab 完整显示）
        for s in ('未支付', '已支付', '已取消', '已完成'):
            status_counts.setdefault(s, 0)
        status_counts['all'] = sum(v for k, v in status_counts.items() if k != 'all')

        # 应用 status 过滤后分页
        paged_query = base_query
        if status:
            paged_query = paged_query.filter(Order.status == status)

        # 取总数（在分页前）
        total = paged_query.count()

        # 应用分页
        # 2026-08-06 修复：原 .order_by(Order.due_date.asc().nullslast(), Order.id.desc()) 生成
        # "ORDER BY ... ASC NULLS LAST" 语法，MySQL 8.0 不支持（NULLS LAST 是 PostgreSQL 扩展，MySQL 始终按
        # ASC 默认 NULL 在前 / DESC 默认 NULL 在后处理），导致 /orders/?status=未支付 报 500
        # 改用 MySQL 兼容写法：先按 IS NULL 排（NULL=1, 非 NULL=0, 升序），再按 due_date 升序
        # 等价于 "NULL 排最后 + 非 NULL 按 due_date 升序" 的语义
        orders = paged_query.order_by(
            Order.due_date.is_(None),
            Order.due_date.asc(),
            Order.id.desc()
        ).offset(skip).limit(limit).all()

        return {
            'items': [OrderQueryService._to_list_item(order) for order in orders],
            'total': total,
            'status_counts': status_counts
        }

    @staticmethod
    def get_order_by_id(db: Session, order_id: int, current_user: User) -> Optional[Order]:
        """
        获取单个订单详情

        Args:
            db: 数据库会话
            order_id: 订单ID
            current_user: 当前用户

        Returns:
            Order对象或None

        Raises:
            HTTPException: 订单不存在或无权限时抛出
        """
        from fastapi import HTTPException, status

        order = db.query(Order).filter(Order.id == order_id, Order.is_active == 1).first()
        if not order:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="未找到该订单"
            )
        if not current_user.is_admin and order.user_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="权限不足"
            )
        return order

    @staticmethod
    def get_order_count_by_figure(db: Session, figure_id: int) -> int:
        """
        获取指定手办的订单数量（只计算未软删除的订单）

        Args:
            db: 数据库会话
            figure_id: 手办ID

        Returns:
            int: 订单数量
        """
        return db.query(func.count(Order.id)).filter(
            Order.figure_id == figure_id,
            Order.is_active == 1
        ).scalar()
