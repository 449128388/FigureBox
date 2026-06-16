<template>
  <el-dialog
    v-model="dialogVisible"
    title="确认删除"
    width="400px"
    @close="handleClose"
  >
    <div v-if="order" class="delete-content">
      <p class="delete-warning">确定要删除这条已出售订单吗？</p>
      <div class="order-info">
        <p><strong>手办名称:</strong> {{ order.figure_name }}</p>
        <p><strong>卖出平台:</strong> {{ order.sell_platform || '-' }}</p>
        <p><strong>卖出价:</strong> ¥{{ formatNumber(order.sell_price) }}</p>
      </div>
      <p class="delete-hint">删除后无法恢复，请谨慎操作。</p>
    </div>

    <template #footer>
      <el-button @click="handleCancel">取消</el-button>
      <el-button type="danger" @click="handleConfirm">确认删除</el-button>
    </template>
  </el-dialog>
</template>

<script>
import { computed } from 'vue'

export default {
  name: 'SoldOrderDeleteConfirmDialog',
  props: {
    show: {
      type: Boolean,
      default: false
    },
    order: {
      type: Object,
      default: null
    }
  },
  emits: ['confirm', 'cancel', 'update:show'],
  setup(props, { emit }) {
    const dialogVisible = computed({
      get: () => props.show,
      set: (val) => emit('update:show', val)
    })

    const handleCancel = () => {
      emit('cancel')
    }

    const handleConfirm = () => {
      emit('confirm')
    }

    return {
      dialogVisible,
      handleCancel,
      handleConfirm
    }
  },
  methods: {
    formatNumber(num) {
      return num.toLocaleString('zh-CN', { minimumFractionDigits: 2, maximumFractionDigits: 2 })
    },
    handleClose() {
      this.$emit('cancel')
    }
  }
}
</script>

<style scoped>
.delete-content {
  padding: 10px 0;
}

.delete-warning {
  font-size: 16px;
  color: #333;
  margin-bottom: 15px;
}

.order-info {
  background: #f9f9f9;
  padding: 15px;
  border-radius: 6px;
  margin-bottom: 15px;
}

.order-info p {
  margin: 8px 0;
  font-size: 14px;
  color: #666;
}

.delete-hint {
  font-size: 13px;
  color: #999;
  margin-top: 0;
}
</style>