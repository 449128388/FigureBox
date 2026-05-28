<!--
  TradeFlow.vue - 交易流水组件

  功能说明：
  - 展示聚合后的交易流水记录，按时间倒序排列
  - 支持按交易类型筛选（全部/收入/支出/费用）
  - 使用 TradeFlowCard 组件展示聚合卡片
  - 支持点击操作按钮处理交易
  - 筛选变更时触发事件重新获取数据

  组件依赖：
  - 接收 tradeData 作为 props，包含交易记录数据
  - TradeFlowCard 组件用于展示聚合交易卡片

  维护提示：
  - 筛选功能通过 selectedFilterType 控制
  - 交易操作通过 handleTradeAction 方法处理
  - 聚合逻辑由后端 TransactionQueryService 实现
  - 筛选变更时触发 filter-change 事件通知父组件重新获取数据
-->
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
          v-for="type in filterTypes"
          :key="type.value"
          :class="{ active: selectedFilterType === type.value }"
          @click="handleFilterChange(type.value)"
        >
          {{ type.label }}
        </el-button>
      </div>
    </div>

    <!-- 交易记录列表 -->
    <div class="trade-records">
      <TradeFlowCard
        v-for="record in tradeRecords"
        :key="record.id"
        :record="record"
        @action="handleTradeAction"
      />

      <!-- 空数据提示 -->
      <div v-if="tradeRecords.length === 0" class="empty-records">
        <el-empty description="暂无交易记录" />
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed } from 'vue'
import { ArrowDown } from '@element-plus/icons-vue'
import TradeFlowCard from './TradeFlowCard.vue'

export default {
  name: 'TradeFlow',
  components: {
    ArrowDown,
    TradeFlowCard
  },
  props: {
    tradeData: {
      type: Object,
      default: () => ({})
    }
  },
  emits: ['handle-trade-action', 'filter-change'],
  setup(props, { emit }) {
    const showFilter = ref(false)
    const selectedFilterType = ref('all')

    // 筛选类型：全部/收入/支出/费用
    const filterTypes = [
      { label: '全部', value: 'all' },
      { label: '收入', value: 'income' },
      { label: '支出', value: 'expense' },
      { label: '费用', value: 'fee' }
    ]

    // 交易记录列表（直接使用后端返回的数据）
    const tradeRecords = computed(() => {
      return props.tradeData?.transactions || []
    })

    // 处理筛选变更
    const handleFilterChange = (filterType) => {
      selectedFilterType.value = filterType
      // 触发筛选变更事件，通知父组件重新获取数据
      emit('filter-change', filterType)
    }

    const handleTradeAction = (action, record) => {
      emit('handle-trade-action', action, record)
    }

    return {
      showFilter,
      selectedFilterType,
      filterTypes,
      tradeRecords,
      handleFilterChange,
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
  flex-wrap: wrap;
}

.filter-row .el-button {
  border-radius: 4px;
}

.filter-row .el-button.active {
  background-color: #409EFF;
  color: white;
}

/* 交易记录列表 */
.trade-records {
  display: flex;
  flex-direction: column;
}

.empty-records {
  padding: 40px 0;
  display: flex;
  justify-content: center;
  align-items: center;
}
</style>
