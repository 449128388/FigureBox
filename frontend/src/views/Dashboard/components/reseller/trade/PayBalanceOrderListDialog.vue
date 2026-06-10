<!--
  PayBalanceOrderListDialog.vue - 补款订单列表弹窗组件

  功能说明：
  - 展示待补款订单列表（Step 1）
  - 支持选择订单进行支付
  - 逾期订单标红置顶
  - 显示手办图片、名称、尾款金额、到期日等信息

  组件依赖：
  - Element Plus 的 Dialog、Card、Button、Empty 等组件
  - 需要传入 visible 控制显示

  维护提示：
  - 列表按逾期状态和到期日排序
  - 点击【去支付】触发选择事件
-->
<template>
  <el-dialog
    v-model="dialogVisible"
    title="支付尾款"
    width="560px"
    :close-on-click-modal="false"
    destroy-on-close
    class="pay-balance-order-list-dialog"
    @close="handleClose"
  >
    <div class="order-list-container">
      <!-- 加载状态 -->
      <div v-if="loading" class="loading-wrapper">
        <el-skeleton :rows="3" animated />
      </div>

      <!-- 空状态 -->
      <el-empty
        v-else-if="orders.length === 0"
        description="暂无待补款订单"
        :image-size="120"
      >
        <template #description>
          <div class="empty-text">
            <p>暂无待补款订单</p>
            <p class="empty-sub">未来7天内没有需要支付尾款的订单</p>
          </div>
        </template>
      </el-empty>

      <!-- 订单列表 -->
      <div v-else class="order-list">
        <div
          v-for="order in orders"
          :key="order.order_id"
          class="order-card"
          :class="{ 'is-overdue': order.is_overdue }"
        >
          <div class="order-content">
            <!-- 手办图片 -->
            <div class="figure-image">
              <el-image
                :src="order.figure_image || '/default-figure.png'"
                fit="cover"
                :preview-src-list="[]"
              >
                <template #error>
                  <div class="image-placeholder">
                    <el-icon><Picture /></el-icon>
                  </div>
                </template>
              </el-image>
            </div>

            <!-- 订单信息 -->
            <div class="order-info">
              <div class="figure-name">{{ order.figure_name }}</div>
              <div class="payment-info">
                <span class="balance-amount">
                  尾款: ¥{{ order.balance }}
                </span>
                <span class="deposit-paid">
                  定金已付: ¥{{ order.deposit }}
                </span>
              </div>
              <div class="due-info" :class="{ 'is-overdue': order.is_overdue }">
                <el-icon v-if="order.is_overdue"><Warning /></el-icon>
                <span>{{ order.due_text }}</span>
                <el-tag
                  v-if="order.is_overdue"
                  type="danger"
                  size="small"
                  effect="dark"
                  class="overdue-tag"
                >
                  逾期提醒
                </el-tag>
              </div>
            </div>

            <!-- 操作按钮 -->
            <div class="order-action">
              <el-button
                type="primary"
                size="small"
                @click="handleSelectOrder(order)"
              >
                去支付
              </el-button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 底部提示 -->
    <template #footer>
      <div class="dialog-footer">
        <span class="footer-tip">
          共 {{ orders.length }} 个待补款订单
          <span v-if="overdueCount > 0" class="overdue-count">
            （{{ overdueCount }} 个已逾期）
          </span>
        </span>
        <el-button @click="handleClose">关闭</el-button>
      </div>
    </template>
  </el-dialog>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import { Picture, Warning } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import axios from '@/axios'

const props = defineProps({
  visible: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['update:visible', 'select-order', 'close'])

// 弹窗可见性
const dialogVisible = computed({
  get: () => props.visible,
  set: (val) => emit('update:visible', val)
})

// 加载状态
const loading = ref(false)

// 订单列表
const orders = ref([])

// 逾期订单数量
const overdueCount = computed(() => {
  return orders.value.filter(order => order.is_overdue).length
})

// 获取待补款订单列表
const fetchPendingOrders = async () => {
  loading.value = true
  try {
    const response = await axios.get('/trade_records/pending-balance-orders')
    orders.value = response.orders || []
  } catch (error) {
    console.error('获取待补款订单失败:', error)
    ElMessage.error('获取待补款订单失败')
    orders.value = []
  } finally {
    loading.value = false
  }
}

// 选择订单
const handleSelectOrder = (order) => {
  emit('select-order', order)
  dialogVisible.value = false
}

// 关闭弹窗
const handleClose = () => {
  dialogVisible.value = false
  emit('close')
}

// 监听弹窗显示，加载数据
watch(() => props.visible, (newVal) => {
  if (newVal) {
    fetchPendingOrders()
  }
})
</script>

<style scoped>
.pay-balance-order-list-dialog :deep(.el-dialog__body) {
  padding: 0;
  max-height: 480px;
  overflow-y: auto;
}

.order-list-container {
  padding: 16px 20px;
  min-height: 200px;
}

.loading-wrapper {
  padding: 20px 0;
}

/* 空状态 */
.empty-text {
  text-align: center;
}

.empty-text p {
  margin: 0;
  color: #606266;
  font-size: 14px;
}

.empty-sub {
  margin-top: 8px !important;
  color: #909399 !important;
  font-size: 12px !important;
}

/* 订单列表 */
.order-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.order-card {
  border: 1px solid #e4e7ed;
  border-radius: 8px;
  padding: 16px;
  background-color: #fff;
  transition: all 0.2s ease;
}

.order-card:hover {
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
}

.order-card.is-overdue {
  border-color: #f56c6c;
  background-color: #fef0f0;
}

.order-content {
  display: flex;
  align-items: center;
  gap: 12px;
}

/* 手办图片 */
.figure-image {
  width: 64px;
  height: 64px;
  border-radius: 4px;
  overflow: hidden;
  flex-shrink: 0;
}

.figure-image :deep(.el-image) {
  width: 100%;
  height: 100%;
}

.image-placeholder {
  width: 100%;
  height: 100%;
  background-color: #f5f7fa;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #909399;
  font-size: 24px;
}

/* 订单信息 */
.order-info {
  flex: 1;
  min-width: 0;
}

.figure-name {
  font-size: 15px;
  font-weight: 600;
  color: #303133;
  margin-bottom: 8px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.payment-info {
  display: flex;
  gap: 16px;
  margin-bottom: 6px;
  font-size: 13px;
}

.balance-amount {
  color: #f56c6c;
  font-weight: 600;
}

.deposit-paid {
  color: #606266;
}

.due-info {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 12px;
  color: #909399;
}

.due-info.is-overdue {
  color: #f56c6c;
}

.due-info .el-icon {
  font-size: 14px;
}

.overdue-tag {
  margin-left: 4px;
}

/* 操作按钮 */
.order-action {
  flex-shrink: 0;
}

/* 底部 */
.dialog-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.footer-tip {
  font-size: 13px;
  color: #909399;
}

.overdue-count {
  color: #f56c6c;
  font-weight: 500;
}
</style>
