<!--
  PayBalanceConfirmDrawer.vue - 支付尾款确认抽屉组件

  功能说明：
  - 展示订单支付详情（Step 2）
  - 支持选择支付方式和支付时间
  - 支持部分支付（输入本次支付金额）
  - 确认支付后更新订单状态并入库

  组件依赖：
  - Element Plus 的 Drawer、Form、Input、Select、DatePicker、Button 等组件
  - 需要传入 visible 和 order 控制显示和数据

  维护提示：
  - 支付金额默认为剩余尾款
  - 支持部分支付，输入金额不能大于尾款
-->
<template>
  <el-drawer
    v-model="drawerVisible"
    :size="480"
    :with-header="false"
    :modal="true"
    :modal-class="'pay-balance-confirm-drawer-modal'"
    direction="rtl"
    destroy-on-close
    @close="handleClose"
  >
    <div class="pay-balance-confirm-drawer">
      <!-- 头部区 -->
      <div class="drawer-header">
        <div class="header-top">
          <el-icon class="close-icon" @click="handleClose"><Close /></el-icon>
          <span class="header-title">支付尾款 - {{ orderData?.figure_name || '' }}</span>
        </div>
      </div>

      <!-- 内容区（可滚动） -->
      <div class="drawer-content">
        <!-- 订单信息卡片 -->
        <div class="order-info-card">
          <div class="info-row">
            <span class="info-label">订单编号</span>
            <span class="info-value">{{ orderData?.order_number || '-' }}</span>
          </div>
          <div class="info-row">
            <span class="info-label">尾款金额</span>
            <span class="info-value highlight">
              ¥{{ orderData?.balance || 0 }}
            </span>
          </div>
          <div v-if="orderData?.is_overdue" class="info-row">
            <span class="info-label">到期状态</span>
            <span class="info-value overdue">{{ orderData?.due_text }}</span>
          </div>
        </div>

        <!-- 支付表单 -->
        <el-form
          ref="formRef"
          :model="formData"
          :rules="formRules"
          label-position="top"
          class="payment-form"
        >
          <!-- 本次支付金额 -->
          <el-form-item label="本次支付金额" prop="amount">
            <el-input
              v-model="formData.amount"
              placeholder="请输入支付金额"
              :disabled="isFullPayment"
            >
              <template #prefix>¥</template>
            </el-input>
            <div class="form-tip">
              <el-checkbox v-model="isFullPayment" size="small">
                全额支付 ¥{{ orderData?.balance || 0 }}
              </el-checkbox>
            </div>
          </el-form-item>

          <!-- 支付方式 -->
          <el-form-item label="支付方式" prop="paymentMethod">
            <el-select
              v-model="formData.paymentMethod"
              placeholder="请选择支付方式"
              style="width: 100%"
            >
              <el-option label="支付宝" value="支付宝" />
              <el-option label="微信支付" value="微信支付" />
              <el-option label="银行卡" value="银行卡" />
              <el-option label="信用卡" value="信用卡" />
              <el-option label="其他" value="其他" />
            </el-select>
          </el-form-item>

          <!-- 支付时间 -->
          <el-form-item label="支付时间" prop="paymentDate">
            <el-date-picker
              v-model="formData.paymentDate"
              type="datetime"
              placeholder="选择支付时间"
              style="width: 100%"
              format="YYYY-MM-DD HH:mm"
              value-format="YYYY-MM-DD HH:mm"
            />
          </el-form-item>
        </el-form>

        <!-- 提示信息 -->
        <div class="payment-tips">
          <el-divider />
          <div class="tip-content">
            <el-icon><InfoFilled /></el-icon>
            <span>支付后该订单将标记为【已完成】并入库</span>
          </div>
          <div v-if="!isFullPayment && remainingAmount > 0" class="tip-content warning">
            <el-icon><Warning /></el-icon>
            <span>本次支付后，剩余尾款 ¥{{ remainingAmount }} 将在订单中保留</span>
          </div>
        </div>
      </div>

      <!-- 底部操作区 -->
      <div class="drawer-footer">
        <el-button @click="handleClose">取消</el-button>
        <el-button
          type="primary"
          :loading="submitLoading"
          @click="handleSubmit"
        >
          确认支付 ¥{{ actualPaymentAmount }}
        </el-button>
      </div>
    </div>
  </el-drawer>
</template>

<script setup>
import { ref, reactive, computed, watch } from 'vue'
import { Close, InfoFilled, Warning } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import axios from '@/axios'

const props = defineProps({
  visible: {
    type: Boolean,
    default: false
  },
  order: {
    type: Object,
    default: null
  }
})

const emit = defineEmits(['update:visible', 'success', 'close'])

// 抽屉可见性
const drawerVisible = computed({
  get: () => props.visible,
  set: (val) => emit('update:visible', val)
})

// 订单数据
const orderData = computed(() => props.order)

// 表单引用
const formRef = ref(null)

// 提交加载状态
const submitLoading = ref(false)

// 是否全额支付
const isFullPayment = ref(true)

// 表单数据
const formData = reactive({
  amount: '',
  paymentMethod: '支付宝',
  paymentDate: ''
})

// 实际支付金额
const actualPaymentAmount = computed(() => {
  if (isFullPayment.value) {
    return orderData.value?.balance || 0
  }
  const amount = parseFloat(formData.amount) || 0
  return amount
})

// 剩余金额（部分支付时）
const remainingAmount = computed(() => {
  const totalBalance = orderData.value?.balance || 0
  const paidAmount = parseFloat(formData.amount) || 0
  return Math.max(0, totalBalance - paidAmount)
})

// 表单验证规则
const formRules = {
  amount: [
    { required: true, message: '请输入支付金额', trigger: 'blur' },
    {
      validator: (rule, value, callback) => {
        if (isFullPayment.value) {
          callback()
          return
        }
        const amount = parseFloat(value)
        if (isNaN(amount) || amount <= 0) {
          callback(new Error('支付金额必须大于0'))
        } else if (amount > (orderData.value?.balance || 0)) {
          callback(new Error(`支付金额不能超过尾款金额 ¥${orderData.value?.balance || 0}`))
        } else {
          callback()
        }
      },
      trigger: 'blur'
    }
  ],
  paymentMethod: [
    { required: true, message: '请选择支付方式', trigger: 'change' }
  ],
  paymentDate: [
    { required: true, message: '请选择支付时间', trigger: 'change' }
  ]
}

// 初始化表单数据
const initFormData = () => {
  if (orderData.value) {
    formData.amount = String(orderData.value.balance || 0)
  } else {
    formData.amount = ''
  }
  formData.paymentMethod = '支付宝'
  formData.paymentDate = formatDateTime(new Date())
  isFullPayment.value = true
}

// 格式化日期时间
const formatDateTime = (date) => {
  const year = date.getFullYear()
  const month = String(date.getMonth() + 1).padStart(2, '0')
  const day = String(date.getDate()).padStart(2, '0')
  const hours = String(date.getHours()).padStart(2, '0')
  const minutes = String(date.getMinutes()).padStart(2, '0')
  return `${year}-${month}-${day} ${hours}:${minutes}`
}

// 关闭抽屉
const handleClose = () => {
  drawerVisible.value = false
  emit('close')
}

// 提交表单
const handleSubmit = async () => {
  const valid = await formRef.value.validate().catch(() => false)
  if (!valid) return

  if (!orderData.value?.order_id) {
    ElMessage.error('订单信息缺失')
    return
  }

  submitLoading.value = true
  try {
    const payload = {
      payment_method: formData.paymentMethod,
      payment_date: formData.paymentDate,
      amount: actualPaymentAmount.value
    }

    await axios.post(`/trade_records/pay-balance/${orderData.value.order_id}`, payload)

    ElMessage.success('尾款支付成功')
    emit('success')
    handleClose()
  } catch (error) {
    console.error('支付尾款失败:', error)
    ElMessage.error(error.response?.data?.detail || '支付尾款失败')
  } finally {
    submitLoading.value = false
  }
}

// 监听全额支付选项变化
watch(isFullPayment, (newVal) => {
  if (newVal && orderData.value) {
    formData.amount = String(orderData.value.balance || 0)
  }
})

// 监听抽屉显示，初始化数据
watch(() => props.visible, (newVal) => {
  if (newVal) {
    initFormData()
  }
})
</script>

<style scoped>
.pay-balance-confirm-drawer {
  display: flex;
  flex-direction: column;
  height: 100%;
}

/* 头部区 */
.drawer-header {
  padding: 16px 20px;
  border-bottom: 1px solid #e8e8e8;
  flex-shrink: 0;
}

.header-top {
  display: flex;
  align-items: center;
  gap: 12px;
}

.close-icon {
  font-size: 20px;
  cursor: pointer;
  color: #666;
  transition: color 0.2s;
}

.close-icon:hover {
  color: #333;
}

.header-title {
  font-size: 16px;
  font-weight: 600;
  color: #333;
}

/* 内容区 */
.drawer-content {
  flex: 1;
  overflow-y: auto;
  padding: 20px;
}

/* 订单信息卡片 */
.order-info-card {
  background-color: #f5f7fa;
  border-radius: 8px;
  padding: 16px;
  margin-bottom: 24px;
}

.info-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.info-row:last-child {
  margin-bottom: 0;
}

.info-label {
  font-size: 14px;
  color: #606266;
}

.info-value {
  font-size: 14px;
  color: #303133;
  font-weight: 500;
}

.info-value.highlight {
  color: #f56c6c;
  font-size: 18px;
  font-weight: 600;
}

.info-value.overdue {
  color: #f56c6c;
}

/* 支付表单 */
.payment-form {
  margin-bottom: 16px;
}

.form-tip {
  margin-top: 8px;
}

/* 提示信息 */
.payment-tips {
  margin-top: 8px;
}

.tip-content {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 13px;
  color: #606266;
  margin-bottom: 8px;
}

.tip-content.warning {
  color: #e6a23c;
}

.tip-content .el-icon {
  font-size: 16px;
  color: #909399;
}

.tip-content.warning .el-icon {
  color: #e6a23c;
}

/* 底部操作区 */
.drawer-footer {
  padding: 16px 20px;
  border-top: 1px solid #e8e8e8;
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  flex-shrink: 0;
}
</style>
