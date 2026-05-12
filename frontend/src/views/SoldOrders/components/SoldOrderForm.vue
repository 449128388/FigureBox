<template>
  <div class="form-overlay" v-if="visible" @click.self="$emit('cancel')">
    <div class="form-container">
      <h3>{{ isEditing ? '编辑已出售订单' : '添加卖出' }}</h3>
      <form @submit.prevent="handleSubmit">
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
              <div class="tab-content">
                <el-form :model="localOrder" label-width="100px">
                  <div class="form-row">
                    <el-form-item label="选择手办 *" :error="figureError">
                      <el-select
                        v-model="localOrder.figure_id"
                        placeholder="🔍 搜索手办..."
                        filterable
                        class="form-select"
                        @change="handleFigureChange"
                      >
                        <el-option
                          v-for="figure in availableFigures"
                          :key="figure.id"
                          :label="figure.name"
                          :value="figure.id"
                        />
                      </el-select>
                    </el-form-item>
                    <el-form-item label="卖出平台 *">
                      <el-select v-model="localOrder.sell_platform" placeholder="请选择平台" class="form-select">
                        <el-option label="闲鱼" value="闲鱼" />
                        <el-option label="淘宝" value="淘宝" />
                        <el-option label="转转" value="转转" />
                        <el-option label="其他" value="其他" />
                      </el-select>
                    </el-form-item>
                  </div>
                  <div class="form-row">
                    <el-form-item label="订单编号">
                      <el-input v-model="localOrder.order_number" placeholder="请输入订单号" class="form-input" />
                    </el-form-item>
                    <el-form-item label="卖出状态">
                      <el-select v-model="localOrder.status" class="form-select">
                        <el-option label="待发货" value="待发货" />
                        <el-option label="已发货" value="已发货" />
                        <el-option label="已完成" value="已完成" />
                        <el-option label="退款/纠纷" value="退款/纠纷" />
                      </el-select>
                    </el-form-item>
                  </div>
                </el-form>
              </div>
            </el-tab-pane>
            
            <!-- 买家信息 -->
            <el-tab-pane label="买家信息" name="buyer">
              <template #label>
                <div class="tab-label">
                  <i class="fa-solid fa-user"></i>
                  <span>买家信息</span>
                </div>
              </template>
              <div class="tab-content">
                <el-form :model="localOrder" label-width="100px">
                  <div class="form-row">
                    <el-form-item label="买家手机号 *">
                      <el-input v-model="localOrder.buyer_phone" placeholder="请输入买家手机号" class="form-input" />
                    </el-form-item>
                  </div>
                  <div class="form-row">
                    <el-form-item label="买家地址">
                      <el-input v-model="localOrder.buyer_address" placeholder="请输入买家地址" class="form-input long-input" />
                    </el-form-item>
                  </div>
                </el-form>
              </div>
            </el-tab-pane>
            
            <!-- 价格与成本 -->
            <el-tab-pane label="价格成本" name="price">
              <template #label>
                <div class="tab-label">
                  <i class="fa-solid fa-money-bill"></i>
                  <span>价格成本</span>
                </div>
              </template>
              <div class="tab-content">
                <el-form :model="localOrder" label-width="80px">
                  <div class="form-row">
                    <el-form-item label="卖出价格 *">
                      <div class="price-input-group">
                        <span class="price-label">¥</span>
                        <el-input
                          v-model.number="localOrder.sell_price"
                          type="number"
                          placeholder="请输入卖出价格"
                          class="price-input"
                          @input="calculateProfit"
                        />
                        <span class="price-hint">(自动计算盈亏)</span>
                      </div>
                    </el-form-item>
                    <el-form-item label="成本价">
                      <div class="price-input-group">
                        <span class="price-label">¥</span>
                        <el-input
                          v-model.number="localOrder.cost_price"
                          type="number"
                          placeholder="请输入成本价格"
                          class="price-input"
                          @input="calculateProfit"
                        />
                        <span class="price-hint">(从库存自动带出)</span>
                      </div>
                    </el-form-item>
                    <el-form-item label="运费">
                      <div class="price-input-group">
                        <span class="price-label">¥</span>
                        <el-input
                          v-model.number="localOrder.shipping_fee"
                          type="number"
                          placeholder="请输入运费"
                          class="price-input"
                          @input="calculateProfit"
                        />
                        <span class="price-hint">(支出)</span>
                      </div>
                    </el-form-item>
                  </div>
                  <div class="form-row">
                    <el-form-item label="平台手续费">
                      <div class="price-input-group platform-fee">
                        <span class="price-label">¥</span>
                        <el-input
                          v-model.number="localOrder.platform_fee"
                          type="number"
                          placeholder="请输入手续费"
                          class="price-input"
                          @input="calculateProfit"
                        />
                        <span v-if="localOrder.sell_platform === '闲鱼'" class="fee-tip">
                          💡 闲鱼按 1% 自动计算
                        </span>
                      </div>
                    </el-form-item>
                  </div>
                </el-form>
              </div>
            </el-tab-pane>
            
            <!-- 物流信息 -->
            <el-tab-pane label="物流信息" name="shipping">
              <template #label>
                <div class="tab-label">
                  <i class="fa-solid fa-truck"></i>
                  <span>物流信息</span>
                </div>
              </template>
              <div class="tab-content">
                <el-form :model="localOrder" label-width="100px">
                  <div class="form-row">
                    <el-form-item label="快递单号">
                      <el-input v-model="localOrder.tracking_number" placeholder="请输入快递单号" class="form-input" />
                    </el-form-item>
                    <el-form-item label="发货日期">
                      <el-date-picker
                        v-model="localOrder.shipping_date"
                        type="date"
                        placeholder="选择发货日期"
                        class="form-input"
                      />
                    </el-form-item>
                  </div>
                </el-form>
              </div>
            </el-tab-pane>
            
            <!-- 盈亏预览 -->
            <el-tab-pane label="盈亏预览" name="profit">
              <template #label>
                <div class="tab-label">
                  <i class="fa-solid fa-chart-line"></i>
                  <span>盈亏预览</span>
                </div>
              </template>
              <div class="tab-content profit-preview">
                <div class="profit-calculation">
                  <span class="calc-item">卖出价: ¥{{ formatNumber(localOrder.sell_price) }}</span>
                  <span class="calc-operator">-</span>
                  <span class="calc-item">成本: ¥{{ formatNumber(localOrder.cost_price) }}</span>
                  <span class="calc-operator">-</span>
                  <span class="calc-item">运费: ¥{{ formatNumber(Math.abs(localOrder.shipping_fee)) }}</span>
                </div>
                <div class="profit-calculation">
                  <span class="calc-operator">-</span>
                  <span class="calc-item">手续费: ¥{{ formatNumber(Math.abs(localOrder.platform_fee)) }}</span>
                  <span class="calc-operator">=</span>
                  <span class="profit-result" :class="profitClass">
                    💰 净利润: {{ currentProfit >= 0 ? '+' : '' }}¥{{ formatNumber(Math.abs(currentProfit)) }}
                    ({{ profitIcon }}{{ formatNumber(Math.abs(currentProfitRate)) }}%)
                  </span>
                </div>
                <div class="profit-indicator">
                  <span :class="['indicator', { active: currentProfit > 0 }]">🟢 盈利</span>
                  <span :class="['indicator', { active: currentProfit < 0 }]">🔴 亏损</span>
                  <span :class="['indicator', { active: currentProfit === 0 }]">⚪ 持平</span>
                </div>
              </div>
            </el-tab-pane>
            
            <!-- 订单备注 -->
            <el-tab-pane label="订单备注" name="remark">
              <template #label>
                <div class="tab-label">
                  <i class="fa-solid fa-sticky-note"></i>
                  <span>订单备注</span>
                </div>
              </template>
              <div class="tab-content">
                <el-form :model="localOrder" label-width="100px">
                  <el-form-item label="备注">
                    <el-input
                      v-model="localOrder.remark"
                      type="textarea"
                      :rows="6"
                      placeholder="请输入订单备注..."
                      class="remark-input"
                    />
                  </el-form-item>
                </el-form>
              </div>
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
import { ref, watch, computed } from 'vue'

export default {
  name: 'SoldOrderForm',
  props: {
    visible: Boolean,
    isEditing: Boolean,
    newOrder: Object,
    availableFigures: Array
  },
  emits: ['saveOrder', 'cancel'],
  setup(props, context) {
    const localOrder = ref({
      figure_id: '',
      sell_platform: '',
      order_number: '',
      sell_price: 0,
      cost_price: 0,
      shipping_fee: 0,
      platform_fee: 0,
      buyer_phone: '',
      buyer_address: '',
      tracking_number: '',
      shipping_date: '',
      status: '待发货',
      remark: ''
    })

    const localActiveTab = ref('basic')
    const figureError = ref('')

    const currentProfit = computed(() => {
      return localOrder.value.sell_price - localOrder.value.cost_price - 
             Math.abs(localOrder.value.shipping_fee) - Math.abs(localOrder.value.platform_fee)
    })

    const currentProfitRate = computed(() => {
      if (localOrder.value.cost_price === 0) return 0
      return (currentProfit.value / localOrder.value.cost_price) * 100
    })

    const profitClass = computed(() => {
      if (currentProfit.value > 0) return 'profit-positive'
      if (currentProfit.value < 0) return 'profit-negative'
      return 'profit-neutral'
    })

    const profitIcon = computed(() => {
      if (currentProfit.value > 0) return '📈'
      if (currentProfit.value < 0) return '📉'
      return ''
    })

    const calculateProfit = () => {
      if (localOrder.value.sell_platform === '闲鱼' && localOrder.value.sell_price > 0) {
        localOrder.value.platform_fee = -localOrder.value.sell_price * 0.01
      }
    }

    const handleFigureChange = (figureId) => {
      const figure = props.availableFigures.find(f => f.id === figureId)
      if (figure) {
        localOrder.value.cost_price = figure.average_purchase_price || 0
      }
    }

    const formatNumber = (num) => {
      return Math.abs(num).toLocaleString('zh-CN', { minimumFractionDigits: 2, maximumFractionDigits: 2 })
    }

    watch(() => props.newOrder, (newVal) => {
      if (newVal) {
        localOrder.value = { ...localOrder.value, ...newVal }
      }
    }, { deep: true, immediate: true })

    const handleSubmit = () => {
      if (!localOrder.value.figure_id) {
        figureError.value = '请选择手办'
        localActiveTab.value = 'basic'
        return
      }
      if (!localOrder.value.sell_platform) {
        figureError.value = ''
        localActiveTab.value = 'basic'
        context.emit('saveOrder', { ...localOrder.value })
        return
      }
      if (!localOrder.value.buyer_phone) {
        figureError.value = ''
        localActiveTab.value = 'buyer'
        context.emit('saveOrder', { ...localOrder.value })
        return
      }
      figureError.value = ''
      context.emit('saveOrder', { ...localOrder.value })
    }

    return {
      localOrder,
      localActiveTab,
      figureError,
      currentProfit,
      currentProfitRate,
      profitClass,
      profitIcon,
      calculateProfit,
      handleFigureChange,
      formatNumber,
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

/* 标签页样式 - Komga风格 */
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

/* 标签内容区域 */
.tab-content {
  padding: 10px 0;
}

/* 表单行 */
.form-row {
  display: flex;
  gap: 20px;
  margin-bottom: 16px;
}

.form-row:last-child {
  margin-bottom: 0;
}

.form-select {
  width: 100%;
}

.form-input {
  width: 100%;
}

.form-input.long-input {
  flex: 2;
}

/* 价格输入 */
.price-input-group {
  display: flex;
  align-items: center;
  gap: 8px;
}

.price-label {
  font-size: 16px;
  font-weight: 600;
  color: #333;
}

.price-input {
  width: 120px;
}

.price-hint {
  font-size: 12px;
  color: #999;
}

.platform-fee {
  flex: 1;
}

.fee-tip {
  font-size: 12px;
  color: #FF9800;
  background: #fff3e0;
  padding: 4px 8px;
  border-radius: 4px;
  margin-left: auto;
}

/* 盈亏预览 */
.profit-preview {
  background: linear-gradient(135deg, #f5f7fa 0%, #e4e8ec 100%);
  padding: 20px;
  border-radius: 8px;
}

.profit-calculation {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 8px;
  margin-bottom: 8px;
}

.calc-item {
  font-size: 14px;
  color: #666;
}

.calc-operator {
  font-size: 14px;
  color: #999;
}

.profit-result {
  font-size: 16px;
  font-weight: 600;
  padding: 8px 12px;
  border-radius: 6px;
}

.profit-positive {
  color: #4CAF50;
  background: #e8f5e9;
}

.profit-negative {
  color: #f44336;
  background: #ffebee;
}

.profit-neutral {
  color: #666;
  background: #f5f5f5;
}

.profit-indicator {
  display: flex;
  gap: 15px;
  margin-top: 10px;
}

.indicator {
  font-size: 14px;
  color: #999;
  padding: 4px 12px;
  border-radius: 4px;
  background: #fff;
  transition: all 0.3s ease;
}

.indicator.active {
  color: #333;
  background: #fff;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

/* 备注输入 */
.remark-input {
  width: 100%;
  resize: none;
}

/* Komga风格的侧边栏标签页 */
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

:deep(.form-container .el-tabs__content) {
  padding: 24px;
  background-color: white;
}

:deep(.form-container .el-tabs--border-card) {
  border: none !important;
  box-shadow: none !important;
}

:deep(.form-container .el-tabs--border-card > .el-tabs__header) {
  border-top: none !important;
  border-bottom: none !important;
  background-color: #f5f5f5;
}

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

:deep(.form-container .el-tabs--border-card > .el-tabs__header .el-tabs__item) {
  border-top: none !important;
  border-bottom: none !important;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .form-container {
    max-height: 90vh;
    margin: 10px;
  }
  
  .form-row {
    flex-direction: column;
  }
  
  .profit-calculation {
    flex-direction: column;
    align-items: flex-start;
  }
}
</style>