<!--
  ActivityFeed.vue - 收藏家模式动态流组件

  功能说明：
  - 展示用户与藏品/订单的所有交互事件
  - 按日期分组渲染时间轴
  - 支持事件类型筛选
  - 支持点击查看事件详情
  - 支持分页加载更多

  组件依赖：
  - 使用 useActivityFeed composable 管理业务逻辑
  - 使用 activityApi.js 进行 API 调用

  Events:
  - activity-action: 操作按钮点击事件
-->

<template>
  <div class="feed-card">
    <div class="feed-header">
      <el-icon><ChatDotRound /></el-icon> 动态流
    </div>

    <!-- 筛选器 -->
    <div class="filter-bar">
      <button
        v-for="opt in filterOptions"
        :key="opt.value"
        class="filter-btn"
        :class="{ active: currentFilter === opt.value }"
        @click="switchFilter(opt.value)"
      >
        <span class="filter-dot" :style="{ background: opt.color }"></span>
        {{ opt.label }}
      </button>
    </div>

    <!-- 加载中 -->
    <div v-if="loading && activityGroups.length === 0" class="loading-state">
      <div class="loading-spinner"></div>
      <div class="loading-text">加载中...</div>
    </div>

    <!-- 动态流内容 -->
    <div v-else-if="activityGroups.length > 0" class="feed-content">
      <div v-for="group in activityGroups" :key="group.date" class="feed-group">
        <div class="feed-date">
          <span class="date-icon">🗓️</span>
          <span>{{ group.date }}</span>
          <span v-if="group.label" class="date-label">· {{ group.label }}</span>
        </div>
        <div class="feed-timeline">
          <div v-for="item in group.items" :key="item.id" class="feed-item">
            <div class="feed-dot" :class="getEventDotClass(item.event_type)"></div>
            <div class="feed-content">
              <div class="feed-title" v-html="item.event_title"></div>
              <div class="feed-meta">
                <button class="feed-detail-btn" @click="showDetail(item.id)">查看详情</button>
                <span class="feed-time">{{ formatTime(item.created_at) }}</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 空状态 -->
    <div v-else class="empty-state">
      <div class="empty-state-icon">🎉</div>
      <div class="empty-state-title">开始你的收藏之旅吧！</div>
      <div class="empty-state-desc">去添加第一体手办</div>
    </div>

    <!-- 加载更多 / 没有更多 -->
    <div class="load-more">
      <button v-if="hasMore" class="load-more-btn" @click="loadMore" :disabled="loading">
        {{ loading ? '加载中...' : '加载更多' }}
      </button>
      <span v-else-if="activityGroups.length > 0" class="load-more-text">没有更多动态了</span>
    </div>
  </div>
</template>

<script>
import { ChatDotRound } from '@element-plus/icons-vue'
import { useActivityFeed } from './ActivityFeed/composables/useActivityFeed.js'

export default {
  name: 'ActivityFeed',

  components: { ChatDotRound },

  props: {
    collectorData: {
      type: Object,
      default: () => ({})
    }
  },

  emits: ['activity-action'],

  setup(props, { emit }) {
    const feed = useActivityFeed()

    const filterOptions = [
      { value: 'all', label: '全部动态', color: '#C49A6C' },
      { value: 'buy', label: '买入', color: '#4A90E2' },
      { value: 'sell', label: '卖出', color: '#D66A6A' },
      { value: 'order', label: '订单', color: '#00BCD4' },
      { value: 'tag', label: '标签', color: '#9B7ED8' },
      { value: 'price', label: '价格', color: '#7EB8A2' }
    ]

    // 加载初始数据
    feed.loadActivities('all')

    return {
      ...feed,
      filterOptions
    }
  }
}
</script>

<style scoped>
.feed-card {
  margin-bottom: 30px;
  background: #fff;
  border-radius: 12px;
  padding: 20px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
}

.feed-header {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 18px;
  font-weight: 600;
  color: #333;
  margin-bottom: 16px;
}

/* ===== Filter Bar ===== */
.filter-bar {
  display: flex;
  gap: 8px;
  margin-bottom: 20px;
  flex-wrap: wrap;
}

.filter-btn {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  padding: 5px 12px;
  border: 1px solid #EBE8E4;
  background: #fff;
  border-radius: 6px;
  font-size: 13px;
  color: #666;
  cursor: pointer;
  transition: all 0.2s;
}

.filter-btn:hover {
  border-color: #E8D5C0;
  color: #C49A6C;
  background: #FDF6EE;
}

.filter-btn.active {
  background: #FDF6EE;
  border-color: #C49A6C;
  color: #C49A6C;
  font-weight: 500;
}

.filter-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
}

/* ===== Date Group ===== */
.feed-group {
  margin-bottom: 20px;
}

.feed-group:last-child {
  margin-bottom: 0;
}

.feed-date {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 13px;
  color: #999;
  margin-bottom: 12px;
  padding-left: 4px;
}

.date-icon {
  font-size: 14px;
}

.date-label {
  color: #666;
  font-weight: 500;
}

/* ===== Timeline ===== */
.feed-timeline {
  position: relative;
  padding-left: 28px;
}

.feed-timeline::before {
  content: "";
  position: absolute;
  left: 8px;
  top: 4px;
  bottom: 0;
  width: 2px;
  background: linear-gradient(180deg, #E8D5C0 0%, transparent 100%);
  border-radius: 1px;
}

/* ===== Feed Item ===== */
.feed-item {
  position: relative;
  padding-bottom: 16px;
}

.feed-item:last-child {
  padding-bottom: 0;
}

.feed-dot {
  position: absolute;
  left: -24px;
  top: 4px;
  width: 12px;
  height: 12px;
  border-radius: 50%;
  border: 2px solid #fff;
  box-shadow: 0 0 0 2px #E8D5C0;
  z-index: 1;
}

.feed-dot.buy { background: #4A90E2; box-shadow: 0 0 0 2px #BBDEFB; }
.feed-dot.full_pay { background: #7EB8A2; box-shadow: 0 0 0 2px #C8E6D5; }
.feed-dot.in_stock { background: #C49A6C; box-shadow: 0 0 0 2px #E8D5C0; }
.feed-dot.sell { background: #D66A6A; box-shadow: 0 0 0 2px #FFCDD2; }
.feed-dot.out { background: #999; box-shadow: 0 0 0 2px #E0E0E0; }
.feed-dot.tag_add { background: #9B7ED8; box-shadow: 0 0 0 2px #E1BEE7; }
.feed-dot.fix { background: #E6A23C; box-shadow: 0 0 0 2px #FFE082; }
.feed-dot.order_create { background: #00BCD4; box-shadow: 0 0 0 2px #B2EBF2; }
.feed-dot.order_cancel { background: #BDBDBD; box-shadow: 0 0 0 2px #E0E0E0; }
.feed-dot.price_update { background: #7EB8A2; box-shadow: 0 0 0 2px #C8E6D5; }

.feed-content {
  background: #FAFAFA;
  border-radius: 10px;
  padding: 12px 14px;
  border: 1px solid #EBE8E4;
  transition: all 0.2s;
}

.feed-content:hover {
  border-color: #E8D5C0;
  background: #FDFBF9;
}

.feed-title {
  font-size: 14px;
  color: #333;
  line-height: 1.6;
}

.feed-title :deep(.highlight) {
  color: #C49A6C;
  font-weight: 600;
}

.feed-title :deep(.price) {
  color: #7EB8A2;
  font-weight: 600;
}

.feed-title :deep(.profit) {
  color: #7EB8A2;
  font-weight: 600;
}

.feed-title :deep(.loss) {
  color: #D66A6A;
  font-weight: 600;
}

.feed-title :deep(.tag-badge) {
  display: inline-block;
  font-size: 11px;
  padding: 1px 6px;
  border-radius: 6px;
  margin-left: 4px;
  vertical-align: middle;
}

.feed-meta {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-top: 8px;
}

.feed-detail-btn {
  padding: 4px 12px;
  border: 1px solid #EBE8E4;
  background: #fff;
  border-radius: 6px;
  font-size: 12px;
  color: #666;
  cursor: pointer;
  transition: all 0.2s;
}

.feed-detail-btn:hover {
  border-color: #C49A6C;
  color: #C49A6C;
  background: #FDF6EE;
}

.feed-time {
  font-size: 12px;
  color: #999;
}

/* ===== Load More ===== */
.load-more {
  text-align: center;
  padding: 20px 0 0;
}

.load-more-btn {
  padding: 8px 24px;
  border: 1px solid #EBE8E4;
  background: #fff;
  border-radius: 20px;
  font-size: 13px;
  color: #666;
  cursor: pointer;
  transition: all 0.2s;
}

.load-more-btn:hover {
  border-color: #C49A6C;
  color: #C49A6C;
}

.load-more-btn:disabled {
  cursor: default;
  opacity: 0.6;
}

.load-more-text {
  font-size: 13px;
  color: #999;
}

/* ===== Empty State ===== */
.empty-state {
  text-align: center;
  padding: 40px 20px;
  color: #999;
}

.empty-state-icon {
  font-size: 48px;
  margin-bottom: 12px;
  opacity: 0.6;
}

.empty-state-title {
  font-size: 16px;
  font-weight: 600;
  color: #333;
  margin-bottom: 6px;
}

.empty-state-desc {
  font-size: 14px;
}

/* ===== Loading State ===== */
.loading-state {
  text-align: center;
  padding: 40px 20px;
}

.loading-spinner {
  display: inline-block;
  width: 24px;
  height: 24px;
  border: 3px solid #EBE8E4;
  border-top-color: #C49A6C;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
  margin-bottom: 8px;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.loading-text {
  font-size: 14px;
  color: #999;
}
</style>
