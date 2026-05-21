<template>
  <div class="tab-content">
    <div class="form-grid">
      <div class="form-group currency-group">
        <label>卖出价格 <span class="required">*</span></label>
        <div class="currency-input-wrapper">
          <el-input-number
            v-model="order.sell_price"
            :min="0"
            :step="1"
            :precision="2"
            controls-position="right"
            class="price-input"
            @change="$emit('profitChange')"
          />
          <el-select v-model="order.sell_price_currency" class="currency-select">
            <el-option label="人民币" value="CNY" />
            <el-option label="美元" value="USD" />
            <el-option label="日元" value="JPY" />
            <el-option label="欧元" value="EUR" />
          </el-select>
        </div>
      </div>
      <div class="form-group currency-group">
        <label>成本价</label>
        <div class="currency-input-wrapper">
          <el-input-number
            v-model="order.cost_price"
            :min="0"
            :step="1"
            :precision="2"
            controls-position="right"
            class="price-input"
            :disabled="true"
            @change="$emit('profitChange')"
          />
          <el-select v-model="order.cost_price_currency" class="currency-select" :disabled="true">
            <el-option label="人民币" value="CNY" />
            <el-option label="美元" value="USD" />
            <el-option label="日元" value="JPY" />
            <el-option label="欧元" value="EUR" />
          </el-select>
        </div>
      </div>
      <div class="form-group currency-group">
        <label>运费</label>
        <div class="currency-input-wrapper">
          <el-input-number
            v-model="order.shipping_fee"
            :min="0"
            :step="1"
            :precision="2"
            controls-position="right"
            class="price-input"
            @change="$emit('profitChange')"
          />
          <el-select v-model="order.shipping_fee_currency" class="currency-select">
            <el-option label="人民币" value="CNY" />
            <el-option label="美元" value="USD" />
            <el-option label="日元" value="JPY" />
            <el-option label="欧元" value="EUR" />
          </el-select>
        </div>
      </div>
      <div class="form-group currency-group">
        <label>
          平台手续费
          <el-tooltip v-if="order.sell_platform === '闲鱼（个人卖家）'" content="基础费率 0.6%，单笔最高 60 元封顶；当月订单>10笔且成交额>1万元后，超出部分加收 1%" placement="top">
            <el-icon class="tooltip-icon"><QuestionFilled /></el-icon>
          </el-tooltip>
          <el-tooltip v-else-if="order.sell_platform === '闲鱼（鱼小铺）'" content="固定费率 1.6%，上不封顶" placement="top">
            <el-icon class="tooltip-icon"><QuestionFilled /></el-icon>
          </el-tooltip>
        </label>
        <div class="currency-input-wrapper">
          <el-input-number
            v-model="order.platform_fee"
            :min="0"
            :step="1"
            :precision="2"
            controls-position="right"
            class="price-input"
            @change="$emit('profitChange')"
          />
          <el-select v-model="order.platform_fee_currency" class="currency-select">
            <el-option label="人民币" value="CNY" />
            <el-option label="美元" value="USD" />
            <el-option label="日元" value="JPY" />
            <el-option label="欧元" value="EUR" />
          </el-select>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { QuestionFilled } from '@element-plus/icons-vue'

export default {
  name: 'PriceCostTab',
  components: { QuestionFilled },
  props: {
    order: Object,
    isEditing: Boolean,
    figureId: [Number, String]
  },
  emits: ['profitChange']
}
</script>

<style scoped>
/* 标签内容区域 */
.tab-content {
  padding: 20px;
}

/* 表单网格 - 单列布局 */
.form-grid {
  display: grid;
  grid-template-columns: 1fr;
  gap: 20px;
}

.form-group {
  margin-bottom: 0;
}

.form-group label {
  display: block;
  margin-bottom: 8px;
  color: #333;
  font-weight: 500;
  font-size: 16px;
}

.form-group label .required {
  color: #f56c6c;
  margin-left: 4px;
}

.tooltip-icon {
  margin-left: 4px;
  color: #909399;
  cursor: help;
}

/* 币种选择框样式 */
.currency-group .currency-input-wrapper {
  display: flex;
  align-items: center;
  gap: 8px;
  max-width: 400px;
}

.currency-group .price-input {
  flex: 1;
}

.currency-group .currency-select {
  flex-shrink: 0;
  width: 100px;
}

.currency-group .currency-select .el-input__inner {
  text-align: center;
}
</style>
