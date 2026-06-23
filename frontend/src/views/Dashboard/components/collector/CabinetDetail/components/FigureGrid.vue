<!--
  FigureGrid.vue - 藏品网格视图组件

  功能说明：
  - 以网格卡片形式展示藏品列表
  - 每个卡片包含图片、状态标签、评分、名称、信息、操作按钮
  - 支持交互式评分编辑

  Props:
  - items: Array - 藏品列表
  - cabinetKey: String - 收藏柜类型key
  - cabinetIcon: String - 收藏柜图标
  - starRatings: Object - 评分数据 { figureId: rating }
  - starEditingIndex: Number - 当前编辑评分的卡片索引

  Events:
  - toggle-star: 点击评分区域时触发，参数 { index }
  - set-rating: 设置评分时触发，参数 { figureId, index, rating }
-->
<template>
  <div class="figure-grid">
    <div
      v-for="(item, index) in items"
      :key="item.id || index"
      class="figure-card"
    >
      <div class="figure-img-wrap">
        <div v-if="item.image" class="figure-img-real">
          <img :src="item.image" :alt="item.name" />
        </div>
        <div v-else class="figure-img-placeholder">{{ cabinetIcon }}</div>
        <span class="figure-status" :class="statusClass">{{ statusText }}</span>
        <!-- 星级评分组件 -->
        <StarRating
          class="figure-stars-wrapper"
          :rating="starRatings[item.id] || 0"
          :is-editing="starEditingIndex === index"
          @click="handleToggleStar(index)"
          @set-rating="handleStarSetRating($event, item.id, index)"
        />
      </div>
      <div class="figure-info">
        <div class="figure-name">{{ item.name || '未知手办' }}</div>
        <div class="figure-line">{{ formatFigureInfo(item) }}</div>
        <div class="figure-line-gray">{{ formatDateInfo(item) }}</div>
        <div class="figure-actions">
          <button class="btn-tiny" @click="handleViewDetail(item)">查看详情</button>
          <button v-if="cabinetKey !== 'out'" class="btn-tiny btn-tiny-primary" @click="handleSell(item)">出柜登记</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import StarRating from './StarRating.vue'
import { STATUS_CLASSES, STATUS_TEXTS } from '../constants/cabinetConfig'
import { formatFigureInfo, formatDateInfo } from '../utils/formatters'

export default {
  name: 'FigureGrid',

  components: {
    StarRating
  },

  emits: ['toggle-star', 'set-rating', 'view-detail', 'sell'],

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
    },
    starEditingIndex: {
      type: Number,
      default: null
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
    formatDateInfo,

    /**
     * 处理切换评分编辑
     * @param {number} index - 卡片索引
     */
    handleToggleStar(index) {
      this.$emit('toggle-star', { index })
    },

    /**
     * 设置评分事件包装器（接收 StarRating 的自定义事件负载）
     * 避免在模板中直接使用 $event.rating 的不确定性
     * @param {Object} payload - StarRating 发出的事件负载 { rating }
     */
    handleStarSetRating(payload, figureId, index) {
      const rating = payload?.rating || payload || 0
      this.$emit('set-rating', { figureId, index, rating })
    },

    /**
     * 处理查看详情
     * @param {Object} item - 藏品数据
     */
    handleViewDetail(item) {
      this.$emit('view-detail', { item })
    },

    /**
     * 处理出柜登记
     * @param {Object} item - 藏品数据
     */
    handleSell(item) {
      this.$emit('sell', { item })
    }
  }
}
</script>

<style scoped>
.figure-grid {
  display: grid;
  grid-template-columns: repeat(5, 1fr);
  gap: 14px;
}

.figure-card {
  background: #fff;
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
  transition: transform 0.2s, box-shadow 0.2s;
}

.figure-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.08);
}

.figure-img-wrap {
  height: 180px;
  background: #F0EEEB;
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
}

.figure-img-placeholder {
  width: 100px;
  height: 100px;
  background: #E0DCD7;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 40px;
  color: #B0ABA5;
}

.figure-img-real {
  width: 100%;
  height: 100%;
}

.figure-img-real img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.figure-status {
  position: absolute;
  top: 10px;
  left: 10px;
  padding: 3px 8px;
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

.figure-stars-wrapper {
  position: absolute;
  bottom: 10px;
  right: 10px;
}

.figure-info {
  padding: 14px;
}

.figure-name {
  font-size: 15px;
  font-weight: 600;
  margin-bottom: 4px;
  color: #1F1F1F;
}

.figure-line {
  font-size: 12px;
  color: #666;
  margin-bottom: 2px;
}

.figure-line-gray {
  font-size: 12px;
  color: #999;
  margin-bottom: 2px;
}

.figure-actions {
  display: flex;
  gap: 8px;
  margin-top: 10px;
}

.btn-tiny {
  flex: 1;
  padding: 6px 0;
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

.btn-tiny-primary {
  background: #FDF6EE;
  border-color: #C49A6C;
  color: #C49A6C;
  font-weight: 500;
}

@media (max-width: 768px) {
  .figure-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}
</style>
