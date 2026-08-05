"""
持仓筛选服务
提供持仓列表的筛选查询功能，支持手办名字模糊搜索和风险状态筛选
采用企业级服务层架构
"""
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import or_

from app.models.figure import Figure
from app.models.order import Order
from app.models.asset_transaction import AssetTransaction


class HoldingFilterService:
    """持仓筛选服务类"""

    @staticmethod
    def filter_holdings(
        db: Session,
        user_id: int,
        keyword: Optional[str] = None,
        status: Optional[str] = None,
        holdings: Optional[List[Dict[str, Any]]] = None
    ) -> List[Dict[str, Any]]:
        """
        筛选持仓列表

        支持按手办名字模糊搜索和风险状态筛选

        Args:
            db: 数据库会话
            user_id: 用户ID
            keyword: 手办名字搜索关键词（模糊匹配）
            status: 风险状态筛选（如 '🚀 暴涨'）
            holdings: 原始持仓列表，如果为None则从数据库查询

        Returns:
            List[Dict[str, Any]]: 筛选后的持仓列表
        """
        # 如果没有传入持仓列表，需要从数据库查询
        # 这里假设 holdings 已经由 HoldingPositionService 构建好
        if holdings is None:
            return []

        filtered_holdings = holdings

        # 1. 按手办名字模糊搜索
        if keyword and keyword.strip():
            keyword_lower = keyword.strip().lower()
            filtered_holdings = [
                h for h in filtered_holdings
                if h.get("figure_name", "").lower().find(keyword_lower) != -1
            ]

        # 2. 按风险状态筛选
        if status and status != "all":
            filtered_holdings = [
                h for h in filtered_holdings
                if h.get("status") == status
            ]

        return filtered_holdings

    @staticmethod
    def paginate_holdings(
        holdings: List[Dict[str, Any]],
        page: int = 1,
        page_size: int = 9
    ) -> Dict[str, Any]:
        """
        对持仓列表进行分页

        Args:
            holdings: 持仓列表
            page: 当前页码（从1开始）
            page_size: 每页条数

        Returns:
            Dict: 包含分页后的数据和分页信息
        """
        total = len(holdings)
        total_pages = max(1, (total + page_size - 1) // page_size)
        page = max(1, min(page, total_pages))

        start = (page - 1) * page_size
        end = start + page_size
        items = holdings[start:end]

        return {
            "items": items,
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": total_pages
        }

    @staticmethod
    def get_filter_options() -> Dict[str, Any]:
        """
        获取筛选选项配置

        Returns:
            Dict[str, Any]: 筛选选项配置
        """
        return {
            "status_options": [
                {"label": "全部", "value": "all"},
                {"label": "🚀 暴涨", "value": "🚀 暴涨"},
                {"label": "📈 上涨", "value": "📈 上涨"},
                {"label": "➖ 横盘", "value": "➖ 横盘"},
                {"label": "📉 告警", "value": "📉 告警"},
                {"label": "🟢 破位", "value": "🟢 破位"},
                {"label": "💀 退市", "value": "💀 退市"}
            ]
        }
