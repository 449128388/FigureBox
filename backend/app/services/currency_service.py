"""
币种转换服务

提供多币种与人民币之间的汇率转换功能
"""
from typing import Dict


class CurrencyService:
    """
    币种转换服务类

    提供汇率转换功能，支持 CNY、USD、JPY、EUR 等币种与人民币的相互转换
    """

    # 汇率配置：相对人民币的汇率
    # 表示 1 单位外币 = ? 人民币
    EXCHANGE_RATES = {
        'CNY': 1.0,     # 人民币
        'JPY': 1/23,    # 日元：1人民币 = 23日元，所以 1日元 = 1/23人民币
        'USD': 7.0,     # 美元：1美元 = 7人民币
        'EUR': 8.0      # 欧元：1欧元 = 8人民币
    }

    @staticmethod
    def to_cny(amount: float, currency: str) -> float:
        """
        将指定币种金额转换为人民币

        Args:
            amount: 金额
            currency: 币种代码 (CNY/USD/JPY/EUR)

        Returns:
            人民币金额
        """
        if not currency or currency == 'CNY':
            return amount

        rate = CurrencyService.EXCHANGE_RATES.get(currency, 1.0)
        return amount * rate

    @staticmethod
    def from_cny(amount_cny: float, currency: str) -> float:
        """
        将人民币金额转换为指定币种

        Args:
            amount_cny: 人民币金额
            currency: 目标币种代码 (CNY/USD/JPY/EUR)

        Returns:
            目标币种金额
        """
        if not currency or currency == 'CNY':
            return amount_cny

        rate = CurrencyService.EXCHANGE_RATES.get(currency, 1.0)
        if rate == 0:
            return 0
        return amount_cny / rate

    @staticmethod
    def get_exchange_rate(currency: str) -> float:
        """
        获取指定币种相对人民币的汇率

        Args:
            currency: 币种代码

        Returns:
            汇率（1单位外币 = ?人民币）
        """
        return CurrencyService.EXCHANGE_RATES.get(currency, 1.0)

    @staticmethod
    def convert(amount: float, from_currency: str, to_currency: str) -> float:
        """
        在任意两种币种之间转换金额

        Args:
            amount: 原始金额
            from_currency: 原始币种
            to_currency: 目标币种

        Returns:
            转换后的金额
        """
        # 先转换为人民币
        cny_amount = CurrencyService.to_cny(amount, from_currency)
        # 再转换为目标币种
        return CurrencyService.from_cny(cny_amount, to_currency)

    @staticmethod
    def calculate_profit_in_cny(
        sell_price: float,
        sell_price_currency: str,
        cost_price: float,
        cost_price_currency: str,
        shipping_fee: float,
        shipping_fee_currency: str,
        platform_fee: float,
        platform_fee_currency: str
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

        Returns:
            包含净利润和利润率的字典
        """
        # 将所有金额转换为人民币
        sell_price_cny = CurrencyService.to_cny(sell_price, sell_price_currency)
        cost_price_cny = CurrencyService.to_cny(cost_price, cost_price_currency)
        shipping_fee_cny = CurrencyService.to_cny(shipping_fee, shipping_fee_currency)
        platform_fee_cny = CurrencyService.to_cny(platform_fee, platform_fee_currency)

        # 计算净利润（人民币）
        # 运费和手续费是支出，所以是减去
        net_profit_cny = sell_price_cny - cost_price_cny - shipping_fee_cny - platform_fee_cny

        # 计算利润率
        profit_rate = (net_profit_cny / cost_price_cny) * 100 if cost_price_cny != 0 else 0

        return {
            'net_profit': round(net_profit_cny, 2),
            'profit_rate': round(profit_rate, 2),
            'sell_price_cny': round(sell_price_cny, 2),
            'cost_price_cny': round(cost_price_cny, 2),
            'shipping_fee_cny': round(shipping_fee_cny, 2),
            'platform_fee_cny': round(platform_fee_cny, 2)
        }
