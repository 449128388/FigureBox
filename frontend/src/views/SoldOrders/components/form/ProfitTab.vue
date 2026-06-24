<template>
  <div class="tab-content profit-preview">
    <!-- 转换说明 -->
    <div class="conversion-notice">
      <el-alert
        type="info"
        :closable="false"
        show-icon
      >
        <template #title>
          <span>盈亏计算已自动将所有币种转换为人民币结算</span>
        </template>
      </el-alert>
    </div>

    <!-- 原始金额展示 -->
    <div class="original-amounts">
      <h4 class="section-title">原始金额</h4>
      <div class="amount-grid">
        <div class="amount-item">
          <span class="amount-label">卖出价:</span>
          <span class="amount-value">{{ formatCurrency(order.sell_price, order.sell_price_currency) }}</span>
          <span v-if="order.sell_price_currency !== 'CNY'" class="amount-converted">
            (≈ ¥{{ formatNumber(convertToCNY(order.sell_price, order.sell_price_currency)) }})
          </span>
        </div>
        <div class="amount-item">
          <span class="amount-label">成本价:</span>
          <span class="amount-value">{{ formatCurrency(order.cost_price, order.cost_price_currency) }}</span>
          <span v-if="order.cost_price_currency !== 'CNY'" class="amount-converted">
            (≈ ¥{{ formatNumber(convertToCNY(order.cost_price, order.cost_price_currency)) }})
          </span>
        </div>
        <div class="amount-item">
          <span class="amount-label">运费:</span>
          <span class="amount-value">{{ formatCurrency(order.shipping_fee, order.shipping_fee_currency) }}</span>
          <span v-if="order.shipping_fee_currency !== 'CNY'" class="amount-converted">
            (≈ ¥{{ formatNumber(convertToCNY(order.shipping_fee, order.shipping_fee_currency)) }})
          </span>
        </div>
        <div class="amount-item">
          <span class="amount-label">手续费:</span>
          <span class="amount-value">{{ formatCurrency(order.platform_fee, order.platform_fee_currency) }}</span>
          <span v-if="order.platform_fee_currency !== 'CNY'" class="amount-converted">
            (≈ ¥{{ formatNumber(convertToCNY(order.platform_fee, order.platform_fee_currency)) }})
          </span>
        </div>
      </div>
    </div>

    <!-- 人民币结算计算过程 -->
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

    <!-- 汇率信息 -->
    <div class="exchange-rate-info">
      <h4 class="section-title">汇率参考</h4>
      <div class="rate-list">
        <span class="rate-item">1 USD = 7.00 CNY</span>
        <span class="rate-item">1 EUR = 8.00 CNY</span>
        <span class="rate-item">1 CNY = 23 JPY</span>
      </div>
    </div>

    <!-- 盈亏状态指示器 -->
    <div class="profit-indicator">
      <span :class="['indicator', { active: currentProfit > 0 }]">🔴 盈利</span>
      <span :class="['indicator', { active: currentProfit < 0 }]">🟢 亏损</span>
      <span :class="['indicator', { active: currentProfit === 0 }]">⚪ 持平</span>
    </div>
  </div>
</template>

<script>
import { computed } from 'vue'

export default {
  name: 'ProfitTab',
  props: {
    order: Object
  },
  setup(props) {
    // 汇率配置：相对人民币的汇率（1单位外币 = ?人民币）
    const EXCHANGE_RATES = {
      'CNY': 1.0,     // 人民币
      'JPY': 1/23,    // 日元：1人民币 = 23日元，所以 1日元 = 1/23人民币
      'USD': 7.0,     // 美元：1美元 = 7人民币
      'EUR': 8.0      // 欧元：1欧元 = 8人民币
    }

    // 币种符号映射
    const CURRENCY_SYMBOLS = {
      'CNY': '¥',
      'USD': '$',
      'JPY': '¥',
      'EUR': '€'
    }

    // 转换为人民币
    const convertToCNY = (amount, currency) => {
      if (!currency || currency === 'CNY') return amount || 0
      const rate = EXCHANGE_RATES[currency] || 1.0
      return (amount || 0) * rate
    }

    // 计算人民币金额
    const sellPriceCNY = computed(() => {
      return convertToCNY(props.order.sell_price, props.order.sell_price_currency)
    })

    const costPriceCNY = computed(() => {
      return convertToCNY(props.order.cost_price, props.order.cost_price_currency)
    })

    const shippingFeeCNY = computed(() => {
      return convertToCNY(props.order.shipping_fee, props.order.shipping_fee_currency)
    })

    const platformFeeCNY = computed(() => {
      return convertToCNY(props.order.platform_fee, props.order.platform_fee_currency)
    })

    // 计算净利润（人民币）
    const currentProfit = computed(() => {
      return sellPriceCNY.value - costPriceCNY.value -
             shippingFeeCNY.value - platformFeeCNY.value
    })

    // 计算利润率
    const currentProfitRate = computed(() => {
      if (costPriceCNY.value === 0) return 0
      return (currentProfit.value / costPriceCNY.value) * 100
    })

    // 盈亏样式类
    const profitClass = computed(() => {
      if (currentProfit.value > 0) return 'profit-positive'
      if (currentProfit.value < 0) return 'profit-negative'
      return 'profit-neutral'
    })

    // 盈亏图标
    const profitIcon = computed(() => {
      if (currentProfit.value > 0) return '📈'
      if (currentProfit.value < 0) return '📉'
      return ''
    })

    // 格式化数字
    const formatNumber = (num) => {
      return Math.abs(num || 0).toLocaleString('zh-CN', {
        minimumFractionDigits: 2,
        maximumFractionDigits: 2
      })
    }

    // 格式化币种金额
    const formatCurrency = (amount, currency) => {
      const symbol = CURRENCY_SYMBOLS[currency] || '¥'
      const value = Math.abs(amount || 0).toLocaleString('zh-CN', {
        minimumFractionDigits: 2,
        maximumFractionDigits: 2
      })
      return `${symbol}${value}`
    }

    return {
      sellPriceCNY,
      costPriceCNY,
      shippingFeeCNY,
      platformFeeCNY,
      currentProfit,
      currentProfitRate,
      profitClass,
      profitIcon,
      formatNumber,
      formatCurrency,
      convertToCNY
    }
  }
}
</script>

<style scoped>
/* 标签内容区域 */
.tab-content {
  padding: 20px;
}

/* 转换说明 */
.conversion-notice {
  margin-bottom: 20px;
}

/* 区块标题 */
.section-title {
  font-size: 14px;
  font-weight: 600;
  color: #333;
  margin-bottom: 12px;
  padding-bottom: 8px;
  border-bottom: 1px solid #e4e8ec;
}

/* 原始金额展示 */
.original-amounts {
  background: #fff;
  padding: 16px;
  border-radius: 8px;
  margin-bottom: 16px;
  border: 1px solid #e4e8ec;
}

.amount-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12px;
}

.amount-item {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 13px;
}

.amount-label {
  color: #666;
  min-width: 60px;
}

.amount-value {
  color: #333;
  font-weight: 500;
}

.amount-converted {
  color: #909399;
  font-size: 12px;
}

/* 人民币结算计算 */
.cny-calculation {
  background: linear-gradient(135deg, #f5f7fa 0%, #e4e8ec 100%);
  padding: 16px;
  border-radius: 8px;
  margin-bottom: 16px;
}

.profit-calculation {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 8px;
  margin-bottom: 8px;
}

.calc-item {
  font-size: 14px;
  color: #666;
}

.calc-operator {
  font-size: 14px;
  color: #999;
}

.profit-result {
  font-size: 16px;
  font-weight: 600;
  padding: 8px 12px;
  border-radius: 6px;
}

/* 盈利红色、亏损绿色 - 符合中国股市涨跌颜色习惯 */
.profit-positive {
  background-color: #ffebee;
  color: #c62828;
}

.profit-negative {
  background-color: #e8f5e9;
  color: #2e7d32;
}

.profit-neutral {
  background-color: #f5f5f5;
  color: #757575;
}

/* 汇率信息 */
.exchange-rate-info {
  background: #fff;
  padding: 16px;
  border-radius: 8px;
  margin-bottom: 16px;
  border: 1px solid #e4e8ec;
}

.rate-list {
  display: flex;
  flex-wrap: wrap;
  gap: 16px;
}

.rate-item {
  font-size: 12px;
  color: #666;
  background: #f5f7fa;
  padding: 4px 12px;
  border-radius: 4px;
}

/* 盈亏状态指示器 */
.profit-indicator {
  display: flex;
  gap: 12px;
  margin-top: 16px;
}

.indicator {
  padding: 4px 12px;
  border-radius: 4px;
  font-size: 12px;
  color: #999;
  background-color: #fff;
  opacity: 0.5;
  transition: all 0.3s;
  border: 1px solid #e4e8ec;
}

.indicator.active {
  opacity: 1;
  color: #333;
  font-weight: 500;
}

.indicator.active[data-type="profit"] {
  background-color: #e8f5e9;
  border-color: #4caf50;
}
</style>
