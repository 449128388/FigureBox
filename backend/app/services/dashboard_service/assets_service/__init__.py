"""
资产服务模块
提供资产相关的核心计算服务

企业级架构说明：
本模块采用 Facade 模式，通过 assets_service.py 提供统一的向后兼容接口
新代码应优先直接使用子服务，Facade 类仅用于保持向后兼容
"""

# Facade 模式统一入口（向后兼容）
from .assets_service import (
    AssetCalculationService,
    HoldingAnalysisService,
    IndexService
)

# 子服务（新代码优先直接使用）
from .asset_core_calculations import (
    TotalAssetsCalculator,
    DailyChangeCalculator,
    PositionCalculator,
    DailyCacheService
)

from .asset_market_benchmark_service import (
    MarketBenchmarkService
)

from .asset_distribution_service import (
    AssetDistributionService
)

from .holding_position_service import (
    HoldingPositionService
)

__all__ = [
    # Facade 统一入口
    'AssetCalculationService',
    'HoldingAnalysisService',
    'IndexService',
    # 子服务
    'TotalAssetsCalculator',
    'DailyChangeCalculator',
    'PositionCalculator',
    'DailyCacheService',
    'MarketBenchmarkService',
    'AssetDistributionService',
    'HoldingPositionService'
]
