<template>
  <div class="tab-content">
    <div class="form-group full-width">
      <label>备注</label>
      <el-input
        v-model="order.remark"
        type="textarea"
        :rows="6"
        placeholder="请输入订单备注..."
      />
    </div>
  </div>
</template>

<script>
export default {
  name: 'RemarkTab',
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

.form-group {
  margin-bottom: 0;
}

.form-group.full-width {
  grid-column: 1 / -1;
}

.form-group label {
  display: block;
  margin-bottom: 8px;
  color: #333;
  font-weight: 500;
  font-size: 16px;
}
</style>