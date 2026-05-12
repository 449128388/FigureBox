/**
 * useBatchSelection.js - 已出售订单批量选择功能组合式函数
 *
 * 功能说明：
 * - 管理订单卡片的批量选择状态
 * - 提供选中/取消选中功能
 * - 提供全选/取消全选功能
 *
 * 使用场景：
 * - 订单列表批量操作（批量删除等）
 * - 需要选择多个订单进行统一处理的场景
 *
 * 维护提示：
 * - selectedIds 存储选中的订单ID集合
 * - 使用 Set 数据结构保证唯一性和高效查询
 */

import { ref, computed } from 'vue'

export function useBatchSelection() {
  const selectedIds = ref(new Set())
  const isBatchMode = ref(false)

  const selectedIdsArray = computed(() => Array.from(selectedIds.value))
  const selectedCount = computed(() => selectedIds.value.size)
  const hasSelection = computed(() => selectedIds.value.size > 0)

  const setSelection = (orderId, selected) => {
    if (selected) {
      selectedIds.value.add(orderId)
    } else {
      selectedIds.value.delete(orderId)
    }
    selectedIds.value = new Set(selectedIds.value)
  }

  const isSelected = (orderId) => {
    return selectedIds.value.has(orderId)
  }

  const selectAll = (orders) => {
    orders.forEach(order => {
      selectedIds.value.add(order.id)
    })
    selectedIds.value = new Set(selectedIds.value)
  }

  const deselectAll = () => {
    selectedIds.value.clear()
    selectedIds.value = new Set()
  }

  const enterBatchMode = () => {
    isBatchMode.value = true
  }

  const exitBatchMode = () => {
    isBatchMode.value = false
    deselectAll()
  }

  const clearAll = () => {
    selectedIds.value.clear()
    isBatchMode.value = false
    selectedIds.value = new Set()
  }

  return {
    selectedIds,
    isBatchMode,
    selectedIdsArray,
    selectedCount,
    hasSelection,
    setSelection,
    isSelected,
    selectAll,
    deselectAll,
    enterBatchMode,
    exitBatchMode,
    clearAll
  }
}