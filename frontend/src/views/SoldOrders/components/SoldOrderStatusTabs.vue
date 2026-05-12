<template>
  <div class="status-tabs-container">
    <div class="status-tabs">
      <button
        v-for="tab in tabs"
        :key="tab.value"
        class="status-tab"
        :class="{ active: currentStatus === tab.value }"
        @click="$emit('changeStatus', tab.value)"
      >
        {{ tab.label }}
        <span class="tab-count">({{ statusCounts[tab.value] || 0 }})</span>
      </button>
    </div>
    <div class="profit-summary">
      <span class="profit-icon">💰</span>
      <span class="profit-label">累计净利润:</span>
      <span class="profit-value" :class="totalNetProfit >= 0 ? 'profit-positive' : 'profit-negative'">
        {{ totalNetProfit >= 0 ? '+' : '' }}¥{{ formatNumber(Math.abs(totalNetProfit)) }}
      </span>
    </div>
  </div>
</template>

<script>
export default {
  name: 'SoldOrderStatusTabs',
  props: {
    currentStatus: {
      type: String,
      default: 'all'
    },
    statusCounts: {
      type: Object,
      default: () => ({})
    },
    totalNetProfit: {
      type: Number,
      default: 0
    }
  },
  emits: ['changeStatus'],
  data() {
    return {
      tabs: [
        { value: 'all', label: '全部' },
        { value: '待发货', label: '待发货' },
        { value: '已发货', label: '已发货' },
        { value: '已完成', label: '已完成' },
        { value: '退款/纠纷', label: '退款/纠纷' }
      ]
    }
  },
  methods: {
    formatNumber(num) {
      return num.toLocaleString('zh-CN', { minimumFractionDigits: 2, maximumFractionDigits: 2 })
    }
  }
}
</script>

<style scoped>
.status-tabs-container {
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: white;
  padding: 15px 20px;
  margin-bottom: 20px;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  flex-wrap: wrap;
  gap: 15px;
}

.status-tabs {
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
}

.status-tab {
  padding: 10px 20px;
  background: #f5f5f5;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-size: 14px;
  font-weight: 500;
  color: #666;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  gap: 5px;
}

.status-tab:hover {
  background: #e0e0e0;
  color: #333;
}

.status-tab.active {
  background-color: #2196F3;
  color: white;
  border: 2px solid #1976D2;
  box-shadow: 0 2px 8px rgba(33, 150, 243, 0.3);
}

.status-tab.active:hover {
  background-color: #1976D2;
}

.tab-count {
  font-weight: 600;
}

.profit-summary {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 15px;
  background: linear-gradient(135deg, #fff3e0 0%, #ffe0b2 100%);
  border-radius: 6px;
  border-left: 4px solid #ff9800;
}

.profit-icon {
  font-size: 20px;
}

.profit-label {
  font-size: 14px;
  color: #666;
}

.profit-value {
  font-size: 18px;
  font-weight: 600;
}

.profit-positive {
  color: #4CAF50;
}

.profit-negative {
  color: #f44336;
}

@media (max-width: 768px) {
  .status-tabs-container {
    flex-direction: column;
    align-items: stretch;
  }
  
  .status-tabs {
    justify-content: center;
  }
  
  .profit-summary {
    justify-content: center;
  }
}
</style>