<template>
  <div class="step-panel" :class="{ active: true }">
    <div class="panel-title">物流与备注</div>
    <div class="panel-subtitle">填写物流信息与订单备注</div>

    <!-- 未支付/已取消时的提示 -->
    <div v-if="isUnpaidOrCancelled" class="info-card">
      <span class="info-card-icon">
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <circle cx="12" cy="12" r="10"></circle>
          <line x1="12" y1="16" x2="12" y2="12"></line>
          <line x1="12" y1="8" x2="12.01" y2="8"></line>
        </svg>
      </span>
      <div class="info-card-text">当前尾款状态为「未支付」或「已取消」，无需填写物流与尾款支付信息。</div>
    </div>

    <!-- 已支付/已完成时的物流字段 -->
    <div v-if="isPaidOrDone" class="conditional-block">
      <div class="form-grid">
        <div class="form-field">
          <label class="form-label">物流订单</label>
          <el-input
            :model-value="trackingNumber"
            placeholder="请输入物流订单号"
            @update:model-value="$emit('update:trackingNumber', $event)"
          />
        </div>
        <div class="form-field">
          <label class="form-label">物流公司</label>
          <el-select
            :model-value="logisticsCompany"
            placeholder="请选择物流公司"
            style="width: 100%;"
            clearable
            @update:model-value="$emit('update:logisticsCompany', $event)"
          >
            <el-option value="顺丰速运" label="顺丰速运" />
            <el-option value="中通快递" label="中通快递" />
            <el-option value="圆通速递" label="圆通速递" />
            <el-option value="申通快递" label="申通快递" />
            <el-option value="韵达快递" label="韵达快递" />
            <el-option value="EMS" label="EMS" />
            <el-option value="其他" label="其他" />
          </el-select>
        </div>
      </div>
    </div>

    <!-- 已支付/已完成时的尾款支付信息 -->
    <div v-if="isPaidOrDone" class="balance-payment-section">
      <div class="section-title">尾款支付信息</div>
      <div class="form-grid">
        <div class="form-field">
          <label class="form-label">尾款支付方式</label>
          <el-select
            :model-value="balancePaymentMethod"
            placeholder="请选择支付方式"
            style="width: 100%;"
            clearable
            @update:model-value="$emit('update:balancePaymentMethod', $event)"
          >
            <el-option value="支付宝" label="支付宝" />
            <el-option value="微信" label="微信" />
            <el-option value="银行卡转账" label="银行卡转账" />
            <el-option value="现金" label="现金" />
          </el-select>
        </div>
        <div class="form-field">
          <label class="form-label">尾款支付时间</label>
          <el-date-picker
            :model-value="balancePaymentTime"
            type="datetime"
            placeholder="选择尾款支付时间"
            style="width: 100%;"
            format="YYYY-MM-DD HH:mm:ss"
            value-format="YYYY-MM-DD HH:mm:ss"
            @update:model-value="$emit('update:balancePaymentTime', $event)"
          />
        </div>
      </div>
    </div>

    <!-- 公共字段：订单编号 + 备注 -->
    <div class="common-section">
      <div class="form-grid">
        <div class="form-field full-width">
          <label class="form-label">订单编号</label>
          <el-input
            :model-value="orderNumber"
            placeholder="请输入订单编号（非必填）"
            @update:model-value="$emit('update:orderNumber', $event)"
          />
        </div>
        <div class="form-field full-width">
          <label class="form-label">订单备注</label>
          <el-input
            :model-value="remarks"
            type="textarea"
            :rows="3"
            placeholder="请输入订单备注（支持换行）"
            @update:model-value="$emit('update:remarks', $event)"
          />
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'Step3LogisticsNotes',
  props: {
    status: { type: String, default: '未支付' },
    trackingNumber: { type: String, default: '' },
    logisticsCompany: { type: String, default: '' },
    balancePaymentMethod: { type: String, default: '' },
    balancePaymentTime: { type: String, default: '' },
    orderNumber: { type: String, default: '' },
    remarks: { type: String, default: '' }
  },
  emits: [
    'update:status',
    'update:trackingNumber',
    'update:logisticsCompany',
    'update:balancePaymentMethod',
    'update:balancePaymentTime',
    'update:orderNumber',
    'update:remarks'
  ],
  computed: {
    isUnpaidOrCancelled() {
      return ['未支付', '已取消'].includes(this.status)
    },
    isPaidOrDone() {
      return ['已支付', '已完成'].includes(this.status)
    }
  }
}
</script>

<style scoped>
.step-panel {
  display: none;
  animation: fadeSlide 0.3s ease-out;
}
.step-panel.active {
  display: block;
}
@keyframes fadeSlide {
  from { opacity: 0; transform: translateX(12px); }
  to { opacity: 1; transform: translateX(0); }
}

.panel-title {
  font-size: 16px;
  font-weight: 600;
  color: #1f1f1f;
  margin-bottom: 6px;
}
.panel-subtitle {
  font-size: 13px;
  color: #999;
  margin-bottom: 24px;
}
.form-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 20px 24px;
}
.form-field {
  display: flex;
  flex-direction: column;
  gap: 6px;
}
.form-field.full-width {
  grid-column: 1 / -1;
}
.form-label {
  font-size: 13px;
  font-weight: 500;
  color: #333;
}

/* 信息提示卡片 */
.info-card {
  background: #f6ffed;
  border: 1px solid #b7eb8f;
  border-radius: 6px;
  padding: 12px 16px;
  margin-bottom: 20px;
  display: flex;
  align-items: flex-start;
  gap: 10px;
}
.info-card-icon {
  color: #52c41a;
  flex-shrink: 0;
  margin-top: 2px;
}
.info-card-text {
  font-size: 13px;
  color: #389e0d;
  line-height: 1.5;
}

.conditional-block {
  margin-bottom: 0;
}
.balance-payment-section {
  margin-top: 20px;
}
.section-title {
  font-size: 14px;
  font-weight: 600;
  color: #333;
  margin-bottom: 16px;
  padding-bottom: 8px;
  border-bottom: 1px solid #f0f0f0;
}
.common-section {
  margin-top: 24px;
  padding-top: 20px;
  border-top: 1px solid #f0f0f0;
}

.form-field :deep(.el-select),
.form-field :deep(.el-date-editor) {
  width: 100%;
}
</style>
