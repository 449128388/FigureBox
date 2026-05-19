"""
自选股服务模块

功能说明：
- 提供市场热门手办列表
- 计算手办涨跌幅、目标价等数据
- 支持按涨跌幅排序筛选

自选股定义：
- 基于全市场手办数据
- 按涨跌幅排序取前N个
- 包含当前价、涨跌幅、目标价等信息

创建时间: 2026-05-18
作者: FigureBox Team
"""

from typing import Dict, Any, List
from sqlalchemy.orm import Session

from app.models.figure import Figure


class WatchlistService:
    """自选股服务类"""

    @classmethod
    def get_watchlist(cls, db: Session, limit: int = 3) -> List[Dict[str, Any]]:
        """
        获取自选股列表（市场热门手办）

        Args:
            db: 数据库会话
            limit: 返回数量限制，默认3个

        Returns:
            List[Dict]: 热门手办列表
        """
        all_figures = db.query(Figure).filter(Figure.is_active == 1).all()

        watchlist = []
        for fig in all_figures:
            if fig.price and fig.price > 0 and fig.market_price and fig.market_price > 0:
                change_percentage = ((fig.market_price - fig.price) / fig.price) * 100

                watchlist.append({
                    "name": fig.name,
                    "current_price": fig.market_price,
                    "change": round(change_percentage, 1),
                    "target_price": int(fig.price * 1.5),
                    "target_distance": f"还需上涨{int(50 - change_percentage)}%" if change_percentage < 50 else "已达到目标"
                })

        # 按涨跌幅排序
        watchlist.sort(key=lambda x: abs(x["change"]), reverse=True)
        return watchlist[:limit]
