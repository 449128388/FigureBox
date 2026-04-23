"""
资产市场基准服务
提供塑料指数和跑赢大盘百分比等市场基准相关的计算逻辑
采用企业级服务层架构
"""
from datetime import date
from typing import Tuple, List

from app.models.figure import Figure


class MarketBenchmarkService:
    """市场基准服务类"""

    # 基准日指数
    BASE_INDEX = 1000
    # 基准日上证指数
    BASE_SH_INDEX = 2900

    @classmethod
    def calculate_plastic_index(
        cls,
        figures: List[Figure],
        total_assets: float
    ) -> Tuple[float, date]:
        """
        计算塑料指数（市值加权复权指数）

        公式：塑料指数 = 基准日指数 × (当前总市值 / 基准日总市值)
        基准日指数 = 1000
        基准日 = 最早购买手办的日期（开户首日）

        关键原则：
        1. 新买入手办不改变指数，只增加成分股
        2. 卖出手办不影响指数，视为成分股剔除
        3. 再版冲击（复刻）通过市场价变化自然反映在指数中

        Args:
            figures: 手办列表
            total_assets: 当前总资产

        Returns:
            Tuple[float, date]: (塑料指数, 基准日)
        """
        # 找到最早的购买日期作为基准日（开户首日）
        purchase_dates = [
            fig.purchase_date for fig in figures if fig.purchase_date
        ]

        if not purchase_dates:
            # 没有手办时，返回基准指数1000和当前日期
            return cls.BASE_INDEX, date.today()

        base_date = min(purchase_dates)

        # 基准日总市值 = 基准日当天所有持仓手办的平均入手价格总和
        # 这是用户的初始投入成本
        base_total_value = sum(
            (fig.average_purchase_price or 0) * (fig.quantity or 1)
            for fig in figures
        )

        # 如果没有成本数据，使用当前总资产作为基准（避免除以0）
        if base_total_value <= 0:
            base_total_value = total_assets if total_assets > 0 else cls.BASE_INDEX

        # 计算塑料指数
        # 公式：塑料指数 = 基准日指数 × (当前总市值 / 基准日总市值)
        plastic_index = round(
            cls.BASE_INDEX * (total_assets / base_total_value), 2
        )

        return plastic_index, base_date

    @classmethod
    def calculate_outperform_percentage(
        cls,
        plastic_index: float,
        sh_index: float
    ) -> float:
        """
        计算跑赢大盘百分比（成立至今）

        塑料指数涨幅 = (当前塑料指数 - 基准日指数) / 基准日指数 × 100%
        上证指数涨幅 = (当前上证指数 - 基准日上证指数) / 基准日上证指数 × 100%
        跑赢大盘 = 塑料指数涨幅 - 上证指数涨幅

        Args:
            plastic_index: 当前塑料指数
            sh_index: 当前上证指数

        Returns:
            float: 跑赢大盘百分比
        """
        plastic_change_percentage = (
            (plastic_index - cls.BASE_INDEX) / cls.BASE_INDEX
        ) * 100
        sh_change_percentage_total = (
            (sh_index - cls.BASE_SH_INDEX) / cls.BASE_SH_INDEX
        ) * 100
        outperform_percentage = round(
            plastic_change_percentage - sh_change_percentage_total, 2
        )

        return outperform_percentage
