<!--
  AssetOverview.vue - 资产概览组件

  功能说明：
  - 展示总市值、日涨跌、仓位等核心资产指标
  - 根据涨跌情况显示不同颜色
  - 仓位状态根据风险等级显示不同样式
  - 使用 DailyChangeDisplay 组件展示日涨跌

  组件依赖：
  - 接收 dashboardData 作为 props，包含 summary 数据
  - DailyChangeDisplay 组件用于展示日涨跌

  维护提示：
  - 使用 formatNumber 方法格式化数字显示
  - 日涨跌和仓位状态通过条件样式展示
-->
<template>
  <div class="asset-overview">
    <div class="overview-item">
      <span class="label" style="margin-bottom: 10px;">总市值:</span>
      <span class="value">¥{{ formatNumber(dashboardData?.summary?.total_market_value || 0) }}</span>
    </div>
    <div class="overview-item">
      <span class="label">日涨跌:</span>
      <DailyChangeDisplay
        :daily-change="dashboardData?.summary?.daily_change || 0"
        :daily-change-percentage="dashboardData?.summary?.daily_change_percentage || 0"
        :has-daily-change="dashboardData?.summary?.has_daily_change || false"
        :comparison-date="dashboardData?.summary?.comparison_date"
        :comparison-type="dashboardData?.summary?.comparison_type"
        :days-since-last-update="dashboardData?.summary?.days_since_last_update"
        :show-stale-warning="dashboardData?.summary?.show_stale_warning || false"
      />
    </div>
    <div class="overview-item">
      <span class="label">仓位:</span>
      <span
        class="value position-value"
        :class="'position-' + (dashboardData?.summary?.position_color || 'red')"
      >
        {{ dashboardData?.summary?.position || '满仓' }}
        <template v-if="dashboardData?.summary?.position_percentage !== undefined">
          ({{ formatNumber(dashboardData?.summary?.invested_cost || 0) }}/{{ dashboardData?.summary?.position_percentage }}%)
        </template>
      </span>
    </div>
  </div>
</template>

<script>
import DailyChangeDisplay from './DailyChangeDisplay.vue'

export default {
  name: 'AssetOverview',
  components: {
    DailyChangeDisplay
  },
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
.asset-overview {
  display: flex;
  gap: 30px;
  margin-bottom: 20px;
  padding: 20px;
  background-color: white;
  border-radius: 8px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
}

.overview-item {
  display: flex;
  flex-direction: column;
}

.overview-item .label {
  font-size: 14px;
  color: #666;
  margin-bottom: 5px;
}

.overview-item .value {
  font-size: 24px;
  font-weight: bold;
  color: #333;
}

/* 仓位状态颜色 */
.position-value.position-gray {
  color: #909399;
  font-weight: bold;
}

.position-value.position-blue {
  color: #409EFF;
  font-weight: bold;
}

.position-value.position-green {
  color: #67C23A;
  font-weight: bold;
}

.position-value.position-yellow {
  color: #E6A23C;
  font-weight: bold;
}

.position-value.position-red {
  color: #F56C6C;
  font-weight: bold;
}

.position-value.position-black {
  color: #303133;
  font-weight: bold;
  background-color: #F2F6FC;
  padding: 2px 8px;
  border-radius: 4px;
}
</style>
