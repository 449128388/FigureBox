<!--
  DetailHeader.vue - 收藏柜详情头部组件

  功能说明：
  - 展示收藏柜图标、标题、副标题
  - 展示藏品数量和陪伴天数统计
  - 支持返回按钮点击事件

  Props:
  - cabinet: Object - 收藏柜数据对象

  Events:
  - back: 点击返回按钮时触发
-->
<template>
  <div class="detail-header">
    <div class="detail-header-left">
      <div class="detail-icon" :style="{ background: cabinet.icon_bg }">
        {{ cabinet.icon }}
      </div>
      <div>
        <div class="detail-title">{{ cabinet.name }}</div>
        <div class="detail-sub">{{ subtitle }}</div>
      </div>
    </div>
    <div class="detail-stats">
      <div class="d-stat">
        <div class="d-stat-num">{{ cabinet.count }}</div>
        <div class="d-stat-label">藏品</div>
      </div>
      <div v-if="showCompanionDays" class="d-stat">
        <div class="d-stat-num">{{ formattedCompanionDays }}</div>
        <div class="d-stat-label">陪伴天数</div>
      </div>
    </div>
  </div>
</template>

<script>
import {
  CABINET_SUBTITLES,
  HIDE_COMPANION_DAYS_TYPES
} from '../constants/cabinetConfig'
import { formatCompanionDays } from '../utils/formatters'

export default {
  name: 'DetailHeader',

  props: {
    cabinet: {
      type: Object,
      required: true
    }
  },

  computed: {
    /**
     * 根据收藏柜类型获取副标题
     */
    subtitle() {
      return CABINET_SUBTITLES[this.cabinet.key] || '我的收藏柜详情'
    },

    /**
     * 是否显示陪伴天数
     */
    showCompanionDays() {
      return !HIDE_COMPANION_DAYS_TYPES.includes(this.cabinet.key)
    },

    /**
     * 格式化后的陪伴天数
     */
    formattedCompanionDays() {
      return formatCompanionDays(this.cabinet.companion_days)
    }
  }
}
</script>

<style scoped>
.detail-header {
  background: #fff;
  border-radius: 12px;
  padding: 20px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.04);
  margin-bottom: 20px;
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.detail-header-left {
  display: flex;
  align-items: center;
  gap: 16px;
}

.detail-icon {
  width: 48px;
  height: 48px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24px;
  flex-shrink: 0;
}

.detail-title {
  font-size: 18px;
  font-weight: 600;
  color: #1F1F1F;
}

.detail-sub {
  font-size: 13px;
  color: #999;
  margin-top: 2px;
}

.detail-stats {
  display: flex;
  gap: 16px;
}

.d-stat {
  text-align: center;
}

.d-stat-num {
  font-size: 20px;
  font-weight: 700;
  color: #1F1F1F;
}

.d-stat-label {
  font-size: 12px;
  color: #999;
}

@media (max-width: 768px) {
  .detail-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 16px;
  }
}
</style>
