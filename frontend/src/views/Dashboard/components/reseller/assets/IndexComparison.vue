<!--
  IndexComparison.vue - 指数对比组件

  功能说明：
  - 展示上证指数、沪深300、塑料小人指数的对比数据
  - 根据指数涨跌显示不同方向和颜色
  - 无历史数据时显示默认值

  组件依赖：
  - 接收 dashboardData 作为 props，包含 summary 数据

  维护提示：
  - 指数趋势通过 trend 属性判断（up/down/flat）
  - 无历史数据时显示 --
-->
<template>
  <div class="index-comparison">
    <!-- 上证指数 -->
    <div class="index-item">
      <span class="label">上证指数:</span>
      <span class="value">{{ dashboardData?.summary?.sh_index_comparison?.current_value || dashboardData?.summary?.sh_index || 3200 }}</span>
      <span 
        v-if="dashboardData?.summary?.sh_index_comparison?.has_history"
        class="index-change"
        :class="{
          up: dashboardData?.summary?.sh_index_comparison?.trend === 'up',
          down: dashboardData?.summary?.sh_index_comparison?.trend === 'down',
          flat: dashboardData?.summary?.sh_index_comparison?.trend === 'flat'
        }"
      >
        <template v-if="dashboardData?.summary?.sh_index_comparison?.trend === 'up'">
          ▲{{ dashboardData?.summary?.sh_index_comparison?.change_percentage }}%
        </template>
        <template v-else-if="dashboardData?.summary?.sh_index_comparison?.trend === 'down'">
          ▼{{ Math.abs(dashboardData?.summary?.sh_index_comparison?.change_percentage) }}%
        </template>
        <template v-else>
          -{{ dashboardData?.summary?.sh_index_comparison?.change_percentage }}%
        </template>
      </span>
      <span v-else class="index-change no-history">--</span>
    </div>
    
    <!-- 沪深300 -->
    <div class="index-item">
      <span class="label">沪深300:</span>
      <span class="value">{{ dashboardData?.summary?.hs300_index_comparison?.current_value || dashboardData?.summary?.hs300_index || 4000 }}</span>
      <span 
        v-if="dashboardData?.summary?.hs300_index_comparison?.has_history"
        class="index-change"
        :class="{
          up: dashboardData?.summary?.hs300_index_comparison?.trend === 'up',
          down: dashboardData?.summary?.hs300_index_comparison?.trend === 'down',
          flat: dashboardData?.summary?.hs300_index_comparison?.trend === 'flat'
        }"
      >
        <template v-if="dashboardData?.summary?.hs300_index_comparison?.trend === 'up'">
          ▲{{ dashboardData?.summary?.hs300_index_comparison?.change_percentage }}%
        </template>
        <template v-else-if="dashboardData?.summary?.hs300_index_comparison?.trend === 'down'">
          ▼{{ Math.abs(dashboardData?.summary?.hs300_index_comparison?.change_percentage) }}%
        </template>
        <template v-else>
          -{{ dashboardData?.summary?.hs300_index_comparison?.change_percentage }}%
        </template>
      </span>
      <span v-else class="index-change no-history">--</span>
    </div>
    
    <!-- 塑料手办指数 -->
    <div class="index-item">
      <span class="label">塑料手办指数:</span>
      <span class="value">{{ dashboardData?.summary?.plastic_index || '--' }}</span>
    </div>
    
    <!-- 跑赢/跑输大盘 - 仅当有手办时显示 -->
    <div class="index-item" v-if="dashboardData?.summary?.has_figures">
      <span
        class="value"
        :class="{
          'a-up': (dashboardData?.summary?.outperform_percentage || 0) > 0,
          'a-down': (dashboardData?.summary?.outperform_percentage || 0) < 0,
          neutral: (dashboardData?.summary?.outperform_percentage || 0) === 0
        }"
      >
        <template v-if="(dashboardData?.summary?.outperform_percentage || 0) > 0">
          🔴 跑赢大盘+{{ dashboardData?.summary?.outperform_percentage }}%
        </template>
        <template v-else-if="(dashboardData?.summary?.outperform_percentage || 0) < 0">
          🟢 跑输大盘{{ dashboardData?.summary?.outperform_percentage }}%
        </template>
        <template v-else>
          ➖ 持平
        </template>
      </span>
    </div>
  </div>
</template>

<script>
export default {
  name: 'IndexComparison',
  props: {
    dashboardData: {
      type: Object,
      default: () => ({})
    }
  }
}
</script>

<style scoped>
.index-comparison {
  display: flex;
  gap: 30px;
  margin-bottom: 20px;
  padding: 20px;
  background-color: white;
  border-radius: 8px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
}

.index-item {
  display: flex;
  align-items: center;
  gap: 10px;
}

.index-item .label {
  font-size: 18px;
  color: #666;
}

.index-item .value {
  font-size: 18px;
  font-weight: bold;
  color: #333;
}

.index-item .value.positive {
  color: #4CAF50;
}

/* 指数涨跌样式 */
.index-item .index-change {
  font-size: 18px;
  font-weight: bold;
  margin: 0 5px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
}

.index-item .index-change.up {
  color: #F56C6C;
}

.index-item .index-change.down {
  color: #67C23A;
}

.index-item .index-change.flat {
  color: #909399;
}

.index-item .index-change.no-history {
  color: #C0C4CC;
  font-weight: normal;
}

/* A股风格颜色 */
.index-item .value.a-up {
  color: #F56C6C;
}

.index-item .value.a-down {
  color: #67C23A;
}
</style>