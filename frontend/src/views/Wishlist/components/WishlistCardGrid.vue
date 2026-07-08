<template>
  <div>
    <div v-if="!loading && items.length === 0" class="empty-state">
      <i class="ri-heart-add-line"></i>
      <h3>暂无愿望清单</h3>
      <p>点击右上角添加你的第一个愿望手办吧</p>
    </div>

    <div v-else class="card-grid">
      <WishlistCard
        v-for="item in items"
        :key="item.id"
        :item="item"
        :selected="selectedIds.includes(item.id)"
        @toggle-select="(id) => $emit('toggle-select', id)"
        @edit="(it) => $emit('edit', it)"
        @delete="(it) => $emit('delete', it)"
        @move-to-library="(it) => $emit('move-to-library', it)"
      />
    </div>
  </div>
</template>

<script setup>
import WishlistCard from './WishlistCard.vue'

defineProps({
  items: { type: Array, default: () => [] },
  selectedIds: { type: Array, default: () => [] },
  loading: { type: Boolean, default: false }
})
defineEmits(['toggle-select', 'edit', 'delete', 'move-to-library'])
</script>

<style scoped>
.card-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 20px;
  margin-bottom: 24px;
}
.empty-state {
  text-align: center;
  padding: 80px 20px;
  background: #fff;
  border-radius: 10px;
  box-shadow: 0 2px 12px rgba(0,0,0,0.06);
}
.empty-state i {
  font-size: 64px;
  color: #d9d9d9;
  display: block;
  margin-bottom: 16px;
}
.empty-state h3 {
  color: #999;
  font-size: 18px;
  margin-bottom: 8px;
}
.empty-state p {
  color: #bbb;
  font-size: 14px;
  margin: 0;
}
</style>
