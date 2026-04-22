"""
服务层模块
提供业务逻辑服务，与API层分离

手办服务架构说明：
- FigureService: 手办服务主入口（Facade模式），保持向后兼容
- FigurePriceService: 手办价格服务（汇率转换、平均价格计算）
- FigureQueryService: 手办查询服务（列表查询、筛选）
- FigureCrudService: 手办CRUD服务（增删改、批量操作）
- FigureImportService: 手办导入服务
- FigureExportService: 手办导出服务
- TagService: 标签服务

订单服务架构说明：
- OrderService: 订单服务主入口（Facade模式），保持向后兼容
- OrderQueryService: 订单查询服务（列表查询、统计）
- OrderCrudService: 订单CRUD服务（增删改）

所有手办相关服务已迁移到 figure_service 包中
所有订单相关服务已迁移到 order_service 包中
"""

from .index_service import IndexService
from .asset_calculation_service import AssetCalculationService
from .holding_analysis_service import HoldingAnalysisService
from .price_update_service import PriceUpdateService

# 从 figure_service 包导入手办相关服务（保持向后兼容）
from .figure_service import (
    FigureService,
    FigurePriceService,
    FigureQueryService,
    FigureCrudService,
    FigureImportService,
    FigureExportService,
    TagService,
)

# 从 order_service 包导入订单相关服务（保持向后兼容）
from .order_service import (
    OrderService,
    OrderQueryService,
    OrderCrudService,
)

__all__ = [
    "IndexService",
    "AssetCalculationService",
    "HoldingAnalysisService",
    "PriceUpdateService",
    # 手办服务
    "FigureService",
    "FigurePriceService",
    "FigureQueryService",
    "FigureCrudService",
    "FigureImportService",
    "FigureExportService",
    "TagService",
    # 订单服务
    "OrderService",
    "OrderQueryService",
    "OrderCrudService",
]
