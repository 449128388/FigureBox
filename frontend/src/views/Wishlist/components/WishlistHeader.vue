<template>
  <div class="page-header">
    <div class="page-title">
      <i class="ri-heart-3-fill" style="color:#ff6b9d"></i>
      <span>愿望清单</span>
    </div>
    <div class="header-actions">
      <button class="btn btn-purple" @click="$emit('open-url')">
        <i class="ri-link"></i>
        <span>URL 智能抓取</span>
      </button>
      <button class="btn btn-primary" @click="$emit('open-manual')">
        <i class="ri-add-line"></i>
        <span>手动添加</span>
      </button>
      <button class="btn btn-default" @click="onRefresh" :class="{ 'is-loading': loading }">
        <i :class="loading ? 'ri-loader-4-line ri-spin' : 'ri-refresh-line'"></i>
        <span>{{ loading ? '刷新中' : '刷新' }}</span>
      </button>
      <router-link to="/wishlist/debug" class="debug-link" title="HTML 抓取调试">
        <i class="ri-bug-line"></i>
      </router-link>
      <button class="btn btn-danger" :disabled="!hasSelected" @click="$emit('batch-delete')">
        <i class="ri-delete-bin-line"></i>
        <span>批量删除</span>
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'

defineProps({
  hasSelected: { type: Boolean, default: false }
})
const emit = defineEmits(['open-url', 'open-manual', 'refresh', 'batch-delete'])

const loading = ref(false)
const onRefresh = async () => {
  if (loading.value) return
  loading.value = true
  try {
    emit('refresh')
    await new Promise(r => setTimeout(r, 600))
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: #fff;
  padding: 20px 24px;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.06);
  margin-bottom: 20px;
}
.page-title {
  font-size: 20px;
  font-weight: 600;
  color: #1a1a1a;
  display: flex;
  align-items: center;
  gap: 10px;
}
.page-title i { color: #ff6b9d; font-size: 22px; }
.header-actions { display: flex; gap: 10px; }
.btn {
  padding: 8px 16px;
  border-radius: 6px;
  border: none;
  cursor: pointer;
  font-size: 14px;
  display: flex;
  align-items: center;
  gap: 6px;
  transition: all 0.3s;
  font-weight: 500;
  color: #fff;
}
.btn:disabled { opacity: 0.5; cursor: not-allowed; }
.btn-primary { background: #52c41a; }
.btn-primary:hover:not(:disabled) { background: #389e0d; }
.btn-info { background: #1890ff; }
.btn-info:hover:not(:disabled) { background: #096dd9; }
.btn-purple { background: #722ed1; }
.btn-purple:hover:not(:disabled) { background: #531dab; }
.btn-danger { background: #ff4d4f; }
.btn-danger:hover:not(:disabled) { background: #cf1322; }
.btn-default {
  background: #f5f5f5;
  color: #666;
  border: 1px solid #d9d9d9;
}
.btn-default:hover:not(:disabled) { background: #e8e8e8; color: #333; }
.debug-link {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 36px;
  height: 36px;
  border-radius: 6px;
  background: #f5f5f5;
  border: 1px solid #d9d9d9;
  color: #999;
  text-decoration: none;
  transition: all 0.3s;
}
.debug-link:hover { background: #e8e8e8; color: #722ed1; border-color: #722ed1; }
.ri-spin { animation: spin 1s linear infinite; }
@keyframes spin { from { transform: rotate(0); } to { transform: rotate(360deg); } }
</style>
