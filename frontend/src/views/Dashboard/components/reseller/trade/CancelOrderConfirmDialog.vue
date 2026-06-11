<template>
  <el-dialog
    v-model="dialogVisible"
    title="⚠️ 取消订单"
    width="480px"
    :close-on-click-modal="false"
    destroy-on-close
    class="cancel-order-confirm-dialog"
    @close="handleClose"
  >
    <div v-if="loading" class="loading-wrapper">
      <el-skeleton :rows="5" animated />
    </div>

    <div v-else-if="orderData" class="confirm-content">
      <!-- 订单信息 -->
      <div class="order-info-card">
        <div class="info-row">
          <span class="info-label">订单</span>
          <span class="info-value">{{ orderData.order_number }}  {{ orderData.figure_name }}</span>
        </div>
        <div class="info-row">
          <span class="info-label">当前状态</span>
          <span class="info-value status-text">{{ orderData.status_text }}</span>
        </div>
      </div>

      <el-divider />

      <!-- 取消后操作 -->
      <div class="cancel-options">
        <div class="option-label">取消后操作:</div>

        <!-- 退款选项 -->
        <div class="refund-options">
          <!-- 预定单：可选退定金或不退 -->
          <template v-if="orderData.is_preorder && !orderData.is_full_payment">
            <el-radio-group v-model="refundOption" class="refund-radio-group">
              <el-radio label="keep">
                仅取消，保留定金（违约损失）
              </el-radio>
              <el-radio label="refund">
                取消并申请退款（退还已支付金额）
              </el-radio>
            </el-radio-group>
          </template>

          <!-- 全款现货/补仓：必须全额退款 -->
          <template v-else>
            <div class="must-refund-notice">
              <el-icon><InfoFilled /></el-icon>
              <span>该订单为{{ orderData.order_type }}，取消后将全额退款</span>
            </div>
          </template>
        </div>

        <!-- 退款金额和方式 -->
        <div v-if="showRefundForm" class="refund-form">
          <div class="refund-amount">
            <span class="label">退款金额:</span>
            <span class="amount">¥{{ actualRefundAmount }}</span>
          </div>

          <div class="refund-method">
            <span class="label">退款方式:</span>
            <el-select v-model="refundMethod" size="small" style="width: 140px">
              <el-option label="原路退回" value="原路退回" />
              <el-option label="支付宝" value="支付宝" />
              <el-option label="微信支付" value="微信支付" />
              <el-option label="银行卡" value="银行卡" />
            </el-select>
          </div>
        </div>
      </div>

      <!-- 库存回滚警告 -->
      <div v-if="orderData.is_in_stock" class="stock-warning-box">
        <el-icon class="warning-icon"><Warning /></el-icon>
        <span>该手办已入库，取消将同步扣减库存 {{ orderData.stock_quantity }}体</span>
      </div>

      <!-- 二次确认 -->
      <div v-if="showDoubleConfirm" class="double-confirm">
        <el-divider />
        <div class="confirm-input">
          <span class="label">请输入"确认取消"以继续:</span>
          <el-input
            v-model="confirmText"
            placeholder="确认取消"
            size="small"
            style="width: 150px; margin-left: 8px;"
          />
        </div>
      </div>
    </div>

    <template #footer>
      <div class="dialog-footer">
        <el-button @click="handleClose">再想想</el-button>
        <el-button
          type="danger"
          :loading="submitLoading"
          :disabled="!canSubmit"
          @click="handleSubmit"
        >
          {{ submitButtonText }}
        </el-button>
      </div>
    </template>
  </el-dialog>
</template>

<script setup>
/**
 * CancelOrderConfirmDialog - 撤单确认弹窗
 *
 * 功能说明：
 * - 展示订单取消详情
 * - 支持选择退款选项（预定单可选退定金或不退）
 * - 全款现货/补仓必须全额退款
 * - 已入库订单显示库存回滚警告
 * - 高危险操作需二次确认
 *
 * 维护提示：
 * - 预定单（有定金）可以选择是否退定金
 * - 全款现货/补仓必须全额退款
 * - 已入库订单取消时会回滚库存
 */
import { ref, computed, watch } from 'vue'
import { ElMessage } from 'element-plus'
import { Warning, InfoFilled } from '@element-plus/icons-vue'
import axios from '@/axios'

const props = defineProps({
  modelValue: {
    type: Boolean,
    default: false
  },
  order: {
    type: Object,
    default: null
  }
})

const emit = defineEmits(['update:modelValue', 'success'])

// 对话框可见性
const dialogVisible = computed({
  get: () => props.modelValue,
  set: (val) => emit('update:modelValue', val)
})

// 数据状态
const orderData = ref(null)
const loading = ref(false)
const submitLoading = ref(false)

// 表单数据
const refundOption = ref('refund') // 'keep' | 'refund'
const refundMethod = ref('原路退回')
const confirmText = ref('')

// 是否显示退款表单
const showRefundForm = computed(() => {
  if (!orderData.value) return false
  // 全款现货/补仓必须退款
  if (orderData.value.is_full_payment) return true
  // 预定单根据选项决定
  return refundOption.value === 'refund'
})

// 实际退款金额
const actualRefundAmount = computed(() => {
  if (!orderData.value) return 0
  if (!showRefundForm.value) return 0
  return orderData.value.refund_amount || 0
})

// 是否显示二次确认
const showDoubleConfirm = computed(() => {
  // 已入库订单或退款金额较大时需要二次确认
  if (!orderData.value) return false
  return orderData.value.is_in_stock || actualRefundAmount.value >= 500
})

// 是否可以提交
const canSubmit = computed(() => {
  if (!orderData.value) return false
  if (showDoubleConfirm.value) {
    return confirmText.value === '确认取消'
  }
  return true
})

// 提交按钮文本
const submitButtonText = computed(() => {
  if (submitLoading.value) return '取消中...'
  if (showDoubleConfirm.value) {
    return confirmText.value === '确认取消' ? '确认取消订单' : '请输入确认文字'
  }
  return '确认取消订单'
})

// 获取订单取消详情
const fetchOrderDetail = async () => {
  if (!props.order?.order_id) return

  loading.value = true
  try {
    const response = await axios.get(`/trade_records/cancelable-orders/${props.order.order_id}`)
    orderData.value = response

    // 初始化表单
    if (response.is_full_payment) {
      refundOption.value = 'refund'
    } else {
      refundOption.value = 'refund'
    }
    refundMethod.value = '原路退回'
    confirmText.value = ''
  } catch (error) {
    console.error('获取订单取消详情失败:', error)
    ElMessage.error(error.response?.data?.error || '获取订单取消详情失败')
    handleClose()
  } finally {
    loading.value = false
  }
}

// 提交取消
const handleSubmit = async () => {
  if (!orderData.value?.order_id) {
    ElMessage.error('订单信息缺失')
    return
  }

  submitLoading.value = true
  try {
    const payload = {
      refund: showRefundForm.value,
      refund_amount: actualRefundAmount.value,
      refund_method: refundMethod.value,
      reason: '用户主动取消'
    }

    await axios.post(`/trade_records/cancel-order/${orderData.value.order_id}`, payload)

    ElMessage.success('订单取消成功')
    emit('success')
    handleClose()
  } catch (error) {
    console.error('取消订单失败:', error)
    ElMessage.error(error.response?.data?.error || '取消订单失败')
  } finally {
    submitLoading.value = false
  }
}

// 关闭弹窗
const handleClose = () => {
  dialogVisible.value = false
  orderData.value = null
  refundOption.value = 'refund'
  refundMethod.value = '原路退回'
  confirmText.value = ''
}

// 监听弹窗打开和订单变化
watch(() => props.modelValue, (newVal) => {
  if (newVal && props.order) {
    fetchOrderDetail()
  }
})

watch(() => props.order, (newVal) => {
  if (newVal && dialogVisible.value) {
    fetchOrderDetail()
  }
})
</script>

<style scoped>
.cancel-order-confirm-dialog :deep(.el-dialog__header) {
  border-bottom: 1px solid #fde2e2;
  padding: 16px 20px;
  margin-right: 0;
  background-color: #fef0f0;
}

.cancel-order-confirm-dialog :deep(.el-dialog__title) {
  font-size: 18px;
  font-weight: 600;
  color: #f56c6c;
}

.cancel-order-confirm-dialog :deep(.el-dialog__body) {
  padding: 20px;
}

.loading-wrapper {
  padding: 20px;
}

.confirm-content {
  min-height: 200px;
}

.order-info-card {
  background-color: #f5f7fa;
  border-radius: 8px;
  padding: 16px;
  margin-bottom: 16px;
}

.info-row {
  display: flex;
  margin-bottom: 8px;
}

.info-row:last-child {
  margin-bottom: 0;
}

.info-label {
  width: 80px;
  color: #606266;
  font-size: 14px;
}

.info-value {
  flex: 1;
  color: #303133;
  font-size: 14px;
  font-weight: 500;
}

.status-text {
  color: #e6a23c;
}

.cancel-options {
  margin-bottom: 16px;
}

.option-label {
  font-size: 14px;
  font-weight: 500;
  color: #303133;
  margin-bottom: 12px;
}

.refund-radio-group {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.refund-radio-group :deep(.el-radio) {
  height: auto;
  line-height: 1.5;
  white-space: normal;
  align-items: flex-start;
}

.must-refund-notice {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px;
  background-color: #fdf6ec;
  border-radius: 4px;
  color: #e6a23c;
  font-size: 13px;
}

.refund-form {
  margin-top: 16px;
  padding: 16px;
  background-color: #f5f7fa;
  border-radius: 8px;
}

.refund-amount {
  display: flex;
  align-items: center;
  margin-bottom: 12px;
}

.refund-amount .label {
  width: 80px;
  color: #606266;
  font-size: 14px;
}

.refund-amount .amount {
  font-size: 20px;
  font-weight: 600;
  color: #f56c6c;
}

.refund-method {
  display: flex;
  align-items: center;
}

.refund-method .label {
  width: 80px;
  color: #606266;
  font-size: 14px;
}

.stock-warning-box {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px 16px;
  background-color: #fef0f0;
  border: 1px solid #fde2e2;
  border-radius: 8px;
  color: #f56c6c;
  font-size: 13px;
}

.warning-icon {
  font-size: 16px;
}

.double-confirm {
  margin-top: 16px;
}

.confirm-input {
  display: flex;
  align-items: center;
}

.confirm-input .label {
  color: #f56c6c;
  font-size: 13px;
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
}
</style>
