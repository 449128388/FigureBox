<template>
  <div class="sold-order-item">
    <div class="figure-image">
      <!-- 批量选择复选框 -->
      <div v-if="isBatchMode" class="batch-checkbox-wrapper">
        <div
          class="checkbox-container"
          :class="{ 'checkbox--checked': isSelected }"
          @click.stop
        >
          <el-checkbox
            :model-value="isSelected"
            size="large"
            @change="handleToggleSelection"
          />
        </div>
      </div>
      <img
        :src="order.figure_image || '/imgs/no_image.png'"
        :alt="order.figure_name"
        loading="lazy"
        decoding="async"
      >
    </div>
    <h3><router-link :to="`/figures/${order.figure_id}`" class="figure-name-link">{{ order.figure_name }}</router-link></h3>
    <p class="sell-platform">卖出平台: {{ order.sell_platform || '-' }}</p>
    <p class="order-number">订单号: {{ order.order_number || '-' }}</p>
    
    <div class="price-section">
      <div class="price-item">
        <span class="price-label">卖出价:</span>
        <span class="price-value sell">¥{{ formatNumber(order.sell_price) }}</span>
      </div>
      <div class="price-item">
        <span class="price-label">成本价:</span>
        <span class="price-value cost">¥{{ formatNumber(order.cost_price) }}</span>
      </div>
      <div class="price-item">
        <span class="price-label">运费:</span>
        <span class="price-value shipping">{{ order.shipping_fee !== 0 ? '-¥' + formatNumber(Math.abs(order.shipping_fee)) : '¥0' }}</span>
      </div>
      <div class="price-item">
        <span class="price-label">手续费:</span>
        <span class="price-value fee">{{ order.platform_fee !== 0 ? '-¥' + formatNumber(Math.abs(order.platform_fee)) : '¥0' }}</span>
      </div>
    </div>
    
    <div class="profit-section">
      <div class="profit-line"></div>
      <div class="profit-info" :class="order.net_profit >= 0 ? 'profit-positive' : 'profit-negative'">
        <span class="profit-icon">{{ order.net_profit >= 0 ? '💰' : '📉' }}</span>
        <span class="profit-text">净利润: {{ order.net_profit >= 0 ? '+' : '' }}¥{{ formatNumber(Math.abs(order.net_profit || 0)) }}</span>
      </div>
      <div class="profit-rate" :class="order.profit_rate >= 0 ? 'rate-positive' : 'rate-negative'">
        <span class="rate-icon">{{ order.profit_rate >= 0 ? '📈' : '📉' }}</span>
        <span class="rate-text">利润率: {{ order.profit_rate >= 0 ? '+' : '' }}{{ (order.profit_rate || 0).toFixed(1) }}%</span>
      </div>
    </div>
    
    <div class="buyer-info">
      <p>买家手机: {{ order.buyer_phone || '-' }}</p>
      <p>快递单: {{ order.tracking_number || '未填写' }}</p>
    </div>
    
    <div class="order-actions">
      <el-button-group class="action-button-group">
        <el-button
          type="primary"
          :icon="Edit"
          @click="$emit('editOrder', order)"
        >
          编辑
        </el-button>
        <el-button
          type="danger"
          :icon="Delete"
          @click="$emit('deleteOrder', order)"
        >
          删除
        </el-button>
      </el-button-group>
    </div>
  </div>
</template>

<script>
import { Edit, Delete } from '@element-plus/icons-vue'

export default {
  name: 'SoldOrderItem',
  props: {
    order: {
      type: Object,
      required: true
    },
    isBatchMode: {
      type: Boolean,
      default: false
    },
    isSelected: {
      type: Boolean,
      default: false
    }
  },
  emits: ['editOrder', 'deleteOrder', 'toggle-selection'],
  setup(props, { emit }) {
    const handleToggleSelection = (selected) => {
      emit('toggle-selection', props.order.id, selected)
    }

    return {
      Edit,
      Delete,
      handleToggleSelection
    }
  },
  methods: {
    formatNumber(num) {
      return num.toLocaleString('zh-CN', { minimumFractionDigits: 2, maximumFractionDigits: 2 })
    }
  }
}
</script>

<style scoped>
.sold-order-item {
  background: white;
  padding: 20px;
  border-radius: 8px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
  display: flex;
  flex-direction: column;
  height: 100%;
}

.sold-order-item .figure-image {
  width: 100%;
  height: 180px;
  border-radius: 4px;
  overflow: hidden;
  margin-bottom: 15px;
  background-color: #f5f5f5;
  position: relative;
}

.batch-checkbox-wrapper {
  position: absolute;
  top: 8px;
  left: 8px;
  z-index: 10;
}

.checkbox-container {
  background: transparent;
  border-radius: 4px;
  padding: 4px;
  transition: all 0.3s ease;
}

.checkbox-container:hover {
  background: transparent;
}

.checkbox--checked {
  background: transparent;
}

.sold-order-item .figure-image img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  content-visibility: auto;
}

.sold-order-item h3 {
  margin-bottom: 10px;
  color: #333;
  font-size: 16px;
}

.sell-platform {
  color: #4CAF50;
  font-weight: 500;
  margin-bottom: 5px;
}

.order-number {
  color: #666;
  font-size: 13px;
  margin-bottom: 15px;
}

.price-section {
  background: #f9f9f9;
  padding: 12px;
  border-radius: 6px;
  margin-bottom: 10px;
}

.price-item {
  display: flex;
  justify-content: space-between;
  margin-bottom: 6px;
}

.price-item:last-child {
  margin-bottom: 0;
}

.price-label {
  color: #888;
  font-size: 13px;
}

.price-value {
  font-weight: 600;
  font-size: 14px;
}

.price-value.sell {
  color: #4CAF50;
}

.price-value.cost {
  color: #666;
}

.price-value.shipping,
.price-value.fee {
  color: #f44336;
}

.profit-section {
  margin-bottom: 15px;
}

.profit-line {
  border-top: 2px dashed #ddd;
  margin-bottom: 10px;
}

.profit-info {
  display: flex;
  align-items: center;
  gap: 6px;
  margin-bottom: 6px;
}

.profit-icon {
  font-size: 16px;
}

.profit-text {
  font-size: 14px;
  font-weight: 600;
}

.profit-positive .profit-text {
  color: #f44336;
}

.profit-negative .profit-text {
  color: #4CAF50;
}

.profit-rate {
  display: flex;
  align-items: center;
  gap: 6px;
}

.rate-icon {
  font-size: 14px;
}

.rate-text {
  font-size: 13px;
  font-weight: 500;
}

.rate-positive .rate-text {
  color: #f44336;
}

.rate-negative .rate-text {
  color: #4CAF50;
}

.buyer-info {
  background: #f5f5f5;
  padding: 10px;
  border-radius: 4px;
  margin-bottom: 15px;
}

.buyer-info p {
  margin: 4px 0;
  font-size: 13px;
  color: #666;
}

.figure-name-link {
  color: #333;
  text-decoration: none;
  cursor: pointer;
  transition: color 0.3s ease;
}

.figure-name-link:hover {
  color: #2196F3;
}

.order-actions {
  display: flex;
  justify-content: center;
  margin-top: auto;
  padding-top: 15px;
  border-top: 1px solid #eee;
}

.action-button-group {
  display: flex;
  gap: 0;
}

.action-button-group :deep(.el-button) {
  min-width: 80px;
}
</style>