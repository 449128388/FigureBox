"""
交易记录服务
提供交易记录相关的业务逻辑，是各子服务的统一入口，保持向后兼容

企业级架构说明：
本文件作为 Facade 模式实现，将业务逻辑拆分到以下子服务：
- MonthlyStatsService: 月度交易统计服务（monthly_stats_service.py）
- TransactionQueryService: 交易流水查询服务（transaction_query_service.py）
- TradeProfitAnalysisService: 盈亏分析服务（profit_analysis_service.py）

新代码应优先直接使用子服务，本文件仅用于保持向后兼容。
"""
from datetime import date
from typing import Dict, Any, List
from sqlalchemy.orm import Session

# 导入子服务
from .monthly_stats_service import MonthlyStatsService
from .transaction_query_service import TransactionQueryService
from .profit_analysis_service import TradeProfitAnalysisService


class TradeRecordsService:
    """
    交易记录服务类（Facade 模式）

    作为各子服务的统一入口，所有方法委托给相应的子服务实现
    保持向后兼容，现有调用代码无需修改
    """

    # ==========================================================================
    # 月度统计服务（委托给 monthly_stats_service）
    # ==========================================================================
    @staticmethod
    def get_monthly_stats(
        db: Session,
        user_id: int,
        month_start: date,
        month_end: date
    ) -> Dict[str, Any]:
        """
        获取月度交易统计

        Args:
            db: 数据库会话
            user_id: 用户ID
            month_start: 月份开始日期
            month_end: 月份结束日期

        Returns:
            Dict: 月度统计，包含买入数量、买入金额、卖出数量、卖出金额、净现金流
        """
        return MonthlyStatsService.get_monthly_stats(db, user_id, month_start, month_end)

    # ==========================================================================
    # 交易流水服务（委托给 transaction_query_service）
    # ==========================================================================
    @staticmethod
    def get_transactions(db: Session, user_id: int) -> List[Dict[str, Any]]:
        """
        获取交易流水记录

        Args:
            db: 数据库会话
            user_id: 用户ID

        Returns:
            List[Dict]: 交易记录列表，按时间倒序排列
        """
        return TransactionQueryService.get_transactions(db, user_id)

    @staticmethod
    def get_buy_transactions(db: Session, user_id: int) -> List[Dict[str, Any]]:
        """
        获取买入交易记录

        Args:
            db: 数据库会话
            user_id: 用户ID

        Returns:
            List[Dict]: 买入交易记录列表
        """
        return TransactionQueryService._get_buy_transactions(db, user_id)

    @staticmethod
    def get_sell_transactions(db: Session, user_id: int) -> List[Dict[str, Any]]:
        """
        获取卖出交易记录

        Args:
            db: 数据库会话
            user_id: 用户ID

        Returns:
            List[Dict]: 卖出交易记录列表
        """
        return TransactionQueryService._get_sell_transactions(db, user_id)

    # ==========================================================================
    # 盈亏分析服务（委托给 profit_analysis_service）
    # ==========================================================================
    @staticmethod
    def get_profit_analysis(
        db: Session,
        user_id: int,
        current_year: int
    ) -> Dict[str, Any]:
        """
        获取盈亏分析数据

        Args:
            db: 数据库会话
            user_id: 用户ID
            current_year: 当前年份

        Returns:
            Dict: 盈亏分析数据，包含年度利润、胜率、交易统计等
        """
        return TradeProfitAnalysisService.get_profit_analysis(db, user_id, current_year)

    @staticmethod
    def calculate_net_profit(sold_order) -> float:
        """
        计算单笔交易的净利润

        Args:
            sold_order: 卖出订单对象

        Returns:
            float: 净利润
        """
        return TradeProfitAnalysisService._calculate_net_profit(sold_order)


# 为了保持向后兼容，导出子服务的别名
MonthlyStatsService = MonthlyStatsService
TransactionQueryService = TransactionQueryService
TradeProfitAnalysisService = TradeProfitAnalysisService
