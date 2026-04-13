<template>
  <div class="trade-flow">
    <div class="flow-header">
      <h4>交易流水 (按时间倒序)</h4>
      <el-button @click="showFilter = !showFilter">
        筛选 <el-icon><ArrowDown /></el-icon>
      </el-button>
    </div>

    <!-- 筛选条件 -->
    <div v-if="showFilter" class="filter-section">
      <div class="filter-row">
        <el-button 
          v-for="type in tradeTypes" 
          :key="type.value"
          :class="{ active: selectedTradeType === type.value }"
          @click="selectedTradeType = type.value"
        >
          {{ type.label }}
        </el-button>
      </div>
      <div class="filter-row">
        <el-button 
          v-for="year in tradeYears" 
          :key="year.value"
          :class="{ active: selectedTradeYear === year.value }"
          @click="selectedTradeYear = year.value"
        >
          {{ year.label }}
        </el-button>
        <el-button 
          v-for="month in tradeMonths" 
          :key="month.value"
          :class="{ active: selectedTradeMonth === month.value }"
          @click="selectedTradeMonth = month.value"
        >
          {{ month.label }}
        </el-button>
      </div>
    </div>

    <!-- 交易记录 -->
    <div class="trade-records">
      <div 
        v-for="record in filteredTradeRecords" 
        :key="record.id"
        class="trade-record"
      >
        <div class="record-header">
          <span class="record-date">📅 {{ record.date }}</span>
          <span class="record-amount" :class="{ positive: record.amount >= 0, negative: record.amount < 0 }">
            {{ record.amount >= 0 ? '+' : '' }}¥{{ formatNumber(Math.abs(record.amount)) }}
          </span>
        </div>
        <div class="record-divider"></div>
        <div class="record-content">
          <div class="record-title">{{ record.title }}</div>
          <div class="record-details">
            <span v-if="record.order_id" class="detail-item">订单号: {{ record.order_id }}</span>
            <span v-if="record.buyer" class="detail-item">买家: {{ record.buyer }}</span>
            <span v-if="record.platform" class="detail-item">平台: {{ record.platform }}</span>
          </div>
          <div class="record-status">
            <span class="status-item">状态: {{ record.status }}</span>
            <span v-if="record.payment_method" class="status-item">支付方式: {{ record.payment_method }}</span>
            <span v-if="record.merchant" class="status-item">商户: {{ record.merchant }}</span>
            <span v-if="record.fee" class="status-item">手续费: -¥{{ formatNumber(record.fee) }}</span>
            <span v-if="record.net_profit" class="status-item" :class="{ positive: record.net_profit >= 0, negative: record.net_profit < 0 }">
              净利润: {{ record.net_profit >= 0 ? '+' : '' }}¥{{ formatNumber(Math.abs(record.net_profit)) }}
            </span>
          </div>
          <div class="record-actions">
            <el-button v-if="record.actions" v-for="action in record.actions" :key="action" size="small" @click="handleTradeAction(action, record)">
              {{ action }}
            </el-button>
          </div>
        </div>
      </div>
      
      <!-- 空数据提示 -->
      <div v-if="filteredTradeRecords.length === 0" class="empty-records">
        <el-empty description="暂无交易记录" />
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed } from 'vue'
import { ArrowDown } from '@element-plus/icons-vue'

export default {
  name: 'TradeFlow',
  components: {
    ArrowDown
  },
  props: {
    tradeData: {
      type: Object,
      default: () => ({})
    },
    formatNumber: {
      type: Function,
      default: (num) => num?.toLocaleString() || '0'
    },
    getMockTradeData: {
      type: Function,
      default: () => ({
        transactions: []
      })
    }
  },
  emits: ['handle-trade-action'],
  setup(props, { emit }) {
    const showFilter = ref(false)
    const selectedTradeType = ref('all')
    const selectedTradeYear = ref('2026')
    const selectedTradeMonth = ref('')
    
    const tradeTypes = [
      { label: '全部类型', value: 'all' },
      { label: '买入', value: 'buy' },
      { label: '卖出', value: 'sell' },
      { label: '补款', value: 'payment' },
      { label: '运费', value: 'shipping' },
      { label: '退款', value: 'refund' }
    ]
    
    const tradeYears = [
      { label: '2026年', value: '2026' },
      { label: '2025年', value: '2025' }
    ]
    
    const tradeMonths = [
      { label: '3月', value: '3' },
      { label: '2月', value: '2' },
      { label: '1月', value: '1' }
    ]
    
    const filteredTradeRecords = computed(() => {
      let records = props.tradeData?.transactions || props.getMockTradeData().transactions
      
      // 按类型筛选
      if (selectedTradeType.value !== 'all') {
        // 这里可以根据实际情况添加类型筛选逻辑
      }
      
      // 按年份筛选
      if (selectedTradeYear.value) {
        // 这里可以根据实际情况添加年份筛选逻辑
      }
      
      // 按月份筛选
      if (selectedTradeMonth.value) {
        // 这里可以根据实际情况添加月份筛选逻辑
      }
      
      return records
    })
    
    const handleTradeAction = (action, record) => {
      emit('handle-trade-action', action, record)
    }
    
    return {
      showFilter,
      selectedTradeType,
      selectedTradeYear,
      selectedTradeMonth,
      tradeTypes,
      tradeYears,
      tradeMonths,
      filteredTradeRecords,
      handleTradeAction
    }
  }
}
</script>

<style scoped>
/* 交易流水 */
.trade-flow {
  margin-bottom: 30px;
  background-color: white;
  border-radius: 8px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
  padding: 20px;
}

.flow-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  flex-wrap: wrap;
  gap: 10px;
}

.flow-header h4 {
  color: #333;
  font-size: 16px;
  font-weight: bold;
  margin: 0;
}

.filter-section {
  margin-bottom: 20px;
  padding: 15px;
  background-color: #f5f5f5;
  border-radius: 8px;
}

.filter-row {
  display: flex;
  gap: 10px;
  margin-bottom: 10px;
  flex-wrap: wrap;
}

.filter-row:last-child {
  margin-bottom: 0;
}

.filter-row .el-button {
  border-radius: 4px;
}

.filter-row .el-button.active {
  background-color: #409EFF;
  color: white;
}

/* 交易记录 */
.trade-records {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.trade-record {
  background-color: #f9f9f9;
  padding: 15px;
  border-radius: 8px;
  border: 1px solid #e0e0e0;
  transition: all 0.3s ease;
}

.trade-record:hover {
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.record-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
}

.record-date {
  font-size: 14px;
  color: #666;
}

.record-amount {
  font-size: 18px;
  font-weight: bold;
}

.record-amount.positive {
  color: #67c23a;
}

.record-amount.negative {
  color: #f56c6c;
}

.record-divider {
  height: 1px;
  background-color: #e0e0e0;
  margin: 10px 0;
}

.record-content {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.record-title {
  font-size: 16px;
  font-weight: bold;
  color: #333;
}

.record-details {
  display: flex;
  flex-wrap: wrap;
  gap: 15px;
  font-size: 14px;
}

.detail-item {
  color: #666;
}

.record-status {
  display: flex;
  flex-wrap: wrap;
  gap: 15px;
  font-size: 14px;
}

.status-item {
  color: #666;
}

.status-item.positive {
  color: #67c23a;
}

.status-item.negative {
  color: #f56c6c;
}

.record-actions {
  display: flex;
  gap: 10px;
  justify-content: flex-start;
  margin-top: 10px;
}

.empty-records {
  padding: 40px 0;
  display: flex;
  justify-content: center;
  align-items: center;
}

@media (max-width: 768px) {
  .flow-header {
    flex-direction: column;
    align-items: flex-start;
  }
  
  .filter-row {
    flex-direction: column;
  }
}
</style>