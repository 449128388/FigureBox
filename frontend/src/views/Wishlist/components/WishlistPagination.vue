<template>
  <div class="pagination-wrapper">
    <span class="page-info">共 {{ total }} 条</span>
    <select v-model="localPageSize" class="page-size" @change="onSizeChange">
      <option :value="15">15条/页</option>
      <option :value="30">30条/页</option>
      <option :value="50">50条/页</option>
    </select>
    <div class="page-btns">
      <button class="page-btn" :disabled="currentPage <= 1" @click="goPage(currentPage - 1)">
        <i class="ri-arrow-left-s-line"></i>
      </button>
      <button
        v-for="p in pageNumbers"
        :key="p"
        :class="['page-btn', { active: p === currentPage }]"
        @click="goPage(p)"
      >{{ p }}</button>
      <button class="page-btn" :disabled="currentPage >= totalPages" @click="goPage(currentPage + 1)">
        <i class="ri-arrow-right-s-line"></i>
      </button>
    </div>
    <div class="page-jump">
      <span>前往</span>
      <input v-model.number="jumpPage" type="number" class="page-input" :min="1" :max="totalPages" />
      <span>页</span>
    </div>
  </div>
</template>

<script setup>
import { computed, ref, watch } from 'vue'

const props = defineProps({
  currentPage: { type: Number, default: 1 },
  pageSize: { type: Number, default: 15 },
  total: { type: Number, default: 0 }
})
const emit = defineEmits(['update:currentPage', 'update:pageSize'])

const localPageSize = ref(props.pageSize)
watch(() => props.pageSize, (v) => { localPageSize.value = v })

const totalPages = computed(() => Math.max(1, Math.ceil(props.total / props.pageSize)))

const pageNumbers = computed(() => {
  const pages = []
  const start = Math.max(1, props.currentPage - 2)
  const end = Math.min(totalPages.value, start + 4)
  for (let i = start; i <= end; i++) pages.push(i)
  return pages
})

const jumpPage = ref(props.currentPage)
watch(() => props.currentPage, (v) => { jumpPage.value = v })

const goPage = (p) => {
  if (p < 1 || p > totalPages.value) return
  emit('update:currentPage', p)
}

const onSizeChange = () => {
  emit('update:pageSize', localPageSize.value)
  emit('update:currentPage', 1)
}
</script>

<style scoped>
.pagination-wrapper {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 12px;
  padding: 20px 0;
  background: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.06);
}
.page-info { color: #666; font-size: 14px; }
.page-size {
  height: 32px;
  border: 1px solid #d9d9d9;
  border-radius: 6px;
  padding: 0 12px;
  outline: none;
  font-size: 13px;
  cursor: pointer;
}
.page-btns { display: flex; gap: 4px; }
.page-btn {
  min-width: 32px;
  height: 32px;
  border: 1px solid #d9d9d9;
  background: #fff;
  border-radius: 6px;
  cursor: pointer;
  color: #666;
  font-size: 14px;
  transition: all 0.3s;
}
.page-btn:hover:not(:disabled):not(.active) {
  color: #1890ff;
  border-color: #1890ff;
}
.page-btn.active {
  background: #1890ff;
  color: #fff;
  border-color: #1890ff;
}
.page-btn:disabled { opacity: 0.5; cursor: not-allowed; }
.page-jump {
  display: flex;
  align-items: center;
  gap: 6px;
  color: #666;
  font-size: 13px;
}
.page-input {
  width: 60px;
  height: 32px;
  border: 1px solid #d9d9d9;
  border-radius: 6px;
  padding: 0 8px;
  outline: none;
  font-size: 13px;
  text-align: center;
}
</style>
