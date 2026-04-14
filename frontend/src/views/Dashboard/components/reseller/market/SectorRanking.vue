<!--
  SectorRanking.vue - 板块涨幅排行组件

  功能说明：
  - 展示不同IP板块的涨幅排行
  - 显示板块排名、名称、包含手办数量和涨跌幅
  - 根据涨幅情况显示不同颜色

  组件依赖：
  - 接收 marketData 作为 props，包含 sectors 数据

  维护提示：
  - 排名通过 index + 1 计算
  - 涨跌情况通过条件样式展示
-->
<template>
  <div class="sector-ranking">
    <div class="section-title">
      板块涨幅排行
    </div>
    <div class="sector-list">
      <div 
        v-for="(sector, index) in marketData?.sectors || []" 
        :key="sector.name"
        class="sector-item"
      >
        <div class="sector-rank">{{ index + 1 }}</div>
        <div class="sector-info">
          <div class="sector-name">{{ sector.name }}</div>
          <div class="sector-stocks">{{ sector.stocks }}</div>
        </div>
        <div class="sector-change" :class="{ positive: sector.change >= 0, negative: sector.change < 0 }">
          {{ sector.change >= 0 ? '+' : '' }}{{ sector.change }}%
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'SectorRanking',
  props: {
    marketData: {
      type: Object,
      default: () => ({})
    }
  }
}
</script>

<style scoped>
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
</style>