"""
手办服务
提供手办相关的业务逻辑，是各子服务的统一入口，保持向后兼容

企业级架构说明：
本文件作为 Facade 模式实现，将业务逻辑拆分到以下子服务：
- FigurePriceService: 价格计算、汇率转换（figure_price_service.py）
- FigureQueryService: 查询、筛选、列表（figure_query_service.py）
- FigureCrudService: 增删改、批量操作（figure_crud_service.py）

新代码应优先直接使用子服务，本文件仅用于保持向后兼容。
"""
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session

from app.models.figure import Figure
from app.schemas.figure import FigureListItem

# 导入子服务（使用相对导入）
from .figure_price_service import FigurePriceService
from .figure_query_service import FigureQueryService
from .figure_crud_service import FigureCrudService


class FigureService:
    """
    手办服务类（Facade 模式）

    作为各子服务的统一入口，所有方法委托给相应的子服务实现
    保持向后兼容，现有调用代码无需修改
    """

    # ==========================================================================
    # 入手形式转换（委托给 FigureQueryService）
    # ==========================================================================
    PURCHASE_TYPE_MAP = FigureQueryService.PURCHASE_TYPE_MAP
    PURCHASE_TYPE_REVERSE_MAP = FigureQueryService.PURCHASE_TYPE_REVERSE_MAP

    @staticmethod
    def convert_purchase_type_to_chinese(purchase_type: str) -> str:
        """将入手形式的英文转换为大写中文"""
        return FigureQueryService.convert_purchase_type_to_chinese(purchase_type)

    @staticmethod
    def convert_purchase_type_to_english(purchase_type: str) -> str:
        """将入手形式的中文转换为英文大写"""
        return FigureQueryService.convert_purchase_type_to_english(purchase_type)

    # ==========================================================================
    # 汇率转换（委托给 FigurePriceService）
    # ==========================================================================
    @staticmethod
    def _convert_to_cny(amount: float, currency: str) -> float:
        """将金额转换为人民币"""
        return FigurePriceService.convert_to_cny(amount, currency)

    # ==========================================================================
    # 价格计算（委托给 FigurePriceService）
    # ==========================================================================
    @staticmethod
    def update_figure_average_purchase_price(db: Session, figure_id: int) -> float:
        """更新手办的平均入手价格"""
        return FigurePriceService.update_figure_average_purchase_price(db, figure_id)

    @staticmethod
    def calculate_figure_average_purchase_price(figure: Figure, orders: List = None) -> float:
        """计算手办的平均入手价格（不保存到数据库）"""
        return FigurePriceService.calculate_figure_average_purchase_price(figure, orders)

    # ==========================================================================
    # 查询相关（委托给 FigureQueryService）
    # ==========================================================================
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
        """构建手办列表查询"""
        return FigureQueryService.build_figure_list_query(
            db, name, purchase_type, purchase_date_start,
            purchase_date_end, tag_id, tag_ids
        )

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
        """获取手办列表"""
        return FigureQueryService.get_figures_list(
            db, skip, limit, name, purchase_type,
            purchase_date_start, purchase_date_end, tag_id, tag_ids
        )

    @staticmethod
    def get_figure_by_id(db: Session, figure_id: int) -> Optional[Figure]:
        """根据ID获取手办详情"""
        return FigureQueryService.get_figure_by_id(db, figure_id)

    # ==========================================================================
    # CRUD 操作（委托给 FigureCrudService）
    # ==========================================================================
    @staticmethod
    def create_figure(db: Session, figure_data: Dict[str, Any], user_id: int = None) -> Figure:
        """创建手办"""
        return FigureCrudService.create_figure(db, figure_data, user_id)

    @staticmethod
    def update_figure(
        db: Session,
        figure_id: int,
        figure_data: Dict[str, Any]
    ) -> Optional[Figure]:
        """更新手办"""
        return FigureCrudService.update_figure(db, figure_id, figure_data)

    @staticmethod
    def delete_figure(db: Session, figure_id: int) -> bool:
        """删除手办（软删除）"""
        return FigureCrudService.delete_figure(db, figure_id)

    @staticmethod
    def batch_delete_figures(db: Session, figure_ids: List[int]) -> Dict[str, Any]:
        """批量删除手办（软删除）"""
        return FigureCrudService.batch_delete_figures(db, figure_ids)
