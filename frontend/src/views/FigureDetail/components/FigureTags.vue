<!--
  FigureTags.vue - 手办标签卡片

  功能说明：
  - 卡片式布局：图标标题栏
  - 标签以统一蓝色 pill 形式展示（背景 #e6f7ff / 文字 #1890ff）

  组件依赖：
  - 接收 figure 作为 props（tags: [{id, name, type?}, ...]）
-->
<template>
  <div class="info-card" v-if="figure.tags && figure.tags.length > 0">
    <div class="card-header-bar">
      <div class="card-title">
        <svg class="card-title-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <path d="M20.59 13.41l-7.17 7.17a2 2 0 0 1-2.83 0L2 12V2h10l8.59 8.59a2 2 0 0 1 0 2.82z"></path>
          <line x1="7" y1="7" x2="7.01" y2="7"></line>
        </svg>
        标签
      </div>
    </div>
    <div class="card-body">
      <div class="tag-list">
        <span
          v-for="tag in figure.tags"
          :key="tag.id"
          class="tag"
        >{{ tag.name }}</span>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'FigureTags',
  props: {
    figure: {
      type: Object,
      required: true
    }
  }
}
</script>

<style scoped>
.info-card {
  background: #fff;
  border-radius: 12px;
  border: 1px solid #e8e8e8;
  overflow: hidden;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.04);
}
.card-header-bar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 16px 24px;
  border-bottom: 1px solid #f0f0f0;
}
.card-title {
  font-size: 15px;
  font-weight: 600;
  color: #1f1f1f;
  display: flex;
  align-items: center;
  gap: 10px;
}
.card-title-icon {
  width: 22px;
  height: 22px;
  color: #1890ff;
}
.card-body { padding: 20px 24px; }
.tag-list {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}
.tag {
  padding: 5px 14px;
  border-radius: 6px;
  font-size: 13px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
  background: #e6f7ff;
  color: #1890ff;
}
.tag:hover { opacity: 0.8; }
</style>
