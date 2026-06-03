<!--
  TradeFlowCard.vue - 交易流水聚合卡片组件

  功能说明：
  - 展示聚合后的交易流水记录
  - 支持卖出卡片和买入卡片两种样式
  - 卖出卡片包含费用明细折叠面板
  - 根据交易类型显示不同颜色（收入红/支出绿）

  视觉规范：
  - 收入金额（卖出毛收入）：🔴 红色
  - 支出金额（买入/费用）：🟢 绿色
  - 净到账：🔴 红色加粗
  - 净利润：🔴 红色
  - 费用明细：⚫ 灰色（弱化展示）
  - 类型标签：【卖出】蓝色 / 【买入】橙色

  组件依赖：
  - 接收 record 作为 props，包含聚合后的交易数据
  - 使用 Element Plus 的 Collapse 组件展示费用明细

  维护提示：
  - 卖出卡片支持费用明细折叠/展开
  - 买入卡片简洁展示
  - 快捷操作按钮根据卡片类型动态显示
-->
<template>
  <div class="trade-flow-card" :class="`card-${record.card_type}`">
    <!-- 卡片头部：时间 + 金额 -->
    <div class="card-header">
      <span class="card-date">📅 {{ record.date }}</span>
      <span
        class="card-amount"
        :class="{
          'amount-income': record.gross_amount > 0,
          'amount-expense': record.gross_amount < 0
        }"
      >
        {{ record.gross_amount >= 0 ? '+' : '' }}¥{{ formatNumber(Math.abs(record.gross_amount)) }}
      </span>
    </div>

    <!-- 分隔线 -->
    <div class="card-divider"></div>

    <!-- 卡片内容 -->
    <div class="card-content">
      <!-- 标题和类型标签 -->
      <div class="card-title">
        <span class="type-tag" :class="`tag-${record.card_type}`">
          {{ record.card_type === 'sell' ? '【卖出】' : '【买入】' }}
        </span>
        <span class="figure-name">{{ record.figure_name }}</span>
        <span v-if="record.quantity > 1" class="quantity">×{{ record.quantity }}体</span>
      </div>

      <!-- 交易信息 -->
      <div class="card-info">
        <span v-if="record.order_number" class="info-item">
          <span class="info-label">订单流水号:</span> {{ record.order_number }}
        </span>
        <span class="info-item">
          <span class="info-label">订单状态:</span> {{ record.status }}
        </span>
        <span class="info-item">
          <span class="info-label">平台:</span> {{ record.platform || '-' }}
        </span>
        <span v-if="record.card_type === 'buy' && record.due_date" class="info-item">
          <span class="info-label">出荷日期:</span> {{ record.due_date }}
        </span>
      </div>

      <!-- 备注信息（仅买入卡片，有数据时展示） -->
      <div v-if="record.card_type === 'buy' && record.remarks" class="remarks-section">
        <span class="remarks-label">备注:</span>
        <span class="remarks-content">{{ record.remarks }}</span>
      </div>

      <!-- 卖出卡片：费用明细折叠面板 -->
      <template v-if="record.card_type === 'sell'">
        <div class="fee-section">
          <el-collapse v-if="record.fee_details && record.fee_details.length > 0">
            <el-collapse-item>
              <template #title>
                <span class="fee-summary">
                  <span class="fee-toggle">▼ 费用明细</span>
                  <span class="net-received">
                    实到账: <strong class="highlight">+¥{{ formatNumber(record.net_received) }}</strong>
                  </span>
                </span>
              </template>
              <div class="fee-list">
                <div
                  v-for="(fee, index) in record.fee_details"
                  :key="index"
                  class="fee-item"
                >
                  <span class="fee-name">├─ {{ fee.name }}</span>
                  <span
                    class="fee-amount"
                    :class="{ 'income': fee.color === 'red', 'expense': fee.color === 'green' }"
                  >
                    {{ fee.amount >= 0 ? '+' : '-' }}¥{{ formatNumber(Math.abs(fee.amount)) }}
                  </span>
                </div>
              </div>
            </el-collapse-item>
          </el-collapse>
          <div v-else class="net-received-simple">
            实到账: <strong class="highlight">+¥{{ formatNumber(record.net_received) }}</strong>
          </div>
        </div>

        <!-- 净利润和利润率 -->
        <div class="profit-section">
          <span class="profit-item">
            <span class="profit-label">净利润:</span>
            <span
              class="profit-value"
              :class="{ 'profit-positive': record.net_profit > 0, 'profit-negative': record.net_profit < 0 }"
            >
              {{ record.net_profit >= 0 ? '+' : '' }}¥{{ formatNumber(record.net_profit) }}
            </span>
          </span>
          <span class="profit-divider">|</span>
          <span class="profit-item">
            <span class="profit-label">利润率:</span>
            <span
              class="profit-value"
              :class="{ 'profit-positive': record.profit_rate > 0, 'profit-negative': record.profit_rate < 0 }"
            >
              {{ record.profit_rate >= 0 ? '+' : '' }}{{ record.profit_rate }}%
            </span>
          </span>
        </div>
      </template>

      <!-- 快捷操作按钮 -->
      <div class="card-actions">
        <template v-if="record.card_type === 'buy'">
          <el-button
            class="ghost-btn"
            size="small"
            @click="handleViewOrder"
          >
            查看订单
          </el-button>
        </template>
        <template v-else>
          <el-button
            v-for="action in record.actions"
            :key="action"
            :class="action === '查看订单' ? 'ghost-btn primary' : 'ghost-btn'"
            size="small"
            @click="handleAction(action)"
          >
            {{ action }}
          </el-button>
        </template>
      </div>
    </div>

    <!-- 买入订单抽屉 -->
    <BuyOrderDrawer
      v-if="record.card_type === 'buy'"
      v-model:visible="buyDrawerVisible"
      :order-id="record.id"
      @close="handleBuyDrawerClose"
      @action="handleBuyDrawerAction"
    />

    <!-- 卖出订单抽屉 -->
    <SellOrderDrawer
      v-if="record.card_type === 'sell'"
      v-model:visible="sellDrawerVisible"
      :sold-order-id="record.id"
      @close="handleSellDrawerClose"
      @refresh="handleSellDrawerRefresh"
    />
  </div>
</template>

<script>
import { ref } from 'vue'
import BuyOrderDrawer from './BuyOrderDrawer.vue'
import SellOrderDrawer from './SellOrderDrawer.vue'

export default {
  name: 'TradeFlowCard',
  components: {
    BuyOrderDrawer,
    SellOrderDrawer
  },
  props: {
    record: {
      type: Object,
      required: true,
      default: () => ({})
    }
  },
  emits: ['action', 'refresh'],
  setup(props, { emit }) {
    const buyDrawerVisible = ref(false)
    const sellDrawerVisible = ref(false)

    const formatNumber = (num) => {
      if (num === undefined || num === null) return '0'
      return num.toLocaleString('zh-CN', { minimumFractionDigits: 0, maximumFractionDigits: 2 })
    }

    const handleAction = (action) => {
      if (action === '查看订单') {
        handleViewOrder()
      } else {
        emit('action', action, props.record)
      }
    }

    // 点击查看订单按钮
    const handleViewOrder = () => {
      if (props.record.card_type === 'buy') {
        buyDrawerVisible.value = true
      } else if (props.record.card_type === 'sell') {
        sellDrawerVisible.value = true
      }
    }

    // 买入抽屉关闭
    const handleBuyDrawerClose = () => {
      buyDrawerVisible.value = false
    }

    // 买入抽屉操作
    const handleBuyDrawerAction = (actionKey, orderId) => {
      emit('action', actionKey, { ...props.record, order_id: orderId })
    }

    // 卖出抽屉关闭
    const handleSellDrawerClose = () => {
      sellDrawerVisible.value = false
    }

    // 卖出抽屉刷新
    const handleSellDrawerRefresh = () => {
      emit('refresh')
    }

    return {
      buyDrawerVisible,
      sellDrawerVisible,
      formatNumber,
      handleAction,
      handleViewOrder,
      handleBuyDrawerClose,
      handleBuyDrawerAction,
      handleSellDrawerClose,
      handleSellDrawerRefresh
    }
  }
}
</script>

<style scoped>
/* 卡片基础样式 */
.trade-flow-card {
  background-color: #f9f9f9;
  padding: 15px;
  border-radius: 8px;
  border: 1px solid #e0e0e0;
  transition: all 0.3s ease;
  margin-bottom: 15px;
}

.trade-flow-card:hover {
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

/* 卡片头部 */
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
}

.card-date {
  font-size: 14px;
  color: #666;
}

.card-amount {
  font-size: 20px;
  font-weight: bold;
}

/* 中国股市颜色标准：收入红，支出绿 */
.amount-income {
  color: #F44336; /* 红色 - 收入 */
}

.amount-expense {
  color: #4CAF50; /* 绿色 - 支出 */
}

/* 分隔线 */
.card-divider {
  height: 1px;
  background-color: #e0e0e0;
  margin: 10px 0;
}

/* 卡片内容 */
.card-content {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

/* 标题和类型标签 */
.card-title {
  font-size: 16px;
  font-weight: bold;
  color: #333;
  display: flex;
  align-items: center;
  gap: 8px;
}

.type-tag {
  padding: 2px 8px;
  border-radius: 4px;
  font-size: 14px;
}

/* 【卖出】标签：浅红底深红字，与红色金额呼应 */
.tag-sell {
  background-color: #FFF2F0;
  color: #CF1322;
  border: 1px solid #FFCCC7;
  border-radius: 4px;
}

/* 【买入】标签：浅绿底深绿字，与绿色金额呼应 */
.tag-buy {
  background-color: #F6FFED;
  color: #389E0D;
  border: 1px solid #B7EB8F;
  border-radius: 4px;
}

.figure-name {
  color: #333;
}

.quantity {
  color: #666;
  font-size: 14px;
}

/* 交易信息 */
.card-info {
  display: flex;
  flex-wrap: wrap;
  gap: 15px;
  font-size: 14px;
  color: #666;
}

.info-label {
  color: #999;
}

/* 备注信息 */
.remarks-section {
  margin-top: 10px;
  padding: 8px 12px;
  background-color: #f0f9ff;
  border-radius: 4px;
  border-left: 3px solid #409EFF;
  font-size: 13px;
}

.remarks-label {
  color: #409EFF;
  font-weight: bold;
  margin-right: 5px;
}

.remarks-content {
  color: #666;
}

/* 费用明细区域 */
.fee-section {
  margin-top: 5px;
}

.fee-summary {
  display: flex;
  justify-content: space-between;
  align-items: center;
  width: 100%;
  padding-right: 10px;
}

.fee-toggle {
  color: #666;
  font-size: 14px;
}

.net-received {
  color: #666;
  font-size: 14px;
}

.net-received .highlight {
  color: #F44336;
  font-weight: bold;
}

.net-received-simple {
  color: #666;
  font-size: 14px;
  text-align: right;
}

.net-received-simple .highlight {
  color: #F44336;
  font-weight: bold;
}

/* 费用列表 */
.fee-list {
  padding: 10px;
  background-color: #f5f5f5;
  border-radius: 4px;
}

.fee-item {
  display: flex;
  justify-content: space-between;
  padding: 5px 0;
  font-size: 14px;
}

.fee-name {
  color: #666;
}

.fee-amount {
  font-weight: bold;
}

.fee-amount.income {
  color: #F44336; /* 红色 - 收入 */
}

.fee-amount.expense {
  color: #4CAF50; /* 绿色 - 支出 */
}

/* 净利润区域 */
.profit-section {
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 14px;
  padding: 10px 0;
  border-top: 1px dashed #e0e0e0;
}

.profit-divider {
  color: #ccc;
}

.profit-label {
  color: #666;
}

.profit-value {
  font-weight: bold;
}

.profit-positive {
  color: #F44336; /* 红色 - 盈利 */
}

.profit-negative {
  color: #4CAF50; /* 绿色 - 亏损 */
}

/* 快捷操作按钮 */
.card-actions {
  display: flex;
  gap: 10px;
  margin-top: 10px;
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

/* 主操作按钮（查看订单）Hover 状态 */
.ghost-btn.primary:hover {
  border-color: #1890FF !important;
  color: #1890FF !important;
}

/* 折叠面板样式覆盖 */
:deep(.el-collapse) {
  border: none;
}

:deep(.el-collapse-item__header) {
  background-color: transparent;
  border: none;
  padding: 0;
  height: auto;
  line-height: normal;
}

:deep(.el-collapse-item__wrap) {
  background-color: transparent;
  border: none;
}

:deep(.el-collapse-item__content) {
  padding: 0;
}
</style>
