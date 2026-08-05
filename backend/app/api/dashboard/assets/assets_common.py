"""
assets_common.py - 资产模块公共服务层

功能说明：
- 提供资产模块各路由共享的通用工具方法
- 封装复用的数据库查询逻辑
- 统一处理用户认证、数据验证等通用操作

依赖：
- sqlalchemy.orm.Session
- app.models.database
- app.models.user.User

创建时间: 2026-05-18
作者: FigureBox Team
"""

from typing import List, Set, Optional
from sqlalchemy.orm import Session
from datetime import datetime, timedelta

from app.models.order import Order
from app.models.figure import Figure
from app.models.user import User


class AssetsCommonService:
    """
    资产模块公共服务类
    
    提供资产相关路由共享的通用工具方法
    """

    @staticmethod
    def get_valid_orders(db: Session, user_id: Optional[int] = None) -> List[Order]:
        """
        获取所有有效订单（排除已取消状态）
        
        Args:
            db: 数据库会话
            user_id: 用户ID（可选，为None时返回所有用户的有效订单）
        
        Returns:
            List[Order]: 有效订单列表
        """
        query = db.query(Order).filter(
            Order.is_active == 1,
            Order.status != "已取消"
        )
        
        if user_id is not None:
            query = query.filter(Order.user_id == user_id)
        
        return query.all()

    @staticmethod
    def get_figure_ids_with_valid_orders(orders: List[Order]) -> Set[int]:
        """
        从订单列表中提取有有效订单的手办ID集合
        
        Args:
            orders: 订单列表
        
        Returns:
            Set[int]: 手办ID集合
        """
        return set(order.figure_id for order in orders)

    @staticmethod
    def get_figures_with_valid_orders(db: Session, orders: List[Order]) -> List[Figure]:
        """
        获取有有效订单的手办列表
        
        Args:
            db: 数据库会话
            orders: 有效订单列表
        
        Returns:
            List[Figure]: 手办列表
        """
        figure_ids = AssetsCommonService.get_figure_ids_with_valid_orders(orders)
        
        if not figure_ids:
            return []
        
        all_figures = db.query(Figure).all()
        return [fig for fig in all_figures if fig.id in figure_ids]

    @staticmethod
    def calculate_time_range(time_range: str) -> datetime:
        """
        根据时间范围字符串计算起始日期
        
        Args:
            time_range: 时间范围字符串 (1m, 3m, 1y, all)
        
        Returns:
            datetime: 起始日期
        """
        now = datetime.now()
        
        if time_range == "1m":
            return now - timedelta(days=30)
        elif time_range == "3m":
            return now - timedelta(days=90)
        elif time_range == "1y":
            return now - timedelta(days=365)
        else:  # all
            return datetime(2000, 1, 1)

    @staticmethod
    def check_token_refresh(request, response) -> None:
        """
        检查是否需要返回新的token（自动续期）
        
        Args:
            request: FastAPI请求对象
            response: FastAPI响应对象
        """
        if hasattr(request.state, 'new_token'):
            response.headers['X-New-Token'] = request.state.new_token
