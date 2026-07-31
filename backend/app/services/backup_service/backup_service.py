"""
backup_service.py - 系统备份/恢复业务服务层（企业级服务层架构）

功能说明：
- 备份：导出全量手办数据 + 关联订单 + 关联售出单 + 关联库存账 + 关联资金账 为 JSON
- 恢复：从 JSON 数据导入手办/订单/售出单/库存账/资金账
- 本服务为个人中心-系统备份模块的统一入口，封装原 FigureExportService / FigureImportService
  的底层能力，向 API 层提供两个职责单一的接口

使用示例：
    from app.services.backup_service import BackupService
    BackupService.export_backup(db)
    BackupService.restore_backup(db, json_data, user_id)
"""
import json
from typing import Dict, Any
from sqlalchemy.orm import Session

from app.services.figure_service import FigureExportService, FigureImportService


class BackupService:
    """系统备份/恢复业务服务（统一入口 Facade）"""

    # ========== 备份 ==========

    @staticmethod
    def export_backup(db: Session) -> Dict[str, Any]:
        """
        导出全量备份数据

        Returns:
            dict: 含 success / filename / json_str / figures / count 的字典
        """
        json_str = FigureExportService.export_all_figures(db)
        filename = FigureExportService.get_export_filename()
        # 同步返回反序列化后的列表，方便 API 层选择响应格式
        figures = json.loads(json_str) if json_str else []
        return {
            "success": True,
            "filename": filename,
            "json_str": json_str,
            "figures": figures,
            "count": len(figures)
        }

    # ========== 恢复 ==========

    @staticmethod
    def restore_backup(db: Session, json_data, user_id: int) -> Dict[str, Any]:
        """
        从 JSON 数据恢复系统数据

        Args:
            db: 数据库会话
            json_data: 要恢复的 JSON 数据（list / dict / str 三种入参均兼容）
            user_id: 当前用户 ID
        """
        # 兼容三种入参：FastAPI 自动反序列化的 list / dict / 原始 JSON 字符串
        if isinstance(json_data, str):
            parsed = json.loads(json_data) if json_data else []
        elif isinstance(json_data, dict):
            parsed = json_data
        else:
            parsed = json_data or []

        # 取 figures 字段（兼容 {figures: [...]} 包装 / 裸数组 两种格式）
        if isinstance(parsed, dict):
            figures_data = parsed.get('figures', [])
        else:
            figures_data = parsed

        if not figures_data:
            return {
                "success": False,
                "imported_figures": 0,
                "updated_figures": 0,
                "imported_orders": 0,
                "errors": ["没有提供要恢复的数据"],
                "message": "恢复失败：备份文件为空"
            }

        result = FigureImportService.import_figures_from_json(
            db=db,
            json_data=figures_data,
            user_id=user_id
        )

        return {
            "success": result['success'],
            "imported_figures": result['imported_figures'],
            "updated_figures": result['updated_figures'],
            "imported_orders": result['imported_orders'],
            "errors": result.get('errors', []),
            "message": f"成功恢复 {result['imported_figures']} 个新手办，更新 {result['updated_figures']} 个手办，导入 {result['imported_orders']} 个订单"
        }
