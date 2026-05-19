<!--
  ProfitAnalysis.vue - 盈亏分析组件

  功能说明：
  - 展示盈亏分析六宫格：浮动盈亏、实现盈亏、变现率、总收益率、年化收益率、最大回撤
  - 根据盈亏情况显示不同颜色
  - 提供盈亏相关的辅助信息

  组件依赖：
  - 接收 dashboardData 作为 props，包含 profit 数据

  维护提示：
  - 使用 formatNumber 方法格式化数字显示
  - 盈亏为正时显示红色，为负时显示绿色（中国股市标准）
-->
<template>
  <div class="profit-analysis">
    <div class="section-title">盈亏分析</div>
    <div class="analysis-grid">
      <!-- 第一行：浮动盈亏、实现盈亏、变现率 -->
      <div class="analysis-row">
        <div class="analysis-item">
          <div class="analysis-label">浮动盈亏</div>
          <div :class="['analysis-value', getValueClass(dashboardData?.profit?.floating)]">
            {{ getValuePrefix(dashboardData?.profit?.floating) }}¥{{ formatNumber(Math.abs(dashboardData?.profit?.floating || 0)) }}
          </div>
          <div class="analysis-desc">(未卖出)</div>
        </div>
        <div class="analysis-item">
          <div class="analysis-label">实现盈亏</div>
          <div :class="['analysis-value', getValueClass(dashboardData?.profit?.realized)]">
            {{ getValuePrefix(dashboardData?.profit?.realized) }}¥{{ formatNumber(Math.abs(dashboardData?.profit?.realized || 0)) }}
          </div>
          <div class="analysis-desc">(已转卖)</div>
        </div>
        <div class="analysis-item">
          <div class="analysis-label">变现率</div>
          <div class="analysis-value">
            <div class="progress-bar">
              <div class="progress-fill" :style="{ width: Math.abs(dashboardData?.profit?.realization_rate || 0) + '%' }"></div>
            </div>
            <span class="progress-text">{{ formatNumber(Math.abs(dashboardData?.profit?.realization_rate || 0)) }}%</span>
          </div>
          <div class="analysis-desc">(落袋为安)</div>
        </div>
      </div>
      <!-- 第二行：总收益率、年化收益率、最大回撤 -->
      <div class="analysis-row">
        <div class="analysis-item">
          <div class="analysis-label">总收益率</div>
          <div :class="['analysis-value', getValueClass(dashboardData?.profit?.total_rate)]">
            {{ getValuePrefix(dashboardData?.profit?.total_rate) }}{{ formatNumber(Math.abs(dashboardData?.profit?.total_rate || 0)) }}%
          </div>
          <div class="analysis-desc">(整体回报率)</div>
        </div>
        <div class="analysis-item">
          <div class="analysis-label">年化收益率</div>
          <div :class="['analysis-value', getValueClass(dashboardData?.profit?.annualized_rate)]">
            {{ getValuePrefix(dashboardData?.profit?.annualized_rate) }}{{ formatNumber(Math.abs(dashboardData?.profit?.annualized_rate || 0)) }}%
          </div>
          <div class="analysis-desc">(消除时间差异)</div>
        </div>
        <div class="analysis-item">
          <div class="analysis-label">最大回撤</div>
          <div :class="['analysis-value', getDrawdownClass(dashboardData?.profit?.max_drawdown)]">
            {{ formatNumber(dashboardData?.profit?.max_drawdown || 0) }}%
          </div>
          <div class="analysis-desc">(最惨时刻)</div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'ProfitAnalysis',
  props: {
    dashboardData: {
      type: Object,
      default: () => ({})
    }
  },
  setup() {
    const formatNumber = (num) => {
      if (num === null || num === undefined) return '0'
      return Number(num).toLocaleString('zh-CN', { minimumFractionDigits: 2, maximumFractionDigits: 2 })
    }

    const getValueClass = (value) => {
      if (value === null || value === undefined) return ''
      return value >= 0 ? 'positive' : 'negative'
    }

    const getValuePrefix = (value) => {
      if (value === null || value === undefined) return ''
      return value >= 0 ? '+' : '-'
    }

    // 最大回撤特殊处理：负值表示亏损，显示绿色；正值表示盈利，显示红色
    const getDrawdownClass = (value) => {
      if (value === null || value === undefined) return ''
      // 最大回撤为负值表示回撤（亏损），显示绿色；为正值表示异常，显示红色
      return value <= 0 ? 'positive' : 'negative'
    }

    return {
      formatNumber,
      getValueClass,
      getValuePrefix,
      getDrawdownClass
    }
  }
}
</script>

<style scoped>
.profit-analysis {
  margin-bottom: 20px;
  background-color: white;
  border-radius: 8px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
  padding: 20px;
}

.analysis-grid {
  display: flex;
  flex-direction: column;
  gap: 15px;
  margin-top: 15px;
}

.analysis-row {
  display: flex;
  gap: 15px;
}

.analysis-row .analysis-item {
  flex: 1;
}

.analysis-item {
  text-align: center;
  padding: 15px;
  background-color: #fafafa;
  border-radius: 6px;
  border: 1px solid #e8e8e8;
}

.analysis-label {
  font-size: 14px;
  color: #666;
  margin-bottom: 8px;
}

.analysis-value {
  font-size: 22px;
  font-weight: bold;
  margin-bottom: 5px;
}

/* 中国股市颜色标准：涨红跌绿 */
.analysis-value.positive {
  color: #F44336; /* 红色 - 盈利 */
}

.analysis-value.negative {
  color: #4CAF50; /* 绿色 - 亏损 */
}

.analysis-desc {
  font-size: 12px;
  color: #999;
}

/* 进度条样式 */
.progress-bar {
  width: 80px;
  height: 12px;
  background-color: #e0e0e0;
  border-radius: 6px;
  overflow: hidden;
  display: inline-block;
  vertical-align: middle;
  margin-right: 8px;
}

.progress-fill {
  height: 100%;
  background: linear-gradient(90deg, #4CAF50 0%, #8BC34A 100%);
  border-radius: 6px;
  transition: width 0.3s ease;
}

.progress-text {
  font-size: 18px;
  vertical-align: middle;
}
</style>
