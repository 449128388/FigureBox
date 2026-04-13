<template>
  <div class="trade-stats">
    <h4>本月交易统计</h4>
    <div class="stats-grid">
      <div class="stat-item">
        <div class="stat-label">买入</div>
        <div class="stat-value">{{ displayTradeData?.monthly_stats?.buy_count || 0 }}笔</div>
        <div class="stat-amount">¥{{ formatNumber(displayTradeData?.monthly_stats?.buy_amount || 0) }}</div>
      </div>
      <div class="stat-item">
        <div class="stat-label">卖出</div>
        <div class="stat-value">{{ displayTradeData?.monthly_stats?.sell_count || 0 }}笔</div>
        <div class="stat-amount">¥{{ formatNumber(displayTradeData?.monthly_stats?.sell_amount || 0) }}</div>
      </div>
      <div class="stat-item">
        <div class="stat-label">净现金流</div>
        <div class="stat-value" :class="{ positive: displayTradeData?.monthly_stats?.net_cashflow >= 0, negative: displayTradeData?.monthly_stats?.net_cashflow < 0 }">
          {{ displayTradeData?.monthly_stats?.net_cashflow >= 0 ? '+' : '' }}¥{{ formatNumber(Math.abs(displayTradeData?.monthly_stats?.net_cashflow || 0)) }}
        </div>
        <div class="stat-status" :class="{ positive: displayTradeData?.monthly_stats?.net_cashflow >= 0, negative: displayTradeData?.monthly_stats?.net_cashflow < 0 }">
          {{ displayTradeData?.monthly_stats?.net_cashflow >= 0 ? '(收入>支出)' : '(支出>收入)' }}
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'TradeStats',
  props: {
    displayTradeData: {
      type: Object,
      default: () => ({})
    },
    formatNumber: {
      type: Function,
      default: (num) => num?.toLocaleString() || '0'
    }
  }
}
</script>

<style scoped>
/* 交易统计 */
.trade-stats {
  margin-bottom: 30px;
  background-color: white;
  border-radius: 8px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
  padding: 20px;
}

.trade-stats h4 {
  margin-bottom: 15px;
  color: #333;
  font-size: 16px;
  font-weight: bold;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 20px;
}

.stat-item {
  background-color: #f9f9f9;
  padding: 20px;
  border-radius: 8px;
  text-align: center;
  border: 1px solid #e0e0e0;
}

.stat-label {
  font-size: 14px;
  color: #666;
  margin-bottom: 5px;
}

.stat-value {
  font-size: 24px;
  font-weight: bold;
  color: #333;
  margin-bottom: 5px;
}

.stat-amount {
  font-size: 16px;
  color: #666;
}

.stat-status {
  font-size: 12px;
  margin-top: 5px;
  padding: 2px 8px;
  border-radius: 4px;
  display: inline-block;
}

.stat-status.positive {
  background-color: #f0f9eb;
  color: #67c23a;
}

.stat-status.negative {
  background-color: #fef0f0;
  color: #f56c6c;
}

@media (max-width: 1200px) {
  .stats-grid {
    grid-template-columns: repeat(1, 1fr);
  }
}
</style>