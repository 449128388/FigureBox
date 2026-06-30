<template>
  <div class="tab-content profit-preview">
    <div class="conversion-notice">
      <el-alert type="info" :closable="false" show-icon>
        <template #title>
          <span>盈亏计算已自动将所有币种转换为人民币结算</span>
        </template>
      </el-alert>
    </div>

    <div class="original-amounts">
      <h4 class="section-title">原始金额</h4>
      <div class="amount-grid">
        <div class="amount-item">
          <span class="amount-label">卖出价:</span>
          <span class="amount-value">{{ formatCurrency(order.sell_price, order.sell_price_currency) }}</span>
          <span v-if="order.sell_price_currency !== 'CNY'" class="amount-converted">
            (≈ ¥{{ formatNumber(toCNY(order.sell_price, order.sell_price_currency)) }})
          </span>
        </div>
        <div class="amount-item">
          <span class="amount-label">成本价:</span>
          <span class="amount-value">{{ formatCurrency(order.cost_price, order.cost_price_currency) }}</span>
          <span v-if="order.cost_price_currency !== 'CNY'" class="amount-converted">
            (≈ ¥{{ formatNumber(toCNY(order.cost_price, order.cost_price_currency)) }})
          </span>
        </div>
        <div class="amount-item">
          <span class="amount-label">运费:</span>
          <span class="amount-value">{{ formatCurrency(order.shipping_fee, order.shipping_fee_currency) }}</span>
          <span v-if="order.shipping_fee_currency !== 'CNY'" class="amount-converted">
            (≈ ¥{{ formatNumber(toCNY(order.shipping_fee, order.shipping_fee_currency)) }})
          </span>
        </div>
        <div class="amount-item">
          <span class="amount-label">手续费:</span>
          <span class="amount-value">{{ formatCurrency(order.platform_fee, order.platform_fee_currency) }}</span>
          <span v-if="order.platform_fee_currency !== 'CNY'" class="amount-converted">
            (≈ ¥{{ formatNumber(toCNY(order.platform_fee, order.platform_fee_currency)) }})
          </span>
        </div>
      </div>
    </div>

    <div class="cny-calculation">
      <h4 class="section-title">人民币结算</h4>
      <div class="profit-calculation">
        <span class="calc-item">卖出价: ¥{{ formatNumber(sellPriceCNY) }}</span>
        <span class="calc-operator">-</span>
        <span class="calc-item">成本: ¥{{ formatNumber(costPriceCNY) }}</span>
        <span class="calc-operator">-</span>
        <span class="calc-item">运费: ¥{{ formatNumber(shippingFeeCNY) }}</span>
      </div>
      <div class="profit-calculation">
        <span class="calc-operator">-</span>
        <span class="calc-item">手续费: ¥{{ formatNumber(platformFeeCNY) }}</span>
        <span class="calc-operator">=</span>
        <span class="profit-result" :class="profitClass">
          💰 净利润: {{ currentProfit >= 0 ? '+' : '' }}¥{{ formatNumber(Math.abs(currentProfit)) }}
          ({{ profitIcon }}{{ formatNumber(Math.abs(currentProfitRate)) }}%)
        </span>
      </div>
    </div>

    <div class="exchange-rate-info">
      <h4 class="section-title">汇率参考</h4>
      <div class="rate-list">
        <span class="rate-item">1 USD = {{ getRate('USD').toFixed(2) }} CNY</span>
        <span class="rate-item">1 EUR = {{ getRate('EUR').toFixed(2) }} CNY</span>
        <span class="rate-item">1 CNY = {{ (1 / getRate('JPY')).toFixed(0) }} JPY</span>
      </div>
    </div>

    <div class="profit-indicator">
      <span :class="['indicator', { active: currentProfit > 0 }]">🔴 盈利</span>
      <span :class="['indicator', { active: currentProfit < 0 }]">🟢 亏损</span>
      <span :class="['indicator', { active: currentProfit === 0 }]">⚪ 持平</span>
    </div>
  </div>
</template>

<script>
import { computed, ref, onMounted } from 'vue'
import { useExchangeRates } from '../../../../composables/useExchangeRates'

export default {
  name: 'ProfitTab',
  props: { order: Object },
  setup(props) {
    const { getRate, toCNY, loadRates } = useExchangeRates()
    const loaded = ref(false)

    onMounted(async () => {
      await loadRates()
      loaded.value = true
    })

    // 兜底默认汇率用于同步计算
    const FALLBACK_RATES = { CNY: 1.0, JPY: 1 / 23, USD: 7.0, EUR: 8.0 }

    const _getRate = (currency) => {
      const r = getRate(currency)
      return r ?? FALLBACK_RATES[currency] ?? 1.0
    }
    const _toCNY = (amount, currency) => {
      if (!currency || currency === 'CNY') return amount || 0
      return (amount || 0) * _getRate(currency)
    }

    const CURRENCY_SYMBOLS = { CNY: '¥', USD: '$', JPY: '¥', EUR: '€' }

    const sellPriceCNY = computed(() => _toCNY(props.order.sell_price, props.order.sell_price_currency))
    const costPriceCNY = computed(() => _toCNY(props.order.cost_price, props.order.cost_price_currency))
    const shippingFeeCNY = computed(() => _toCNY(props.order.shipping_fee, props.order.shipping_fee_currency))
    const platformFeeCNY = computed(() => _toCNY(props.order.platform_fee, props.order.platform_fee_currency))
    const currentProfit = computed(() => sellPriceCNY.value - costPriceCNY.value - shippingFeeCNY.value - platformFeeCNY.value)
    const currentProfitRate = computed(() => costPriceCNY.value === 0 ? 0 : (currentProfit.value / costPriceCNY.value) * 100)
    const profitClass = computed(() => {
      if (currentProfit.value > 0) return 'profit-positive'
      if (currentProfit.value < 0) return 'profit-negative'
      return 'profit-neutral'
    })
    const profitIcon = computed(() => {
      if (currentProfit.value > 0) return '📈'
      if (currentProfit.value < 0) return '📉'
      return ''
    })
    const formatNumber = (num) => Math.abs(num || 0).toLocaleString('zh-CN', { minimumFractionDigits: 2, maximumFractionDigits: 2 })
    const formatCurrency = (amount, currency) => {
      const symbol = CURRENCY_SYMBOLS[currency] || '¥'
      const value = Math.abs(amount || 0).toLocaleString('zh-CN', { minimumFractionDigits: 2, maximumFractionDigits: 2 })
      return `${symbol}${value}`
    }

    return { sellPriceCNY, costPriceCNY, shippingFeeCNY, platformFeeCNY, currentProfit, currentProfitRate, profitClass, profitIcon, formatNumber, formatCurrency, toCNY: _toCNY, getRate: _getRate, loaded }
  }
}
</script>

<style scoped>
.tab-content { padding: 20px; }
.conversion-notice { margin-bottom: 20px; }
.section-title { font-size: 14px; font-weight: 600; color: #333; margin-bottom: 12px; padding-bottom: 8px; border-bottom: 1px solid #e4e8ec; }
.original-amounts { background: #fff; padding: 16px; border-radius: 8px; margin-bottom: 16px; border: 1px solid #e4e8ec; }
.amount-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 12px; }
.amount-item { display: flex; align-items: center; gap: 8px; font-size: 13px; }
.amount-label { color: #666; min-width: 60px; }
.amount-value { color: #333; font-weight: 500; }
.amount-converted { color: #909399; font-size: 12px; }
.cny-calculation { background: linear-gradient(135deg, #f5f7fa 0%, #e4e8ec 100%); padding: 16px; border-radius: 8px; margin-bottom: 16px; }
.profit-calculation { display: flex; align-items: center; flex-wrap: wrap; gap: 8px; margin-bottom: 8px; }
.calc-item { font-size: 14px; color: #666; }
.calc-operator { font-size: 14px; color: #999; }
.profit-result { font-size: 16px; font-weight: 600; padding: 8px 12px; border-radius: 6px; }
.profit-positive { background-color: #ffebee; color: #c62828; }
.profit-negative { background-color: #e8f5e9; color: #2e7d32; }
.profit-neutral { background-color: #f5f5f5; color: #757575; }
.exchange-rate-info { background: #fff; padding: 16px; border-radius: 8px; margin-bottom: 16px; border: 1px solid #e4e8ec; }
.rate-list { display: flex; flex-wrap: wrap; gap: 16px; }
.rate-item { font-size: 12px; color: #666; background: #f5f7fa; padding: 4px 12px; border-radius: 4px; }
.profit-indicator { display: flex; gap: 12px; margin-top: 16px; }
.indicator { padding: 4px 12px; border-radius: 4px; font-size: 12px; color: #999; background-color: #fff; opacity: 0.5; transition: all 0.3s; border: 1px solid #e4e8ec; }
.indicator.active { opacity: 1; color: #333; font-weight: 500; }
.indicator.active[data-type="profit"] { background-color: #e8f5e9; border-color: #4caf50; }
</style>
