<!--
  AssetTransactionForm.vue - 资产交易表单组件

  功能说明：
  - 提供买入（补仓）和卖出交易的表单
  - 支持输入价格、数量、备注
  - 显示当前持仓和平均成本参考
  - 支持股票式补仓功能

  组件依赖：
  - Element Plus 的 el-form、el-input-number、el-button 组件
  - 接收 figureId 和 currentHolding 作为 props

  维护提示：
  - 买入时检查价格必须大于0
  - 卖出时检查数量不能超过当前持仓
  - 提交成功后清空表单
-->
<template>
  <div class="transaction-form">
    <h3 class="section-title">{{ isBuy ? '补仓' : '卖出' }}</h3>

    <!-- 参考信息 -->
    <div class="reference-info" v-if="averageCost">
      <div class="info-item">
        <span class="label">当前持仓:</span>
        <span class="value">{{ currentHolding }} 个</span>
      </div>
      <div class="info-item">
        <span class="label">平均成本:</span>
        <span class="value">¥{{ formatPrice(averageCost.average_cost) }}</span>
      </div>
      <div class="info-item" v-if="!isBuy && currentHolding > 0">
        <span class="label">可卖出:</span>
        <span class="value">{{ currentHolding }} 个</span>
      </div>
    </div>

    <el-form :model="form" label-width="80px" class="transaction-form-content">
      <el-form-item label="单价" required>
        <el-input-number
          v-model="form.price"
          :min="0"
          :step="1"
          :precision="2"
          placeholder="请输入单价"
          style="width: 200px"
        />
        <span class="unit">元</span>
      </el-form-item>

      <el-form-item label="数量" required>
        <el-input-number
          v-model="form.quantity"
          :min="1"
          :step="1"
          :max="isBuy ? undefined : currentHolding"
          placeholder="请输入数量"
          style="width: 200px"
        />
        <span class="unit">个</span>
        <span v-if="!isBuy && currentHolding > 0" class="hint">
          (最多可卖出 {{ currentHolding }} 个)
        </span>
      </el-form-item>

      <el-form-item label="总金额">
        <span class="total-amount">¥{{ formatPrice(totalAmount) }}</span>
      </el-form-item>

      <el-form-item label="备注">
        <el-input
          v-model="form.notes"
          type="textarea"
          :rows="2"
          placeholder="请输入备注（可选）"
          maxlength="255"
          show-word-limit
        />
      </el-form-item>

      <el-form-item>
        <el-button
          type="primary"
          @click="handleSubmit"
          :loading="loading"
          :disabled="!canSubmit"
        >
          {{ isBuy ? '买入' : '卖出' }}
        </el-button>
        <el-button @click="handleReset" :disabled="loading">重置</el-button>
      </el-form-item>
    </el-form>

    <!-- 补仓建议 -->
    <div class="suggestion-box" v-if="isBuy && averageCost && form.price > 0">
      <div v-if="form.price < averageCost.average_cost" class="suggestion buy">
        <el-icon><Info-Filled /></el-icon>
        <span>当前价格低于平均成本，建议补仓以降低成本</span>
      </div>
      <div v-else class="suggestion hold">
        <el-icon><Info-Filled /></el-icon>
        <span>当前价格高于平均成本，谨慎补仓</span>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed, watch } from 'vue'

export default {
  name: 'AssetTransactionForm',
  props: {
    figureId: {
      type: Number,
      required: true
    },
    isBuy: {
      type: Boolean,
      default: true
    },
    currentHolding: {
      type: Number,
      default: 0
    },
    averageCost: {
      type: Object,
      default: null
    },
    loading: {
      type: Boolean,
      default: false
    }
  },
  emits: ['submit', 'reset'],
  setup(props, { emit }) {
    // 表单数据
    const form = ref({
      price: 0,
      quantity: 1,
      notes: ''
    })

    // 计算总金额
    const totalAmount = computed(() => {
      return (form.value.price || 0) * (form.value.quantity || 0)
    })

    // 是否可以提交
    const canSubmit = computed(() => {
      if (form.value.price <= 0) return false
      if (form.value.quantity <= 0) return false
      if (!props.isBuy && form.value.quantity > props.currentHolding) return false
      return true
    })

    // 格式化价格
    const formatPrice = (price) => {
      if (price === null || price === undefined) return '0.00'
      return Number(price).toFixed(2)
    }

    // 提交表单
    const handleSubmit = () => {
      if (!canSubmit.value) return

      const data = {
        figure_id: props.figureId,
        price: form.value.price,
        quantity: form.value.quantity,
        notes: form.value.notes || undefined
      }

      emit('submit', data)
    }

    // 重置表单
    const handleReset = () => {
      form.value = {
        price: 0,
        quantity: 1,
        notes: ''
      }
      emit('reset')
    }

    // 监听 isBuy 变化，重置表单
    watch(() => props.isBuy, () => {
      handleReset()
    })

    return {
      form,
      totalAmount,
      canSubmit,
      formatPrice,
      handleSubmit,
      handleReset
    }
  }
}
</script>

<style scoped>
.transaction-form {
  padding: 20px;
  background-color: #f5f7fa;
  border-radius: 8px;
  margin-top: 20px;
}

.section-title {
  margin: 0 0 15px 0;
  font-size: 16px;
  font-weight: 600;
  color: #333;
}

.reference-info {
  display: flex;
  gap: 20px;
  margin-bottom: 20px;
  padding: 12px 15px;
  background-color: white;
  border-radius: 4px;
}

.info-item {
  display: flex;
  align-items: center;
  gap: 8px;
}

.info-item .label {
  color: #606266;
  font-size: 14px;
}

.info-item .value {
  font-weight: 600;
  font-size: 14px;
  color: #303133;
}

.transaction-form-content {
  background-color: white;
  padding: 20px;
  border-radius: 4px;
}

.unit {
  margin-left: 8px;
  color: #606266;
}

.total-amount {
  font-size: 16px;
  font-weight: 600;
  color: #f56c6c;
}

.hint {
  margin-left: 10px;
  color: #909399;
  font-size: 12px;
}

.suggestion-box {
  margin-top: 15px;
}

.suggestion {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 15px;
  border-radius: 4px;
  font-size: 14px;
}

.suggestion.buy {
  background-color: #f0f9eb;
  color: #67c23a;
}

.suggestion.hold {
  background-color: #fdf6ec;
  color: #e6a23c;
}
</style>