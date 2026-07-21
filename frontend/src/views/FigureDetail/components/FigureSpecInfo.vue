<!--
  FigureSpecInfo.vue - 手办规格信息卡片

  功能说明：
  - 卡片式布局：图标标题栏
  - 横向 spec-row：每个规格项含 emoji 图标 + 标签 + 数值

  组件依赖：
  - 接收 figure 作为 props
-->
<template>
  <div class="info-card" v-if="hasContent">
    <div class="card-header-bar">
      <div class="card-title">
        <svg class="card-title-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <path d="M21 16V8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16z"></path>
        </svg>
        规格信息
      </div>
    </div>
    <div class="card-body">
      <div class="spec-row">
        <div class="spec-item" v-if="figure.scale">
          <div class="spec-icon">📐</div>
          <div class="spec-text">
            <span class="spec-label">比例</span>
            <span class="spec-value">{{ figure.scale }}</span>
          </div>
        </div>
        <div class="spec-item" v-if="figure.material">
          <div class="spec-icon">🧱</div>
          <div class="spec-text">
            <span class="spec-label">材质</span>
            <span class="spec-value">{{ figure.material }}</span>
          </div>
        </div>
        <div class="spec-item" v-if="figure.size">
          <div class="spec-icon">📏</div>
          <div class="spec-text">
            <span class="spec-label">尺寸</span>
            <span class="spec-value">{{ figure.size }}</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'FigureSpecInfo',
  props: {
    figure: {
      type: Object,
      required: true
    }
  },
  computed: {
    hasContent() {
      const f = this.figure
      return !!(f.scale || f.material || f.size)
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
.spec-row {
  display: flex;
  gap: 24px;
}
.spec-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 16px;
  background: #fafafa;
  border-radius: 8px;
  flex: 1;
}
.spec-icon { font-size: 24px; }
.spec-text { display: flex; flex-direction: column; gap: 2px; }
.spec-label { font-size: 12px; color: #999; }
.spec-value { font-size: 14px; color: #333; font-weight: 500; }
</style>
