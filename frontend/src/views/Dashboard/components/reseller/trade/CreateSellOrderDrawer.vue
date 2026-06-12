<!--
  CreateSellOrderDrawer.vue - 标记转卖抽屉组件

  功能说明：
  - 从右侧滑入的抽屉创建卖出订单
  - 从库存中选择手办（仅显示 quantity>0 的）
  - 自动计算净利润预览
  - 支持填写卖出平台、单价、运费、手续费等信息

  抽屉规格：
  - 宽度：520px
  - 遮罩层透明度：40%
  - 关闭方式：点击遮罩/点击右上角✕/底部【取消】按钮

  组件依赖：
  - Element Plus 的 Drawer、Form、Input、Select、Button 等组件
  - 需要传入 visible 控制显示

  维护提示：
  - 选择手办后自动填充成本价和库存数量
  - 数量不能超过库存
  - 自动计算实到账和净利润预览
-->
<template>
  <el-drawer
    v-model="drawerVisible"
    :size="520"
    :with-header="false"
    :modal="true"
    :modal-class="'create-sell-order-drawer-modal'"
    direction="rtl"
    destroy-on-close
    @close="handleClose"
  >
    <div class="create-sell-order-drawer">
      <!-- 头部区 -->
      <div class="drawer-header">
        <div class="header-top">
          <el-icon class="close-icon" @click="handleClose"><Close /></el-icon>
          <span class="header-title">标记转卖</span>
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
          <!-- 选择库存手办 -->
          <div class="form-section">
            <h4 class="section-title">选择库存手办</h4>
            <el-form-item prop="figureId">
              <el-select
                v-model="formData.figureId"
                filterable
                placeholder="请选择库存手办"
                style="width: 100%"
                popper-class="inventory-figure-dropdown"
                @change="handleFigureChange"
              >
                <el-option
                  v-for="item in inventoryOptions"
                  :key="item.id"
                  :label="`${item.name} (库存: ${item.quantity}体)`"
                  :value="item.id"
                >
                  <div class="figure-option">
                    <el-image
                      v-if="item.image_url"
                      :src="item.image_url"
                      class="figure-thumb"
                      fit="cover"
                    />
                    <div v-else class="figure-thumb placeholder">
                      <el-icon><Picture /></el-icon>
                    </div>
                    <div class="figure-info">
                      <div class="figure-name">{{ item.name }}</div>
                      <div class="figure-stock">库存: {{ item.quantity }}体</div>
                    </div>
                  </div>
                </el-option>
                <template #empty>
                  <div class="empty-option">
                    <span>暂无库存手办</span>
                  </div>
                </template>
              </el-select>
            </el-form-item>

            <!-- 数量选择 -->
            <el-form-item label="数量" prop="quantity">
              <el-input-number
                v-model="formData.quantity"
                :min="1"
                :max="maxQuantity"
                :disabled="!selectedFigure"
                style="width: 100%"
              />
              <div v-if="selectedFigure" class="quantity-hint">
                最多可卖出 {{ maxQuantity }} 体
              </div>
            </el-form-item>
          </div>

          <!-- 成交信息 -->
          <div class="form-section">
            <h4 class="section-title">成交信息</h4>
            <el-form-item label="卖出平台" prop="sellPlatform">
              <el-select
                v-model="formData.sellPlatform"
                placeholder="请选择卖出平台"
                style="width: 100%"
                @change="handlePlatformChange"
              >
                <el-option label="闲鱼（个人卖家）" value="闲鱼（个人卖家）" />
                <el-option label="闲鱼（鱼小铺）" value="闲鱼（鱼小铺）" />
                <el-option label="淘宝" value="淘宝" />
                <el-option label="转转" value="转转" />
                <el-option label="微信群" value="微信群" />
                <el-option label="QQ群" value="QQ群" />
                <el-option label="快速卖出" value="快速卖出" />
                <el-option label="其他" value="其他" />
              </el-select>
            </el-form-item>

            <el-form-item label="卖出单价" prop="sellPrice">
              <el-input v-model="formData.sellPrice" placeholder="0.00" @input="handlePriceChange">
                <template #prefix>¥</template>
              </el-input>
            </el-form-item>

            <el-form-item label="运费" prop="shippingFee">
              <el-input v-model="formData.shippingFee" placeholder="0.00" @input="calculateProfit">
                <template #prefix>¥</template>
              </el-input>
            </el-form-item>

            <el-form-item label="平台手续费" prop="platformFee">
              <el-input v-model="formData.platformFee" placeholder="0.00" @input="calculateProfit">
                <template #prefix>¥</template>
              </el-input>
            </el-form-item>

            <!-- 分割线 -->
            <div class="divider"></div>

            <!-- 计算结果 -->
            <div class="calculation-result">
              <div class="result-item">
                <span class="result-label">实到账:</span>
                <span class="result-value">¥{{ formatPrice(actualAmount) }}</span>
              </div>
              <div class="result-item">
                <span class="result-label">净利润预览:</span>
                <span :class="['result-value', 'profit', netProfit >= 0 ? 'positive' : 'negative']">
                  {{ netProfit >= 0 ? '+' : '' }}¥{{ formatPrice(netProfit) }}
                </span>
              </div>
            </div>
          </div>

          <!-- 买家信息 -->
          <div class="form-section">
            <h4 class="section-title">买家信息</h4>
            <div class="form-row">
              <el-form-item label="手机号" prop="buyerPhone" class="form-item-half">
                <el-input v-model="formData.buyerPhone" placeholder="选填" />
              </el-form-item>
              <el-form-item label="地址" prop="buyerAddress" class="form-item-half">
                <el-input v-model="formData.buyerAddress" placeholder="选填" />
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
                placeholder="选填，可填写其他相关信息"
              />
            </el-form-item>
          </div>
        </el-form>
      </div>

      <!-- 底部操作区 -->
      <div class="drawer-footer">
        <el-button @click="handleClose">取消</el-button>
        <el-button
          type="primary"
          :loading="submitLoading"
          @click="handleSubmit"
        >
          确认卖出
        </el-button>
      </div>
    </div>
  </el-drawer>
</template>

<script setup>
import { ref, reactive, computed, watch } from 'vue'
import { Close, Picture } from '@element-plus/icons-vue'
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

// 库存选项
const inventoryOptions = ref([])

// 选中的手办
const selectedFigure = computed(() => {
  return inventoryOptions.value.find(item => item.id === formData.figureId)
})

// 最大可卖出数量
const maxQuantity = computed(() => {
  return selectedFigure.value?.quantity || 1
})

// 表单数据
const formData = reactive({
  figureId: null,
  quantity: 1,
  sellPlatform: '闲鱼（鱼小铺）',
  sellPrice: '',
  shippingFee: '0',
  platformFee: '0',
  buyerPhone: '',
  buyerAddress: '',
  remarks: ''
})

// 计算结果
const actualAmount = ref(0)
const netProfit = ref(0)

// 表单验证规则
const formRules = {
  figureId: [{ required: true, message: '请选择库存手办', trigger: 'change' }],
  quantity: [{ required: true, message: '请输入数量', trigger: 'blur' }],
  sellPlatform: [{ required: true, message: '请选择卖出平台', trigger: 'change' }],
  sellPrice: [{ required: true, message: '请输入卖出单价', trigger: 'blur' }]
}

// 获取库存列表
const fetchInventory = async () => {
  try {
    const response = await axios.get('/assets/holdings', {
      params: { has_stock: true }
    })
    inventoryOptions.value = response || []
  } catch (error) {
    console.error('获取库存列表失败:', error)
    ElMessage.error('获取库存列表失败')
  }
}

// 处理手办选择变化
const handleFigureChange = (figureId) => {
  formData.quantity = 1
  // 选择手办后重新计算手续费（使用当前选中的平台）
  handlePlatformChange(formData.sellPlatform)
}

// 处理价格变化（重新计算手续费）
const handlePriceChange = () => {
  // 修改卖出单价后重新计算手续费（使用当前选中的平台）
  handlePlatformChange(formData.sellPlatform)
}

// 处理平台变化（自动计算手续费）
const handlePlatformChange = async (platform) => {
  const sellPrice = parseFloat(formData.sellPrice || 0)
  if (!platform || !formData.quantity || sellPrice <= 0) {
    formData.platformFee = '0'
    calculateProfit()
    return
  }

  if (platform === '闲鱼（鱼小铺）') {
    // 鱼小铺固定费率 1.6%，上不封顶
    const fee = sellPrice * formData.quantity * 0.016
    formData.platformFee = fee.toFixed(2)
    calculateProfit()
    return
  }

  if (platform === '闲鱼（个人卖家）') {
    // 个人卖家：基础费率 0.6%，单笔最高 60 元封顶
    // 当月订单>10笔且成交额>1万元后，超出部分加收 1%
    const totalSellPrice = sellPrice * formData.quantity
    const baseRate = 0.006
    const baseFee = totalSellPrice * baseRate
    let totalFee = Math.min(baseFee, 60)

    try {
      const stats = await axios.get('/sold_orders/xianyu-monthly-stats/')
      const monthlyOrderCount = stats.order_count || 0
      const monthlyAmount = stats.total_amount || 0
      const exceedsThreshold = monthlyOrderCount > 10 && monthlyAmount > 10000

      if (exceedsThreshold) {
        const extraRate = 0.01
        totalFee = totalSellPrice * (baseRate + extraRate)
      }
    } catch (error) {
      // 获取统计失败，使用基础费率（已封顶60元）
    }

    formData.platformFee = (Math.round(totalFee * 100) / 100).toFixed(2)
    calculateProfit()
    return
  }

  // 其他平台：手续费为0
  formData.platformFee = '0'
  calculateProfit()
}

// 计算利润
const calculateProfit = () => {
  const sellPrice = parseFloat(formData.sellPrice || 0)
  const quantity = formData.quantity || 0
  const shippingFee = parseFloat(formData.shippingFee || 0)
  const platformFee = parseFloat(formData.platformFee || 0)
  const costPrice = selectedFigure.value?.cost_price || 0

  const totalSellPrice = sellPrice * quantity
  const totalCost = costPrice * quantity

  // 实到账 = 总卖出价 - 运费 - 平台手续费
  actualAmount.value = totalSellPrice - shippingFee - platformFee

  // 净利润 = 实到账 - 总成本
  netProfit.value = actualAmount.value - totalCost
}

// 格式化价格
const formatPrice = (price) => {
  if (price === undefined || price === null) return '0.00'
  return parseFloat(price).toFixed(2)
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
  formData.sellPlatform = '闲鱼（鱼小铺）'
  formData.sellPrice = ''
  formData.shippingFee = '0'
  formData.platformFee = '0'
  formData.buyerPhone = ''
  formData.buyerAddress = ''
  formData.remarks = ''
  actualAmount.value = 0
  netProfit.value = 0
  if (formRef.value) {
    formRef.value.resetFields()
  }
}

// 提交表单
const handleSubmit = async () => {
  const valid = await formRef.value.validate().catch(() => false)
  if (!valid) return

  submitLoading.value = true
  try {
    const figure = selectedFigure.value
    const payload = {
      figure_id: formData.figureId,
      figure_name: figure?.name || '',
      quantity: formData.quantity,
      sell_price: parseFloat(formData.sellPrice),
      cost_price: figure?.cost_price || 0,
      shipping_fee: parseFloat(formData.shippingFee || 0),
      platform_fee: parseFloat(formData.platformFee || 0),
      sell_platform: formData.sellPlatform,
      buyer_phone: formData.buyerPhone,
      buyer_address: formData.buyerAddress,
      remarks: formData.remarks
    }

    await axios.post('/sold-orders/create-from-inventory', payload)
    ElMessage.success('卖出订单创建成功')
    emit('success')
    handleClose()
  } catch (error) {
    console.error('创建卖出订单失败:', error)
    ElMessage.error(error.response?.data?.detail || '创建卖出订单失败')
  } finally {
    submitLoading.value = false
  }
}

// 监听抽屉显示状态
watch(() => props.visible, (newVal) => {
  if (newVal) {
    fetchInventory()
  }
})

// 监听数量变化，重新计算利润
watch(() => formData.quantity, calculateProfit)
</script>

<style scoped>
.create-sell-order-drawer {
  display: flex;
  flex-direction: column;
  height: 100%;
}

.drawer-header {
  flex-shrink: 0;
  padding: 16px 20px;
  border-bottom: 1px solid #e4e7ed;
}

.header-top {
  display: flex;
  align-items: center;
  gap: 12px;
}

.close-icon {
  font-size: 20px;
  cursor: pointer;
  color: #606266;
  transition: color 0.2s;
}

.close-icon:hover {
  color: #409eff;
}

.header-title {
  font-size: 18px;
  font-weight: 600;
  color: #303133;
}

.drawer-content {
  flex: 1;
  overflow-y: auto;
  padding: 20px;
}

.drawer-footer {
  flex-shrink: 0;
  padding: 16px 20px;
  border-top: 1px solid #e4e7ed;
  display: flex;
  justify-content: flex-end;
  gap: 12px;
}

.form-section {
  margin-bottom: 24px;
}

.section-title {
  font-size: 14px;
  font-weight: 600;
  color: #303133;
  margin-bottom: 16px;
  padding-bottom: 8px;
  border-bottom: 1px solid #e4e7ed;
}

.form-row {
  display: flex;
  gap: 16px;
}

.form-item-half {
  flex: 1;
}

/* 手办选项样式 */
.figure-option {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 8px;
  min-height: 64px;
  box-sizing: border-box;
}

/* 只针对标记转卖-选择库存手办的下拉菜单 */
:global(.inventory-figure-dropdown .el-select-dropdown__item) {
  display: flex;
  align-items: center;
  min-height: 80px;
  padding: 12px 16px;
  box-sizing: border-box;
}

:global(.inventory-figure-dropdown .el-select-dropdown__item span) {
  display: flex;
  align-items: center;
  width: 100%;
}

.figure-thumb {
  width: 48px;
  height: 48px;
  border-radius: 4px;
  object-fit: cover;
  flex-shrink: 0;
}

.figure-thumb.placeholder {
  background: #f5f7fa;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #c0c4cc;
}

.figure-info {
  flex: 1;
  min-width: 0;
}

.figure-name {
  font-size: 14px;
  font-weight: 500;
  color: #303133;
  margin-bottom: 4px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.figure-stock {
  font-size: 12px;
  color: #67c23a;
  margin-bottom: 2px;
}

.figure-cost {
  font-size: 12px;
  color: #909399;
}

.quantity-hint {
  font-size: 12px;
  color: #909399;
  margin-top: 4px;
}

/* 分割线 */
.divider {
  height: 1px;
  background: #e4e7ed;
  margin: 16px 0;
}

/* 计算结果样式 */
.calculation-result {
  display: flex;
  justify-content: space-between;
  padding: 12px 0;
}

.result-item {
  display: flex;
  align-items: center;
  gap: 8px;
}

.result-label {
  font-size: 14px;
  color: #606266;
}

.result-value {
  font-size: 16px;
  font-weight: 600;
}

.result-value.profit.positive {
  color: #f56c6c;
}

.result-value.profit.negative {
  color: #67c23a;
}

.empty-option {
  padding: 20px;
  text-align: center;
  color: #909399;
}
</style>
