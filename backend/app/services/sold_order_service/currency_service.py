"""
币种转换服务

提供多币种与人民币之间的汇率转换功能
"""
from typing import Dict, Optional
from sqlalchemy.orm import Session


# 兜底默认汇率（当统一汇率服务不可用时使用）
FALLBACK_RATES = {
    'CNY': 1.0,
    'USD': 7.0,
    'JPY': 1/23,
    'EUR': 8.0,
    'HKD': 0.9,
    'GBP': 9.0
}


class CurrencyService:
    """
    币种转换服务类

    提供汇率转换功能，支持 CNY、USD、JPY、EUR 等币种与人民币的相互转换

    汇率数据来源：
    - 优先使用 ExchangeRateService 从中国外汇交易中心获取的实时汇率
    - 当 db 参数为空或服务不可用时，使用 FALLBACK_RATES 兜底
    """

    @staticmethod
    def _get_rates(db: Optional[Session] = None) -> Dict[str, float]:
        """获取汇率数据"""
        if db is not None:
            try:
                from app.services.exchange_rate_service import ExchangeRateService
                return ExchangeRateService.get_exchange_rates(db)
            except Exception:
                pass
        return dict(FALLBACK_RATES)

    @staticmethod
    def to_cny(amount: float, currency: str, db: Optional[Session] = None) -> float:
        """
        将指定币种金额转换为人民币

        Args:
            amount: 金额
            currency: 币种代码 (CNY/USD/JPY/EUR)
            db: 数据库会话（可选，提供时使用实时汇率）

        Returns:
            人民币金额
        """
        if not currency or currency == 'CNY':
            return amount

        rates = CurrencyService._get_rates(db)
        rate = rates.get(currency, 1.0)
        return amount * rate

    @staticmethod
    def from_cny(amount_cny: float, currency: str, db: Optional[Session] = None) -> float:
        """
        将人民币金额转换为指定币种

        Args:
            amount_cny: 人民币金额
            currency: 目标币种代码 (CNY/USD/JPY/EUR)
            db: 数据库会话（可选，提供时使用实时汇率）

        Returns:
            目标币种金额
        """
        if not currency or currency == 'CNY':
            return amount_cny

        rates = CurrencyService._get_rates(db)
        rate = rates.get(currency, 1.0)
        if rate == 0:
            return 0
        return amount_cny / rate

    @staticmethod
    def get_exchange_rate(currency: str, db: Optional[Session] = None) -> float:
        """
        获取指定币种相对人民币的汇率

        Args:
            currency: 币种代码
            db: 数据库会话（可选，提供时使用实时汇率）

        Returns:
            汇率（1单位外币 = ?人民币）
        """
        rates = CurrencyService._get_rates(db)
        return rates.get(currency, 1.0)

    @staticmethod
    def convert(amount: float, from_currency: str, to_currency: str, db: Optional[Session] = None) -> float:
        """
        在任意两种币种之间转换金额

        Args:
            amount: 原始金额
            from_currency: 原始币种
            to_currency: 目标币种
            db: 数据库会话（可选，提供时使用实时汇率）

        Returns:
            转换后的金额
        """
        cny_amount = CurrencyService.to_cny(amount, from_currency, db)
        return CurrencyService.from_cny(cny_amount, to_currency, db)

    @staticmethod
    def calculate_profit_in_cny(
        sell_price: float,
        sell_price_currency: str,
        cost_price: float,
        cost_price_currency: str,
        shipping_fee: float,
        shipping_fee_currency: str,
        platform_fee: float,
        platform_fee_currency: str,
        db: Optional[Session] = None
    ) -> Dict[str, float]:
        """
        计算净利润（统一转换为人民币）

        Args:
            sell_price: 卖出价格
            sell_price_currency: 卖出价格币种
            cost_price: 成本价格
            cost_price_currency: 成本价格币种
            shipping_fee: 运费
            shipping_fee_currency: 运费币种
            platform_fee: 平台手续费
            platform_fee_currency: 平台手续费币种
            db: 数据库会话（可选，提供时使用实时汇率）

        Returns:
            包含净利润和利润率的字典
        """
        sell_price_cny = CurrencyService.to_cny(sell_price, sell_price_currency, db)
        cost_price_cny = CurrencyService.to_cny(cost_price, cost_price_currency, db)
        shipping_fee_cny = CurrencyService.to_cny(shipping_fee, shipping_fee_currency, db)
        platform_fee_cny = CurrencyService.to_cny(platform_fee, platform_fee_currency, db)

        net_profit_cny = sell_price_cny - cost_price_cny - shipping_fee_cny - platform_fee_cny
        profit_rate = (net_profit_cny / cost_price_cny) * 100 if cost_price_cny != 0 else 0

        return {
            'net_profit': round(net_profit_cny, 2),
            'profit_rate': round(profit_rate, 2),
            'sell_price_cny': round(sell_price_cny, 2),
            'cost_price_cny': round(cost_price_cny, 2),
            'shipping_fee_cny': round(shipping_fee_cny, 2),
            'platform_fee_cny': round(platform_fee_cny, 2)
        }
