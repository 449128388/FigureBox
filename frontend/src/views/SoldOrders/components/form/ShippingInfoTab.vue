<template>
  <div class="tab-content">
    <div class="form-grid">
      <div class="form-group">
        <label>快递单号</label>
        <el-input v-model="order.tracking_number" placeholder="请输入快递单号" />
      </div>
      <div class="form-group">
        <label>物流公司</label>
        <el-select v-model="order.logistics_company" placeholder="请选择物流公司" style="width: 100%;" clearable>
          <el-option value="顺丰速运" label="顺丰速运" />
          <el-option value="中通快递" label="中通快递" />
          <el-option value="圆通速递" label="圆通速递" />
          <el-option value="申通快递" label="申通快递" />
          <el-option value="韵达快递" label="韵达快递" />
          <el-option value="德邦快递" label="德邦快递" />
          <el-option value="京东快递" label="京东快递" />
          <el-option value="EMS" label="EMS" />
          <el-option value="其他" label="其他" />
          
        </el-select>
      </div>
      <div class="form-group">
        <label>发货日期</label>
        <el-date-picker
          v-model="order.shipping_date"
          type="date"
          placeholder="选择发货日期"
          style="width: 100%;"
        />
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'ShippingInfoTab',
  props: {
    order: Object
  }
}
</script>

<style scoped>
/* 标签内容区域 */
.tab-content {
  padding: 20px;
}

/* 表单网格 */
.form-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
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
</style>