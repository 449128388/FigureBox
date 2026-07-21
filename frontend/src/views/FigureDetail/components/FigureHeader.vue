<!--
  FigureHeader.vue - 手办详情页头组件

  功能说明：
  - 展示手办的中文名（主标题）和日文名·制造商·比例（副标题）
  - 提供「返回列表」链接

  组件依赖：
  - 接收 figure 作为 props
  - 业务逻辑：getPageSubtitle（从 composable 导入）
-->
<template>
  <div class="page-header">
    <div class="page-title-area">
      <a class="back-btn" @click="goBack">
        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <line x1="19" y1="12" x2="5" y2="12"></line>
          <polyline points="12 19 5 12 12 5"></polyline>
        </svg>
        返回列表
      </a>
      <div class="title-block">
        <h1 class="page-title">{{ figure.name || '未命名手办' }}</h1>
        <div v-if="subtitle" class="page-subtitle">{{ subtitle }}</div>
      </div>
    </div>
  </div>
</template>

<script>
import { useFigureDetail } from '../composables/useFigureDetail'

export default {
  name: 'FigureHeader',
  props: {
    figure: {
      type: Object,
      required: true
    }
  },
  computed: {
    subtitle() {
      const { getPageSubtitle } = useFigureDetail()
      return getPageSubtitle(this.figure)
    }
  },
  methods: {
    goBack() {
      this.$router.push('/figures')
    }
  }
}
</script>

<style scoped>
.page-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 24px;
}
.page-title-area {
  display: flex;
  align-items: center;
  gap: 16px;
}
.back-btn {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 8px 16px;
  border: 1px solid #d9d9d9;
  border-radius: 8px;
  background: #fff;
  color: #666;
  font-size: 14px;
  cursor: pointer;
  transition: all 0.2s;
  text-decoration: none;
}
.back-btn:hover { border-color: #40a9ff; color: #40a9ff; }
.title-block { display: flex; flex-direction: column; gap: 4px; }
.page-title {
  font-size: 22px;
  font-weight: 600;
  color: #1f1f1f;
  margin: 0;
}
.page-subtitle {
  font-size: 13px;
  color: #999;
}
</style>
