<template>
  <div class="form-overlay" v-if="visible" @click.self="$emit('cancel')">
    <div class="form-container">
      <h3>{{ isEditing ? '编辑已出售订单' : '添加已出售订单' }}</h3>
      <form @submit.prevent="handleSubmit" novalidate>
        <div class="form-layout">
          <el-tabs type="border-card" :tab-position="'left'" lazy v-model="localActiveTab">
            <!-- 基础信息 -->
            <el-tab-pane label="基础信息" name="basic">
              <template #label>
                <div class="tab-label">
                  <i class="fa-solid fa-file-text"></i>
                  <span>基础信息</span>
                </div>
              </template>
              <BasicInfoTab
                :order="localOrder"
                :available-figures="availableFigures"
                :is-editing="isEditing"
                @figure-change="handleFigureChange"
              />
            </el-tab-pane>
            
            <!-- 价格与成本 -->
            <el-tab-pane label="价格成本" name="price">
              <template #label>
                <div class="tab-label">
                  <i class="fa-solid fa-money-bill"></i>
                  <span>价格成本</span>
                </div>
              </template>
              <PriceCostTab
                :order="localOrder"
                :is-editing="isEditing"
                :figure-id="localOrder.figure_id"
                @profit-change="calculateProfit"
              />
            </el-tab-pane>
            
            <!-- 物流信息 -->
            <el-tab-pane label="物流信息" name="shipping">
              <template #label>
                <div class="tab-label">
                  <i class="fa-solid fa-truck"></i>
                  <span>物流信息</span>
                </div>
              </template>
              <ShippingInfoTab :order="localOrder" />
            </el-tab-pane>
            
            <!-- 盈亏预览 -->
            <el-tab-pane label="盈亏预览" name="profit">
              <template #label>
                <div class="tab-label">
                  <i class="fa-solid fa-chart-line"></i>
                  <span>盈亏预览</span>
                </div>
              </template>
              <ProfitTab :order="localOrder" />
            </el-tab-pane>
            
            <!-- 订单备注 -->
            <el-tab-pane label="订单备注" name="remark">
              <template #label>
                <div class="tab-label">
                  <i class="fa-solid fa-sticky-note"></i>
                  <span>订单备注</span>
                </div>
              </template>
              <RemarkTab :order="localOrder" />
            </el-tab-pane>
          </el-tabs>
        </div>
        
        <div class="form-actions">
          <el-button class="btn-cancel" @click="$emit('cancel')">取消</el-button>
          <el-button class="btn-submit" type="primary" native-type="submit">保存</el-button>
        </div>
      </form>
    </div>
  </div>
</template>

<script>
import { ref, watch } from 'vue'
import { ElMessage } from 'element-plus'
import BasicInfoTab from './form/BasicInfoTab.vue'
import PriceCostTab from './form/PriceCostTab.vue'
import ShippingInfoTab from './form/ShippingInfoTab.vue'
import ProfitTab from './form/ProfitTab.vue'
import RemarkTab from './form/RemarkTab.vue'

export default {
  name: 'SoldOrderForm',
  components: {
    BasicInfoTab,
    PriceCostTab,
    ShippingInfoTab,
    ProfitTab,
    RemarkTab
  },
  props: {
    visible: Boolean,
    isEditing: Boolean,
    newOrder: Object,
    availableFigures: Array
  },
  emits: ['saveOrder', 'cancel', 'calculatePlatformFee'],
  setup(props, context) {
    const localOrder = ref({
      figure_id: '',
      sell_platform: '',
      order_number: '',
      quantity: 1,
      payment_method: '',
      sell_date: '',
      sell_price: 0,
      cost_price: 0,
      shipping_fee: 0,
      platform_fee: 0,
      sell_price_currency: 'CNY',
      cost_price_currency: 'CNY',
      shipping_fee_currency: 'CNY',
      platform_fee_currency: 'CNY',
      buyer_phone: '',
      buyer_address: '',
      tracking_number: '',
      shipping_date: '',
      status: '待发货',
      remark: ''
    })

    const localActiveTab = ref('basic')

    // 计算闲鱼平台手续费
    const calculateXianyuFee = async () => {
      const platform = localOrder.value.sell_platform
      const sellPrice = localOrder.value.sell_price || 0

      if (!platform || sellPrice <= 0) {
        localOrder.value.platform_fee = 0
        return
      }

      if (platform !== '闲鱼（个人卖家）' && platform !== '闲鱼（鱼小铺）') {
        localOrder.value.platform_fee = 0
        return
      }

      if (platform === '闲鱼（鱼小铺）') {
        localOrder.value.platform_fee = sellPrice * 0.016
        return
      }

      if (platform === '闲鱼（个人卖家）') {
        const currentOrderId = props.isEditing ? localOrder.value.id : null

        try {
          context.emit('calculatePlatformFee', {
            platform: platform,
            sellPrice: sellPrice,
            orderId: currentOrderId,
            callback: (monthlyStats) => {
              const baseRate = 0.006
              const baseFee = sellPrice * baseRate
              let totalFee = Math.min(baseFee, 60)

              const monthlyOrderCount = (monthlyStats?.order_count || 0)
              const monthlyAmount = (monthlyStats?.total_amount || 0)

              const exceedsThreshold = monthlyOrderCount > 10 && monthlyAmount > 10000

              if (exceedsThreshold) {
                const extraRate = 0.01
                totalFee = sellPrice * (baseRate + extraRate)
              }

              localOrder.value.platform_fee = Math.round(totalFee * 100) / 100
            }
          })
        } catch (error) {
          const baseFee = sellPrice * 0.006
          localOrder.value.platform_fee = Math.min(baseFee, 60)
        }
      }
    }

    watch(() => localOrder.value.sell_platform, () => {
      calculateXianyuFee()
    })

    watch(() => localOrder.value.sell_price, () => {
      calculateXianyuFee()
    })

    const calculateProfit = () => {
      // 利润计算由ProfitTab组件自动处理
    }

    const handleFigureChange = (figureId) => {
      // 已在BasicInfoTab中处理，这里可以添加额外逻辑
    }

    watch(() => props.newOrder, (newVal) => {
      if (newVal) {
        localOrder.value = { ...localOrder.value, ...newVal }
      }
    }, { deep: true, immediate: true })

    // 监听表单显示状态，打开时重置标签页到第一个
    watch(() => props.visible, (newVal) => {
      if (newVal) {
        localActiveTab.value = 'basic'
      }
    })

    // 表单校验
    const validateForm = () => {
      const order = localOrder.value
      const errors = []

      if (!order.figure_id || order.figure_id === '') {
        errors.push('请选择手办')
      }

      if (!order.sell_platform || order.sell_platform === '') {
        errors.push('请选择卖出平台')
      }

      if (order.sell_price === null || order.sell_price === undefined || order.sell_price === '') {
        errors.push('请输入卖出价格')
      } else if (order.sell_price <= 0) {
        errors.push('卖出价格必须大于0')
      }

      if (!order.status || order.status === '') {
        errors.push('请选择卖出状态')
      }

      if (!order.buyer_phone || order.buyer_phone === '') {
        errors.push('请输入买家手机号')
      } else {
        const phonePattern = /^1[3-9]\d{9}$/
        if (!phonePattern.test(order.buyer_phone)) {
          errors.push('手机号格式不正确，请输入11位有效手机号')
        }
      }

      if (!order.payment_method || order.payment_method === '') {
        errors.push('请选择支付方式')
      }

      if (!order.sell_date || order.sell_date === '') {
        errors.push('请选择卖出时间')
      }

      return errors
    }

    const handleSubmit = () => {
      const errors = validateForm()
      if (errors.length > 0) {
        ElMessage.error(errors[0])
        return
      }
      context.emit('saveOrder', { ...localOrder.value })
    }

    return {
      localOrder,
      localActiveTab,
      calculateProfit,
      handleFigureChange,
      handleSubmit
    }
  }
}
</script>

<style scoped>
/* 表单样式 - 统一成手办管理风格 */
.form-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
  overflow-y: auto;
}

.form-container {
  background: white;
  padding: 0;
  border-radius: 8px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);
  width: 100%;
  max-width: 900px;
  max-height: 90vh;
  overflow: hidden;
  margin: 20px;
}

.form-container h3 {
  margin-bottom: 0;
  padding: 20px 24px;
  color: #333;
  text-align: left;
  font-size: 20px;
  font-weight: 600;
  border-bottom: 1px solid #e0e0e0;
}

.form-layout {
  margin-bottom: 0;
}

.form-actions {
  margin-top: 0;
  padding: 16px 24px;
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  border-top: 1px solid #e0e0e0;
  background-color: #fafafa;
}

.btn-cancel {
  background-color: transparent;
  color: #005ed3;
  border: 1px solid #005ed3;
  border-radius: 4px;
  padding: 8px 16px;
  font-weight: 500;
  transition: all 0.2s;
}

.btn-cancel:hover {
  background-color: rgba(0, 94, 211, 0.08);
  color: #004bb5;
  border-color: #004bb5;
}

.btn-submit {
  background-color: #005ed3;
  color: white;
  border-radius: 4px;
  padding: 8px 16px;
  font-weight: 500;
  border: none;
  transition: all 0.2s;
}

.btn-submit:hover {
  background-color: #004bb5;
  color: white;
}

/* 标签页样式 */
.tab-label {
  display: flex;
  align-items: center;
  justify-content: flex-start;
  gap: 12px;
  width: 100%;
  padding: 8px 0;
  font-size: 15px;
}

.tab-label i {
  font-size: 18px;
  width: 24px;
  text-align: center;
}

/* Komga风格的侧边栏 - 使用:deep()深度选择器覆盖Element Plus默认样式 */
:deep(.form-container .el-tabs__header) {
  background-color: #f5f5f5;
  border-right: 1px solid #e0e0e0;
}

:deep(.form-container .el-tabs__item) {
  height: 62px !important;
  padding: 0 24px !important;
  text-align: left;
  justify-content: flex-start;
  border-left: 3px solid transparent;
  transition: background-color 0.15s ease, color 0.15s ease;
  background-color: white !important;
  will-change: background-color, color;
}

:deep(.form-container .el-tabs__item:hover) {
  background-color: rgba(0, 0, 0, 0.04) !important;
  color: #333 !important;
}

:deep(.form-container .el-tabs__item.is-active) {
  background-color: white;
  border-left-color: #2196F3;
  color: #2196F3;
  font-weight: 500;
  position: relative;
}

/* 添加左侧滑动指示器 */
:deep(.form-container .el-tabs__item.is-active)::after {
  content: '';
  position: absolute;
  left: 0;
  top: 19px;
  width: 3px;
  height: 24px;
  background-color: #2196F3;
  border-radius: 0 2px 2px 0;
}

/* 标签内容区域样式 */
:deep(.form-container .el-tabs__content) {
  padding: 24px;
  background-color: white;
}

/* 移除默认边框 */
:deep(.form-container .el-tabs--border-card) {
  border: none !important;
  box-shadow: none !important;
}

/* 移除标签页容器的上下边框 */
:deep(.form-container .el-tabs--border-card > .el-tabs__header) {
  border-top: none !important;
  border-bottom: none !important;
  background-color: #f5f5f5;
}

/* 移除导航包裹的边框 */
:deep(.form-container .el-tabs__nav-wrap) {
  margin-bottom: 0;
  border-top: none !important;
  border-bottom: none !important;
}

:deep(.form-container .el-tabs__nav-scroll) {
  background-color: #f5f5f5;
  border-top: none !important;
  border-bottom: none !important;
}

/* 确保标签项没有额外的边框 */
:deep(.form-container .el-tabs--border-card > .el-tabs__header .el-tabs__item) {
  border-top: none !important;
  border-bottom: none !important;
}
</style>