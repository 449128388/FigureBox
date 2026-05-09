/**
 * useBatchSelection.js - 订单批量选择功能组合式函数
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
  // 选中的订单ID集合
  const selectedIds = ref(new Set())
  // 是否启用批量选择模式
  const isBatchMode = ref(false)

  // 选中的订单ID数组（方便使用）
  const selectedIdsArray = computed(() => Array.from(selectedIds.value))
  // 选中的数量
  const selectedCount = computed(() => selectedIds.value.size)
  // 是否有选中的订单
  const hasSelection = computed(() => selectedIds.value.size > 0)

  /**
   * 设置订单的选中状态
   * @param {number} orderId - 订单ID
   * @param {boolean} selected - 是否选中
   */
  const setSelection = (orderId, selected) => {
    if (selected) {
      selectedIds.value.add(orderId)
    } else {
      selectedIds.value.delete(orderId)
    }
    // 触发响应式更新
    selectedIds.value = new Set(selectedIds.value)
  }

  /**
   * 检查订单是否被选中
   * @param {number} orderId - 订单ID
   * @returns {boolean}
   */
  const isSelected = (orderId) => {
    return selectedIds.value.has(orderId)
  }

  /**
   * 全选所有订单
   * @param {Array} orders - 订单列表
   */
  const selectAll = (orders) => {
    orders.forEach(order => {
      selectedIds.value.add(order.id)
    })
    selectedIds.value = new Set(selectedIds.value)
  }

  /**
   * 取消全选
   */
  const deselectAll = () => {
    selectedIds.value.clear()
    selectedIds.value = new Set()
  }

  /**
   * 进入批量选择模式
   */
  const enterBatchMode = () => {
    isBatchMode.value = true
  }

  /**
   * 退出批量选择模式
   */
  const exitBatchMode = () => {
    isBatchMode.value = false
    deselectAll()
  }

  /**
   * 清空所有状态
   */
  const clearAll = () => {
    selectedIds.value.clear()
    isBatchMode.value = false
    selectedIds.value = new Set()
  }

  return {
    // 状态
    selectedIds,
    isBatchMode,

    // 计算属性
    selectedIdsArray,
    selectedCount,
    hasSelection,

    // 方法
    setSelection,
    isSelected,
    selectAll,
    deselectAll,
    enterBatchMode,
    exitBatchMode,
    clearAll
  }
}
