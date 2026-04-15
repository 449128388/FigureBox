<!--
  AssetTransactionList.vue - 资产交易记录列表组件

  功能说明：
  - 显示手办的所有交易记录（买入/卖出）
  - 支持股票式补仓功能展示
  - 显示交易类型、价格、数量、时间等信息
  - 支持删除交易记录

  组件依赖：
  - Element Plus 的 el-table、el-tag、el-button 组件
  - 接收 transactions 作为 props

  维护提示：
  - 使用 transaction_type 区分买入/卖出
  - 买入显示绿色，卖出显示红色
  - 时间倒序排列（最新的在前面）
-->
<template>
  <div class="transaction-list">
    <h3 class="section-title">交易记录</h3>
    <el-table :data="transactions" style="width: 100%" v-loading="loading" empty-text="暂无交易记录">
      <el-table-column prop="transaction_type" label="类型" width="80">
        <template #default="{ row }">
          <el-tag :type="row.transaction_type === 'buy' ? 'success' : 'danger'" size="small">
            {{ row.transaction_type === 'buy' ? '买入' : '卖出' }}
          </el-tag>
        </template>
      </el-table-column>

      <el-table-column prop="price" label="单价" width="100">
        <template #default="{ row }">
          {{ formatPrice(row.price) }}
        </template>
      </el-table-column>

      <el-table-column prop="quantity" label="数量" width="80">
        <template #default="{ row }">
          {{ row.quantity }}
        </template>
      </el-table-column>

      <el-table-column prop="total_amount" label="总金额" width="100">
        <template #default="{ row }">
          {{ formatPrice(row.total_amount) }}
        </template>
      </el-table-column>

      <el-table-column prop="remaining_quantity" label="剩余持仓" width="100">
        <template #default="{ row }">
          <span v-if="row.transaction_type === 'buy'">
            {{ row.remaining_quantity || 0 }}
          </span>
          <span v-else>-</span>
        </template>
      </el-table-column>

      <el-table-column prop="transaction_date" label="交易时间" width="160">
        <template #default="{ row }">
          {{ formatDate(row.transaction_date) }}
        </template>
      </el-table-column>

      <el-table-column prop="notes" label="备注" min-width="120" show-overflow-tooltip>
        <template #default="{ row }">
          {{ row.notes || '-' }}
        </template>
      </el-table-column>

      <el-table-column label="操作" width="80" fixed="right">
        <template #default="{ row }">
          <el-button type="danger" size="small" @click="handleDelete(row)" :disabled="loading">
            删除
          </el-button>
        </template>
      </el-table-column>
    </el-table>

    <!-- 统计信息 -->
    <div class="transaction-summary" v-if="transactions.length > 0">
      <div class="summary-item">
        <span class="label">总买入:</span>
        <span class="value buy">{{ totalBuyQuantity }} 个</span>
      </div>
      <div class="summary-item">
        <span class="label">总卖出:</span>
        <span class="value sell">{{ totalSellQuantity }} 个</span>
      </div>
      <div class="summary-item">
        <span class="label">当前持仓:</span>
        <span class="value">{{ currentHolding }} 个</span>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'AssetTransactionList',
  props: {
    transactions: {
      type: Array,
      default: () => []
    },
    loading: {
      type: Boolean,
      default: false
    }
  },
  emits: ['delete'],
  setup(props, { emit }) {
    // 计算属性
    const totalBuyQuantity = computed(() => {
      return props.transactions
        .filter(t => t.transaction_type === 'buy')
        .reduce((sum, t) => sum + t.quantity, 0)
    })

    const totalSellQuantity = computed(() => {
      return props.transactions
        .filter(t => t.transaction_type === 'sell')
        .reduce((sum, t) => sum + t.quantity, 0)
    })

    const currentHolding = computed(() => {
      const buyQty = props.transactions
        .filter(t => t.transaction_type === 'buy')
        .reduce((sum, t) => sum + (t.remaining_quantity || 0), 0)
      const sellQty = totalSellQuantity.value
      return buyQty - sellQty
    })

    // 格式化价格
    const formatPrice = (price) => {
      if (price === null || price === undefined) return '-'
      return `¥${Number(price).toFixed(2)}`
    }

    // 格式化日期
    const formatDate = (dateStr) => {
      if (!dateStr) return '-'
      const date = new Date(dateStr)
      return date.toLocaleString('zh-CN', {
        year: 'numeric',
        month: '2-digit',
        day: '2-digit',
        hour: '2-digit',
        minute: '2-digit'
      })
    }

    // 删除交易记录
    const handleDelete = (row) => {
      emit('delete', row.id)
    }

    return {
      totalBuyQuantity,
      totalSellQuantity,
      currentHolding,
      formatPrice,
      formatDate,
      handleDelete
    }
  }
}
</script>

<script setup>
import { computed } from 'vue'
</script>

<style scoped>
.transaction-list {
  margin-top: 20px;
}

.section-title {
  margin: 0 0 15px 0;
  font-size: 16px;
  font-weight: 600;
  color: #333;
}

.transaction-summary {
  display: flex;
  gap: 20px;
  margin-top: 15px;
  padding: 12px 15px;
  background-color: #f5f7fa;
  border-radius: 4px;
}

.summary-item {
  display: flex;
  align-items: center;
  gap: 8px;
}

.summary-item .label {
  color: #606266;
  font-size: 14px;
}

.summary-item .value {
  font-weight: 600;
  font-size: 14px;
  color: #303133;
}

.summary-item .value.buy {
  color: #67c23a;
}

.summary-item .value.sell {
  color: #f56c6c;
}
</style>
