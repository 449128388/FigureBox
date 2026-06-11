<template>
  <el-dialog
    v-model="dialogVisible"
    title="取消订单"
    width="560px"
    :close-on-click-modal="false"
    destroy-on-close
    class="cancel-order-list-dialog"
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
        description="暂无可取消的订单"
        :image-size="120"
      >
        <template #description>
          <div class="empty-text">
            <p>暂无可取消的订单</p>
            <p class="empty-subtext">只有"待付尾款"、"已付定金"、"待发货"状态的订单可以取消</p>
          </div>
        </template>
      </el-empty>

      <!-- 订单列表 -->
      <div v-else class="order-list">
        <div
          v-for="order in orders"
          :key="order.order_id"
          class="order-card"
          :class="{ 'is-in-stock': order.is_in_stock }"
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
              <div class="order-number">{{ order.order_number }}</div>
              <div class="payment-info">
                <span class="order-type" :class="order.order_type">{{ order.order_type }}</span>
                <span class="paid-amount">
                  已付: ¥{{ order.paid_amount }}
                </span>
              </div>
              <div class="stock-warning" v-if="order.is_in_stock">
                <el-icon><Warning /></el-icon>
                <span>该订单已入库，取消将回滚库存</span>
              </div>
            </div>

            <!-- 操作按钮 -->
            <div class="order-action">
              <el-button
                type="danger"
                size="small"
                @click="handleSelectOrder(order)"
              >
                取消订单
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
          共 {{ orders.length }} 个可取消订单
          <span v-if="inStockCount > 0" class="stock-count">
            （{{ inStockCount }} 个已入库）
          </span>
        </span>
        <el-button @click="handleClose">关闭</el-button>
      </div>
    </template>
  </el-dialog>
</template>

<script setup>
/**
 * CancelOrderListDialog - 撤单订单列表弹窗
 *
 * 功能说明：
 * - 展示可取消的订单列表
 * - 显示订单基本信息、已支付金额、是否已入库
 * - 点击【取消订单】进入确认弹窗
 *
 * 维护提示：
 * - 只显示状态为'待付尾款'、'已付定金'、'待发货'的订单
 * - 已入库订单会有警告提示
 */
import { ref, computed, watch } from 'vue'
import { ElMessage } from 'element-plus'
import { Picture, Warning } from '@element-plus/icons-vue'
import axios from '@/axios'

const props = defineProps({
  modelValue: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['update:modelValue', 'select-order'])

// 对话框可见性
const dialogVisible = computed({
  get: () => props.modelValue,
  set: (val) => emit('update:modelValue', val)
})

// 数据状态
const orders = ref([])
const loading = ref(false)

// 已入库订单数量
const inStockCount = computed(() => {
  return orders.value.filter(order => order.is_in_stock).length
})

// 获取可取消订单列表
const fetchCancelableOrders = async () => {
  loading.value = true
  try {
    const response = await axios.get('/trade_records/cancelable-orders')
    orders.value = response.orders || []
  } catch (error) {
    console.error('获取可取消订单失败:', error)
    ElMessage.error('获取可取消订单失败')
    orders.value = []
  } finally {
    loading.value = false
  }
}

// 选择订单
const handleSelectOrder = (order) => {
  emit('select-order', order)
}

// 关闭弹窗
const handleClose = () => {
  dialogVisible.value = false
  orders.value = []
}

// 监听弹窗打开
watch(() => props.modelValue, (newVal) => {
  if (newVal) {
    fetchCancelableOrders()
  }
})
</script>

<style scoped>
.cancel-order-list-dialog :deep(.el-dialog__header) {
  border-bottom: 1px solid #e4e7ed;
  padding: 16px 20px;
  margin-right: 0;
}

.cancel-order-list-dialog :deep(.el-dialog__title) {
  font-size: 18px;
  font-weight: 600;
  color: #f56c6c;
}

.cancel-order-list-dialog :deep(.el-dialog__body) {
  padding: 20px;
}

.order-list-container {
  max-height: 400px;
  overflow-y: auto;
}

.loading-wrapper {
  padding: 20px;
}

.empty-text {
  text-align: center;
}

.empty-text p {
  margin: 0;
  color: #606266;
  font-size: 14px;
}

.empty-subtext {
  color: #909399;
  font-size: 12px;
  margin-top: 8px;
}

.order-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.order-card {
  border: 1px solid #e4e7ed;
  border-radius: 8px;
  padding: 16px;
  transition: all 0.3s;
}

.order-card:hover {
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
}

.order-card.is-in-stock {
  border-color: #f56c6c;
  background-color: #fef0f0;
}

.order-content {
  display: flex;
  align-items: center;
  gap: 12px;
}

.figure-image {
  width: 60px;
  height: 60px;
  border-radius: 4px;
  overflow: hidden;
  flex-shrink: 0;
}

.figure-image .el-image {
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
}

.order-info {
  flex: 1;
  min-width: 0;
}

.figure-name {
  font-size: 15px;
  font-weight: 500;
  color: #303133;
  margin-bottom: 4px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.order-number {
  font-size: 12px;
  color: #909399;
  margin-bottom: 6px;
}

.payment-info {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 4px;
}

.order-type {
  font-size: 11px;
  padding: 2px 6px;
  border-radius: 3px;
  background-color: #ecf5ff;
  color: #409eff;
}

.order-type.现货 {
  background-color: #e6f7ff;
  color: #13c2c2;
}

.order-type.补仓 {
  background-color: #fff7e6;
  color: #fa8c16;
}

.paid-amount {
  font-size: 13px;
  color: #f56c6c;
  font-weight: 500;
}

.stock-warning {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 11px;
  color: #f56c6c;
}

.order-action {
  flex-shrink: 0;
}

.dialog-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.footer-tip {
  font-size: 13px;
  color: #606266;
}

.stock-count {
  color: #f56c6c;
}
</style>
