/**
 * useBatchSelection.js - 批量选择功能组合式函数
 *
 * 功能说明：
 * - 管理手办卡片的批量选择状态
 * - 提供选中/取消选中功能
 * - 提供全选/取消全选功能
 * - 提供禁用状态判断（检查手办是否有未完成订单）
 *
 * 使用场景：
 * - 手办列表批量操作（批量删除、批量导出等）
 * - 需要选择多个手办进行统一处理的场景
 *
 * 维护提示：
 * - selectedIds 存储选中的手办ID集合
 * - disabledIds 存储禁用的手办ID集合（有未完成订单）
 * - 使用 Set 数据结构保证唯一性和高效查询
 */

import { ref, computed } from 'vue'

export function useBatchSelection() {
  // 选中的手办ID集合
  const selectedIds = ref(new Set())
  // 禁用的手办ID集合（有未完成订单）
  const disabledIds = ref(new Set())
  // 是否启用批量选择模式
  const isBatchMode = ref(false)

  // 选中的手办ID数组（方便使用）
  const selectedIdsArray = computed(() => Array.from(selectedIds.value))
  // 选中的数量
  const selectedCount = computed(() => selectedIds.value.size)
  // 是否有选中的手办
  const hasSelection = computed(() => selectedIds.value.size > 0)

  /**
   * 切换手办的选中状态
   * @param {number} figureId - 手办ID
   * @param {boolean} hasIncompleteOrders - 是否有未完成订单
   */
  const toggleSelection = (figureId, hasIncompleteOrders = false) => {
    if (hasIncompleteOrders || disabledIds.value.has(figureId)) {
      return // 禁用的手办不能选择
    }

    if (selectedIds.value.has(figureId)) {
      selectedIds.value.delete(figureId)
    } else {
      selectedIds.value.add(figureId)
    }
    // 触发响应式更新
    selectedIds.value = new Set(selectedIds.value)
  }

  /**
   * 设置手办的选中状态
   * @param {number} figureId - 手办ID
   * @param {boolean} selected - 是否选中
   * @param {boolean} hasIncompleteOrders - 是否有未完成订单
   */
  const setSelection = (figureId, selected, hasIncompleteOrders = false) => {
    if (hasIncompleteOrders || disabledIds.value.has(figureId)) {
      return // 禁用的手办不能选择
    }

    if (selected) {
      selectedIds.value.add(figureId)
    } else {
      selectedIds.value.delete(figureId)
    }
    // 触发响应式更新
    selectedIds.value = new Set(selectedIds.value)
  }

  /**
   * 检查手办是否被选中
   * @param {number} figureId - 手办ID
   * @returns {boolean}
   */
  const isSelected = (figureId) => {
    return selectedIds.value.has(figureId)
  }

  /**
   * 检查手办是否被禁用
   * @param {number} figureId - 手办ID
   * @returns {boolean}
   */
  const isDisabled = (figureId) => {
    return disabledIds.value.has(figureId)
  }

  /**
   * 设置手办的禁用状态
   * @param {number} figureId - 手办ID
   * @param {boolean} disabled - 是否禁用
   */
  const setDisabled = (figureId, disabled) => {
    if (disabled) {
      disabledIds.value.add(figureId)
      // 如果已选中，需要取消选中
      if (selectedIds.value.has(figureId)) {
        selectedIds.value.delete(figureId)
        selectedIds.value = new Set(selectedIds.value)
      }
    } else {
      disabledIds.value.delete(figureId)
    }
    // 触发响应式更新
    disabledIds.value = new Set(disabledIds.value)
  }

  /**
   * 全选所有可选的手办
   * @param {Array} figures - 手办列表
   * @param {Function} hasIncompleteOrdersFn - 检查是否有未完成订单的函数
   */
  const selectAll = (figures, hasIncompleteOrdersFn = null) => {
    figures.forEach(figure => {
      const hasIncomplete = hasIncompleteOrdersFn ? hasIncompleteOrdersFn(figure) : false
      if (!hasIncomplete && !disabledIds.value.has(figure.id)) {
        selectedIds.value.add(figure.id)
      }
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
    disabledIds.value.clear()
    isBatchMode.value = false
    selectedIds.value = new Set()
    disabledIds.value = new Set()
  }

  return {
    // 状态
    selectedIds,
    disabledIds,
    isBatchMode,

    // 计算属性
    selectedIdsArray,
    selectedCount,
    hasSelection,

    // 方法
    toggleSelection,
    setSelection,
    isSelected,
    isDisabled,
    setDisabled,
    selectAll,
    deselectAll,
    enterBatchMode,
    exitBatchMode,
    clearAll
  }
}
