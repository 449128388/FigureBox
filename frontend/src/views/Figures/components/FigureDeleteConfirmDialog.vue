<!--
  FigureDeleteConfirmDialog.vue - 手办删除确认对话框组件

  功能说明：
  - 提供手办删除前的二次确认
  - 显示手办名称和关联订单信息
  - 需要用户勾选确认复选框才能启用删除按钮
  - 采用 Element Plus 的 el-dialog 组件实现

  组件依赖：
  - 接收 show、figure、orderCount 作为 props
  - 通过 confirm 和 cancel 事件与父组件通信

  维护提示：
  - 复选框未选中时删除按钮禁用
  - 复选框选中后删除按钮变为红色
  - 显示手办名称和关联订单数量
-->
<template>
  <el-dialog
    v-model="visible"
    title="删除手办"
    width="500px"
    :close-on-click-modal="false"
    :close-on-press-escape="false"
    class="delete-confirm-dialog"
    @close="handleCancel"
  >
    <div class="delete-confirm-content">
      <p class="delete-warning-text">
        <strong>{{ figureName }}</strong>
        连同所存储媒体文件将从此服务器中删除。此操作<strong class="highlight">无法撤销</strong>。继续吗？
      </p>

      <!-- 订单信息提示 -->
      <div v-if="orderCount > 0" class="order-info">
        <el-alert
          :title="`该手办关联 ${orderCount} 个订单，请先删除订单记录`"
          type="warning"
          :closable="false"
          show-icon
        />
      </div>

      <!-- 确认复选框 -->
      <div class="confirm-checkbox">
        <el-checkbox v-model="confirmed" size="large">
          是的，删除手办 "{{ figureName }}" 及其文件
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
  name: 'FigureDeleteConfirmDialog',
  props: {
    show: {
      type: Boolean,
      default: false
    },
    figure: {
      type: Object,
      default: () => ({})
    },
    orderCount: {
      type: Number,
      default: 0
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
      return props.figure?.name || '未知手办'
    })

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
