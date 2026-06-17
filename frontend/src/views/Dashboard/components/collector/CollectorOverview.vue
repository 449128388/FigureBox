<!--
  CollectorOverview.vue - 收藏家模式概览组件

  功能说明：
  - 展示收藏家的核心数据概览
  - 包括藏品总数、本月新入柜、已出藏品三个关键指标
  - 参考 collector_mode.html 的 summary-card 样式设计

  组件依赖：
  - 接收 collectorData 作为 props，包含 summary 数据

  维护提示：
  - 数据为空时显示默认值
-->
<template>
  <div class="summary-grid">
    <!-- 左卡片：藏品总数 -->
    <div class="summary-card">
      <div class="summary-icon icon-total">🧸</div>
      <div class="summary-label">藏品总数</div>
      <div class="summary-value-wrap">
        <span class="summary-value">{{ collectorData?.summary?.total_collection || 0 }}</span>
        <span class="summary-unit">体</span>
      </div>
      <div class="summary-meta">
        覆盖 {{ collectorData?.summary?.unique_works || 0 }} 个作品 / {{ collectorData?.summary?.unique_manufacturers || 0 }} 个厂商
      </div>
    </div>

    <!-- 中卡片：本月新入柜 -->
    <div class="summary-card">
      <div class="summary-icon icon-new">🆕</div>
      <div class="summary-label">本月新入柜</div>
      <div class="summary-value-wrap">
        <span class="summary-value">+{{ collectorData?.summary?.this_month_count || 0 }}</span>
        <span class="summary-unit">体</span>
      </div>
      <div class="summary-meta">{{ collectorData?.summary?.recent_figures || '暂无新入库' }}</div>
    </div>

    <!-- 右卡片：已出藏品 -->
    <div class="summary-card">
      <div class="summary-icon icon-sold">📤</div>
      <div class="summary-label">已出藏品</div>
      <div class="summary-value-wrap">
        <span class="summary-value">{{ collectorData?.summary?.total_sold_count || 0 }}</span>
        <span class="summary-unit">体</span>
      </div>
      <div class="summary-meta">陪伴时长 {{ formatCompanionDays(collectorData?.summary?.total_companion_days) }}</div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'CollectorOverview',
  props: {
    collectorData: {
      type: Object,
      default: () => ({})
    }
  },
  methods: {
    formatCompanionDays(days) {
      if (!days || days <= 0) return '0 天'
      return `${days.toLocaleString()} 天`
    }
  }
}
</script>

<style scoped>
.summary-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 16px;
  margin-bottom: 24px;
}

.summary-card {
  background: var(--card-bg, #FFFFFF);
  border-radius: var(--radius, 12px);
  padding: 24px 20px;
  box-shadow: var(--shadow, 0 2px 8px rgba(0,0,0,0.04));
  text-align: center;
  transition: transform 0.2s, box-shadow 0.2s;
}

.summary-card:hover {
  transform: translateY(-2px);
  box-shadow: var(--shadow-hover, 0 4px 16px rgba(0,0,0,0.08));
}

.summary-icon {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  margin: 0 auto 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 20px;
}

.icon-total {
  background: #E8F4F8;
}

.icon-new {
  background: #FDF6EE;
}

.icon-sold {
  background: #F0F5E8;
}

.summary-label {
  font-size: 13px;
  color: var(--text-secondary, #666666);
  margin-bottom: 6px;
}

.summary-value-wrap {
  display: flex;
  align-items: baseline;
  justify-content: center;
  gap: 2px;
}

.summary-value {
  font-size: 24px;
  font-weight: 700;
  color: var(--text-primary, #1F1F1F);
}

.summary-unit {
  font-size: 14px;
  font-weight: 500;
  color: var(--text-secondary, #666666);
  margin-left: 2px;
}

.summary-meta {
  font-size: 12px;
  color: var(--text-tertiary, #999999);
  margin-top: 6px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

@media (max-width: 768px) {
  .summary-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 480px) {
  .summary-grid {
    grid-template-columns: 1fr;
  }
}
</style>
