<!--
  FormAuthorTab.vue - 手办表单作者信息标签页组件

  功能说明：
  - 提供手办作者相关信息的输入表单
  - 包含涂装、原画、作品等字段
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
      <label>涂装</label>
      <el-input 
        v-model="localFigure.painting" 
        placeholder="请输入涂装"
        :class="{ 'error-input': paintingError }"
        @input="$emit('validate-painting-input')"
      ></el-input>
      <div v-if="paintingError" class="error-message">{{ paintingError }}</div>
    </div>
    <div class="form-group">
      <label>原画</label>
      <el-input 
        v-model="localFigure.original_art" 
        placeholder="请输入原画"
        :class="{ 'error-input': originalArtError }"
        @input="$emit('validate-original-art-input')"
      ></el-input>
      <div v-if="originalArtError" class="error-message">{{ originalArtError }}</div>
    </div>
    <div class="form-group">
      <label>作品</label>
      <el-input 
        v-model="localFigure.work" 
        placeholder="请输入作品"
        :class="{ 'error-input': workError }"
        @input="$emit('validate-work-input')"
      ></el-input>
      <div v-if="workError" class="error-message">{{ workError }}</div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'FormAuthorTab',
  props: {
    figure: {
      type: Object,
      required: true
    },
    paintingError: String,
    originalArtError: String,
    workError: String
  },
  emits: [
    'update:figure',
    'validate-painting-input',
    'validate-original-art-input',
    'validate-work-input'
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
