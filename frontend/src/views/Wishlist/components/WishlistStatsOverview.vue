<template>
  <div class="stats-overview">
    <div class="stat-card">
      <div class="stat-icon pink">
        <i class="ri-heart-3-line"></i>
      </div>
      <div class="stat-info">
        <h3>{{ stats.total }}</h3>
        <p>愿望总数</p>
        <div v-if="stats.last_month_total !== undefined" class="stat-change" :class="totalTrendClass">
          <i :class="totalTrendIcon"></i>
          <span>{{ totalTrendText }}</span>
          <span class="stat-change-tip">较上月</span>
        </div>
      </div>
    </div>

    <div class="stat-card">
      <div class="stat-icon orange">
        <i class="ri-calendar-check-line"></i>
      </div>
      <div class="stat-info">
        <h3>{{ stats.releasing_this_month }}</h3>
        <p>本月即将发售</p>
        <div v-if="stats.releasing_names && stats.releasing_names.length" class="stat-change text-up">
          <span>{{ stats.releasing_names.slice(0, 2).join('、') }}<span v-if="stats.releasing_names.length > 2">等</span></span>
        </div>
      </div>
    </div>

    <div class="stat-card">
      <div class="stat-icon blue">
        <i class="ri-money-cny-circle-line"></i>
      </div>
      <div class="stat-info">
        <h3>¥{{ formatCurrency(stats.budget_total) }}</h3>
        <p>预算合计</p>
        <div v-if="stats.transferred_amount" class="stat-change text-down">
          <span>-¥{{ formatCurrency(stats.transferred_amount) }}</span>
          <span class="stat-change-tip">已转采购</span>
        </div>
      </div>
    </div>

    <div class="stat-card">
      <div class="stat-icon green">
        <i class="ri-shopping-cart-2-line"></i>
      </div>
      <div class="stat-info">
        <h3>{{ stats.pending_purchase }}</h3>
        <p>待购数量</p>
        <div v-if="stats.released_purchase_count !== undefined" class="stat-change text-up">
          <span>{{ stats.released_purchase_count }}</span>
          <span class="stat-change-tip">已发售待购</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  stats: { type: Object, required: true }
})

const formatCurrency = (n) => {
  const num = Number(n) || 0
  return num.toLocaleString('zh-CN', { minimumFractionDigits: 0, maximumFractionDigits: 2 })
}

const totalTrendClass = computed(() => {
  const diff = (props.stats.last_month_total || 0)
  if (diff > 0) return 'text-up'
  if (diff < 0) return 'text-down'
  return ''
})

const totalTrendIcon = computed(() => {
  const diff = (props.stats.last_month_total || 0)
  if (diff > 0) return 'ri-arrow-up-line'
  if (diff < 0) return 'ri-arrow-down-line'
  return 'ri-subtract-line'
})

const totalTrendText = computed(() => {
  const diff = Math.abs(props.stats.last_month_total || 0)
  if (diff === 0) return '0'
  return (props.stats.last_month_total > 0 ? '+' : '-') + diff
})
</script>

<style scoped>
.stats-overview {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16px;
  margin-bottom: 20px;
}
.stat-card {
  background: #fff;
  padding: 20px;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.06);
  display: flex;
  align-items: center;
  gap: 16px;
  transition: all 0.3s;
}
.stat-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 24px rgba(0,0,0,0.12);
}
.stat-icon {
  width: 48px;
  height: 48px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24px;
  flex-shrink: 0;
}
.stat-icon.pink { background: #fff0f6; color: #eb2f96; }
.stat-icon.blue { background: #e6f4ff; color: #1890ff; }
.stat-icon.orange { background: #fff7e6; color: #fa8c16; }
.stat-icon.green { background: #f6ffed; color: #52c41a; }
.stat-info { flex: 1; min-width: 0; }
.stat-info h3 {
  font-size: 24px;
  font-weight: 600;
  color: #1a1a1a;
  margin-bottom: 4px;
  line-height: 1.2;
}
.stat-info p {
  color: #999;
  font-size: 13px;
  margin: 0 0 6px 0;
}
.stat-change {
  font-size: 12px;
  display: flex;
  align-items: center;
  gap: 4px;
  margin-top: 2px;
}
.stat-change.text-up { color: #f5222d; }
.stat-change.text-down { color: #52c41a; }
.stat-change-tip {
  color: #999;
  font-size: 11px;
  margin-left: 2px;
}
</style>
