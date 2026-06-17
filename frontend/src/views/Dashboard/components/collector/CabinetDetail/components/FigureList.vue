<!--
  FigureList.vue - 藏品列表视图组件

  功能说明：
  - 以列表形式展示藏品
  - 每行包含缩略图、名称、信息、状态标签、评分、操作按钮
  - 信息密度更高，适合快速浏览

  Props:
  - items: Array - 藏品列表
  - cabinetKey: String - 收藏柜类型key
  - cabinetIcon: String - 收藏柜图标
  - starRatings: Object - 评分数据 { figureId: rating }

  Events:
  - 暂无
-->
<template>
  <div class="figure-list">
    <div
      v-for="(item, index) in items"
      :key="item.id || index"
      class="list-item"
    >
      <div class="list-thumb">
        <div v-if="item.image" class="list-thumb-img">
          <img :src="item.image" :alt="item.name" />
        </div>
        <div v-else class="list-thumb-placeholder">{{ cabinetIcon }}</div>
      </div>
      <div class="list-body">
        <div class="list-title">{{ item.name || '未知手办' }}</div>
        <div class="list-meta">{{ formatFigureInfo(item) }} · {{ formatDateInfo(item) }}</div>
        <div class="list-tags">
          <span class="list-status-tag" :class="statusClass">{{ statusText }}</span>
          <!-- 列表模式喜爱度评分（只读） -->
          <span class="list-star-tag">
            <span
              v-for="s in 5"
              :key="s"
              class="star-mini"
              :class="{ filled: s <= (starRatings[item.id] || 0) }"
            >★</span>
          </span>
        </div>
      </div>
      <div class="list-actions">
        <button class="btn-tiny">查看详情</button>
      </div>
    </div>
  </div>
</template>

<script>
import { STATUS_CLASSES, STATUS_TEXTS } from '../constants/cabinetConfig'
import { formatFigureInfo, formatDateInfo } from '../utils/formatters'

export default {
  name: 'FigureList',

  props: {
    items: {
      type: Array,
      required: true
    },
    cabinetKey: {
      type: String,
      required: true
    },
    cabinetIcon: {
      type: String,
      default: '📦'
    },
    starRatings: {
      type: Object,
      default: () => ({})
    }
  },

  computed: {
    /**
     * 状态样式类
     */
    statusClass() {
      return STATUS_CLASSES[this.cabinetKey] || 'st-in'
    },

    /**
     * 状态文本
     */
    statusText() {
      return STATUS_TEXTS[this.cabinetKey] || '在柜'
    }
  },

  methods: {
    formatFigureInfo,
    formatDateInfo
  }
}
</script>

<style scoped>
.figure-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.list-item {
  background: #fff;
  border-radius: 12px;
  padding: 14px 16px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
  display: flex;
  align-items: center;
  gap: 14px;
  transition: transform 0.2s, box-shadow 0.2s;
}

.list-item:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.08);
}

.list-thumb {
  width: 56px;
  height: 56px;
  background: #F0EEEB;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  overflow: hidden;
}

.list-thumb-img {
  width: 100%;
  height: 100%;
}

.list-thumb-img img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.list-thumb-placeholder {
  font-size: 24px;
  color: #B0ABA5;
}

.list-body {
  flex: 1;
  min-width: 0;
}

.list-title {
  font-size: 15px;
  font-weight: 600;
  color: #1F1F1F;
  margin-bottom: 4px;
}

.list-meta {
  font-size: 12px;
  color: #666;
  margin-bottom: 6px;
}

.list-tags {
  display: flex;
  align-items: center;
  gap: 8px;
}

.list-status-tag {
  display: inline-block;
  padding: 2px 8px;
  border-radius: 10px;
  font-size: 11px;
  font-weight: 600;
  color: #fff;
}

.st-in {
  background: #7EB8A2;
}

.st-air {
  background: #9B7ED8;
}

.st-fix {
  background: #E6A23C;
}

.st-out {
  background: #999;
}

.list-star-tag {
  font-size: 11px;
  color: #E6A23C;
  letter-spacing: 1px;
}

.star-mini {
  color: #ddd;
}

.star-mini.filled {
  color: #E6A23C;
}

.list-actions {
  flex-shrink: 0;
}

.btn-tiny {
  padding: 6px 12px;
  text-align: center;
  border: 1px solid #EBE8E4;
  background: #fff;
  border-radius: 6px;
  font-size: 12px;
  color: #666;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-tiny:hover {
  border-color: #C49A6C;
  color: #C49A6C;
}
</style>
