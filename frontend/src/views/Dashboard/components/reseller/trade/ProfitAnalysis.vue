<!--
  ProfitAnalysis.vue - 交易盈亏分析组件

  功能说明：
  - 展示交易相关的盈亏分析报表
  - 包含本年已实现收益、本年交易胜率、平均盈利、平均亏损等指标
  - 显示最大单笔盈利和最大单笔亏损
  - 根据盈亏情况显示不同颜色

  组件依赖：
  - 接收 displayTradeData 作为 props，包含 profit_analysis 数据
  - 接收 formatNumber 作为 props 用于数字格式化

  维护提示：
  - 盈亏为正时显示绿色，为负时显示红色
  - 使用 Math.abs 处理负值显示
-->
<template>
  <div class="profit-analysis">
    <h4>📊 盈亏分析报表</h4>
    <div class="analysis-grid">
      <div class="analysis-item">
        <div class="analysis-label">本年已实现收益</div>
        <div class="analysis-value" :class="{ positive: displayTradeData?.profit_analysis?.yearly_profit >= 0, negative: displayTradeData?.profit_analysis?.yearly_profit < 0 }">
          {{ displayTradeData?.profit_analysis?.yearly_profit >= 0 ? '+' : '' }}¥{{ formatNumber(Math.abs(displayTradeData?.profit_analysis?.yearly_profit || 0)) }}
        </div>
      </div>
      <div class="analysis-item">
        <div class="analysis-label">本年交易胜率</div>
        <div class="analysis-value">
          {{ displayTradeData?.profit_analysis?.win_rate || 0 }}% ({{ displayTradeData?.profit_analysis?.win_count || 0 }}胜{{ displayTradeData?.profit_analysis?.loss_count || 0 }}负)
        </div>
      </div>
      <div class="analysis-item">
        <div class="analysis-label">平均盈利</div>
        <div class="analysis-value positive">+¥{{ formatNumber(displayTradeData?.profit_analysis?.avg_profit || 0) }}/笔</div>
      </div>
      <div class="analysis-item">
        <div class="analysis-label">平均亏损</div>
        <div class="analysis-value negative">-¥{{ formatNumber(displayTradeData?.profit_analysis?.avg_loss || 0) }}/笔</div>
      </div>
      <div class="analysis-item full-width">
        <div class="analysis-label">最大单笔盈利</div>
        <div class="analysis-value positive">{{ displayTradeData?.profit_analysis?.max_profit_item || '' }} +¥{{ formatNumber(displayTradeData?.profit_analysis?.max_profit || 0) }}</div>
      </div>
      <div class="analysis-item full-width">
        <div class="analysis-label">最大单笔亏损</div>
        <div class="analysis-value negative">{{ displayTradeData?.profit_analysis?.max_loss_item || '' }} -¥{{ formatNumber(displayTradeData?.profit_analysis?.max_loss || 0) }}</div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'ProfitAnalysis',
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
/* 盈亏分析 */
.profit-analysis {
  background-color: #f9f9f9;
  padding: 20px;
  border-radius: 8px;
  border: 1px solid #e0e0e0;
  margin-bottom: 30px;
  text-align: center;
}

.profit-analysis h4 {
  margin-bottom: 20px;
  color: #333;
  font-size: 16px;
  font-weight: bold;
  text-align: center;
}

.analysis-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 20px;
}

.analysis-item {
  background-color: white;
  padding: 15px;
  border-radius: 6px;
  border: 1px solid #e0e0e0;
  text-align: center;
}

.analysis-item.full-width {
  grid-column: 1 / -1;
}

.analysis-label {
  font-size: 14px;
  color: #666;
  margin-bottom: 5px;
  text-align: center;
}

.analysis-value {
  font-size: 18px;
  font-weight: bold;
  text-align: center;
}

.analysis-value.positive {
  color: #67c23a;
}

.analysis-value.negative {
  color: #f56c6c;
}

@media (max-width: 1200px) {
  .analysis-grid {
    grid-template-columns: 1fr;
  }
}
</style>