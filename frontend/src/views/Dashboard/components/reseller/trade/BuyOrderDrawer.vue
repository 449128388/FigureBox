<!--
  BuyOrderDrawer.vue - 买入订单详情抽屉组件

  功能说明：
  - 从右侧滑入的抽屉展示买入订单详情
  - 包含头部区、订单信息区、支付明细区、物流信息区、备注区
  - 根据订单状态动态展示底部操作按钮
  - 支持备注编辑功能

  抽屉规格：
  - 宽度：600-720px
  - 遮罩层透明度：40%
  - 关闭方式：点击遮罩/点击右上角✕/底部【关闭】按钮

  组件依赖：
  - Element Plus 的 Drawer、Button、Input、Timeline 等组件
  - 需要传入 orderId 和 visible 控制显示

  维护提示：
  - 订单状态映射在 BuyOrderService 中定义
  - 操作按钮根据订单状态动态生成
  - 备注编辑使用就地编辑模式
-->
<template>
  <el-drawer
    v-model="drawerVisible"
    :size="680"
    :with-header="false"
    :modal="true"
    :modal-class="'buy-order-drawer-modal'"
    direction="rtl"
    destroy-on-close
    @close="handleClose"
  >
    <div class="buy-order-drawer" v-if="orderData">
      <!-- 头部区 -->
      <div class="drawer-header">
        <div class="header-top">
          <span class="header-title">查看买入订单</span>
        </div>
        <div class="header-info">
          <div class="figure-image">
            <img v-if="orderData.header?.figure_image" :src="orderData.header.figure_image" alt="手办图片" />
            <div v-else class="figure-placeholder">暂无图片</div>
          </div>
          <div class="figure-info">
            <h3 class="figure-name">{{ orderData.header?.figure_name }}</h3>
            <p class="figure-series">{{ orderData.header?.figure_series }}</p>
            <p class="figure-meta">
              <span>数量: {{ orderData.header?.quantity }}体</span>
              <span class="divider">|</span>
              <span>平台: {{ orderData.header?.platform }}</span>
            </p>
          </div>
        </div>
      </div>

      <!-- 内容区（可滚动） -->
      <div class="drawer-content">
        <!-- 订单信息区 -->
        <div class="section order-info-section">
          <h4 class="section-title">订单信息</h4>
          <div class="info-grid">
            <div class="info-row">
              <span class="info-label">订单编号</span>
              <span class="info-value">{{ orderData.order_info?.order_number }}</span>
            </div>
            <div class="info-row">
              <span class="info-label">订单类型</span>
              <span class="info-value">
                <el-tag
                  size="small"
                  :style="{ backgroundColor: orderData.order_info?.order_type?.color, borderColor: orderData.order_info?.order_type?.color, color: '#fff' }"
                >
                  {{ orderData.order_info?.order_type?.name }}
                </el-tag>
              </span>
            </div>
            <div class="info-row">
              <span class="info-label">购买店铺</span>
              <span class="info-value">{{ orderData.order_info?.platform }}</span>
            </div>
            <div class="info-row">
              <span class="info-label">下单时间</span>
              <span class="info-value">{{ orderData.order_info?.order_time }}</span>
            </div>
            <div class="info-row">
              <span class="info-label">当前状态</span>
              <span class="info-value">
                <el-tag
                  size="small"
                  :type="orderData.order_info?.status?.color || 'info'"
                  effect="dark"
                >
                  {{ orderData.order_info?.status?.icon }} {{ orderData.order_info?.status?.label }}
                </el-tag>
              </span>
            </div>
          </div>
        </div>

        <!-- 支付明细区 -->
        <div class="section payment-section">
          <h4 class="section-title">支付明细</h4>
          <div class="payment-content">
            <!-- 全款/现货订单 -->
            <template v-if="isFullPayment">
              <div class="payment-info-list">
                <div class="payment-info-item">
                  <span class="label">实付金额</span>
                  <span class="value amount">
                    ¥{{ formatNumber(orderData.payment?.total_amount_cny) }}
                    <span v-if="hasMultiCurrency(orderData.payment?.total_by_currency)" class="original-currency">
                      <span v-for="(amount, currency, idx) in orderData.payment?.total_by_currency" :key="idx">
                        {{ idx > 0 ? ' + ' : '' }}({{ formatCurrency(amount, currency) }})
                      </span>
                    </span>
                  </span>
                </div>
                <div class="payment-info-item">
                  <span class="label">支付方式</span>
                  <span class="value">{{ orderData.payment?.items?.[0]?.method || '-' }}</span>
                </div>
                <div class="payment-info-item">
                  <span class="label">支付时间</span>
                  <span class="value">{{ orderData.payment?.items?.[0]?.full_date || '-' }}</span>
                </div>
                <div class="payment-info-item">
                  <span class="label">流水单号</span>
                  <span class="value">{{ orderData.payment?.items?.[0]?.transaction_no || '-' }}</span>
                </div>
              </div>
            </template>

            <!-- 预定订单（定金+尾款） -->
            <template v-else>
              <div class="payment-timeline">
                <div
                  v-for="(item, index) in orderData.payment?.items"
                  :key="index"
                  class="timeline-item"
                  :class="{ 'pending': item.status === 'pending' }"
                >
                  <div class="timeline-left">
                    <el-icon v-if="item.status === 'paid'" class="status-icon success"><CircleCheck /></el-icon>
                    <el-icon v-else-if="item.status === 'cancelled'" class="status-icon cancelled"><CircleClose /></el-icon>
                    <el-icon v-else class="status-icon pending"><Clock /></el-icon>
                  </div>
                  <div class="timeline-content">
                    <div class="timeline-header">
                      <span class="payment-type">{{ item.type }}</span>
                      <span v-if="item.amount_display" class="payment-amount payment-amount--empty">{{ item.amount_display }}</span>
                      <span v-else class="payment-amount">{{ formatCurrency(item.amount, item.currency) }}</span>
                    </div>
                    <div class="timeline-meta">
                      <span class="payment-date">{{ item.date }}</span>
                      <span class="payment-method">{{ item.method }}</span>
                      <el-tag v-if="item.status === 'pending'" size="small" type="warning">待支付</el-tag>
                      <el-tag v-else-if="item.status === 'paid'" size="small" type="success">已支付</el-tag>
                      <el-tag v-else-if="item.status === 'cancelled'" size="small" type="danger">已取消</el-tag>
                    </div>
                  </div>
                </div>
              </div>
              <div class="payment-total">
                <span class="total-label">
                  实付合计
                  <span v-if="hasMultiCurrency(orderData.payment?.total_by_currency)" class="total-currency-hint">（折合人民币）</span>
                </span>
                <span class="total-amount">
                  ¥{{ formatNumber(orderData.payment?.total_amount_cny) }}
                </span>
              </div>
              <div v-if="hasMultiCurrency(orderData.payment?.total_by_currency)" class="payment-original-currencies">
                <span class="original-label">原始金额：</span>
                <span v-for="(amount, currency, idx) in orderData.payment?.total_by_currency" :key="idx">
                  {{ idx > 0 ? ' + ' : '' }}{{ formatCurrency(amount, currency) }}
                </span>
              </div>
            </template>
          </div>
        </div>

        <!-- 物流信息区 -->
        <div class="section logistics-section">
          <h4 class="section-title">
            物流信息
            <el-button
              v-if="orderData.order_info?.status_code !== '已完成' && !isEditingLogistics"
              type="primary"
              link
              size="small"
              @click="startEditLogistics"
            >
              <el-icon><Edit /></el-icon>
              补录物流
            </el-button>
          </h4>
          <div class="logistics-content">
            <template v-if="isEditingLogistics">
              <div class="info-grid">
                <div class="info-row">
                  <span class="info-label">快递单号</span>
                  <span class="info-value">
                    <el-input
                      v-model="editingTrackingNumber"
                      size="small"
                      placeholder="请输入快递单号"
                      style="width: 200px;"
                    />
                  </span>
                </div>
              </div>
              <div class="logistics-actions">
                <el-button size="small" @click="cancelEditLogistics">取消</el-button>
                <el-button type="primary" size="small" @click="saveLogistics">保存</el-button>
              </div>
            </template>
            <template v-else>
              <div class="info-grid">
                <div class="info-row">
                  <span class="info-label">快递单号</span>
                  <span class="info-value">{{ orderData.logistics?.tracking_number || '--' }}</span>
                </div>
                <div class="info-row">
                  <span class="info-label">物流公司</span>
                  <span class="info-value">{{ orderData.logistics?.logistics_company || '--' }}</span>
                </div>
                <div class="info-row">
                  <span class="info-label">发货状态</span>
                  <span class="info-value">
                    <el-tag size="small" :type="orderData.logistics?.tracking_number ? getLogisticsStatusType(orderData.logistics?.status) : 'info'">
                      {{ orderData.logistics?.tracking_number ? orderData.logistics?.status : '待发货' }}
                    </el-tag>
                  </span>
                </div>
                <div class="info-row" v-if="orderData.logistics?.delivery_time">
                  <span class="info-label">签收时间</span>
                  <span class="info-value">{{ orderData.logistics?.delivery_time }}</span>
                </div>
              </div>
            </template>
          </div>
        </div>

        <!-- 备注区 -->
        <div class="section remarks-section">
          <h4 class="section-title">
            备注
            <el-button
              v-if="!isEditingRemarks"
              type="primary"
              link
              size="small"
              @click="startEditRemarks"
            >
              <el-icon><Edit /></el-icon>
              编辑
            </el-button>
          </h4>
          <div class="remarks-content">
            <template v-if="isEditingRemarks">
              <el-input
                v-model="editingRemarks"
                type="textarea"
                :rows="3"
                placeholder="请输入备注内容"
              />
              <div class="remarks-actions">
                <el-button size="small" @click="cancelEditRemarks">取消</el-button>
                <el-button type="primary" size="small" @click="saveRemarks">保存</el-button>
              </div>
            </template>
            <template v-else>
              <p class="remarks-text">{{ orderData.remarks || '暂无备注' }}</p>
            </template>
          </div>
        </div>
      </div>

      <!-- 底部操作栏 -->
      <div class="drawer-footer">
        <el-button
          v-for="action in availableActions"
          :key="action.key"
          :type="action.type"
          @click="handleAction(action.key)"
        >
          {{ action.label }}
        </el-button>
      </div>
    </div>
  </el-drawer>
</template>

<script>
import { ref, computed, watch } from 'vue'
import { Close, CircleCheck, CircleClose, Clock, Edit } from '@element-plus/icons-vue'
import axios from '../../../../../axios'

export default {
  name: 'BuyOrderDrawer',
  components: {
    Close,
    CircleCheck,
    CircleClose,
    Clock,
    Edit
  },
  props: {
    visible: {
      type: Boolean,
      default: false
    },
    orderId: {
      type: [Number, String],
      default: null
    }
  },
  emits: ['update:visible', 'close', 'action'],
  setup(props, { emit }) {
    const drawerVisible = computed({
      get: () => props.visible,
      set: (val) => emit('update:visible', val)
    })

    const orderData = ref(null)
    const availableActions = ref([])
    const isEditingRemarks = ref(false)
    const editingRemarks = ref('')
    const isEditingLogistics = ref(false)
    const editingTrackingNumber = ref('')

    // 是否为全款支付
    const isFullPayment = computed(() => {
      const paymentType = orderData.value?.payment?.payment_type
      return paymentType === '全款预定' || paymentType === '现货'
    })

    // 监听 visible 变化，打开时加载数据
    watch(() => props.visible, (newVal) => {
      if (newVal && props.orderId) {
        loadOrderDetail()
      }
    })

    // 加载订单详情
    const loadOrderDetail = async () => {
      try {
        const response = await axios.get(`/trade_records/buy-order/${props.orderId}`)
        orderData.value = response.order
        availableActions.value = response.actions
      } catch (error) {
        console.error('加载订单详情失败:', error)
      }
    }

    // 格式化数字
    const formatNumber = (num) => {
      if (num === undefined || num === null) return '0'
      return num.toLocaleString('zh-CN', { minimumFractionDigits: 0, maximumFractionDigits: 2 })
    }

    // 获取订单类型标签样式
    const getOrderTypeTag = (type) => {
      const typeMap = {
        '全款预定': 'primary',
        '散货': 'success',
        '现货': 'warning',
        '补仓': 'info'
      }
      return typeMap[type] || 'info'
    }

    // 获取物流状态标签样式
    const getLogisticsStatusType = (status) => {
      const statusMap = {
        '已签收': 'success',
        '运输中': 'primary',
        '待发货': 'warning'
      }
      return statusMap[status] || 'info'
    }

    // 获取币种符号
    const getCurrencySymbol = (currency) => {
      const symbolMap = {
        'CNY': '¥',
        'JPY': '¥',
        'USD': '$',
        'EUR': '€'
      }
      return symbolMap[currency] || '¥'
    }

    // 格式化金额显示，区分日元和人名币符号
    const formatCurrency = (amount, currency) => {
      const symbol = getCurrencySymbol(currency)
      const formatted = formatNumber(amount)
      if (currency === 'JPY') {
        return `JP¥${formatted}`
      }
      return `${symbol}${formatted}`
    }

    // 判断是否存在多币种
    const hasMultiCurrency = (totalByCurrency) => {
      if (!totalByCurrency) return false
      const currencies = Object.keys(totalByCurrency)
      return currencies.length > 1 || (currencies.length === 1 && currencies[0] !== 'CNY')
    }

    // 开始编辑备注
    const startEditRemarks = () => {
      editingRemarks.value = orderData.value?.remarks || ''
      isEditingRemarks.value = true
    }

    // 取消编辑备注
    const cancelEditRemarks = () => {
      isEditingRemarks.value = false
      editingRemarks.value = ''
    }

    // 保存备注
    const saveRemarks = async () => {
      try {
        await axios.put(`/trade_records/buy-order/${props.orderId}/remarks`, {
          remarks: editingRemarks.value
        })
        orderData.value.remarks = editingRemarks.value
        isEditingRemarks.value = false
      } catch (error) {
        console.error('保存备注失败:', error)
      }
    }

    // 处理操作按钮点击
    const handleAction = (actionKey) => {
      if (actionKey === 'close') {
        handleClose()
      } else if (actionKey === 'edit_remarks') {
        startEditRemarks()
      } else {
        emit('action', actionKey, props.orderId)
      }
    }

    // 开始编辑物流信息
    const startEditLogistics = () => {
      editingTrackingNumber.value = orderData.value?.logistics?.tracking_number || ''
      isEditingLogistics.value = true
    }

    // 取消编辑物流信息
    const cancelEditLogistics = () => {
      isEditingLogistics.value = false
      editingTrackingNumber.value = ''
    }

    // 保存物流信息
    const saveLogistics = async () => {
      try {
        const response = await axios.put(`/trade_records/buy-order/${props.orderId}/logistics`, {
          tracking_number: editingTrackingNumber.value
        })
        // 更新本地数据
        if (!orderData.value.logistics) {
          orderData.value.logistics = {}
        }
        orderData.value.logistics.tracking_number = editingTrackingNumber.value
        orderData.value.logistics.logistics_company = response.logistics_company || ''
        orderData.value.logistics.has_tracking = true
        orderData.value.logistics.status = response.status || '已发货'
        isEditingLogistics.value = false
      } catch (error) {
        console.error('保存物流信息失败:', error)
      }
    }

    // 关闭抽屉
    const handleClose = () => {
      drawerVisible.value = false
      orderData.value = null
      availableActions.value = []
      isEditingRemarks.value = false
      editingRemarks.value = ''
      isEditingLogistics.value = false
      editingTrackingNumber.value = ''
      emit('close')
    }

    return {
      drawerVisible,
      orderData,
      availableActions,
      isEditingRemarks,
      editingRemarks,
      isEditingLogistics,
      editingTrackingNumber,
      isFullPayment,
      formatNumber,
      formatCurrency,
      getOrderTypeTag,
      getLogisticsStatusType,
      getCurrencySymbol,
      hasMultiCurrency,
      startEditRemarks,
      cancelEditRemarks,
      saveRemarks,
      startEditLogistics,
      cancelEditLogistics,
      saveLogistics,
      handleAction,
      handleClose
    }
  }
}
</script>

<style scoped>
/* 抽屉遮罩层样式 */
:global(.buy-order-drawer-modal) {
  background-color: rgba(0, 0, 0, 0.4) !important;
}

/* 抽屉内容区 */
.buy-order-drawer {
  display: flex;
  flex-direction: column;
  height: 100%;
}

/* 头部区 */
.drawer-header {
  padding: 20px;
  border-bottom: 1px solid #e0e0e0;
  background-color: #f9f9f9;
}

.header-top {
  display: flex;
  align-items: center;
  margin-bottom: 15px;
}

.close-btn {
  font-size: 20px;
  margin-right: 15px;
}

.header-title {
  flex: 1;
  font-size: 18px;
  font-weight: bold;
  color: #333;
}

.header-info {
  display: flex;
  gap: 15px;
}

.figure-image {
  width: 80px;
  height: 80px;
  border-radius: 8px;
  overflow: hidden;
  background-color: #f0f0f0;
  flex-shrink: 0;
}

.figure-image img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.figure-placeholder {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #999;
  font-size: 12px;
}

.figure-info {
  flex: 1;
}

.figure-name {
  margin: 0 0 5px 0;
  font-size: 16px;
  color: #333;
}

.figure-series {
  margin: 0 0 10px 0;
  font-size: 13px;
  color: #666;
}

.figure-meta {
  margin: 0;
  font-size: 13px;
  color: #999;
}

.figure-meta .divider {
  margin: 0 8px;
}

/* 内容区（可滚动） */
.drawer-content {
  flex: 1;
  overflow-y: auto;
  padding: 20px;
}

/* 分区样式 */
.section {
  margin-bottom: 25px;
}

.section-title {
  font-size: 15px;
  font-weight: bold;
  color: #333;
  margin: 0 0 15px 0;
  padding-bottom: 10px;
  border-bottom: 1px solid #f0f0f0;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

/* 信息网格 */
.info-grid {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.info-row {
  display: flex;
  align-items: center;
}

.info-label {
  width: 80px;
  color: #999;
  font-size: 14px;
}

.info-value {
  flex: 1;
  color: #333;
  font-size: 14px;
}

/* 支付明细区 */
.payment-content {
  background-color: #f9f9f9;
  padding: 15px;
  border-radius: 8px;
}

.payment-info-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.payment-info-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.payment-info-item .label {
  color: #666;
  font-size: 14px;
}

.payment-info-item .value {
  color: #333;
  font-size: 14px;
}

.payment-info-item .value.amount {
  font-size: 18px;
  font-weight: bold;
  color: #F44336;
}

/* 支付时间线 */
.payment-timeline {
  display: flex;
  flex-direction: column;
  gap: 15px;
  margin-bottom: 15px;
}

.timeline-item {
  display: flex;
  gap: 12px;
}

.timeline-item.pending {
  opacity: 0.7;
}

.timeline-left {
  display: flex;
  align-items: flex-start;
  padding-top: 2px;
}

.status-icon {
  font-size: 20px;
}

.status-icon.success {
  color: #67C23A;
}

.status-icon.pending {
  color: #E6A23C;
}

.status-icon.cancelled {
  color: #909399;
}

.timeline-content {
  flex: 1;
}

.timeline-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 5px;
}

.payment-type {
  font-weight: bold;
  color: #333;
}

.payment-amount {
  font-size: 16px;
  font-weight: bold;
  color: #F44336;
}

.payment-amount--empty {
  color: #999;
  font-weight: normal;
}

.timeline-meta {
  display: flex;
  gap: 10px;
  align-items: center;
  font-size: 13px;
  color: #999;
}

.payment-total {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-top: 15px;
  border-top: 1px solid #e0e0e0;
}

.total-label {
  font-size: 14px;
  color: #666;
}

.total-amount {
  font-size: 20px;
  font-weight: bold;
  color: #F44336;
}

.original-currency {
  font-size: 12px;
  font-weight: normal;
  color: #999;
  margin-left: 4px;
}

.total-currency-hint {
  font-size: 12px;
  font-weight: normal;
  color: #999;
}

.payment-original-currencies {
  margin-top: 8px;
  padding-top: 8px;
  border-top: 1px dashed #e0e0e0;
  font-size: 12px;
  color: #999;
}

.original-label {
  color: #999;
}

/* 物流信息区 */
.logistics-content {
  background-color: #f9f9f9;
  padding: 15px;
  border-radius: 8px;
}

.empty-logistics {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.empty-text {
  color: #999;
}

/* 备注区 */
.remarks-content {
  background-color: #f9f9f9;
  padding: 15px;
  border-radius: 8px;
}

.remarks-text {
  margin: 0;
  color: #666;
  line-height: 1.6;
  white-space: pre-wrap;
  word-break: break-word;
}

.remarks-actions {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
  margin-top: 10px;
}

/* 物流操作按钮 */
.logistics-actions {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
  margin-top: 10px;
}

/* 底部操作栏 */
.drawer-footer {
  padding: 15px 20px;
  border-top: 1px solid #e0e0e0;
  display: flex;
  justify-content: flex-end;
  gap: 10px;
  background-color: #fff;
}
</style>
