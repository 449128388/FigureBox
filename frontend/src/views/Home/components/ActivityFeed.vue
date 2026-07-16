<template>
  <div class="card">
    <div class="card-header">
      <div class="card-title"><i class="ri-history-line"></i> 最近动态</div>
      <div class="card-more">查看全部 <i class="ri-arrow-right-s-line"></i></div>
    </div>
    <div class="card-body">
      <div v-if="!activities.length" class="empty-state">暂无动态</div>
      <div v-else class="activity-list">
        <div v-for="(act, i) in activities.slice(0, 5)" :key="i" class="activity-item" @click="act.figure_id && $router.push('/figures/' + act.figure_id)">
          <div :class="['activity-dot', act.type]"></div>
          <div class="activity-content">
            <div class="activity-text" v-html="act.text"></div>
            <div class="activity-time">{{ act.time_label }}</div>
          </div>
          <div v-if="act.figure_image" class="activity-thumb">
            <img :src="act.figure_image" alt="" @error="e => { e.target.style.display = 'none' }" />
          </div>
          <div v-else class="activity-thumb"><i class="ri-image-line"></i></div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
defineProps({
  activities: { type: Array, default: () => [] }
})
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
.activity-list { display: flex; flex-direction: column; gap: 12px; }
.activity-item {
  display: flex; align-items: flex-start; gap: 12px; padding: 12px;
  border-radius: 8px; transition: all 0.2s; cursor: pointer;
}
.activity-item:hover { background: #f8f9fa; }
.activity-dot {
  width: 8px; height: 8px; border-radius: 50%; margin-top: 6px; flex-shrink: 0;
}
.activity-dot.buy { background: #52c41a; }
.activity-dot.sell { background: #fa8c16; }
.activity-dot.wish { background: #1890ff; }
.activity-dot.price { background: #ff4d4f; }
.activity-dot.cancel { background: #ff4d4f; }
.activity-content { flex: 1; }
.activity-text { font-size: 13px; color: #333; line-height: 1.5; }
.activity-text :deep(strong) { color: #1a1a1a; }
.activity-time { font-size: 12px; color: #bbb; margin-top: 4px; }
.activity-thumb {
  width: 40px; height: 40px; border-radius: 6px; background: #f0f0f0;
  display: flex; align-items: center; justify-content: center; font-size: 18px;
  flex-shrink: 0; overflow: hidden;
}
.activity-thumb img { width: 100%; height: 100%; object-fit: cover; }
</style>
