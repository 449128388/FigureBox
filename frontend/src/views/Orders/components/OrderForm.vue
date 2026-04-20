<!--
  OrderForm.vue - 订单表单组件

  功能说明：
  - 提供订单添加和编辑功能
  - 包含手办选择、定金、尾款、购买日期、出货日期、状态等字段
  - 支持表单验证和错误提示
  - 编辑模式下禁用手办选择

  组件依赖：
  - 使用 Element Plus 的 el-select、el-input-number、el-date-picker 组件

  维护提示：
  - 通过 visible 属性控制显示
  - 通过 isEditing 属性判断是添加还是编辑模式
  - 表单提交通过 saveOrder 事件向父组件传递
  - 手办选择在编辑模式下被禁用
  - 表单容器最大宽度 800px，禁止水平滚动
-->
<template>
  <div class="form-overlay" v-if="visible">
    <div class="form-container">
      <h3>{{ isEditing ? '编辑订单' : '添加订单' }}</h3>
      <form @submit.prevent="$emit('saveOrder', newOrder)">
        <div class="form-grid">
          <div class="form-group">
            <label>手办</label>
            <el-select
              v-model="newOrder.figure_id"
              placeholder="请选择手办"
              style="width: 100%;"
              :class="{ 'error-input': figureError }"
              :disabled="isEditing"
            >
              <el-option 
                v-for="figure in availableFigures" 
                :key="figure.id" 
                :label="figure.name" 
                :value="figure.id" 
              />
            </el-select>
            <div v-if="figureError" class="error-message">{{ figureError }}</div>
          </div>
          <div class="form-group">
            <label>定金</label>
            <div class="price-currency-container">
              <el-input-number v-model="newOrder.deposit" placeholder="请输入定金" :min="0" :step="1" style="flex: 1;"></el-input-number>
              <el-select v-model="newOrder.deposit_currency" placeholder="选择币种" style="width: 100px;">
                <el-option value="CNY" label="人民币" />
                <el-option value="JPY" label="日元" />
                <el-option value="USD" label="美元" />
                <el-option value="EUR" label="欧元" />
              </el-select>
            </div>
          </div>
          <div class="form-group">
            <label>尾款</label>
            <div class="price-currency-container">
              <el-input-number v-model="newOrder.balance" placeholder="请输入尾款" :min="0" :step="1" style="flex: 1;"></el-input-number>
              <el-select v-model="newOrder.balance_currency" placeholder="选择币种" style="width: 100px;">
                <el-option value="CNY" label="人民币" />
                <el-option value="JPY" label="日元" />
                <el-option value="USD" label="美元" />
                <el-option value="EUR" label="欧元" />
              </el-select>
            </div>
          </div>
          <div class="form-group">
            <label>出荷日期</label>
            <el-date-picker
              v-model="newOrder.due_date"
              type="date"
              placeholder="选择出荷日期"
              style="width: 100%;"
              :class="{ 'error-input': dueDateError }"
            ></el-date-picker>
            <div v-if="dueDateError" class="error-message">{{ dueDateError }}</div>
          </div>
          <div class="form-group">
            <label>尾款状态</label>
            <el-select v-model="newOrder.status" placeholder="请选择尾款状态" style="width: 100%;">
              <el-option value="未支付" label="未支付" />
              <el-option value="已支付" label="已支付" />
              <el-option value="已取消" label="已取消" />
              <el-option value="已完成" label="已完成" />
            </el-select>
          </div>
          <div class="form-group">
            <label>购买店铺</label>
            <el-input v-model="newOrder.shop_name" placeholder="请输入购买店铺" style="width: 100%;"></el-input>
          </div>
          <div class="form-group">
            <label>店铺联系方式</label>
            <el-input v-model="newOrder.shop_contact" placeholder="请输入店铺联系方式" style="width: 100%;"></el-input>
          </div>
          <div class="form-group" v-if="isEditing || newOrder.status === '已支付' || newOrder.status === '已完成'">
            <label>物流订单</label>
            <el-input v-model="newOrder.tracking_number" placeholder="请输入物流订单号" style="width: 100%;"></el-input>
          </div>
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
export default {
  name: 'OrderForm',
  props: {
    visible: {
      type: Boolean,
      default: false
    },
    isEditing: {
      type: Boolean,
      default: false
    },
    newOrder: {
      type: Object,
      required: true
    },
    availableFigures: {
      type: Array,
      default: () => []
    },
    figureError: {
      type: String,
      default: ''
    },
    dueDateError: {
      type: String,
      default: ''
    }
  },
  emits: ['saveOrder', 'cancel']
}
</script>

<style scoped>
/* 表单样式 */
.form-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.form-container {
  background: white;
  padding: 30px;
  border-radius: 8px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);
  width: 90%;
  max-width: 800px;
  max-height: 80vh;
  overflow-y: auto;
  overflow-x: hidden;
  box-sizing: border-box;
}

.form-container h3 {
  margin-top: 0;
  margin-bottom: 20px;
  color: #333;
  font-size: 20px;
  font-weight: 600;
  border-bottom: 1px solid #e0e0e0;
  padding-bottom: 10px;
}

.form-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 15px;
  margin-bottom: 20px;
}

.form-group {
  display: flex;
  flex-direction: column;
}

.form-group label {
  margin-bottom: 8px;
  font-weight: 500;
  color: #333;
}

/* 价格和币种组合容器 */
.price-currency-container {
  display: flex;
  gap: 10px;
  width: 100%;
  box-sizing: border-box;
}

/* 错误提示样式 */
:deep(.error-input .el-input__wrapper) {
  box-shadow: 0 0 0 1px #f56c6c inset !important;
}

:deep(.error-input .el-input__wrapper:hover) {
  box-shadow: 0 0 0 1px #f56c6c inset !important;
}

:deep(.error-input .el-input__wrapper.is-focus) {
  box-shadow: 0 0 0 1px #f56c6c inset !important;
}

:deep(.error-input .el-select .el-input__wrapper) {
  box-shadow: 0 0 0 1px #f56c6c inset !important;
}

:deep(.error-input .el-select .el-input__wrapper:hover) {
  box-shadow: 0 0 0 1px #f56c6c inset !important;
}

:deep(.error-input .el-select .el-input__wrapper.is-focus) {
  box-shadow: 0 0 0 1px #f56c6c inset !important;
}

/* 【新增】日期选择器错误样式 */
:deep(.error-input .el-input__wrapper) {
  box-shadow: 0 0 0 1px #f56c6c inset !important;
}

:deep(.error-input .el-input__wrapper:hover) {
  box-shadow: 0 0 0 1px #f56c6c inset !important;
}

:deep(.error-input .el-input__wrapper.is-focus) {
  box-shadow: 0 0 0 1px #f56c6c inset !important;
}

.error-message {
  color: #f56c6c;
  font-size: 12px;
  line-height: 1;
  padding-top: 4px;
}

.form-actions {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
  margin-top: 20px;
  padding-top: 20px;
  border-top: 1px solid #e0e0e0;
}

.btn-cancel {
  padding: 10px 20px;
  border: 1px solid #dcdfe6;
  border-radius: 6px;
  background-color: white;
  color: #606266;
  cursor: pointer;
  font-size: 14px;
  font-weight: 500;
  transition: all 0.3s ease;
}

.btn-cancel:hover {
  color: #409eff;
  border-color: #c6e2ff;
  background-color: #ecf5ff;
}

.btn-submit {
  padding: 10px 20px;
  border: none;
  border-radius: 6px;
  background-color: #4CAF50;
  color: white;
  cursor: pointer;
  font-size: 14px;
  font-weight: 500;
  transition: all 0.3s ease;
}

.btn-submit:hover {
  background-color: #45a049;
  transform: translateY(-2px);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
}

@media (max-width: 768px) {
  .form-grid {
    grid-template-columns: 1fr;
  }
  
  .form-container {
    width: 95%;
    padding: 20px;
  }
}
</style>