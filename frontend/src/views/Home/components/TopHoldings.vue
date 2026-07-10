<template>
  <div class="card">
    <div class="card-header">
      <div class="card-title"><i class="ri-trophy-line"></i> 持仓 TOP5</div>
      <div class="card-more" @click="$router.push('/dashboard')">资产看板 <i class="ri-arrow-right-s-line"></i></div>
    </div>
    <div class="card-body">
      <div v-if="!holdings.length" class="empty-state">暂无持仓数据</div>
      <div v-else class="figure-list">
        <div v-for="(h, i) in holdings" :key="h.id" class="figure-row" @click="$router.push('/figures/' + h.id)">
          <div class="figure-img">
            <img v-if="h.image" :src="h.image" :alt="h.name" @error="e => { e.target.style.display = 'none' }" />
            <i v-else class="ri-box-3-line"></i>
          </div>
          <div class="figure-info">
            <div class="figure-name">{{ h.name }}</div>
            <div class="figure-meta">{{ [h.manufacturer, h.scale].filter(Boolean).join(' · ') }}</div>
          </div>
          <div>
            <div class="figure-price">¥{{ formatPrice(h.current_price || h.purchase_price) }}</div>
            <div :class="['figure-change', (h.profit_pct || 0) >= 0 ? 'up' : 'down']">{{ (h.profit_pct || 0) >= 0 ? '+' : '' }}{{ (h.profit_pct || 0).toFixed(1) }}%</div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
defineProps({
  holdings: { type: Array, default: () => [] }
})
const formatPrice = (v) => {
  if (!v) return '0'
  return Number(v).toLocaleString('zh-CN', { minimumFractionDigits: 0 })
}
</script>

<style scoped>
.card {
  background: #fff; border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.06); overflow: hidden;
}
.card-header {
  padding: 16px 20px; border-bottom: 1px solid #f0f0f0;
  display: flex; align-items: center; justify-content: space-between;
}
.card-title { font-size: 15px; font-weight: 600; display: flex; align-items: center; gap: 8px; }
.card-title i { color: #1890ff; }
.card-body { padding: 16px 20px; }
.card-more { font-size: 13px; color: #1890ff; cursor: pointer; display: flex; align-items: center; gap: 4px; }
.card-more:hover { color: #096dd9; }
.empty-state { text-align: center; padding: 32px 0; color: #ccc; font-size: 14px; }
.figure-list { display: flex; flex-direction: column; gap: 12px; }
.figure-row {
  display: flex; align-items: center; gap: 12px; padding: 10px;
  border-radius: 8px; transition: all 0.2s; cursor: pointer;
}
.figure-row:hover { background: #f8f9fa; }
.figure-img {
  width: 48px; height: 48px; border-radius: 8px; background: #f0f0f0;
  display: flex; align-items: center; justify-content: center; font-size: 20px;
  flex-shrink: 0; overflow: hidden;
}
.figure-img img { width: 100%; height: 100%; object-fit: cover; }
.figure-info { flex: 1; min-width: 0; }
.figure-name { font-size: 14px; font-weight: 500; color: #1a1a1a; margin-bottom: 2px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.figure-meta { font-size: 12px; color: #999; }
.figure-price { font-size: 14px; font-weight: 600; color: #ff4d4f; text-align: right; }
.figure-change { font-size: 12px; text-align: right; }
.figure-change.up { color: #ff4d4f; }
.figure-change.down { color: #52c41a; }
</style>
