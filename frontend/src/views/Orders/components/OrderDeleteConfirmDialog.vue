<!--
  OrderDeleteConfirmDialog.vue - 订单删除确认对话框组件

  功能说明：
  - 提供订单删除前的二次确认
  - 显示订单关联的手办名称和金额信息
  - 需要用户勾选确认复选框才能启用删除按钮
  - 采用 Element Plus 的 el-dialog 组件实现
  - 支持多币种显示和人民币转换

  组件依赖：
  - 接收 show、order 作为 props
  - 通过 confirm 和 cancel 事件与父组件通信

  维护提示：
  - 复选框未选中时删除按钮禁用
  - 复选框选中后删除按钮变为红色
  - 显示订单关联的手办名称和金额信息
  - 支持多币种显示和人民币转换
-->
<template>
  <el-dialog
    v-model="visible"
    title="删除订单"
    width="500px"
    :close-on-click-modal="false"
    :close-on-press-escape="false"
    class="delete-confirm-dialog"
    @close="handleCancel"
  >
    <div class="delete-confirm-content">
      <p class="delete-warning-text">
        <strong>{{ figureName }}</strong>
        的订单记录将被删除。此操作<strong class="highlight">无法撤销</strong>。继续吗？
      </p>

      <!-- 订单信息提示 -->
      <div class="order-info">
        <el-alert type="info" :closable="false" show-icon>
          <template #title>
            <div class="order-amount-info">
              <div class="original-amount">
                订单金额：定金 {{ deposit }}{{ depositCurrency }} + 尾款 {{ balance }}{{ balanceCurrency }}
              </div>
              <div v-if="hasNonCNYCurrency" class="converted-amount">
                换算为人民币：定金 {{ depositCNY.toFixed(2) }}元 + 尾款 {{ balanceCNY.toFixed(2) }}元 = 总计 {{ totalCNY.toFixed(2) }}元
              </div>
              <div v-else class="total-amount">
                = 总计 {{ totalAmount.toFixed(2) }}元
              </div>
            </div>
          </template>
        </el-alert>
      </div>

      <!-- 确认复选框 -->
      <div class="confirm-checkbox">
        <el-checkbox v-model="confirmed" size="large">
          是的，删除 "{{ figureName }}" 的订单记录
        </el-checkbox>
      </div>
    </div>

    <template #footer>
      <div class="dialog-footer">
        <el-button @click="handleCancel">取消</el-button>
        <el-button
          type="danger"
          :disabled="!confirmed"
          @click="handleConfirm"
          class="delete-btn"
        >
          删除
        </el-button>
      </div>
    </template>
  </el-dialog>
</template>

<script>
import { ref, computed, watch } from 'vue'

export default {
  name: 'OrderDeleteConfirmDialog',
  props: {
    show: {
      type: Boolean,
      default: false
    },
    order: {
      type: Object,
      default: () => ({})
    }
  },
  emits: ['update:show', 'confirm', 'cancel'],
  setup(props, { emit }) {
    const confirmed = ref(false)

    const visible = computed({
      get: () => props.show,
      set: (val) => emit('update:show', val)
    })

    const figureName = computed(() => {
      return props.order?.figure_name || props.order?.figure?.name || '未知手办'
    })

    const deposit = computed(() => {
      return props.order?.deposit || 0
    })

    const balance = computed(() => {
      return props.order?.balance || 0
    })

    const depositCurrency = computed(() => {
      return getCurrencySymbol(props.order?.deposit_currency || 'CNY')
    })

    const balanceCurrency = computed(() => {
      return getCurrencySymbol(props.order?.balance_currency || 'CNY')
    })

    // 汇率转换函数
    const convertToCNY = (amount, currency) => {
      if (!amount) return 0
      
      const exchangeRates = {
        'CNY': 1.0,    // 人民币
        'JPY': 1/23,   // 日元
        'USD': 7.0,    // 美元
        'EUR': 8.0     // 欧元
      }
      
      const rate = exchangeRates[currency] || 1.0
      return amount * rate
    }

    const depositCNY = computed(() => {
      return convertToCNY(deposit.value, props.order?.deposit_currency || 'CNY')
    })

    const balanceCNY = computed(() => {
      return convertToCNY(balance.value, props.order?.balance_currency || 'CNY')
    })

    const totalCNY = computed(() => {
      return depositCNY.value + balanceCNY.value
    })

    const totalAmount = computed(() => {
      return deposit.value + balance.value
    })

    const hasNonCNYCurrency = computed(() => {
      const depositCurr = props.order?.deposit_currency || 'CNY'
      const balanceCurr = props.order?.balance_currency || 'CNY'
      return depositCurr !== 'CNY' || balanceCurr !== 'CNY'
    })

    // 获取币种符号
    const getCurrencySymbol = (currency) => {
      switch(currency) {
        case 'CNY': return '元'
        case 'JPY': return '日元'
        case 'USD': return '美元'
        case 'EUR': return '欧元'
        default: return '元'
      }
    }

    // 对话框关闭时重置确认状态
    watch(() => props.show, (newVal) => {
      if (!newVal) {
        confirmed.value = false
      }
    })

    const handleConfirm = () => {
      if (confirmed.value) {
        emit('confirm')
        confirmed.value = false
      }
    }

    const handleCancel = () => {
      emit('cancel')
      confirmed.value = false
    }

    return {
      confirmed,
      visible,
      figureName,
      deposit,
      balance,
      depositCurrency,
      balanceCurrency,
      depositCNY,
      balanceCNY,
      totalCNY,
      totalAmount,
      hasNonCNYCurrency,
      handleConfirm,
      handleCancel
    }
  }
}
</script>

<style scoped>
.delete-confirm-content {
  padding: 10px 0;
}

.delete-warning-text {
  font-size: 14px;
  line-height: 1.6;
  color: #606266;
  margin-bottom: 20px;
}

.delete-warning-text strong {
  color: #303133;
}

.delete-warning-text .highlight {
  color: #f56c6c;
  font-weight: bold;
}

.order-info {
  margin-bottom: 20px;
}

.order-amount-info {
  line-height: 1.6;
}

.original-amount {
  margin-bottom: 4px;
}

.converted-amount {
  color: #606266;
  font-size: 13px;
  margin-top: 4px;
}

.total-amount {
  color: #606266;
  font-size: 13px;
}

.confirm-checkbox {
  margin-top: 20px;
}

.confirm-checkbox :deep(.el-checkbox__label) {
  font-size: 14px;
  color: #606266;
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
}

.delete-btn {
  background-color: #f56c6c;
  border-color: #f56c6c;
}

.delete-btn:hover:not(:disabled) {
  background-color: #f78989;
  border-color: #f78989;
}

.delete-btn:disabled {
  background-color: #fab6b6;
  border-color: #fab6b6;
}
</style>
