"""
手办查询服务
提供手办查询相关的业务逻辑，包括列表查询、筛选、构建查询等
"""
from datetime import datetime
from typing import List, Optional
from sqlalchemy.orm import Session, selectinload
from sqlalchemy import desc

from app.models.figure import Figure
from app.models.tag import figure_tag
from app.schemas.figure import FigureListItem
from .figure_price_service import FigurePriceService


class FigureQueryService:
    """手办查询服务类"""

    # 入手形式映射表：英文大写 -> 中文
    PURCHASE_TYPE_MAP = {
        "OTHER": "其他",
        "PREORDER": "预定",
        "INSTOCK": "现货",
        "SECONDHAND": "二手",
        "LOOSE": "散货",
        "DOMESTIC": "国产"
    }

    # 反向映射表：中文 -> 英文大写
    PURCHASE_TYPE_REVERSE_MAP = {v: k for k, v in PURCHASE_TYPE_MAP.items()}

    @classmethod
    def convert_purchase_type_to_chinese(cls, purchase_type: str) -> str:
        """将入手形式的英文转换为大写中文"""
        if not purchase_type:
            return purchase_type
        return cls.PURCHASE_TYPE_MAP.get(purchase_type.upper(), purchase_type)

    @classmethod
    def convert_purchase_type_to_english(cls, purchase_type: str) -> str:
        """将入手形式的中文转换为英文大写"""
        if not purchase_type:
            return purchase_type
        return cls.PURCHASE_TYPE_REVERSE_MAP.get(purchase_type, purchase_type)

    @staticmethod
    def build_figure_list_query(
        db: Session,
        name: Optional[str] = None,
        purchase_type: Optional[str] = None,
        purchase_date_start: Optional[str] = None,
        purchase_date_end: Optional[str] = None,
        tag_id: Optional[int] = None,
        tag_ids: Optional[List[int]] = None
    ):
        """
        构建手办列表查询

        Args:
            db: 数据库会话
            name: 名称模糊搜索
            purchase_type: 入手形式
            purchase_date_start: 入手日期开始
            purchase_date_end: 入手日期结束
            tag_id: 单个标签ID
            tag_ids: 多个标签ID列表

        Returns:
            Query对象
        """
        # 只查询激活状态的手办
        query = db.query(Figure).filter(Figure.is_active == True)

        # 按名称搜索（模糊匹配）
        if name:
            query = query.filter(Figure.name.ilike(f"%{name}%"))

        # 按入手形式过滤
        if purchase_type:
            chinese_purchase_type = FigureQueryService.convert_purchase_type_to_chinese(purchase_type)
            query = query.filter(Figure.purchase_type == chinese_purchase_type)

        # 按入手日期范围过滤
        if purchase_date_start:
            try:
                start_date = datetime.strptime(purchase_date_start, "%Y-%m-%d").date()
                query = query.filter(Figure.purchase_date >= start_date)
            except ValueError:
                pass

        if purchase_date_end:
            try:
                end_date = datetime.strptime(purchase_date_end, "%Y-%m-%d").date()
                query = query.filter(Figure.purchase_date <= end_date)
            except ValueError:
                pass

        # 按标签ID筛选（单个标签）
        if tag_id:
            figure_ids = db.query(figure_tag.c.figure_id).filter(
                figure_tag.c.tag_id == tag_id
            ).all()
            figure_id_list = [id_tuple[0] for id_tuple in figure_ids]
            if not figure_id_list:
                return None  # 表示没有符合条件的手办
            query = query.filter(Figure.id.in_(figure_id_list))

        # 按标签ID列表筛选（多标签联合筛选）
        if tag_ids and len(tag_ids) > 0:
            for tid in tag_ids:
                figure_ids = db.query(figure_tag.c.figure_id).filter(
                    figure_tag.c.tag_id == tid
                ).all()
                figure_id_list = [id_tuple[0] for id_tuple in figure_ids]
                if not figure_id_list:
                    return None  # 表示没有符合条件的手办
                query = query.filter(Figure.id.in_(figure_id_list))

        # 按 id 降序排序（最新的在前面）
        query = query.order_by(desc(Figure.id))

        # 使用 selectinload 预加载标签数据，避免 N+1 查询问题
        query = query.options(selectinload(Figure.tags))

        return query

    @staticmethod
    def get_figures_list(
        db: Session,
        skip: int = 0,
        limit: int = 100,
        name: Optional[str] = None,
        purchase_type: Optional[str] = None,
        purchase_date_start: Optional[str] = None,
        purchase_date_end: Optional[str] = None,
        tag_id: Optional[int] = None,
        tag_ids: Optional[List[int]] = None
    ) -> List[FigureListItem]:
        """
        获取手办列表（使用精简响应模型）

        Returns:
            List[FigureListItem]: 手办列表项
        """
        from app.models.order import Order

        query = FigureQueryService.build_figure_list_query(
            db, name, purchase_type, purchase_date_start,
            purchase_date_end, tag_id, tag_ids
        )

        if query is None:
            return []

        # 预加载订单数据
        query = query.options(selectinload(Figure.orders))

        figures = query.offset(skip).limit(limit).all()

        # 转换为精简响应模型
        result = []
        for figure in figures:
            # 计算订单数量和平均入手价格
            orders = [o for o in figure.orders if o.is_active == 1] if figure.orders else []
            order_count = len(orders)

            # 计算平均入手价格
            average_purchase_price = FigurePriceService.calculate_orders_average_price(orders)

            item = FigureListItem(
                id=figure.id,
                name=figure.name,
                japanese_name=figure.japanese_name,
                price=figure.price,
                currency=figure.currency,
                market_price=figure.market_price,
                market_currency=figure.market_currency,
                manufacturer=figure.manufacturer,
                release_date=figure.release_date,
                purchase_currency=figure.purchase_currency,
                purchase_date=figure.purchase_date,
                purchase_method=figure.purchase_method,
                purchase_type=figure.purchase_type,
                quantity=figure.quantity,
                scale=figure.scale,
                painting=figure.painting,
                original_art=figure.original_art,
                work=figure.work,
                material=figure.material,
                size=figure.size,
                image=figure.images[0] if figure.images and len(figure.images) > 0 else None,
                tags=figure.tags,
                order_count=order_count,
                average_purchase_price=average_purchase_price
            )
            result.append(item)

        return result

    @staticmethod
    def get_figure_by_id(db: Session, figure_id: int) -> Optional[Figure]:
        """
        根据ID获取手办详情

        Args:
            db: 数据库会话
            figure_id: 手办ID

        Returns:
            Figure对象或None
        """
        return db.query(Figure).filter(Figure.id == figure_id).first()

    @staticmethod
    def get_figure_count(
        db: Session,
        name: Optional[str] = None,
        purchase_type: Optional[str] = None,
        purchase_date_start: Optional[str] = None,
        purchase_date_end: Optional[str] = None,
        tag_id: Optional[int] = None,
        tag_ids: Optional[List[int]] = None
    ) -> int:
        """
        获取手办总数

        Args:
            db: 数据库会话
            name: 名称模糊搜索
            purchase_type: 入手形式
            purchase_date_start: 入手日期开始
            purchase_date_end: 入手日期结束
            tag_id: 单个标签ID
            tag_ids: 多个标签ID列表

        Returns:
            int: 手办总数
        """
        query = FigureQueryService.build_figure_list_query(
            db, name, purchase_type, purchase_date_start,
            purchase_date_end, tag_id, tag_ids
        )

        if query is None:
            return 0

        return query.count()

    @staticmethod
    def get_figures_with_orders(
        db: Session,
        figure_ids: List[int]
    ) -> List[Figure]:
        """
        获取手办及其关联订单

        Args:
            db: 数据库会话
            figure_ids: 手办ID列表

        Returns:
            List[Figure]: 手办列表（包含订单关系）
        """
        return db.query(Figure).filter(
            Figure.id.in_(figure_ids),
            Figure.is_active == True
        ).options(
            selectinload(Figure.orders)
        ).all()
