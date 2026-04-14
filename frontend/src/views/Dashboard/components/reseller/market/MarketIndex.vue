<!--
  MarketIndex.vue - 塑料小人指数组件

  功能说明：
  - 展示塑料小人指数(HPI)的核心数据
  - 显示指数值、涨跌幅、成交量等关键指标
  - 展示上涨、持平、下跌的手办数量
  - 显示涨停和跌停的手办信息

  组件依赖：
  - 接收 marketData 作为 props，包含 index 数据

  维护提示：
  - 使用 formatNumber 方法格式化数字显示
  - 涨跌情况通过条件样式展示
-->
<template>
  <div class="market-index">
    <div class="index-header">
      <h3>塑料小人指数 (HPI)</h3>
      <div class="index-stats">
        <div class="stat-item">
          <div class="stat-label">涨:</div>
          <div class="stat-value">{{ marketData?.index?.up_count || 0 }}</div>
        </div>
        <div class="stat-item">
          <div class="stat-label">平:</div>
          <div class="stat-value">{{ marketData?.index?.flat_count || 0 }}</div>
        </div>
        <div class="stat-item">
          <div class="stat-label">跌:</div>
          <div class="stat-value">{{ marketData?.index?.down_count || 0 }}</div>
        </div>
      </div>
    </div>
    <div class="index-content">
      <div class="index-main">
        <div class="index-value">{{ marketData?.index?.value || 0 }}</div>
        <div class="index-change" :class="{ positive: marketData?.index?.change >= 0, negative: marketData?.index?.change < 0 }">
          {{ marketData?.index?.change >= 0 ? '↑' : '↓' }} {{ marketData?.index?.change >= 0 ? '+' : '' }}{{ marketData?.index?.change || 0 }} ({{ marketData?.index?.change_percentage >= 0 ? '+' : '' }}{{ marketData?.index?.change_percentage || 0 }}%)
        </div>
        <div class="index-volume">成交量: ¥{{ formatNumber(marketData?.index?.volume || 0) }}</div>
      </div>
      <div class="index-limits">
        <div class="limit-item">
          <span class="limit-label">涨停(10%):</span>
          <span class="limit-stocks">{{ marketData?.index?.limit_up || '无' }}</span>
        </div>
        <div class="limit-item">
          <span class="limit-label">跌停(-10%):</span>
          <span class="limit-stocks">{{ marketData?.index?.limit_down || '无' }}</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'MarketIndex',
  props: {
    marketData: {
      type: Object,
      default: () => ({})
    }
  },
  methods: {
    formatNumber(num) {
      return num?.toLocaleString() || '0'
    }
  }
}
</script>

<style scoped>
/* 塑料小人指数 */
.market-index {
  margin-bottom: 30px;
  padding: 20px;
  background-color: #f5f5f5;
  border-radius: 8px;
}

.index-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  padding-bottom: 15px;
  border-bottom: 1px solid #e0e0e0;
}

.index-header h3 {
  margin: 0;
  font-size: 18px;
  color: #333;
}

.index-stats {
  display: flex;
  gap: 20px;
}

.index-stats .stat-item {
  background-color: #f9f9f9;
  padding: 20px;
  border-radius: 8px;
  text-align: center;
  border: 1px solid #e0e0e0;
}

.index-stats .stat-label {
  font-size: 14px;
  color: #666;
  margin-bottom: 5px;
}

.index-stats .stat-value {
  font-size: 24px;
  font-weight: bold;
  color: #333;
  margin-bottom: 5px;
}

.stat-item {
  display: flex;
  align-items: center;
  gap: 5px;
}

.stat-label {
  font-size: 14px;
  color: #666;
}

.stat-value {
  font-size: 16px;
  font-weight: bold;
  color: #333;
}

.index-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.index-main {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.index-value {
  font-size: 36px;
  font-weight: bold;
  color: #333;
}

.index-change {
  font-size: 18px;
  font-weight: bold;
}

.index-change.positive {
  color: #F56C6C;
}

.index-change.negative {
  color: #67C23A;
}

.index-volume {
  font-size: 14px;
  color: #666;
}

.index-limits {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.limit-item {
  display: flex;
  align-items: center;
  gap: 10px;
}

.limit-label {
  font-size: 14px;
  color: #666;
  min-width: 80px;
}

.limit-stocks {
  font-size: 14px;
  color: #333;
  font-weight: 500;
}

@media (max-width: 768px) {
  .index-content {
    flex-direction: column;
    gap: 20px;
    align-items: flex-start;
  }
  
  .index-stats {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 20px;
  }
}
</style>