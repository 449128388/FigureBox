<template>
  <div class="watchlist-section">
    <div class="section-title">📈 我的自选股 (关注列表)</div>
    <div class="watchlist-table">
      <table>
        <thead>
          <tr>
            <th>手办名称</th>
            <th>现价</th>
            <th>涨跌幅</th>
            <th>目标价</th>
            <th>距离目标</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="item in marketData?.watchlist || []" :key="item.name">
            <td>{{ item.name }}</td>
            <td>¥{{ formatNumber(item.current_price) }}</td>
            <td :class="{ positive: item.change >= 0, negative: item.change < 0 }">
              {{ item.change >= 0 ? '+' : '' }}{{ item.change }}%
            </td>
            <td>¥{{ formatNumber(item.target_price) }}</td>
            <td>{{ item.target_distance }}</td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script>
export default {
  name: 'WatchlistSection',
  props: {
    marketData: {
      type: Object,
      default: () => ({})
    }
  },
  methods: {
    formatNumber(num) {
      return num?.toLocaleString() || '0'
    }
  }
}
</script>

<style scoped>
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

@media (max-width: 768px) {
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