<!--
  FigureHero.vue - 藏品Hero区子组件

  Props:
  - figure: Object - 藏品数据
  - cabinetIcon: String - 收藏柜图标
  - statusText: String - 状态文本
  - isStarFigure: Boolean - 是否为镇柜之宝

  依赖：
  - formatFigureInfo 工具函数
-->
<template>
  <div class="figure-hero">
    <div class="figure-img-large">
      <img v-if="figure.image" :src="figure.image" :alt="figure.name" />
      <span v-else class="figure-emoji">{{ cabinetIcon }}</span>
    </div>
    <div class="figure-hero-info">
      <div class="figure-hero-name">{{ figure.name || '未知手办' }}</div>
      <div class="figure-hero-meta">{{ formatFigureInfo(figure) }}</div>
      <div class="figure-hero-meta">
        入库时间: {{ figure.transaction_date || '未知' }} · 陪伴 <strong>{{ figure.holding_days || 0 }} 天</strong>
      </div>
      <div class="figure-hero-tags">
        <span class="tag-pill tag-in">{{ statusText }}</span>
        <span v-if="isStarFigure" class="tag-pill tag-star">镇柜之宝</span>
      </div>
    </div>
  </div>
</template>

<script>
import { formatFigureInfo } from '../../../utils/formatters'

export default {
  name: 'FigureHero',

  props: {
    figure: {
      type: Object,
      required: true
    },
    cabinetIcon: {
      type: String,
      default: '📦'
    },
    statusText: {
      type: String,
      default: '在柜'
    },
    isStarFigure: {
      type: Boolean,
      default: false
    }
  },

  methods: {
    formatFigureInfo
  }
}
</script>

<style scoped>
.figure-hero {
  display: flex;
  gap: 20px;
  margin-bottom: 24px;
}

.figure-img-large {
  width: 160px;
  height: 160px;
  background: #F0EEEB;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  border: 1px solid #EBE8E4;
  overflow: hidden;
}

.figure-img-large img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.figure-emoji {
  font-size: 64px;
  color: #B0ABA5;
}

.figure-hero-info {
  flex: 1;
  display: flex;
  flex-direction: column;
  justify-content: center;
}

.figure-hero-name {
  font-size: 20px;
  font-weight: 600;
  margin-bottom: 6px;
  color: #1F1F1F;
}

.figure-hero-meta {
  font-size: 13px;
  color: #666;
  margin-bottom: 4px;
}

.figure-hero-tags {
  display: flex;
  gap: 8px;
  margin-top: 10px;
}

.tag-pill {
  padding: 3px 10px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 500;
}

.tag-in {
  background: #E8F4F8;
  color: #7EB8A2;
}

.tag-star {
  background: #FDF6EE;
  color: #C49A6C;
}
</style>
