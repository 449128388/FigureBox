<template>
  <div class="asset-view">
    <!-- 资产概览区 -->
    <AssetOverview :dashboardData="dashboardData" />

    <!-- 指数对比 -->
    <IndexComparison :dashboardData="dashboardData" />

    <!-- 资产分布和收益曲线 -->
    <ChartSection :dashboardData="dashboardData" />

    <!-- 盈亏分析 -->
    <ProfitAnalysis :dashboardData="dashboardData" />

    <!-- 持仓列表 -->
    <HoldingsList 
      :dashboardData="dashboardData"
      @sell-asset="$emit('sell-asset', $event)"
      @add-position="$emit('add-position', $event)"
      @cut-loss="$emit('cut-loss', $event)"
      @edit-price="$emit('edit-price', $event)"
    />
  </div>
</template>

<script>
import AssetOverview from './assets/AssetOverview.vue'
import IndexComparison from './assets/IndexComparison.vue'
import ChartSection from './assets/ChartSection.vue'
import ProfitAnalysis from './assets/ProfitAnalysis.vue'
import HoldingsList from './assets/HoldingsList.vue'

export default {
  name: 'AssetView',
  components: {
    AssetOverview,
    IndexComparison,
    ChartSection,
    ProfitAnalysis,
    HoldingsList
  },
  props: {
    dashboardData: {
      type: Object,
      default: () => ({})
    }
  },
  emits: ['sell-asset', 'add-position', 'cut-loss', 'edit-price']
}
</script>

<style scoped>
.asset-view {
  width: 100%;
}
</style>