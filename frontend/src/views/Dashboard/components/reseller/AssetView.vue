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
      @edit-price="handleEditPrice"
    />

    <!-- 修改市场价弹窗 -->
    <PriceUpdateDialog
      ref="priceUpdateDialog"
      @update-success="handlePriceUpdateSuccess"
    />
  </div>
</template>

<script>
import { ref } from 'vue'
import AssetOverview from './assets/AssetOverview.vue'
import IndexComparison from './assets/IndexComparison.vue'
import ChartSection from './assets/ChartSection.vue'
import ProfitAnalysis from './assets/ProfitAnalysis.vue'
import HoldingsList from './assets/HoldingsList.vue'
import PriceUpdateDialog from './assets/PriceUpdateDialog.vue'

export default {
  name: 'AssetView',
  components: {
    AssetOverview,
    IndexComparison,
    ChartSection,
    ProfitAnalysis,
    HoldingsList,
    PriceUpdateDialog
  },
  props: {
    dashboardData: {
      type: Object,
      default: () => ({})
    }
  },
  emits: ['sell-asset', 'add-position', 'cut-loss', 'edit-price', 'refresh-data'],
  setup(props, { emit }) {
    const priceUpdateDialog = ref(null)

    // 处理修改市场价事件
    const handleEditPrice = (item) => {
      if (priceUpdateDialog.value) {
        priceUpdateDialog.value.openDialog(item)
      }
    }

    // 处理价格更新成功
    const handlePriceUpdateSuccess = (result) => {
      // 触发刷新数据事件
      emit('refresh-data')
      // 同时触发原有的edit-price事件以保持兼容性
      emit('edit-price', result)
    }

    return {
      priceUpdateDialog,
      handleEditPrice,
      handlePriceUpdateSuccess
    }
  }
}
</script>

<style scoped>
.asset-view {
  width: 100%;
}
</style>