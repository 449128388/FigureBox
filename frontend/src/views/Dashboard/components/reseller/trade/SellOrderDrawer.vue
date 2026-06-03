<!--
  SellOrderDrawer.vue - 卖出订单详情抽屉组件

  功能说明：
  - 从右侧滑入的抽屉展示卖出订单详情
  - 包含头部区、手办信息区、订单信息区、收款明细区、盈亏信息区、物流信息区、备注区
  - 支持物流补录和备注编辑功能

  抽屉规格：
  - 宽度：680px
  - 遮罩层透明度：40%
  - 关闭方式：点击遮罩/点击右上角✕/底部【关闭】按钮

  组件依赖：
  - Element Plus 的 Drawer、Button、Input、Tag 等组件
  - 需要传入 soldOrderId 和 visible 控制显示

  维护提示：
  - 订单数据从 SellOrderService 获取
  - 盈亏计算在服务端完成
  - 物流信息支持补录编辑
-->
<template>
  <el-drawer
    v-model="drawerVisible"
    :size="680"
    :with-header="false"
    :modal="true"
    :modal-class="'sell-order-drawer-modal'"
    direction="rtl"
    destroy-on-close
    @close="handleClose"
  >
    <div class="sell-order-drawer" v-if="orderData">
      <!-- 头部区 -->
      <div class="drawer-header">
        <div class="header-top">
          <el-button
            class="close-btn"
            type="text"
            @click="handleClose"
          >
            <el-icon><Close /></el-icon>
          </el-button>
          <span class="header-title">查看卖出订单</span>
          <span class="order-number-tag">#{{ orderData.header?.order_number }}</span>
        </div>
      </div>

      <!-- 手办信息区 -->
      <div class="figure-section">
        <div class="figure-image">
          <img v-if="orderData.figure?.image" :src="orderData.figure.image" alt="手办图片" />
          <div v-else class="figure-placeholder">暂无图片</div>
        </div>
        <div class="figure-info">
          <h3 class="figure-name">中文名称：{{ orderData.figure?.name }}</h3>
          <p class="figure-meta">
            <span>数量：{{ orderData.figure?.quantity }}体</span>
            <span class="divider">|</span>
            <span>平台：{{ orderData.figure?.platform }}</span>
          </p>
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
                  type="primary"
                  effect="dark"
                >
                  【卖出】
                </el-tag>
              </span>
            </div>
            <div class="info-row">
              <span class="info-label">卖出平台</span>
              <span class="info-value">{{ orderData.order_info?.sell_platform }}</span>
            </div>
            <div class="info-row">
              <span class="info-label">成交时间</span>
              <span class="info-value">{{ orderData.order_info?.transaction_date }}</span>
            </div>
            <div class="info-row">
              <span class="info-label">当前状态</span>
              <span class="info-value">
                <el-tag
                  size="small"
                  type="success"
                  effect="dark"
                >
                  ✅ {{ orderData.order_info?.status }}
                </el-tag>
              </span>
            </div>
          </div>
        </div>

        <!-- 收款明细区 -->
        <div class="section payment-section">
          <h4 class="section-title">收款明细</h4>
          <div class="payment-content">
            <div class="payment-list">
              <div class="payment-item income">
                <span class="payment-label">卖出价格</span>
                <span class="payment-value">+{{ formatCurrency(orderData.payment?.sell_price, orderData.payment?.sell_price_currency) }}</span>
              </div>
              <div class="payment-item expense">
                <span class="payment-label">运费</span>
                <span class="payment-value">-{{ formatCurrency(orderData.payment?.shipping_fee, orderData.payment?.shipping_fee_currency) }}</span>
              </div>
              <div class="payment-item expense">
                <span class="payment-label">平台手续费</span>
                <span class="payment-value">-{{ formatCurrency(orderData.payment?.platform_fee, orderData.payment?.platform_fee_currency) }}</span>
              </div>
            </div>
            <div class="payment-divider"></div>
            <div class="payment-item net-received">
              <span class="payment-label">实到账</span>
              <span class="payment-value">+{{ formatCurrency(orderData.payment?.net_received, 'CNY') }}</span>
            </div>
          </div>
        </div>

        <!-- 盈亏信息区 -->
        <div class="section profit-section">
          <h4 class="section-title">盈亏信息</h4>
          <div class="profit-content">
            <div class="cost-list">
              <div class="cost-item">
                <span class="cost-label">成本单价</span>
                <span class="cost-value">{{ formatCurrency(orderData.profit?.cost_price, orderData.profit?.cost_price_currency) }}/体</span>
              </div>
              <div class="cost-item">
                <span class="cost-label">成本合计</span>
                <span class="cost-value">{{ formatCurrency(orderData.profit?.total_cost, orderData.profit?.cost_price_currency) }}</span>
              </div>
            </div>
            <div class="profit-divider"></div>
            <div class="profit-summary">
              <div class="profit-item net-profit">
                <span class="profit-label">净利润</span>
                <span class="profit-value">+{{ formatCurrency(orderData.profit?.net_profit, 'CNY') }}</span>
              </div>
              <div class="profit-item profit-rate">
                <span class="profit-label">利润率</span>
                <span class="profit-value">+{{ orderData.profit?.profit_rate }}%</span>
              </div>
            </div>
          </div>
        </div>

        <!-- 物流信息区 -->
        <div class="section logistics-section">
          <h4 class="section-title">
            物流信息
            <el-button
              v-if="!isEditingLogistics"
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
                    <el-tag size="small" :type="orderData.logistics?.tracking_number ? 'success' : 'info'">
                      {{ orderData.logistics?.tracking_number ? orderData.logistics?.status : '待发货' }}
                    </el-tag>
                  </span>
                </div>
                <div class="info-row">
                  <span class="info-label">买家手机号</span>
                  <span class="info-value">{{ orderData.buyer?.phone ? maskPhone(orderData.buyer.phone) : '--' }}</span>
                </div>
                <div class="info-row">
                  <span class="info-label">买家地址</span>
                  <span class="info-value">{{ orderData.buyer?.address || '--' }}</span>
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
              <div class="remarks-block">
                <p class="remarks-text">{{ orderData.remarks || '暂无备注' }}</p>
              </div>
            </template>
          </div>
        </div>
      </div>

      <!-- 底部操作栏 -->
      <div class="drawer-footer">
        <el-button class="ghost-btn" @click="startEditRemarks">编辑备注</el-button>
        <el-button type="primary" @click="handleClose">关闭</el-button>
      </div>
    </div>
  </el-drawer>
</template>

<script>
import { ref, computed, watch } from 'vue'
import { Close, Edit } from '@element-plus/icons-vue'
import axios from '../../../../../axios'

export default {
  name: 'SellOrderDrawer',
  components: {
    Close,
    Edit
  },
  props: {
    visible: {
      type: Boolean,
      default: false
    },
    soldOrderId: {
      type: [Number, String],
      default: null
    }
  },
  emits: ['update:visible', 'close', 'refresh'],
  setup(props, { emit }) {
    const drawerVisible = computed({
      get: () => props.visible,
      set: (val) => emit('update:visible', val)
    })

    const orderData = ref(null)
    const isEditingRemarks = ref(false)
    const editingRemarks = ref('')
    const isEditingLogistics = ref(false)
    const editingTrackingNumber = ref('')

    // 监听 visible 变化，打开时加载数据
    watch(() => props.visible, (newVal) => {
      if (newVal && props.soldOrderId) {
        loadOrderDetail()
      }
    })

    // 加载订单详情
    const loadOrderDetail = async () => {
      try {
        const response = await axios.get(`/trade_records/sell-order/${props.soldOrderId}`)
        orderData.value = response.order
      } catch (error) {
        console.error('加载卖出订单详情失败:', error)
      }
    }

    // 格式化数字
    const formatNumber = (num) => {
      if (num === undefined || num === null) return '0'
      return num.toLocaleString('zh-CN', { minimumFractionDigits: 2, maximumFractionDigits: 2 })
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

    // 格式化金额显示
    const formatCurrency = (amount, currency) => {
      const symbol = getCurrencySymbol(currency)
      const formatted = formatNumber(amount)
      if (currency === 'JPY') {
        return `JP¥${formatted}`
      }
      return `${symbol}${formatted}`
    }

    // 手机号脱敏
    const maskPhone = (phone) => {
      if (!phone || phone.length < 7) return phone
      return phone.substring(0, 3) + '****' + phone.substring(7)
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
        await axios.put(`/trade_records/sell-order/${props.soldOrderId}/remarks`, {
          remarks: editingRemarks.value
        })
        orderData.value.remarks = editingRemarks.value
        isEditingRemarks.value = false
      } catch (error) {
        console.error('保存备注失败:', error)
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
        const response = await axios.put(`/trade_records/sell-order/${props.soldOrderId}/logistics`, {
          tracking_number: editingTrackingNumber.value
        })
        // 更新本地数据
        if (!orderData.value.logistics) {
          orderData.value.logistics = {}
        }
        orderData.value.logistics.tracking_number = editingTrackingNumber.value
        orderData.value.logistics.logistics_company = response.logistics_company || ''
        orderData.value.logistics.status = response.status || '已发货'
        isEditingLogistics.value = false
        emit('refresh')
      } catch (error) {
        console.error('保存物流信息失败:', error)
      }
    }

    // 关闭抽屉
    const handleClose = () => {
      drawerVisible.value = false
      orderData.value = null
      isEditingRemarks.value = false
      editingRemarks.value = ''
      isEditingLogistics.value = false
      editingTrackingNumber.value = ''
      emit('close')
    }

    return {
      drawerVisible,
      orderData,
      isEditingRemarks,
      editingRemarks,
      isEditingLogistics,
      editingTrackingNumber,
      formatNumber,
      formatCurrency,
      maskPhone,
      startEditRemarks,
      cancelEditRemarks,
      saveRemarks,
      startEditLogistics,
      cancelEditLogistics,
      saveLogistics,
      handleClose
    }
  }
}
</script>

<style scoped>
/* 抽屉遮罩层样式 */
:global(.sell-order-drawer-modal) {
  background-color: rgba(0, 0, 0, 0.4) !important;
}

/* 抽屉内容区 */
.sell-order-drawer {
  display: flex;
  flex-direction: column;
  height: 100%;
}

/* 头部区 */
.drawer-header {
  padding: 15px 20px;
  border-bottom: 1px solid #e0e0e0;
  background-color: #f9f9f9;
}

.header-top {
  display: flex;
  align-items: center;
  gap: 15px;
}

.close-btn {
  font-size: 20px;
  padding: 0;
  color: #666;
}

.header-title {
  flex: 1;
  font-size: 18px;
  font-weight: bold;
  color: #333;
}

.order-number-tag {
  font-size: 14px;
  color: #666;
  background-color: #e0e0e0;
  padding: 4px 10px;
  border-radius: 4px;
}

/* 手办信息区 */
.figure-section {
  display: flex;
  gap: 15px;
  padding: 20px;
  border-bottom: 1px solid #e0e0e0;
  background-color: #fafafa;
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
  margin: 0 0 10px 0;
  font-size: 16px;
  color: #333;
}

.figure-meta {
  margin: 0;
  font-size: 13px;
  color: #666;
}

.figure-meta .divider {
  margin: 0 8px;
  color: #ccc;
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
  width: 90px;
  color: #999;
  font-size: 14px;
}

.info-value {
  flex: 1;
  color: #333;
  font-size: 14px;
}

/* 收款明细区 */
.payment-content {
  background-color: #f9f9f9;
  padding: 15px;
  border-radius: 8px;
}

.payment-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.payment-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.payment-label {
  color: #666;
  font-size: 14px;
}

.payment-value {
  font-size: 15px;
  font-weight: bold;
}

.payment-item.income .payment-value {
  color: #F44336; /* 红色 - 收入 */
}

.payment-item.expense .payment-value {
  color: #4CAF50; /* 绿色 - 支出 */
}

.payment-divider {
  height: 1px;
  background-color: #e0e0e0;
  margin: 12px 0;
}

.payment-item.net-received .payment-label {
  font-weight: bold;
  color: #333;
}

.payment-item.net-received .payment-value {
  font-size: 18px;
  font-weight: bold;
  color: #F44336;
}

/* 盈亏信息区 */
.profit-content {
  background-color: #f9f9f9;
  padding: 15px;
  border-radius: 8px;
}

.cost-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.cost-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.cost-label {
  color: #666;
  font-size: 14px;
}

.cost-value {
  color: #333;
  font-size: 14px;
}

.profit-divider {
  height: 1px;
  background-color: #e0e0e0;
  margin: 12px 0;
}

.profit-summary {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.profit-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.profit-item.net-profit .profit-label {
  font-weight: bold;
  color: #333;
}

.profit-item.net-profit .profit-value {
  font-size: 18px;
  font-weight: bold;
  color: #F44336;
}

.profit-item.profit-rate .profit-value {
  color: #F44336;
  font-weight: bold;
}

/* 物流信息区 */
.logistics-content {
  background-color: #f9f9f9;
  padding: 15px;
  border-radius: 8px;
}

.logistics-actions {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
  margin-top: 10px;
}

/* 备注区 */
.remarks-content {
  background-color: #f9f9f9;
  padding: 15px;
  border-radius: 8px;
}

.remarks-block {
  background-color: #fff;
  padding: 12px;
  border-radius: 4px;
  border-left: 3px solid #409EFF;
}

.remarks-text {
  margin: 0;
  color: #666;
  line-height: 1.6;
  font-size: 14px;
}

.remarks-actions {
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

/* 线框按钮（Ghost Button）样式 */
.ghost-btn {
  background-color: #FFF !important;
  border: 1px solid #D9D9D9 !important;
  color: #595959 !important;
  transition: all 0.3s ease;
}

.ghost-btn:hover {
  border-color: #1890FF !important;
  color: #1890FF !important;
}

/* 区域标题中的按钮字体大小调整为15px */
.section-title .el-button {
  font-size: 15px;
}
</style>
