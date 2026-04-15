"""
手办服务
提供手办相关的业务逻辑，包括CRUD操作、筛选查询等
"""
from datetime import datetime
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session, selectinload
from sqlalchemy import desc

from app.models.figure import Figure
from app.models.tag import Tag, figure_tag
from app.schemas.figure import FigureCreate, FigureUpdate, FigureListItem
from app.services.asset_transaction_service import AssetTransactionService
from app.services.order_transaction_service import OrderTransactionService


class FigureService:
    """手办服务类"""
    
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
            chinese_purchase_type = FigureService.convert_purchase_type_to_chinese(purchase_type)
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
        query = FigureService.build_figure_list_query(
            db, name, purchase_type, purchase_date_start, 
            purchase_date_end, tag_id, tag_ids
        )
        
        if query is None:
            return []
        
        figures = query.offset(skip).limit(limit).all()
        
        # 转换为精简响应模型
        result = []
        for figure in figures:
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
                purchase_price=figure.purchase_price,
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
                description=figure.description,
                image=figure.images[0] if figure.images and len(figure.images) > 0 else None,
                tags=figure.tags
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
    def create_figure(db: Session, figure_data: Dict[str, Any], user_id: int = None) -> Figure:
        """
        创建手办
        
        Args:
            db: 数据库会话
            figure_data: 手办数据字典
            user_id: 用户ID，用于创建资产交易记录
            
        Returns:
            创建的Figure对象
        """
        # 提取标签ID列表
        tag_ids = figure_data.pop('tag_ids', [])
        
        # 处理市场价：当市场价为0或未设置时，市场价默认等于定价
        if (figure_data.get('market_price') == 0 or figure_data.get('market_price') is None) \
           and figure_data.get('price') is not None:
            figure_data['market_price'] = figure_data['price']
            figure_data['market_currency'] = figure_data['currency']
        
        # 将入手形式的英文转换为中文
        if figure_data.get('purchase_type'):
            figure_data['purchase_type'] = FigureService.convert_purchase_type_to_chinese(
                figure_data['purchase_type']
            )
        
        # 创建手办对象
        db_figure = Figure(**figure_data)
        db.add(db_figure)
        db.commit()
        db.refresh(db_figure)
        
        # 关联标签
        if tag_ids:
            tags = db.query(Tag).filter(Tag.id.in_(tag_ids)).all()
            db_figure.tags = tags
            db.commit()
            db.refresh(db_figure)
        
        # 【新增】同时创建资产交易记录（库存账）和资金流水记录（资金账）
        # 【修复】无论入手价格是否为0，都创建交易记录，保证数据完整性
        if user_id:
            try:
                # 1. 创建资产交易记录（库存账）- 记录数量变动
                AssetTransactionService.create_transaction_from_figure(
                    db=db,
                    user_id=user_id,
                    figure_id=db_figure.id,
                    price=figure_data['purchase_price'],
                    quantity=figure_data.get('quantity', 1)
                )

                # 2. 创建资金流水记录（资金账）- 记录资金变动
                OrderTransactionService.create_transaction_from_figure(
                    db=db,
                    user_id=user_id,
                    figure=db_figure,
                    transaction_type="full",
                    notes=f"自动创建：从手办管理数据中创建 - {db_figure.name}"
                )

                db.commit()
            except Exception as e:
                # 如果创建交易记录失败，不影响手办创建
                db.rollback()
                # 可以在这里记录日志
                print(f"创建交易记录失败: {e}")

        return db_figure
    
    @staticmethod
    def update_figure(
        db: Session, 
        figure_id: int, 
        figure_data: Dict[str, Any]
    ) -> Optional[Figure]:
        """
        更新手办
        
        Args:
            db: 数据库会话
            figure_id: 手办ID
            figure_data: 更新的数据字典
            
        Returns:
            更新后的Figure对象或None（不存在时）
        """
        # 只更新激活状态的手办
        db_figure = db.query(Figure).filter(
            Figure.id == figure_id,
            Figure.is_active == True
        ).first()
        if not db_figure:
            return None
        
        # 提取标签ID列表
        tag_ids = figure_data.pop('tag_ids', None)
        
        # 将入手形式的英文转换为中文
        if 'purchase_type' in figure_data and figure_data['purchase_type']:
            figure_data['purchase_type'] = FigureService.convert_purchase_type_to_chinese(
                figure_data['purchase_type']
            )
        
        # 更新其他字段
        for key, value in figure_data.items():
            setattr(db_figure, key, value)
        
        # 更新标签关联
        if tag_ids is not None:
            tags = db.query(Tag).filter(Tag.id.in_(tag_ids)).all()
            db_figure.tags = tags
        
        db.commit()
        db.refresh(db_figure)
        return db_figure
    
    @staticmethod
    def delete_figure(db: Session, figure_id: int) -> bool:
        """
        删除手办
        
        Args:
            db: 数据库会话
            figure_id: 手办ID
            
        Returns:
            bool: 是否删除成功
        """
        # 只删除激活状态的手办
        db_figure = db.query(Figure).filter(
            Figure.id == figure_id,
            Figure.is_active == True
        ).first()
        if not db_figure:
            return False
        
        # 检查是否有关联的订单
        from app.models.order import Order
        associated_orders = db.query(Order).filter(
            Order.figure_id == figure_id
        ).first()
        
        if associated_orders:
            raise ValueError("无法删除有关联尾款的手办")
        
        # 【修改】软删除关联的资产交易记录（库存账）
        from app.models.asset import AssetTransaction, OrderTransaction
        from datetime import datetime
        
        # 软删除资产交易记录
        db.query(AssetTransaction).filter(
            AssetTransaction.figure_id == figure_id
        ).update({
            'is_active': False,
            'deleted_at': datetime.now()
        })

        # 软删除资金流水记录（资金账）
        db.query(OrderTransaction).filter(
            OrderTransaction.figure_id == figure_id
        ).update({
            'is_active': False,
            'deleted_at': datetime.now()
        })

        # 软删除手办
        db_figure.is_active = False
        db_figure.deleted_at = datetime.now()
        db.commit()
        return True
