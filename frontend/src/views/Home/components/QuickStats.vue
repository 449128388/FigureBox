<template>
  <div class="quick-stats">
    <div class="q-stat-card" @click="$router.push('/orders')">
      <div class="q-stat-icon orange"><i class="ri-shopping-bag-3-line"></i></div>
      <div class="q-stat-info">
        <h3>{{ stats.pending_orders || 0 }}</h3>
        <p>待付尾款</p>
        <div class="q-stat-trend" :class="stats.monthly_unpaid < 0 ? 'trend-down' : 'trend-up'">{{ stats.monthly_unpaid || 0 }} <span class="trend-label">较上月</span></div>
      </div>
    </div>
    <div class="q-stat-card" @click="$router.push('/figures')">
      <div class="q-stat-icon green"><i class="ri-add-circle-line"></i></div>
      <div class="q-stat-info">
        <h3>+{{ stats.monthly_new || 0 }}</h3>
        <p>本月新增入库</p>
        <div class="q-stat-trend trend-down">持平 <span class="trend-label">较上月</span></div>
      </div>
    </div>
    <div class="q-stat-card" @click="$router.push('/dashboard')">
      <div class="q-stat-icon purple"><i class="ri-line-chart-line"></i></div>
      <div class="q-stat-info">
        <h3>¥{{ formatNumber(stats.total_assets) }}</h3>
        <p>总资产</p>
        <div class="q-stat-trend" :class="outperformClass">
          {{ outperformLabel }} {{ formatNumber(outperformAbs) }}%
        </div>
      </div>
    </div>
    <div class="q-stat-card" @click="$router.push('/dashboard')">
      <div class="q-stat-icon red"><i class="ri-check-double-line"></i></div>
      <div class="q-stat-info">
        <h3>{{ stats.sell_correct_count || 0 }}</h3>
        <p>卖对次数</p>
        <div class="q-stat-trend trend-up">{{ stats.win_rate || 0 }}% <span class="trend-label">胜率</span></div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  stats: { type: Object, default: () => ({}) }
})

const outperformClass = computed(() => (props.stats.hpi_change || 0) >= 0 ? 'trend-up' : 'trend-down')
const outperformLabel = computed(() => (props.stats.hpi_change || 0) >= 0 ? '跑赢大盘' : '跑输大盘')
const outperformAbs = computed(() => Math.abs(props.stats.hpi_change || 0))

const formatNumber = (n) => {
  if (n === null || n === undefined) return '0'
  return Number(n).toLocaleString('zh-CN', { minimumFractionDigits: 0, maximumFractionDigits: 2 })
}
</script>

<style scoped>
.quick-stats {
  display: grid; grid-template-columns: repeat(4, 1fr); gap: 16px; margin-bottom: 24px;
}
.q-stat-card {
  background: #fff; border-radius: 12px; padding: 20px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.06); display: flex; align-items: center; gap: 16px;
  transition: all 0.3s; cursor: pointer;
}
.q-stat-card:hover { transform: translateY(-3px); box-shadow: 0 8px 24px rgba(0,0,0,0.12); }
.q-stat-icon {
  width: 48px; height: 48px; border-radius: 12px;
  display: flex; align-items: center; justify-content: center; font-size: 24px;
}
.q-stat-icon.blue { background: #e6f4ff; color: #1890ff; }
.q-stat-icon.green { background: #f6ffed; color: #52c41a; }
.q-stat-icon.orange { background: #fff7e6; color: #fa8c16; }
.q-stat-icon.purple { background: #f9f0ff; color: #722ed1; }
.q-stat-icon.red { background: #fff1f0; color: #ff4d4f; }
.q-stat-info h3 { font-size: 24px; font-weight: 700; color: #1a1a1a; margin-bottom: 2px; }
.q-stat-info p { color: #999; font-size: 13px; }
.q-stat-trend { font-size: 12px; font-weight: 600; margin-top: 4px; }
.trend-up { color: #ff4d4f; }
.trend-down { color: #52c41a; }
.trend-label { color: #999; font-weight: 400; }
@media (max-width: 1024px) { .quick-stats { grid-template-columns: repeat(2, 1fr); } }
@media (max-width: 768px) { .quick-stats { grid-template-columns: 1fr; } }
</style>
