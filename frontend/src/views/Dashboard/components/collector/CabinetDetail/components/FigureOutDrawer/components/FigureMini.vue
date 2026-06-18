<!--
  FigureMini.vue - 藏品信息展示子组件（Mini版）

  功能说明：
  - 展示藏品的缩略图、名称、元信息、收藏柜标签
  - 用于出柜登记抽屉等需要紧凑展示的场景

  Props:
  - figure: Object - 藏品数据
  - cabinetIcon: String - 默认图标（当藏品无图片时显示）
  - cabinetName: String - 收藏柜名称

  使用示例：
  <FigureMini
    :figure="figureData"
    cabinet-icon="🧸"
    cabinet-name="海景房专区"
  />
-->
<template>
  <div class="figure-mini">
    <!-- 藏品缩略图 -->
    <div class="figure-thumb">
      <img v-if="hasImage" :src="imageUrl" :alt="displayName" />
      <span v-else class="figure-emoji">{{ cabinetIcon }}</span>
    </div>

    <!-- 藏品信息 -->
    <div class="figure-info">
      <div class="figure-name">{{ displayName }}</div>
      <div class="figure-meta">{{ metaText }}</div>
      <div class="figure-cabinet-tag">{{ cabinetTag }}</div>
    </div>
  </div>
</template>

<script>
import { DEFAULT_FIGURE_NAME, DEFAULT_FIGURE_META } from '../constants'
import { formatFigureMeta, formatCabinetTag } from '../utils'

export default {
  name: 'FigureMini',

  props: {
    /**
     * 藏品数据对象
     */
    figure: {
      type: Object,
      default: () => ({})
    },

    /**
     * 默认图标（当藏品无图片时显示）
     */
    cabinetIcon: {
      type: String,
      default: '📦'
    },

    /**
     * 收藏柜名称
     */
    cabinetName: {
      type: String,
      default: ''
    }
  },

  computed: {
    /**
     * 藏品图片 URL
     */
    imageUrl() {
      return this.figure?.image || ''
    },

    /**
     * 是否有图片
     */
    hasImage() {
      return !!this.imageUrl
    },

    /**
     * 显示名称（带默认值）
     */
    displayName() {
      return this.figure?.name || DEFAULT_FIGURE_NAME
    },

    /**
     * 元信息文本
     */
    metaText() {
      return formatFigureMeta(this.figure)
    },

    /**
     * 收藏柜标签文本
     */
    cabinetTag() {
      return formatCabinetTag(this.cabinetName)
    }
  }
}
</script>

<style scoped>
.figure-mini {
  display: flex;
  gap: 16px;
  align-items: center;
  background: #FAFAFA;
  border-radius: 10px;
  padding: 16px;
  border: 1px solid var(--border-color, #EBE8E4);
  margin-bottom: 20px;
}

.figure-thumb {
  width: 64px;
  height: 64px;
  background: #F0EEEB;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 32px;
  flex-shrink: 0;
  overflow: hidden;
}

.figure-thumb img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.figure-emoji {
  color: #B0ABA5;
}

.figure-info {
  flex: 1;
}

.figure-name {
  font-size: 16px;
  font-weight: 600;
  margin-bottom: 4px;
  color: var(--text-primary, #1F1F1F);
}

.figure-meta {
  font-size: 13px;
  color: var(--text-secondary, #666666);
}

.figure-cabinet-tag {
  display: inline-block;
  padding: 2px 8px;
  border-radius: 10px;
  font-size: 11px;
  font-weight: 600;
  background: var(--accent-light, #FDF6EE);
  color: var(--accent-color, #C49A6C);
  margin-top: 6px;
}
</style>
