"""
手办服务模块

提供手办相关的所有业务逻辑服务，采用 Facade 模式组织：
- FigureService: 主入口（Facade），保持向后兼容
- FigurePriceService: 价格计算、汇率转换
- FigureQueryService: 查询、筛选、列表
- FigureCrudService: 增删改、批量操作
- FigureImportService: 手办导入
- FigureExportService: 手办导出
- TagService: 标签管理

使用示例：
    from app.services.figure_service import FigureService
    from app.services.figure_service import FigurePriceService, FigureQueryService
"""

from .figure_service import FigureService
from .figure_price_service import FigurePriceService
from .figure_query_service import FigureQueryService
from .figure_crud_service import FigureCrudService
from .figure_import_service import FigureImportService
from .figure_export_service import FigureExportService
from .tag_service import TagService

__all__ = [
    "FigureService",
    "FigurePriceService",
    "FigureQueryService",
    "FigureCrudService",
    "FigureImportService",
    "FigureExportService",
    "TagService",
]
