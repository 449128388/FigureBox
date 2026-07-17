<template>
  <div class="step-panel" :class="{ active: true }">
    <div class="panel-title">店铺与支付</div>
    <div class="panel-subtitle">填写购买店铺信息与定金支付详情</div>

    <div class="form-grid">
      <!-- 购买店铺 -->
      <div class="form-field">
        <label class="form-label">购买店铺</label>
        <el-input
          :model-value="shopName"
          placeholder="请输入购买店铺"
          @update:model-value="$emit('update:shopName', $event)"
        />
      </div>

      <!-- 店铺联系方式 -->
      <div class="form-field">
        <label class="form-label">店铺联系方式</label>
        <el-input
          :model-value="shopContact"
          placeholder="请输入店铺联系方式"
          @update:model-value="$emit('update:shopContact', $event)"
        />
      </div>

      <!-- 定金支付方式 -->
      <div class="form-field">
        <label class="form-label">定金支付方式</label>
        <el-select
          :model-value="paymentMethod"
          placeholder="请选择定金支付方式"
          style="width: 100%;"
          clearable
          @update:model-value="$emit('update:paymentMethod', $event)"
        >
          <el-option value="支付宝" label="支付宝" />
          <el-option value="微信" label="微信" />
          <el-option value="银行卡转账" label="银行卡转账" />
          <el-option value="现金" label="现金" />
        </el-select>
      </div>

      <!-- 定金支付时间 -->
      <div class="form-field">
        <label class="form-label">定金支付时间</label>
        <el-date-picker
          :model-value="paymentTime"
          type="datetime"
          placeholder="选择定金支付时间"
          style="width: 100%;"
          format="YYYY-MM-DD HH:mm:ss"
          value-format="YYYY-MM-DD HH:mm:ss"
          @update:model-value="$emit('update:paymentTime', $event)"
        />
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'Step2ShopPayment',
  props: {
    shopName: { type: String, default: '' },
    shopContact: { type: String, default: '' },
    paymentMethod: { type: String, default: '' },
    paymentTime: { type: String, default: '' }
  },
  emits: [
    'update:shopName',
    'update:shopContact',
    'update:paymentMethod',
    'update:paymentTime'
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
.form-field :deep(.el-select),
.form-field :deep(.el-date-editor) {
  width: 100%;
}
</style>
