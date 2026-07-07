<!--
  MarketView.vue - 倒狗模式行情模块组件

  功能说明：
  - 整合行情相关的所有子组件
  - 包含塑料小人指数(HPI)详情、K线图、成分股列表

  组件依赖：
  - HPIDetail.vue - 塑料小人指数详情组件（K线+成分股）
-->
<template>
  <div class="market-view">
    <div class="market-section">
      <!-- 塑料小人指数详情 -->
      <HPIDetail :marketData="marketData" />
    </div>
  </div>
</template>

<script>
import HPIDetail from './market/HPIDetail.vue'

export default {
  name: 'MarketView',
  components: {
    HPIDetail
  },
  props: {
    marketData: {
      type: Object,
      default: () => ({})
    }
  }
}
</script>

<style scoped>
.market-view { width: 100%; }
.market-section { padding: 20px; background-color: white; border-radius: 8px; box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1); }
</style>
