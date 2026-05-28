<!--
  TradeView.vue - 倒狗模式交易模块组件

  功能说明：
  - 整合交易相关的所有子组件
  - 包含交易统计、快速操作、交易流水、盈亏分析报表
  - 处理交易相关的操作事件

  组件依赖：
  - MonthSelector.vue - 月份切换器组件
  - TradeStats.vue - 交易统计组件
  - QuickActions.vue - 快速操作组件
  - TradeFlow.vue - 交易流水组件
  - ProfitAnalysis.vue - 盈亏分析组件

  维护提示：
  - 接收 displayTradeData、tradeData 等作为 props
  - 通过事件向父组件传递操作
  - 提供 formatNumber 方法给子组件使用
-->
<template>
  <div class="trade-view">
    <!-- 月份切换器 -->
    <MonthSelector
      v-model="currentMonth"
      @change="handleMonthChange"
    />

    <!-- 本月交易统计 -->
    <TradeStats
      :displayTradeData="displayTradeData"
      :formatNumber="formatNumber"
    />

    <!-- 快速操作 -->
    <QuickActions
      @open-buy-dialog="$emit('open-buy-dialog')"
      @open-sell-dialog="$emit('open-sell-dialog')"
      @open-payment-dialog="$emit('open-payment-dialog')"
      @open-cancel-dialog="$emit('open-cancel-dialog')"
    />

    <!-- 盈亏分析报表 -->
    <ProfitAnalysis
      :displayTradeData="displayTradeData"
      :formatNumber="formatNumber"
    />

    <!-- 交易流水 -->
    <TradeFlow
      :tradeData="tradeData"
      :formatNumber="formatNumber"
      @handle-trade-action="handleTradeAction"
    />
  </div>
</template>

<script>
import { computed, ref, watch } from 'vue'
import MonthSelector from './trade/MonthSelector.vue'
import TradeStats from './trade/TradeStats.vue'
import QuickActions from './trade/QuickActions.vue'
import TradeFlow from './trade/TradeFlow.vue'
import ProfitAnalysis from './trade/ProfitAnalysis.vue'

export default {
  name: 'TradeView',
  components: {
    MonthSelector,
    TradeStats,
    QuickActions,
    TradeFlow,
    ProfitAnalysis
  },
  props: {
    tradeData: {
      type: Object,
      default: () => ({})
    },
    selectedMonth: {
      type: Object,
      default: () => ({
        year: new Date().getFullYear(),
        month: new Date().getMonth() + 1
      })
    }
  },
  emits: ['open-buy-dialog', 'open-sell-dialog', 'open-payment-dialog', 'open-cancel-dialog', 'view-record', 'delete-record', 'month-change'],
  setup(props, { emit }) {
    const formatNumber = (num) => {
      return num?.toLocaleString() || '0'
    }
    
    const handleTradeAction = (action, record) => {
      // 处理交易操作

    }

    // 当前月份（与父组件同步）
    const currentMonth = ref({ ...props.selectedMonth })

    // 监听父组件传入的月份变化
    watch(() => props.selectedMonth, (newVal) => {
      currentMonth.value = { ...newVal }
    }, { deep: true })

    // 处理月份切换
    const handleMonthChange = (newMonth) => {
      emit('month-change', newMonth)
    }

    // 计算显示的交易数据
    const displayTradeData = computed(() => {
      return props.tradeData || {}
    })

    return {
      formatNumber,
      handleTradeAction,
      displayTradeData,
      currentMonth,
      handleMonthChange
    }
  }
}
</script>

<style scoped>
.trade-view {
  width: 100%;
}
</style>