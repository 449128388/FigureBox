<!--
  TradeFlow.vue - 交易流水组件

  功能说明：
  - 展示聚合后的交易流水记录，按时间倒序排列
  - 支持按交易类型筛选（全部/收入/支出/费用）
  - 支持高级筛选（时间、手办、平台、状态、金额、关键词）
  - 使用 TradeFlowCard 组件展示聚合卡片
  - 支持点击操作按钮处理交易
  - 筛选变更时触发事件重新获取数据

  组件依赖：
  - 接收 tradeData 作为 props，包含交易记录数据
  - TradeFlowCard 组件用于展示聚合交易
  - TradeFlowFilter 组件用于高级筛选

  维护提示：
  - 筛选功能通过 filterParams 控制
  - 交易操作通过 handleTradeAction 方法处理
  - 聚合逻辑由后端 TransactionQueryService 实现
  - 筛选变更时触发 filter-change 事件通知父组件重新获取数据
-->
<template>
  <div class="trade-flow">
    <div class="flow-header">
      <h4>交易流水 (按时间倒序)</h4>
      <el-button @click="showFilter = !showFilter">
        查询 <el-icon><ArrowDown /></el-icon>
      </el-button>
    </div>

    <!-- 高级筛选面板 -->
    <div v-if="showFilter" class="filter-panel">
      <TradeFlowFilter
        v-model="filterParams"
        @confirm="handleFilterConfirm"
        @reset="handleFilterReset"
      />
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
import { ref, computed, reactive } from 'vue'
import { ArrowDown } from '@element-plus/icons-vue'
import TradeFlowCard from './TradeFlowCard.vue'
import TradeFlowFilter from './TradeFlowFilter.vue'

export default {
  name: 'TradeFlow',
  components: {
    ArrowDown,
    TradeFlowCard,
    TradeFlowFilter
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

    // 筛选参数
    const filterParams = reactive({
      filterType: 'all',
      timeType: 'last30days',
      dateRange: [],
      figureIds: [],
      platforms: [],
      statusList: [],
      minAmount: null,
      maxAmount: null,
      keyword: ''
    })

    // 交易记录列表（直接使用后端返回的数据）
    const tradeRecords = computed(() => {
      return props.tradeData?.transactions || []
    })

    // 处理筛选确认
    const handleFilterConfirm = (params) => {
      Object.assign(filterParams, params)
      // 触发筛选变更事件，通知父组件重新获取数据
      emit('filter-change', { ...filterParams })
    }

    // 处理筛选重置
    const handleFilterReset = () => {
      // 重置后触发筛选变更事件
      emit('filter-change', { ...filterParams })
    }

    const handleTradeAction = (action, record) => {
      emit('handle-trade-action', action, record)
    }

    return {
      showFilter,
      filterParams,
      tradeRecords,
      handleFilterConfirm,
      handleFilterReset,
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

.filter-panel {
  margin-bottom: 20px;
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
