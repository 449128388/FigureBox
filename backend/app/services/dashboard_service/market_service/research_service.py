"""
智能投研服务模块

功能说明：
- 提供智能投研报告生成
- 分析市场热门手办表现
- 生成买入建议、目标价、止损价等

投研逻辑：
- 找出涨幅最大的手办作为推荐标的
- 计算目标价（基于入手价的150%）
- 设置止损价（基于当前市场价的80%）
- 生成推荐理由

创建时间: 2026-05-18
作者: FigureBox Team
"""

from datetime import date
from typing import Dict, Any
from sqlalchemy.orm import Session

from app.models.figure import Figure


class ResearchService:
    """智能投研服务类"""

    @classmethod
    def get_research_report(cls, db: Session) -> Dict[str, Any]:
        """
        获取智能投研报告

        Args:
            db: 数据库会话

        Returns:
            Dict: 投研报告数据
        """
        all_figures = db.query(Figure).filter(Figure.is_active == 1).all()

        # 找出涨幅最大的手办
        best_figure = None
        max_change = -float('inf')

        for fig in all_figures:
            if fig.price and fig.price > 0 and fig.market_price and fig.market_price > 0:
                change_percentage = ((fig.market_price - fig.price) / fig.price) * 100
                if change_percentage > max_change:
                    max_change = change_percentage
                    best_figure = fig

        if best_figure:
            target_price = int(best_figure.price * 1.5)
            return {
                "rating": f"{best_figure.name} 买入",
                "target_price": f"¥{target_price} (+{int((target_price / best_figure.market_price - 1) * 100)}%)",
                "stop_loss": f"¥{int(best_figure.market_price * 0.8)} (-20%)",
                "institution": "FigureBox研究院",
                "date": date.today().strftime("%Y-%m-%d"),
                "reason": f"{best_figure.name}表现强势，涨幅达{round(max_change, 1)}%，建议关注"
            }
        else:
            return {
                "rating": "GSC 初音韶华 买入",
                "target_price": "¥2,800 (+40%)",
                "stop_loss": "¥1,600 (-20%)",
                "institution": "FigureBox研究院",
                "date": date.today().strftime("%Y-%m-%d"),
                "reason": "再版停产公告+海景房属性+即将出荷"
            }
