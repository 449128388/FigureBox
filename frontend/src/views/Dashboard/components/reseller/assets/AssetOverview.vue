<template>
  <div class="asset-overview">
    <div class="overview-item">
      <span class="label">总资产:</span>
      <span class="value">¥{{ formatNumber(dashboardData?.summary?.total_assets || 128500) }}</span>
    </div>
    <div class="overview-item">
      <span class="label">日涨跌:</span>
      <span 
        class="value" 
        :class="{ 
          positive: dashboardData?.summary?.has_daily_change && dashboardData?.summary?.daily_change >= 0, 
          negative: dashboardData?.summary?.has_daily_change && dashboardData?.summary?.daily_change < 0 
        }"
      >
        <template v-if="dashboardData?.summary?.has_daily_change">
          {{ dashboardData?.summary?.daily_change >= 0 ? '+' : '' }}¥{{ formatNumber(Math.abs(dashboardData?.summary?.daily_change || 0)) }}({{ dashboardData?.summary?.daily_change >= 0 ? '+' : '' }}{{ (dashboardData?.summary?.daily_change_percentage || 0).toFixed(2) }}%)
        </template>
        <template v-else>
          -- (--%)
        </template>
      </span>
    </div>
    <div class="overview-item">
      <span class="label">仓位:</span>
      <span 
        class="value position-value"
        :class="'position-' + (dashboardData?.summary?.position_color || 'red')"
      >
        {{ dashboardData?.summary?.position || '满仓' }}
        <template v-if="dashboardData?.summary?.position_percentage !== undefined">
          ({{ dashboardData?.summary?.position_percentage }}%)
        </template>
      </span>
    </div>
  </div>
</template>

<script>
export default {
  name: 'AssetOverview',
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

.overview-item .value.positive {
  color: #4CAF50;
}

.overview-item .value.negative {
  color: #F44336;
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