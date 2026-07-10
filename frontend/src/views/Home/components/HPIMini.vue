<template>
  <div class="hpi-mini">
    <div class="hpi-mini-header">
      <div>
        <div class="hpi-mini-title">塑料小人指数 (HPI)</div>
        <div class="hpi-mini-value">{{ formatHPI(hpiValue) }}</div>
        <div :class="['hpi-mini-change', hpiChange >= 0 ? 'up' : 'down']">
          {{ hpiChange >= 0 ? '↑' : '↓' }} {{ Math.abs(hpiChange) > 0 ? '+' : '' }}{{ hpiChange.toFixed(2) }} ({{ hpiChangePct.toFixed(2) }}%)
        </div>
      </div>
      <i class="ri-line-chart-line" style="font-size: 40px; opacity: 0.3;"></i>
    </div>
    <div class="hpi-mini-chart">
      <div v-for="(h, i) in bars" :key="i" class="mini-bar" :style="{ height: h + '%' }"></div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
const props = defineProps({
  hpiValue: { type: Number, default: 1000 },
  hpiChange: { type: Number, default: 0 },
  hpiChangePct: { type: Number, default: 0 }
})
const formatHPI = (v) => v?.toLocaleString('zh-CN', { minimumFractionDigits: 2, maximumFractionDigits: 2 }) || '1,000.00'
// Generate random bars for visual effect
const bars = computed(() => {
  return [30, 45, 35, 60, 50, 80, 100].map(v => v * (0.8 + Math.random() * 0.4))
})
</script>

<style scoped>
.hpi-mini {
  background: linear-gradient(135deg, #1890ff 0%, #36cfc9 100%);
  border-radius: 12px; padding: 20px; color: #fff;
  position: relative; overflow: hidden;
}
.hpi-mini::before {
  content: ""; position: absolute; top: -20px; right: -20px; width: 100px; height: 100px;
  background: rgba(255,255,255,0.1); border-radius: 50%;
}
.hpi-mini-header { display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 16px; }
.hpi-mini-title { font-size: 14px; opacity: 0.9; }
.hpi-mini-value { font-size: 32px; font-weight: 700; margin-bottom: 4px; }
.hpi-mini-change { font-size: 14px; opacity: 0.9; }
.hpi-mini-change.up { color: #fff; }
.hpi-mini-change.down { color: rgba(255,255,255,0.7); }
.hpi-mini-chart { height: 60px; margin-top: 12px; display: flex; align-items: flex-end; gap: 4px; }
.mini-bar { flex: 1; background: rgba(255,255,255,0.3); border-radius: 2px 2px 0 0; transition: all 0.3s; }
.mini-bar:hover { background: rgba(255,255,255,0.6); }
</style>
