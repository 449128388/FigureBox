/**
 * useWishlist.js - 愿望清单核心 composable
 *
 * 负责列表/筛选/分页/CRUD/状态流转/转库等业务逻辑
 */
import { ref, computed, watch } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { wishlistApi } from '../api/wishlistApi'

export function useWishlist() {
  // ========== 列表数据 ==========
  const items = ref([])
  const total = ref(0)
  const loading = ref(false)
  const currentPage = ref(1)
  const pageSize = ref(15)
  const pageSizes = [15, 30, 50]

  // ========== 筛选 ==========
  const filterName = ref('')
  const filterStatus = ref('')
  const filterMaker = ref('')
  const filterStart = ref('')  // YYYY-MM-DD
  const filterEnd = ref('')    // YYYY-MM-DD

  // ========== 选中 ==========
  const selectedIds = ref([])
  const allSelected = computed({
    get: () => items.value.length > 0 && selectedIds.value.length === items.value.length,
    set: (val) => {
      selectedIds.value = val ? items.value.map(i => i.id) : []
    }
  })

  // ========== 加载数据 ==========
  const loadList = async () => {
    loading.value = true
    try {
      const params = {
        skip: (currentPage.value - 1) * pageSize.value,
        limit: pageSize.value
      }
      if (filterName.value) params.name = filterName.value
      if (filterStatus.value) params.status = filterStatus.value
      if (filterMaker.value) params.manufacturer = filterMaker.value
      if (filterStart.value) params.release_start = filterStart.value
      if (filterEnd.value) params.release_end = filterEnd.value

      const res = await wishlistApi.list(params)
      items.value = res.items || []
      total.value = res.total || 0
    } catch (e) {
      ElMessage.error('加载愿望清单失败')
      items.value = []
      total.value = 0
    } finally {
      loading.value = false
    }
  }

  // 监听筛选条件变化
  watch([filterName, filterStatus, filterMaker, filterStart, filterEnd], () => {
    currentPage.value = 1
    loadList()
  })

  watch([currentPage, pageSize], () => {
    loadList()
  })

  // ========== 操作 ==========
  const handleFilter = () => {
    currentPage.value = 1
    loadList()
  }

  const resetFilter = () => {
    filterName.value = ''
    filterStatus.value = ''
    filterMaker.value = ''
    filterStart.value = ''
    filterEnd.value = ''
    currentPage.value = 1
    loadList()
  }

  const refresh = () => {
    loadList()
  }

  // 删除
  const deleteItem = async (id) => {
    try {
      await ElMessageBox.confirm('确定删除该愿望？', '确认', {
        type: 'warning',
        confirmButtonText: '删除',
        cancelButtonText: '取消'
      })
    } catch {
      return false
    }
    try {
      await wishlistApi.delete(id)
      ElMessage.success('删除成功')
      await loadList()
      return true
    } catch (e) {
      ElMessage.error('删除失败')
      return false
    }
  }

  // 状态流转
  const changeStatus = async (id, status) => {
    try {
      await wishlistApi.changeStatus(id, status)
      ElMessage.success('状态已更新')
      await loadList()
      return true
    } catch (e) {
      ElMessage.error('状态更新失败')
      return false
    }
  }

  // 转入手办库
  const moveToLibrary = async (id) => {
    try {
      await ElMessageBox.confirm('转入手办库后将移出愿望清单，确认继续？', '确认', {
        type: 'info',
        confirmButtonText: '转入',
        cancelButtonText: '取消'
      })
    } catch {
      return false
    }
    try {
      await wishlistApi.moveToLibrary(id, 'preorder')
      ElMessage.success('已转入手办库（预定）')
      await loadList()
      return true
    } catch (e) {
      ElMessage.error('转库失败')
      return false
    }
  }

  // 批量删除
  const batchDelete = async () => {
    if (selectedIds.value.length === 0) {
      ElMessage.warning('请先选择要删除的项目')
      return
    }
    try {
      await ElMessageBox.confirm(
        `确定删除选中的 ${selectedIds.value.length} 项愿望？`,
        '批量删除',
        { type: 'warning' }
      )
    } catch {
      return
    }
    try {
      await Promise.all(selectedIds.value.map(id => wishlistApi.delete(id)))
      ElMessage.success('批量删除成功')
      selectedIds.value = []
      await loadList()
    } catch (e) {
      ElMessage.error('批量删除失败')
    }
  }

  return {
    // state
    items, total, loading,
    currentPage, pageSize, pageSizes,
    filterName, filterStatus, filterMaker, filterStart, filterEnd,
    selectedIds, allSelected,
    // actions
    loadList, handleFilter, resetFilter, refresh,
    deleteItem, changeStatus, moveToLibrary, batchDelete
  }
}
