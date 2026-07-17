<template>
  <div class="amount-row">
    <div class="stepper">
      <button type="button" class="stepper-btn" @click="adjust(-step)">−</button>
      <el-input
        :model-value="modelValue"
        class="stepper-input"
        :min="min"
        placeholder="0"
        controls-position="right"
        @update:model-value="$emit('update:modelValue', Number($event) || 0)"
      />
      <button type="button" class="stepper-btn" @click="adjust(step)">+</button>
    </div>
    <el-select
      :model-value="currencyModelValue"
      class="currency-select"
      style="width: 110px;"
      @update:model-value="$emit('update:currencyModelValue', $event)"
    >
      <el-option v-for="opt in currencyOptions" :key="opt.value" :value="opt.value" :label="opt.label" />
    </el-select>
  </div>
</template>

<script>
export default {
  name: 'AmountStepper',
  props: {
    modelValue: { type: Number, default: 0 },
    currencyModelValue: { type: String, default: 'CNY' },
    min: { type: Number, default: 0 },
    step: { type: Number, default: 10 }
  },
  emits: ['update:modelValue', 'update:currencyModelValue'],
  data() {
    return {
      currencyOptions: [
        { value: 'CNY', label: '人民币' },
        { value: 'JPY', label: '日元' },
        { value: 'USD', label: '美元' },
        { value: 'EUR', label: '欧元' }
      ]
    }
  },
  methods: {
    adjust(delta) {
      const val = Number(this.modelValue) || 0
      const newVal = Math.max(this.min, val + delta)
      if (newVal !== this.modelValue) {
        this.$emit('update:modelValue', newVal)
      }
    }
  }
}
</script>

<style scoped>
.amount-row {
  display: flex;
  align-items: center;
  gap: 8px;
  width: 100%;
}
.amount-row .stepper {
  flex: 1;
  min-width: 0;
}
.stepper {
  display: flex;
  align-items: center;
  border: 1px solid #d9d9d9;
  border-radius: 6px;
  overflow: hidden;
  background: #fff;
  height: 32px;
}
.stepper-btn {
  width: 32px;
  height: 100%;
  border: none;
  background: #fafafa;
  color: #999;
  cursor: pointer;
  font-size: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s;
  user-select: none;
  flex-shrink: 0;
}
.stepper-btn:hover {
  background: #f0f0f0;
  color: #666;
}
.stepper :deep(.stepper-input .el-input__wrapper) {
  border: none !important;
  box-shadow: none !important;
  padding: 0;
  height: 100%;
  border-radius: 0;
}
.stepper :deep(.stepper-input .el-input__inner) {
  text-align: center;
  font-size: 14px;
  color: #333;
  border: none;
  height: 100%;
}
.currency-select :deep(.el-input__wrapper) {
  height: 32px;
  border: 1px solid #d9d9d9;
  border-radius: 6px;
  background: #fff;
  transition: all 0.2s;
}
.currency-select :deep(.el-input__wrapper:hover) {
  border-color: #40a9ff;
}
.currency-select :deep(.el-input__wrapper.is-focus) {
  border-color: #40a9ff;
  box-shadow: 0 0 0 3px rgba(24, 144, 255, 0.1);
}
.currency-select :deep(.el-input__inner) {
  font-size: 13px;
  color: #333;
}
</style>
