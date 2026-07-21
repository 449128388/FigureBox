<!--
  FigureAuthorInfo.vue - 手办作者信息卡片

  功能说明：
  - 卡片式布局：图标标题栏
  - 作者横向 author-row：每位作者含圆形头像（首字） + 角色（涂装/原画/作品） + 姓名

  组件依赖：
  - 接收 figure 作为 props
  - 业务逻辑 getAuthorInitial 从 useFigureDetail 导入
-->
<template>
  <div class="info-card" v-if="hasContent">
    <div class="card-header-bar">
      <div class="card-title">
        <svg class="card-title-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"></path>
          <circle cx="12" cy="7" r="4"></circle>
        </svg>
        作者信息
      </div>
    </div>
    <div class="card-body">
      <div class="author-row">
        <div class="author-item" v-if="figure.painting">
          <div class="author-avatar" :style="{ background: avatarColor(figure.painting) }">
            {{ getInitial(figure.painting) }}
          </div>
          <div class="author-text">
            <span class="author-role">涂装</span>
            <span class="author-name">{{ figure.painting }}</span>
          </div>
        </div>
        <div class="author-item" v-if="figure.original_art">
          <div class="author-avatar" :style="{ background: avatarColor(figure.original_art) }">
            {{ getInitial(figure.original_art) }}
          </div>
          <div class="author-text">
            <span class="author-role">原画</span>
            <span class="author-name">{{ figure.original_art }}</span>
          </div>
        </div>
        <div class="author-item" v-if="figure.work">
          <div class="author-avatar" :style="{ background: avatarColor(figure.work) }">
            {{ getInitial(figure.work) }}
          </div>
          <div class="author-text">
            <span class="author-role">作品</span>
            <span class="author-name">{{ figure.work }}</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { useFigureDetail } from '../composables/useFigureDetail'

// 简易字符串哈希 → 色相
const hashHue = (str) => {
  let h = 0
  for (let i = 0; i < str.length; i++) {
    h = (h * 31 + str.charCodeAt(i)) % 360
  }
  return h
}

export default {
  name: 'FigureAuthorInfo',
  props: {
    figure: {
      type: Object,
      required: true
    }
  },
  computed: {
    hasContent() {
      const f = this.figure
      return !!(f.painting || f.original_art || f.work)
    }
  },
  methods: {
    getInitial(name) {
      return useFigureDetail().getAuthorInitial(name)
    },
    avatarColor(name) {
      const hue = hashHue(name || '?')
      return `hsl(${hue}, 65%, 90%)`
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
.author-row {
  display: flex;
  gap: 24px;
  flex-wrap: wrap;
}
.author-item {
  display: flex;
  align-items: center;
  gap: 12px;
  flex: 1;
  min-width: 140px;
}
.author-avatar {
  width: 44px;
  height: 44px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 16px;
  font-weight: 600;
  color: #333;
  flex-shrink: 0;
}
.author-text { display: flex; flex-direction: column; gap: 2px; }
.author-role { font-size: 12px; color: #999; }
.author-name { font-size: 14px; color: #333; font-weight: 500; }
</style>
