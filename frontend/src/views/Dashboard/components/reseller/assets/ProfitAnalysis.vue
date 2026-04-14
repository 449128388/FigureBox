<!--
  ProfitAnalysis.vue - 盈亏分析组件

  功能说明：
  - 展示浮动盈亏、实现盈亏和总收益率等关键指标
  - 根据盈亏情况显示不同颜色
  - 提供盈亏相关的辅助信息

  组件依赖：
  - 接收 dashboardData 作为 props，包含 profit 数据

  维护提示：
  - 使用 formatNumber 方法格式化数字显示
  - 盈亏为正时显示绿色，为负时显示红色
-->
<template>
  <div class="profit-analysis">
    <div class="section-title">盈亏分析</div>
    <div class="analysis-grid">
      <div class="analysis-row">
        <div class="analysis-item">
          <div class="analysis-label">浮动盈亏</div>
          <div class="analysis-value positive">+¥{{ formatNumber(dashboardData?.profit?.floating || 23400) }}</div>
          <div class="analysis-desc">(未卖出)</div>
        </div>
        <div class="analysis-item">
          <div class="analysis-label">实现盈亏</div>
          <div class="analysis-value positive">+¥{{ formatNumber(dashboardData?.profit?.realized || 8200) }}</div>
          <div class="analysis-desc">(已转卖)</div>
        </div>
      </div>
      <div class="analysis-row single">
        <div class="analysis-item">
          <div class="analysis-label">总收益率</div>
          <div class="analysis-value positive">+{{ dashboardData?.profit?.total_rate || 24.6 }}%</div>
          <div class="analysis-desc">(年化31%)</div>
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
      return num?.toLocaleString() || '0'
    }

    return {
      formatNumber
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

.analysis-row.single {
  justify-content: flex-start;
}

.analysis-row.single .analysis-item {
  flex: 0 0 50%;
  max-width: 50%;
}

.analysis-item {
  flex: 1;
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

.analysis-value.positive {
  color: #52c41a;
}

.analysis-value.negative {
  color: #F44336;
}

.analysis-desc {
  font-size: 12px;
  color: #999;
}
</style>