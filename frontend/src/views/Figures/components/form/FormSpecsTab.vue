<!--
  FormSpecsTab.vue - 手办表单规格信息标签页组件

  功能说明：
  - 提供手办规格相关信息的输入表单
  - 包含制造商、比例、材质、尺寸等字段
  - 支持表单验证和错误提示

  组件依赖：
  - 使用 Element Plus 的 el-input 组件

  维护提示：
  - 接收 figure 作为 props，双向绑定表单数据
  - 接收各种错误信息作为 props 显示错误提示
  - 输入事件通过 validate-* 事件向父组件传递，触发验证
-->
<template>
  <div class="form-grid">
    <div class="form-group">
      <label>制造商</label>
      <el-input 
        v-model="localFigure.manufacturer" 
        placeholder="请输入制造商"
        :class="{ 'error-input': manufacturerError }"
        @input="$emit('validate-manufacturer-input')"
      ></el-input>
      <div v-if="manufacturerError" class="error-message">{{ manufacturerError }}</div>
    </div>   
    <div class="form-group">
      <label>比例</label>
      <el-input 
        v-model="localFigure.scale" 
        placeholder="请输入比例"
        :class="{ 'error-input': scaleError }"
        @input="$emit('validate-scale-input')"
      ></el-input>
      <div v-if="scaleError" class="error-message">{{ scaleError }}</div>
    </div>
    <div class="form-group">
      <label>材质</label>
      <el-input 
        v-model="localFigure.material" 
        placeholder="请输入材质"
        :class="{ 'error-input': materialError }"
        @input="$emit('validate-material-input')"
      ></el-input>
      <div v-if="materialError" class="error-message">{{ materialError }}</div>
    </div>
    <div class="form-group">
      <label>尺寸</label>
      <el-input 
        v-model="localFigure.size" 
        placeholder="请输入尺寸"
        :class="{ 'error-input': sizeError }"
        @input="$emit('validate-size-input')"
      ></el-input>
      <div v-if="sizeError" class="error-message">{{ sizeError }}</div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'FormSpecsTab',
  props: {
    figure: {
      type: Object,
      required: true
    },
    manufacturerError: String,
    scaleError: String,
    materialError: String,
    sizeError: String
  },
  emits: [
    'update:figure',
    'validate-manufacturer-input',
    'validate-scale-input',
    'validate-material-input',
    'validate-size-input'
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
