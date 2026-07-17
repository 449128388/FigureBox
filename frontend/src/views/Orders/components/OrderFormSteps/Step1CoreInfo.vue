<template>
  <div class="step-panel" :class="{ active: true }">
    <div class="panel-title">核心信息</div>
    <div class="panel-subtitle">填写手办基本信息与订单金额</div>

    <div class="form-grid">
      <!-- 手办 -->
      <div class="form-field">
        <label class="form-label">
          手办 <span style="color:#ff4d4f">*</span>
        </label>
        <el-select
          :model-value="figureId"
          placeholder="请选择手办"
          style="width: 100%;"
          :disabled="isEditing"
          :class="{ 'error-input': figureError }"
          filterable
          @update:model-value="$emit('update:figureId', $event)"
        >
          <el-option
            v-for="figure in availableFigures"
            :key="figure.id"
            :label="figure.name"
            :value="figure.id"
          />
        </el-select>
        <div v-if="figureError" class="field-error">{{ figureError }}</div>
      </div>

      <!-- 定金 -->
      <div class="form-field">
        <label class="form-label">
          定金 <span style="color:#ff4d4f">*</span>
        </label>
        <AmountStepper
          :model-value="deposit"
          :currency-model-value="depositCurrency"
          @update:model-value="$emit('update:deposit', $event)"
          @update:currency-model-value="$emit('update:depositCurrency', $event)"
        />
      </div>

      <!-- 尾款 -->
      <div class="form-field">
        <label class="form-label">尾款</label>
        <AmountStepper
          :model-value="balance"
          :currency-model-value="balanceCurrency"
          @update:model-value="$emit('update:balance', $event)"
          @update:currency-model-value="$emit('update:balanceCurrency', $event)"
        />
      </div>

      <!-- 出荷日期 -->
      <div class="form-field">
        <label class="form-label">出荷日期</label>
        <el-date-picker
          :model-value="dueDate"
          type="date"
          placeholder="选择出荷日期"
          style="width: 100%;"
          :class="{ 'error-input': dueDateError }"
          value-format="YYYY-MM-DD"
          @update:model-value="$emit('update:dueDate', $event)"
        />
        <div v-if="dueDateError" class="field-error">{{ dueDateError }}</div>
      </div>

      <!-- 订单类型 -->
      <div class="form-field">
        <label class="form-label">订单类型</label>
        <el-select :model-value="orderType" placeholder="请选择订单类型" style="width: 100%;" @update:model-value="$emit('update:orderType', $event)">
          <el-option value="定金预定" label="定金预定" />
          <el-option value="全款预定" label="全款预定" />
          <el-option value="现货" label="现货" />
          <el-option value="补仓" label="补仓" />
        </el-select>
      </div>

      <!-- 尾款状态 -->
      <div class="form-field">
        <label class="form-label">
          尾款状态 <span style="color:#ff4d4f">*</span>
        </label>
        <el-select :model-value="status" placeholder="请选择尾款状态" style="width: 100%;" @update:model-value="$emit('update:status', $event)">
          <el-option value="未支付" label="未支付" />
          <el-option value="已支付" label="已支付" />
          <el-option value="已取消" label="已取消" />
          <el-option value="已完成" label="已完成" />
        </el-select>
      </div>
    </div>
  </div>
</template>

<script>
import AmountStepper from '../OrderFormUI/AmountStepper.vue'

export default {
  name: 'Step1CoreInfo',
  components: { AmountStepper },
  props: {
    figureId: [Number, String],
    deposit: { type: Number, default: 0 },
    depositCurrency: { type: String, default: 'CNY' },
    balance: { type: Number, default: 0 },
    balanceCurrency: { type: String, default: 'CNY' },
    dueDate: [String, Object],
    orderType: { type: String, default: '定金预定' },
    status: { type: String, default: '未支付' },
    isEditing: { type: Boolean, default: false },
    availableFigures: { type: Array, default: () => [] },
    figureError: { type: String, default: '' },
    dueDateError: { type: String, default: '' }
  },
  emits: [
    'update:figureId',
    'update:deposit',
    'update:depositCurrency',
    'update:balance',
    'update:balanceCurrency',
    'update:dueDate',
    'update:orderType',
    'update:status'
  ]
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
.form-label {
  font-size: 13px;
  font-weight: 500;
  color: #333;
}
.field-error {
  font-size: 12px;
  color: #f56c6c;
  line-height: 1;
}
.form-field :deep(.el-select),
.form-field :deep(.el-date-editor) {
  width: 100%;
}
.form-field :deep(.error-input .el-input__wrapper) {
  box-shadow: 0 0 0 1px #f56c6c inset !important;
}
</style>
