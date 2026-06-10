<!--
  CreateBuyOrderDrawer.vue - 新增买入订单抽屉组件

  功能说明：
  - 从右侧滑入的抽屉创建新的买入订单
  - 支持四种业务类型：预定、全款预定、现货、补仓
  - 根据订单类型动态切换支付信息表单
  - 支持手办搜索选择和新建

  抽屉规格：
  - 宽度：520px
  - 遮罩层透明度：40%
  - 关闭方式：点击遮罩/点击右上角✕/底部【取消】按钮

  组件依赖：
  - Element Plus 的 Drawer、Form、Input、Select、DatePicker、Button 等组件
  - 需要传入 visible 控制显示

  维护提示：
  - 订单类型切换时动态显示/隐藏字段
  - 补仓类型自动填充平台和备注
-->
<template>
  <el-drawer
    v-model="drawerVisible"
    :size="520"
    :with-header="false"
    :modal="true"
    :modal-class="'create-buy-order-drawer-modal'"
    direction="rtl"
    destroy-on-close
    @close="handleClose"
  >
    <div class="create-buy-order-drawer">
      <!-- 头部区 -->
      <div class="drawer-header">
        <div class="header-top">
          <el-icon class="close-icon" @click="handleClose"><Close /></el-icon>
          <span class="header-title">新增买入订单</span>
        </div>
      </div>

      <!-- 内容区（可滚动） -->
      <div class="drawer-content">
        <el-form
          ref="formRef"
          :model="formData"
          :rules="formRules"
          label-position="top"
          class="order-form"
        >
          <!-- 手办信息 -->
          <div class="form-section">
            <h4 class="section-title">手办信息</h4>
            <el-form-item label="中文名称" prop="figureId">
              <el-select
                v-model="formData.figureId"
                filterable
                remote
                reserve-keyword
                placeholder="请输入手办名称搜索"
                :remote-method="searchFigures"
                :loading="figureLoading"
                style="width: 100%"
              >
                <el-option
                  v-for="item in figureOptions"
                  :key="item.id"
                  :label="item.name"
                  :value="item.id"
                />
                <template #empty>
                  <div class="empty-option">
                    <span>未找到相关手办</span>
                    <el-button type="primary" link @click="goToCreateFigure">
                      去新建手办
                    </el-button>
                  </div>
                </template>
              </el-select>
            </el-form-item>

            <el-form-item label="数量" prop="quantity">
              <el-input-number v-model="formData.quantity" :min="1" :max="99" style="width: 100%" />
            </el-form-item>
          </div>

          <!-- 订单类型 -->
          <div class="form-section">
            <h4 class="section-title">订单类型</h4>
            <el-form-item prop="orderType">
              <div class="order-type-cards">
                <div
                  v-for="type in orderTypes"
                  :key="type.value"
                  :class="['type-card', { active: formData.orderType === type.value }]"
                  @click="selectOrderType(type.value)"
                >
                  <span class="type-name">{{ type.label }}</span>
                </div>
              </div>
            </el-form-item>
          </div>

          <!-- 支付信息 -->
          <div class="form-section">
            <h4 class="section-title">支付信息</h4>

            <!-- 预定/全款预定：显示定金、尾款、尾款到期日、出荷日期 -->
            <template v-if="formData.orderType === '预定' || formData.orderType === '全款预定'">
              <div class="form-row">
                <el-form-item label="定金" prop="deposit" class="form-item-half">
                  <el-input v-model="formData.deposit" placeholder="0.00">
                    <template #prefix>¥</template>
                  </el-input>
                </el-form-item>
                <el-form-item label="尾款" prop="balance" class="form-item-half">
                  <el-input v-model="formData.balance" placeholder="0.00">
                    <template #prefix>¥</template>
                  </el-input>
                </el-form-item>
              </div>
              <el-form-item label="出荷日期" prop="dueDate">
                <el-date-picker
                  v-model="formData.dueDate"
                  type="date"
                  placeholder="选择出荷日期"
                  style="width: 100%"
                  value-format="YYYY-MM-DD"
                />
              </el-form-item>
            </template>

            <!-- 现货/补仓：显示实付金额 -->
            <template v-if="formData.orderType === '现货' || formData.orderType === '补仓'">
              <el-form-item label="实付金额" prop="totalAmount">
                <el-input v-model="formData.totalAmount" placeholder="0.00">
                  <template #prefix>¥</template>
                </el-input>
              </el-form-item>
            </template>
          </div>

          <!-- 物流信息 -->
          <div class="form-section">
            <h4 class="section-title">物流信息</h4>
            <div class="form-row">
              <el-form-item label="快递单号" prop="trackingNumber" class="form-item-half">
                <el-input v-model="formData.trackingNumber" placeholder="选填" />
              </el-form-item>
              <el-form-item label="物流公司" prop="logisticsCompany" class="form-item-half">
                <el-select v-model="formData.logisticsCompany" placeholder="选填" style="width: 100%">
                  <el-option label="顺丰" value="顺丰" />
                  <el-option label="圆通" value="圆通" />
                  <el-option label="中通" value="中通" />
                  <el-option label="韵达" value="韵达" />
                  <el-option label="申通" value="申通" />
                  <el-option label="EMS" value="EMS" />
                  <el-option label="其他" value="其他" />
                </el-select>
              </el-form-item>
            </div>
          </div>

          <!-- 备注 -->
          <div class="form-section">
            <h4 class="section-title">备注</h4>
            <el-form-item prop="remarks">
              <el-input
                v-model="formData.remarks"
                type="textarea"
                :rows="3"
                placeholder="请输入备注信息"
              />
            </el-form-item>
          </div>
        </el-form>
      </div>

      <!-- 底部操作区 -->
      <div class="drawer-footer">
        <el-button @click="handleClose">取消</el-button>
        <el-button type="primary" :loading="submitLoading" @click="handleSubmit">
          确认创建
        </el-button>
      </div>
    </div>
  </el-drawer>
</template>

<script setup>
import { ref, reactive, watch, computed } from 'vue'
import { Close } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import axios from '@/axios'

const props = defineProps({
  visible: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['update:visible', 'success'])

// 抽屉可见性
const drawerVisible = computed({
  get: () => props.visible,
  set: (val) => emit('update:visible', val)
})

// 表单引用
const formRef = ref(null)

// 提交加载状态
const submitLoading = ref(false)

// 手办搜索加载状态
const figureLoading = ref(false)

// 手办选项
const figureOptions = ref([])

// 订单类型选项
const orderTypes = [
  { label: '预定', value: '预定' },
  { label: '全款预定', value: '全款预定' },
  { label: '现货', value: '现货' },
  { label: '补仓', value: '补仓' }
]

// 表单数据
const formData = reactive({
  figureId: null,
  quantity: 1,
  orderType: '预定',
  deposit: '',
  balance: '',
  dueDate: '',
  totalAmount: '',
  trackingNumber: '',
  logisticsCompany: '',
  remarks: ''
})

// 表单验证规则
const formRules = {
  figureId: [{ required: true, message: '请选择手办', trigger: 'change' }],
  quantity: [{ required: true, message: '请输入数量', trigger: 'blur' }],
  orderType: [{ required: true, message: '请选择订单类型', trigger: 'change' }],
  deposit: [{ required: true, message: '请输入定金', trigger: 'blur' }],
  balance: [{ required: true, message: '请输入尾款', trigger: 'blur' }],
  dueDate: [{ required: true, message: '请选择出荷日期', trigger: 'change' }],
  totalAmount: [{ required: true, message: '请输入实付金额', trigger: 'blur' }]
}

// 搜索手办
const searchFigures = async (query) => {
  if (query.length < 1) return
  figureLoading.value = true
  try {
    const response = await axios.get('/figures/search', {
      params: { keyword: query }
    })
    figureOptions.value = response || []
  } catch (error) {
    console.error('搜索手办失败:', error)
  } finally {
    figureLoading.value = false
  }
}

// 跳转到新建手办页面
const goToCreateFigure = () => {
  window.open('/figures', '_blank')
}

// 选择订单类型
const selectOrderType = (type) => {
  formData.orderType = type

  // 补仓特殊处理
  if (type === '补仓') {
    const now = new Date()
    const dateStr = now.toLocaleString('zh-CN', {
      year: 'numeric',
      month: '2-digit',
      day: '2-digit',
      hour: '2-digit',
      minute: '2-digit'
    }).replace(/\//g, '-')
    const amount = formData.totalAmount || '0'
    formData.remarks = `${dateStr} 花费¥${amount} 补仓购入`
  } else {
    formData.remarks = ''
  }
}

// 关闭抽屉
const handleClose = () => {
  drawerVisible.value = false
  resetForm()
}

// 重置表单
const resetForm = () => {
  formData.figureId = null
  formData.quantity = 1
  formData.orderType = '预定'
  formData.deposit = ''
  formData.balance = ''
  formData.dueDate = ''
  formData.totalAmount = ''
  formData.trackingNumber = ''
  formData.logisticsCompany = ''
  formData.remarks = ''
  figureOptions.value = []
}

// 提交表单
const handleSubmit = async () => {
  const valid = await formRef.value.validate().catch(() => false)
  if (!valid) return

  submitLoading.value = true
  try {
    // 构建请求数据
    const payload = {
      figure_id: formData.figureId,
      quantity: formData.quantity,
      order_type: formData.orderType,
      tracking_number: formData.trackingNumber,
      logistics_company: formData.logisticsCompany,
      remarks: formData.remarks
    }

    // 根据订单类型添加不同的字段
    if (formData.orderType === '预定' || formData.orderType === '全款预定') {
      payload.deposit = parseFloat(formData.deposit)
      payload.balance = parseFloat(formData.balance)
      payload.due_date = formData.dueDate
    } else {
      payload.total_amount = parseFloat(formData.totalAmount)
    }

    await axios.post('/trade_records/buy-orders', payload)
    ElMessage.success('订单创建成功')
    emit('success')
    handleClose()
  } catch (error) {
    console.error('创建订单失败:', error)
    ElMessage.error(error.response?.data?.detail || '创建订单失败')
  } finally {
    submitLoading.value = false
  }
}

// 监听实付金额变化，更新补仓备注
watch(() => formData.totalAmount, (newVal) => {
  if (formData.orderType === '补仓' && newVal) {
    const now = new Date()
    const dateStr = now.toLocaleString('zh-CN', {
      year: 'numeric',
      month: '2-digit',
      day: '2-digit',
      hour: '2-digit',
      minute: '2-digit'
    }).replace(/\//g, '-')
    formData.remarks = `${dateStr} 花费¥${newVal} 补仓购入`
  }
})
</script>

<style scoped>
.create-buy-order-drawer {
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
  font-size: 18px;
  font-weight: 600;
  color: #333;
}

/* 内容区 */
.drawer-content {
  flex: 1;
  overflow-y: auto;
  padding: 20px;
}

.form-section {
  margin-bottom: 24px;
}

.section-title {
  font-size: 14px;
  font-weight: 600;
  color: #333;
  margin: 0 0 16px 0;
  padding-bottom: 8px;
  border-bottom: 1px solid #f0f0f0;
}

.form-row {
  display: flex;
  gap: 16px;
}

.form-item-half {
  flex: 1;
}

/* 订单类型卡片 */
.order-type-cards {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 12px;
}

.type-card {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 12px 8px;
  border: 1px solid #d9d9d9;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.2s;
  background-color: #fff;
}

.type-card:hover {
  border-color: #1890ff;
  color: #1890ff;
}

.type-card.active {
  background-color: #e6f7ff;
  border-color: #1890ff;
  color: #1890ff;
}

.type-name {
  font-size: 14px;
  font-weight: 500;
}

/* 空选项 */
.empty-option {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 16px;
  gap: 8px;
}

.empty-option span {
  color: #999;
  font-size: 14px;
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

/* 表单样式调整 */
:deep(.el-form-item__label) {
  font-weight: 500;
  color: #333;
}

:deep(.el-input__wrapper) {
  box-shadow: 0 0 0 1px #d9d9d9 inset;
}

:deep(.el-input__wrapper:hover) {
  box-shadow: 0 0 0 1px #1890ff inset;
}

:deep(.el-textarea__inner) {
  box-shadow: 0 0 0 1px #d9d9d9 inset;
}

:deep(.el-textarea__inner:hover) {
  box-shadow: 0 0 0 1px #1890ff inset;
}
</style>
