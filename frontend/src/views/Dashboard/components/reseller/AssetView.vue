<!--
  AssetView.vue - 倒狗模式资产模块组件

  功能说明：
  - 整合资产相关的所有子组件
  - 包含资产概览、指数对比、资产分布、收益曲线、盈亏分析、持仓列表
  - 处理资产操作事件（卖出、加仓、止损、修改价格）

  组件依赖：
  - AssetOverview.vue - 资产概览组件
  - IndexComparison.vue - 指数对比组件
  - ChartSection.vue - 资产分布和收益曲线组件
  - ProfitAnalysis.vue - 盈亏分析组件
  - HoldingsList.vue - 持仓列表组件
  - PriceUpdateDialog.vue - 修改市场价弹窗
  - AddPositionDialog.vue - 补仓弹窗
  - QuickSellDialog.vue - 快速卖出弹窗

  维护提示：
  - 接收 dashboardData 作为 props
  - 通过事件向父组件传递操作
  - 价格更新通过 PriceUpdateDialog 组件处理
  - 补仓通过 AddPositionDialog 组件处理
  - 快速卖出通过 QuickSellDialog 组件处理
-->
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
      @sell-asset="handleQuickSell"
      @add-position="handleAddPosition"
      @cut-loss="$emit('cut-loss', $event)"
      @edit-price="handleEditPrice"
    />

    <!-- 修改市场价弹窗 -->
    <PriceUpdateDialog
      ref="priceUpdateDialog"
      @update-success="handlePriceUpdateSuccess"
    />

    <!-- 补仓弹窗 -->
    <AddPositionDialog
      ref="addPositionDialog"
      @add-success="handleAddPositionSuccess"
    />

    <!-- 快速卖出弹窗 -->
    <QuickSellDialog
      ref="quickSellDialog"
      @sell-success="handleQuickSellSuccess"
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
import AddPositionDialog from './assets/AddPositionDialog.vue'
import QuickSellDialog from './assets/QuickSellDialog.vue'

export default {
  name: 'AssetView',
  components: {
    AssetOverview,
    IndexComparison,
    ChartSection,
    ProfitAnalysis,
    HoldingsList,
    PriceUpdateDialog,
    AddPositionDialog,
    QuickSellDialog
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
    const addPositionDialog = ref(null)
    const quickSellDialog = ref(null)

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

    // 处理补仓事件
    const handleAddPosition = (item) => {
      if (addPositionDialog.value) {
        addPositionDialog.value.openDialog(item)
      }
    }

    // 处理补仓成功
    const handleAddPositionSuccess = (result) => {
      // 触发刷新数据事件
      emit('refresh-data')
      // 同时触发原有的add-position事件以保持兼容性
      emit('add-position', result)
    }

    // 处理快速卖出事件
    const handleQuickSell = (item) => {
      if (quickSellDialog.value) {
        quickSellDialog.value.openDialog(item)
      }
    }

    // 处理快速卖出成功
    const handleQuickSellSuccess = (result) => {
      // 触发刷新数据事件
      emit('refresh-data')
      // 同时触发原有的sell-asset事件以保持兼容性
      emit('sell-asset', result)
    }

    return {
      priceUpdateDialog,
      addPositionDialog,
      quickSellDialog,
      handleEditPrice,
      handlePriceUpdateSuccess,
      handleAddPosition,
      handleAddPositionSuccess,
      handleQuickSell,
      handleQuickSellSuccess
    }
  }
}
</script>

<style scoped>
.asset-view {
  width: 100%;
}
</style>