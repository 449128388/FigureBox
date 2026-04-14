<!--
  FormBasicTab.vue - 手办表单基础信息标签页组件

  功能说明：
  - 提供手办基础信息的输入表单
  - 包含名称、定价、币种、日文名、制造商、入手价格、入手形式、入手时间、市场价等字段
  - 支持图片上传和预览功能
  - 支持表单验证和错误提示

  组件依赖：
  - 使用 Element Plus 的 el-input、el-input-number、el-select、el-date-picker 组件
  - 集成 ImageUpload 组件处理图片上传

  维护提示：
  - 接收 figure 作为 props，双向绑定表单数据
  - 接收各种错误信息作为 props 显示错误提示
  - 输入事件通过 validate-* 事件向父组件传递，触发验证
  - 图片操作通过 view-image、remove-image、file-upload 事件向父组件传递
-->
<template>
  <div class="form-grid">
    <div class="form-group">
      <label>名称</label>
      <el-input 
        v-model="localFigure.name" 
        placeholder="请输入名称" 
        :class="{ 'error-input': nameError }"
        @input="$emit('validate-name-input')"
        ref="nameInput"
      ></el-input>
      <div v-if="nameError" class="error-message">{{ nameError }}</div>
    </div>
    <div class="form-group">
      <label>定价</label>
      <div class="price-currency-container">
        <el-input-number v-model="localFigure.price" placeholder="请输入定价" :min="0" :step="1" required style="width: 200px;"></el-input-number>
        <el-select v-model="localFigure.currency" placeholder="选择币种" style="width: 120px;">
          <el-option value="CNY" label="人民币" />
          <el-option value="JPY" label="日元" />
          <el-option value="USD" label="美元" />
          <el-option value="EUR" label="欧元" />
        </el-select>
      </div>
    </div>
    <div class="form-group">
      <label>日文名</label>
      <el-input
        v-model="localFigure.japanese_name"
        placeholder="请输入日文名"
        :class="{ 'error-input': japaneseNameError }"
        @input="$emit('validate-japanese-name-input')"
        maxlength="100"
        show-word-limit
      ></el-input>
      <div v-if="japaneseNameError" class="error-message">{{ japaneseNameError }}</div>
    </div>
    <div class="form-group">
      <label>入手价格</label>
      <div class="price-currency-container">
        <el-input-number v-model="localFigure.purchase_price" placeholder="请输入入手价格" :min="0" :step="1" style="width: 200px;"></el-input-number>
        <el-select v-model="localFigure.purchase_currency" placeholder="选择币种" style="width: 120px;">
          <el-option value="CNY" label="人民币" />
          <el-option value="JPY" label="日元" />
          <el-option value="USD" label="美元" />
          <el-option value="EUR" label="欧元" />
        </el-select>
      </div>
    </div>
    <div class="form-group">
      <label>出货日</label>
      <el-date-picker v-model="localFigure.release_date" type="date" placeholder="选择出货日" style="width: 100%;"></el-date-picker>
    </div>
    <div class="form-group">
      <label>入手时间</label>
      <el-date-picker v-model="localFigure.purchase_date" type="date" placeholder="选择入手时间" style="width: 100%;"></el-date-picker>
    </div>
    <div class="form-group">
      <label>入手途径</label>
      <el-input 
        v-model="localFigure.purchase_method" 
        placeholder="请输入入手途径"
        :class="{ 'error-input': purchaseMethodError }"
        @input="$emit('validate-purchase-method-input')"
      ></el-input>
      <div v-if="purchaseMethodError" class="error-message">{{ purchaseMethodError }}</div>
    </div>
    <div class="form-group">
      <label>入手形式</label>
      <el-select v-model="localFigure.purchase_type" placeholder="请选择入手形式" style="width: 100%;">
        <el-option value="OTHER" label="其他" />
        <el-option value="PREORDER" label="预定" />
        <el-option value="INSTOCK" label="现货" />
        <el-option value="SECONDHAND" label="二手" />
        <el-option value="LOOSE" label="散货" />
        <el-option value="DOMESTIC" label="国产" />
      </el-select>
    </div>
    <div class="form-group">
      <label>数量</label>
      <el-input-number v-model="localFigure.quantity" placeholder="请输入数量" :min="1" :step="1" style="width: 200px;"></el-input-number>
    </div>
    <div class="form-group">
      <label>市场价</label>
      <div class="price-currency-container">
        <el-input-number v-model="localFigure.market_price" :min="0" :step="1" style="width: 200px;"></el-input-number>
        <el-select v-model="localFigure.market_currency" style="width: 120px;">
          <el-option value="CNY" label="人民币" />
          <el-option value="JPY" label="日元" />
          <el-option value="USD" label="美元" />
          <el-option value="EUR" label="欧元" />
        </el-select>
      </div>
    </div>
  </div>
  
  <!-- 图片上传 -->
  <ImageUpload
    :images="localFigure.images"
    @view-image="$emit('view-image', $event)"
    @remove-image="$emit('remove-image', $event)"
    @file-upload="$emit('file-upload', $event)"
  />
</template>

<script>
import ImageUpload from './ImageUpload.vue'

export default {
  name: 'FormBasicTab',
  components: { ImageUpload },
  props: {
    figure: {
      type: Object,
      required: true
    },
    nameError: String,
    japaneseNameError: String,
    purchaseMethodError: String
  },
  emits: [
    'update:figure',
    'validate-name-input',
    'validate-japanese-name-input',
    'validate-purchase-method-input',
    'view-image',
    'remove-image',
    'file-upload'
  ],
  computed: {
    localFigure: {
      get() {
        return this.figure
      },
      set(value) {
        this.$emit('update:figure', value)
      }
    }
  }
}
</script>

<style scoped>
.form-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 15px;
  margin-bottom: 20px;
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

.price-currency-container {
  display: flex;
  gap: 10px;
}

.error-message {
  color: #f56c6c;
  font-size: 12px;
  margin-top: 4px;
}

@media (max-width: 768px) {
  .form-grid {
    grid-template-columns: 1fr;
  }
}
</style>
