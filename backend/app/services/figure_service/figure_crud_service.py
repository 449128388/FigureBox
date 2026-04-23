"""
手办CRUD服务
提供手办增删改查的业务逻辑，包括创建、更新、删除、批量删除等
"""
from datetime import datetime
from typing import Optional, Dict, Any, List
from sqlalchemy.orm import Session

from app.models.figure import Figure
from app.models.tag import Tag
from app.models.order import Order
from app.models.asset import AssetTransaction, OrderTransaction
from app.services.asset_transaction_service import AssetTransactionService
from .figure_price_service import FigurePriceService
from .figure_query_service import FigureQueryService


class FigureCrudService:
    """手办CRUD服务类"""

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
            figure_data['purchase_type'] = FigureQueryService.convert_purchase_type_to_chinese(
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
            figure_data['purchase_type'] = FigureQueryService.convert_purchase_type_to_chinese(
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
        删除手办（软删除）

        Args:
            db: 数据库会话
            figure_id: 手办ID

        Returns:
            bool: 是否删除成功

        Raises:
            ValueError: 当手办存在未软删除的关联订单时
        """
        # 只删除激活状态的手办
        db_figure = db.query(Figure).filter(
            Figure.id == figure_id,
            Figure.is_active == True
        ).first()
        if not db_figure:
            return False

        # 检查是否有关联的未软删除订单（is_active=1）
        active_orders = db.query(Order).filter(
            Order.figure_id == figure_id,
            Order.is_active == 1
        ).first()

        if active_orders:
            raise ValueError("无法删除有关联尾款的手办，请先删除或软删除所有关联订单")

        # 软删除关联的资产交易记录（库存账）
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

    @staticmethod
    def batch_delete_figures(db: Session, figure_ids: List[int]) -> Dict[str, Any]:
        """
        批量删除手办（软删除）

        Args:
            db: 数据库会话
            figure_ids: 要删除的手办ID列表

        Returns:
            Dict: 删除结果统计
            {
                'success_count': 成功删除数量,
                'failed_count': 失败数量,
                'failed_ids': 失败的ID列表,
                'errors': 错误信息列表
            }
        """
        success_count = 0
        failed_count = 0
        failed_ids = []
        errors = []

        for figure_id in figure_ids:
            try:
                # 检查手办是否存在
                db_figure = db.query(Figure).filter(
                    Figure.id == figure_id,
                    Figure.is_active == True
                ).first()

                if not db_figure:
                    failed_count += 1
                    failed_ids.append(figure_id)
                    errors.append(f"手办ID {figure_id} 不存在或已被删除")
                    continue

                # 检查是否有关联的未软删除订单
                active_orders = db.query(Order).filter(
                    Order.figure_id == figure_id,
                    Order.is_active == 1
                ).first()

                if active_orders:
                    failed_count += 1
                    failed_ids.append(figure_id)
                    errors.append(f"手办ID {figure_id} 有关联未完成订单，无法删除")
                    continue

                # 软删除关联的资产交易记录（库存账）
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
                success_count += 1

            except Exception as e:
                db.rollback()
                failed_count += 1
                failed_ids.append(figure_id)
                errors.append(f"手办ID {figure_id} 删除失败: {str(e)}")

        return {
            'success_count': success_count,
            'failed_count': failed_count,
            'failed_ids': failed_ids,
            'errors': errors
        }
