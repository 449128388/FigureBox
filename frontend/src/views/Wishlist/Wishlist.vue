<template>
  <div class="wishlist-page">
    <TopHeader />
    <div class="main-container">
      <!-- 头部 -->
      <WishlistHeader
        :has-selected="selectedIds.length > 0"
        @open-url="openUrlModal"
        @open-manual="openManualModal"
        @refresh="onRefresh"
        @batch-delete="onBatchDelete"
      />

      <!-- 统计卡片 -->
      <WishlistStatsOverview :stats="stats" />

      <!-- 筛选条 -->
      <WishlistFilterBar
        v-model:filterName="filterName"
        v-model:filterStatus="filterStatus"
        v-model:filterMaker="filterMaker"
        v-model:filterStart="filterStart"
        v-model:filterEnd="filterEnd"
        @reset="onResetFilter"
        @search="onSearchFilter"
      />

      <!-- 卡片网格 -->
      <WishlistCardGrid
        :items="items"
        :selected-ids="selectedIds"
        :loading="loading"
        @toggle-select="toggleSelect"
        @edit="onEdit"
        @delete="onDelete"
        @move-to-library="onMoveToLibrary"
      />

      <!-- 分页 -->
      <WishlistPagination
        v-if="total > 0"
        v-model:current-page="currentPage"
        v-model:page-size="pageSize"
        :total="total"
      />
    </div>

    <!-- URL 抓取弹窗 -->
    <WishlistUrlModal
      :visible="urlModalVisible"
      @close="urlModalVisible = false"
      @saved="onSaved"
    />

    <!-- 手动录入弹窗 -->
    <WishlistManualModal
      :visible="formVisible"
      :is-editing="formIsEditing"
      :form="formData"
      :saving="formSaving"
      @close="manualClose"
      @save="onManualSave"
    />
  </div>
</template>

<script setup>
import { onMounted, ref, reactive } from 'vue'
import { ElMessage } from 'element-plus'
import { useWishlist } from './composables/useWishlist'
import { useWishlistStats } from './composables/useWishlistStats'
import { useWishlistForm } from './composables/useWishlistForm'

import WishlistHeader from './components/WishlistHeader.vue'
import WishlistStatsOverview from './components/WishlistStatsOverview.vue'
import WishlistFilterBar from './components/WishlistFilterBar.vue'
import WishlistCardGrid from './components/WishlistCardGrid.vue'
import WishlistPagination from './components/WishlistPagination.vue'
import WishlistUrlModal from './components/WishlistUrlModal.vue'
import WishlistManualModal from './components/WishlistManualModal.vue'
import TopHeader from '../../components/TopHeader.vue'

const {
  items, total, loading,
  currentPage, pageSize,
  filterName, filterStatus, filterMaker, filterStart, filterEnd,
  selectedIds,
  loadList, resetFilter, refresh,
  deleteItem, moveToLibrary, batchDelete
} = useWishlist()

const { stats, load: loadStats } = useWishlistStats()
const {
  visible: formVisible,
  isEditing: formIsEditing,
  form: formData,
  saving: formSaving,
  openForCreate,
  openForEdit,
  close: manualClose,
  save: manualSave
} = useWishlistForm()

const urlModalVisible = ref(false)

const openUrlModal = () => {
  urlModalVisible.value = true
}

const openManualModal = () => {
  openForCreate()
}

const onRefresh = () => {
  refresh()
  loadStats()
}

const onResetFilter = () => {
  resetFilter()
}
const onSearchFilter = () => {
  refresh()
}

const toggleSelect = (id) => {
  const idx = selectedIds.value.indexOf(id)
  if (idx >= 0) selectedIds.value.splice(idx, 1)
  else selectedIds.value.push(id)
}

const onEdit = (item) => {
  openForEdit(item)
}

const onDelete = async (item) => {
  const ok = await deleteItem(item.id)
  if (ok) loadStats()
}

const onMoveToLibrary = async (item) => {
  const ok = await moveToLibrary(item.id)
  if (ok) loadStats()
}

const onBatchDelete = () => {
  batchDelete()
}

const onManualSave = async () => {
  const result = await manualSave()
  if (result) {
    await loadList()
    await loadStats()
  }
}

const onSaved = async (created) => {
  await loadList()
  await loadStats()
}

onMounted(() => {
  loadList()
  loadStats()
})
</script>

<style scoped>
.wishlist-page {
  background: #f5f5f5;
  min-height: 100vh;
  padding-top: 64px;
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
  color: #1f1f1f;
  font-size: 14px;
  line-height: 1.5;
}
.main-container {
  max-width: 1400px;
  margin: 0 auto;
  padding: 24px 32px;
}
</style>
