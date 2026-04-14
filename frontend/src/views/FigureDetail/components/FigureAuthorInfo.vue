<!--
  FigureAuthorInfo.vue - 手办作者信息组件

  功能说明：
  - 展示手办的作者相关信息
  - 包括涂装、原画、作品等字段
  - 仅在有相关信息时显示

  组件依赖：
  - 接收 figure 作为 props，包含 painting、original_art、work 等字段

  维护提示：
  - 使用 v-if 条件渲染，仅当有相关信息时显示
  - 布局采用 info-section 样式
-->
<template>
  <div class="info-section" v-if="figure.painting || figure.original_art || figure.work">
    <h2>作者信息</h2>
    <div class="info-item" v-if="figure.painting">
      <span class="label">涂装:</span>
      <span class="value">{{ figure.painting }}</span>
    </div>
    <div class="info-item" v-if="figure.original_art">
      <span class="label">原画:</span>
      <span class="value">{{ figure.original_art }}</span>
    </div>
    <div class="info-item" v-if="figure.work">
      <span class="label">作品:</span>
      <span class="value">{{ figure.work }}</span>
    </div>
  </div>
</template>

<script>
export default {
  name: 'FigureAuthorInfo',
  props: {
    figure: {
      type: Object,
      required: true
    }
  }
}
</script>

<style scoped>
.info-section {
  background-color: white;
  padding: 20px;
  border-radius: 8px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
}

.info-section h2 {
  margin-top: 0;
  margin-bottom: 20px;
  color: #333;
  font-size: 20px;
  font-weight: 600;
  border-bottom: 1px solid #e0e0e0;
  padding-bottom: 10px;
}

.info-item {
  display: flex;
  margin-bottom: 12px;
}

.label {
  flex: 0 0 100px;
  font-weight: 500;
  color: #666;
}

.value {
  flex: 1;
  color: #333;
  padding: 2px 0;
  min-height: 20px;
  line-height: 1.5;
}
</style>