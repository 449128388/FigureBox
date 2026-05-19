"""
板块分析服务模块

功能说明：
- 提供板块涨幅排行分析
- 按IP系列(work)分组计算板块表现
- 支持获取热门板块及其代表手办

板块定义：
- 按作品出处(work)进行分组
- 计算板块内手办的平均涨跌幅
- 展示板块代表手办

创建时间: 2026-05-18
作者: FigureBox Team
"""

from typing import Dict, Any, List
from sqlalchemy.orm import Session

from app.models.figure import Figure


class SectorService:
    """板块分析服务类"""

    @classmethod
    def get_sector_performance(cls, db: Session) -> List[Dict[str, Any]]:
        """
        获取板块涨幅排行

        按IP系列(work)分组，计算每个板块的平均涨跌幅

        Args:
            db: 数据库会话

        Returns:
            List[Dict]: 板块列表，包含名称、涨幅、代表手办
        """
        all_figures = db.query(Figure).filter(Figure.is_active == 1).all()

        if not all_figures:
            return []

        # 按作品分组
        work_groups = {}
        for fig in all_figures:
            work = fig.work or "其他"
            if work not in work_groups:
                work_groups[work] = []
            work_groups[work].append(fig)

        sectors = []
        for work, work_figures in work_groups.items():
            if len(work_figures) > 0:
                # 计算板块平均涨跌幅
                valid_figures = [f for f in work_figures if f.price and f.price > 0]
                if valid_figures:
                    avg_change = sum(
                        ((f.market_price or f.price or 0) - f.price) / f.price * 100
                        for f in valid_figures
                    ) / len(valid_figures)

                    # 取前3个手办作为代表
                    sector_figures = [f.name for f in work_figures[:3]]

                    sectors.append({
                        "name": work,
                        "change": round(avg_change, 1),
                        "stocks": "、".join(sector_figures) if sector_figures else "暂无"
                    })

        # 按涨幅排序，取前5个板块
        sectors.sort(key=lambda x: abs(x["change"]), reverse=True)
        return sectors[:5]
