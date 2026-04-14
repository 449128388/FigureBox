<!--
  MarketView.vue - 倒狗模式行情模块组件

  功能说明：
  - 整合行情相关的所有子组件
  - 包含塑料小人指数、K线图、板块涨幅排行、自选股、智能投研
  - 提供市场数据的集中展示

  组件依赖：
  - MarketIndex.vue - 塑料小人指数组件
  - KlineSection.vue - K线图组件
  - SectorRanking.vue - 板块涨幅排行组件
  - WatchlistSection.vue - 自选股组件
  - ResearchSection.vue - 智能投研组件

  维护提示：
  - 接收 marketData 作为 props
  - 所有子组件通过 props 接收数据
-->
<template>
  <div class="market-view">
    <div class="market-section">
      <!-- 塑料小人指数 -->
      <MarketIndex :marketData="marketData" />

      <!-- K线图 -->
      <KlineSection :marketData="marketData" />

      <!-- 板块涨幅排行 -->
      <SectorRanking :marketData="marketData" />

      <!-- 自选股 -->
      <WatchlistSection :marketData="marketData" />

      <!-- 智能投研 -->
      <ResearchSection :marketData="marketData" />
    </div>
  </div>
</template>

<script>
import MarketIndex from './market/MarketIndex.vue'
import KlineSection from './market/KlineSection.vue'
import SectorRanking from './market/SectorRanking.vue'
import WatchlistSection from './market/WatchlistSection.vue'
import ResearchSection from './market/ResearchSection.vue'

export default {
  name: 'MarketView',
  components: {
    MarketIndex,
    KlineSection,
    SectorRanking,
    WatchlistSection,
    ResearchSection
  },
  props: {
    marketData: {
      type: Object,
      default: () => ({})
    }
  },
  emits: ['add-watchlist']
}
</script>

<style scoped>
.market-view {
  width: 100%;
}

.market-section {
  padding: 20px;
  background-color: white;
  border-radius: 8px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
}

/* 塑料小人指数 */
.market-index {
  margin-bottom: 30px;
  padding: 20px;
  background-color: #f5f5f5;
  border-radius: 8px;
}

.index-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  padding-bottom: 15px;
  border-bottom: 1px solid #e0e0e0;
}

.index-header h3 {
  margin: 0;
  font-size: 18px;
  color: #333;
}

.index-stats {
  display: flex;
  gap: 20px;
}

.index-stats .stat-item {
  background-color: #f9f9f9;
  padding: 20px;
  border-radius: 8px;
  text-align: center;
  border: 1px solid #e0e0e0;
}

.index-stats .stat-label {
  font-size: 14px;
  color: #666;
  margin-bottom: 5px;
}

.index-stats .stat-value {
  font-size: 24px;
  font-weight: bold;
  color: #333;
  margin-bottom: 5px;
}

.stat-item {
  display: flex;
  align-items: center;
  gap: 5px;
}

.stat-label {
  font-size: 14px;
  color: #666;
}

.stat-value {
  font-size: 16px;
  font-weight: bold;
  color: #333;
}

.index-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.index-main {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.index-value {
  font-size: 36px;
  font-weight: bold;
  color: #333;
}

.index-change {
  font-size: 18px;
  font-weight: bold;
}

.index-change.positive {
  color: #F56C6C;
}

.index-change.negative {
  color: #67C23A;
}

.index-volume {
  font-size: 14px;
  color: #666;
}

.index-limits {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.limit-item {
  display: flex;
  align-items: center;
  gap: 10px;
}

.limit-label {
  font-size: 14px;
  color: #666;
  min-width: 80px;
}

.limit-stocks {
  font-size: 14px;
  color: #333;
  font-weight: 500;
}

/* K线图 */
.kline-section {
  margin-bottom: 30px;
}

.kline-header {
  margin-bottom: 15px;
}

.kline-tabs {
  display: flex;
  gap: 10px;
}

.kline-tabs .el-button.active {
  background-color: #4CAF50;
  color: white;
}

.kline-chart-container {
  position: relative;
  background-color: #f5f5f5;
  border-radius: 8px;
  padding: 20px;
}

.kline-chart {
  width: 100%;
  height: 300px;
  margin-bottom: 15px;
  background: linear-gradient(to bottom, #f0f9ff 0%, #ffffff 100%);
  border-radius: 4px;
  overflow: hidden;
}

.kline-indicators {
  display: flex;
  gap: 30px;
  margin-top: 15px;
  padding-top: 15px;
  border-top: 1px solid #e0e0e0;
}

.indicator-item {
  display: flex;
  align-items: center;
  gap: 10px;
}

.indicator-label {
  font-size: 14px;
  color: #666;
}

.indicator-value {
  font-size: 14px;
  font-weight: bold;
  color: #333;
}

.indicator-value.warning {
  color: #E6A23C;
}

/* 板块涨幅排行 */
.sector-ranking {
  margin-bottom: 30px;
}

.section-title {
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 18px;
  font-weight: bold;
  margin-bottom: 15px;
  color: #333;
}

.sector-list {
  background-color: #f5f5f5;
  border-radius: 8px;
  padding: 20px;
}

.sector-item {
  display: flex;
  align-items: center;
  margin-bottom: 15px;
  padding-bottom: 15px;
  border-bottom: 1px solid #e0e0e0;
}

.sector-item:last-child {
  margin-bottom: 0;
  padding-bottom: 0;
  border-bottom: none;
}

.sector-rank {
  width: 40px;
  font-size: 18px;
  font-weight: 600;
  color: #666;
  margin-right: 15px;
}

.sector-info {
  flex: 1;
}

.sector-name {
  font-size: 16px;
  font-weight: 500;
  color: #333;
  margin-bottom: 5px;
}

.sector-stocks {
  font-size: 14px;
  color: #666;
}

.sector-change {
  font-size: 16px;
  font-weight: 600;
  min-width: 80px;
  text-align: right;
}

.sector-change.positive {
  color: #F56C6C;
}

.sector-change.negative {
  color: #67C23A;
}

/* 自选股 */
.watchlist-section {
  margin-bottom: 30px;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15px;
}

.watchlist-table {
  background-color: #f5f5f5;
  border-radius: 8px;
  padding: 20px;
  overflow-x: auto;
}

.watchlist-table table {
  width: 100%;
  border-collapse: collapse;
}

.watchlist-table th,
.watchlist-table td {
  padding: 12px 15px;
  text-align: left;
  border-bottom: 1px solid #e0e0e0;
}

.watchlist-table th {
  background-color: #e3f2fd;
  font-weight: 600;
  color: #1976D2;
}

.watchlist-table tr:hover {
  background-color: #e3f2fd;
}

.cell.change.positive {
  color: #F56C6C;
  font-weight: bold;
}

.cell.change.negative {
  color: #67C23A;
  font-weight: bold;
}

.cell.target {
  color: #1976D2;
  font-weight: 500;
}

.cell.distance {
  color: #666;
}

/* 投研观点 */
.research-section {
  margin-bottom: 30px;
}

.research-card {
  background-color: #f5f5f5;
  border-radius: 8px;
  padding: 20px;
}

.research-item {
  display: flex;
  margin-bottom: 15px;
  align-items: flex-start;
}

.research-label {
  width: 100px;
  font-size: 14px;
  font-weight: 600;
  color: #666;
}

.research-value {
  flex: 1;
  font-size: 14px;
  color: #333;
  line-height: 1.5;
}

.research-date {
  font-size: 12px;
  color: #999;
  text-align: right;
}

@media (max-width: 768px) {
  .index-content {
    flex-direction: column;
    gap: 20px;
    align-items: flex-start;
  }
  
  .index-stats {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 20px;
  }
  
  .research-targets {
    flex-direction: column;
    gap: 10px;
  }
  
  .table-header,
  .table-row {
    grid-template-columns: 1fr 1fr;
    gap: 5px;
  }
  
  .header-cell:nth-child(3),
  .header-cell:nth-child(4),
  .header-cell:nth-child(5),
  .cell:nth-child(3),
  .cell:nth-child(4),
  .cell:nth-child(5) {
    display: none;
  }
}
</style>