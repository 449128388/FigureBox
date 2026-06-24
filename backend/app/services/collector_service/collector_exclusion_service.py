"""
collector_exclusion_service.py - 收藏家模式展示分类排除服务

功能说明：
- 提供「软出柜」业务逻辑：将手办从某个展示分类中排除（不删除藏品）
- 支持排除记录的增删查
- 所有自动分类查询通过 LEFT JOIN 排除表过滤已移出的记录

使用方式：
    from app.services.collector_service.collector_exclusion_service import CollectorExclusionService

    # 排除某手办
    CollectorExclusionService.exclude_figure(db, user_id, figure_id, cabinet_type)

    # 取消排除
    CollectorExclusionService.remove_exclusion(db, user_id, figure_id, cabinet_type)

    # 获取被排除的 figure_id 集合
    excluded = CollectorExclusionService.get_excluded_figure_ids(db, user_id, cabinet_type)
"""

from sqlalchemy.orm import Session
from typing import Set, Optional

from app.models.cabinet_exclusion import CabinetFigureExclusion
from app.models.figure import Figure
from app.services.collector_service.collector_activity_service import CollectorActivityService


class CollectorExclusionService:
    """收藏家模式展示分类排除服务类"""

    # 支持排除的分类列表
    SUPPORTED_CABINET_TYPES = {'star', 'new', 'fix', 'air', 'dup', 'wait', 'maker'}

    @staticmethod
    def exclude_figure(
        db: Session,
        user_id: int,
        figure_id: int,
        cabinet_type: str,
        source_cabinet: Optional[str] = None,
        exclude_reason: Optional[str] = None
    ) -> CabinetFigureExclusion:
        """
        将手办从指定展示分类中排除（软出柜）

        Args:
            db: 数据库会话
            user_id: 用户ID
            figure_id: 手办ID
            cabinet_type: 分类标识
            source_cabinet: 触发移出的源分类（可选）
            exclude_reason: 移出原因（可选）

        Returns:
            CabinetFigureExclusion: 创建的排除记录
        """
        if cabinet_type not in CollectorExclusionService.SUPPORTED_CABINET_TYPES:
            raise ValueError(f"不支持的分类标识: {cabinet_type}，支持: {CollectorExclusionService.SUPPORTED_CABINET_TYPES}")

        # 检查是否已存在排除记录（幂等）
        existing = db.query(CabinetFigureExclusion).filter(
            CabinetFigureExclusion.user_id == user_id,
            CabinetFigureExclusion.figure_id == figure_id,
            CabinetFigureExclusion.cabinet_type == cabinet_type
        ).first()

        if existing:
            return existing

        exclusion = CabinetFigureExclusion(
            user_id=user_id,
            figure_id=figure_id,
            cabinet_type=cabinet_type,
            source_cabinet=source_cabinet,
            exclude_reason=exclude_reason
        )
        db.add(exclusion)
        db.commit()
        db.refresh(exclusion)

        # 记录动态流事件
        try:
            cabinet_names = {
                'star': '海景房专区', 'new': '最近入柜', 'fix': '修复工坊',
                'air': '预定中', 'dup': '复数专区', 'wait': '待出荷', 'maker': '本命厂商'
            }
            figure = db.query(Figure).filter(Figure.id == figure_id).first()
            figure_name = figure.name if figure else "未知"
            cabinet_name = cabinet_names.get(cabinet_type, cabinet_type)
            CollectorActivityService.record_out_event(
                db=db,
                user_id=user_id,
                figure_id=figure_id,
                figure_name=figure_name,
                from_cabinet=cabinet_name,
                reason=exclude_reason,
                target_id=exclusion.id
            )
        except Exception:
            db.rollback()

        return exclusion

    @staticmethod
    def remove_exclusion(
        db: Session,
        user_id: int,
        figure_id: int,
        cabinet_type: str
    ) -> bool:
        """
        取消手办在指定分类中的排除（恢复展示）

        Args:
            db: 数据库会话
            user_id: 用户ID
            figure_id: 手办ID
            cabinet_type: 分类标识

        Returns:
            bool: 是否成功取消
        """
        deleted = db.query(CabinetFigureExclusion).filter(
            CabinetFigureExclusion.user_id == user_id,
            CabinetFigureExclusion.figure_id == figure_id,
            CabinetFigureExclusion.cabinet_type == cabinet_type
        ).delete()
        db.commit()
        return deleted > 0

    @staticmethod
    def get_excluded_figure_ids(
        db: Session,
        user_id: int,
        cabinet_type: str
    ) -> Set[int]:
        """
        获取指定分类下用户已排除的手办 ID 集合

        Args:
            db: 数据库会话
            user_id: 用户ID
            cabinet_type: 分类标识

        Returns:
            Set[int]: 被排除的手办ID集合
        """
        records = db.query(CabinetFigureExclusion.figure_id).filter(
            CabinetFigureExclusion.user_id == user_id,
            CabinetFigureExclusion.cabinet_type == cabinet_type
        ).all()
        return {r.figure_id for r in records}

    @staticmethod
    def get_all_excluded_figure_ids(
        db: Session,
        user_id: int
    ) -> Set[int]:
        """
        获取用户在所有分类下已排除的手办 ID 集合

        Args:
            db: 数据库会话
            user_id: 用户ID

        Returns:
            Set[int]: 被排除的手办ID集合
        """
        records = db.query(CabinetFigureExclusion.figure_id).filter(
            CabinetFigureExclusion.user_id == user_id
        ).all()
        return {r.figure_id for r in records}

    @staticmethod
    def bulk_get_excluded_ids_by_cabinet(
        db: Session,
        user_id: int
    ) -> dict:
        """
        批量获取用户在所有分类下的排除 ID 映射

        Returns:
            dict: { cabinet_type: set([figure_id, ...]) }
        """
        records = db.query(
            CabinetFigureExclusion.figure_id,
            CabinetFigureExclusion.cabinet_type
        ).filter(
            CabinetFigureExclusion.user_id == user_id
        ).all()

        result = {}
        for r in records:
            if r.cabinet_type not in result:
                result[r.cabinet_type] = set()
            result[r.cabinet_type].add(r.figure_id)
        return result
