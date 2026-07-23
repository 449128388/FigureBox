/**
 * useHoldingsPagination - 持仓列表分页业务逻辑组合式函数
 *
 * 功能说明：
 * - 管理持仓列表的分页状态
 * - 提供分页切换、跳转等方法
 * - 计算当前页数据
 *
 * 使用示例：
 * const {
 *   page, pageSize, total, paginatedData,
 *   handlePageChange, handleSizeChange
 * } = useHoldingsPagination(holdingsData)
 *
 * 维护提示：
 * - 支持9/18/36三种每页条数
 * - 页码超出范围时自动校正
 */

import { ref, computed } from 'vue'

/**
 * @param {import('vue').Ref|import('vue').ComputedRef} dataSource - 数据源（响应式）
 * @returns {Object} 分页状态和方法
 */
export function useHoldingsPagination(dataSource) {
  // 当前页码（从1开始）
  const page = ref(1)
  // 每页条数
  const pageSize = ref(9)
  // 可选的每页条数
  const pageSizeOptions = [9, 18, 36]

  // 总条数
  const total = computed(() => {
    const data = dataSource.value
    return Array.isArray(data) ? data.length : 0
  })

  // 总页数
  const totalPages = computed(() => {
    return Math.max(1, Math.ceil(total.value / pageSize.value))
  })

  // 当前页的数据
  const paginatedData = computed(() => {
    const data = dataSource.value
    if (!Array.isArray(data) || data.length === 0) {
      return []
    }
    const start = (page.value - 1) * pageSize.value
    const end = start + pageSize.value
    return data.slice(start, end)
  })

  // 当前页显示范围文本（如 "共 18 条"）
  const rangeText = computed(() => {
    if (total.value === 0) return ''
    return `共 ${total.value} 条`
  })

  // 处理页码变化
  const handlePageChange = (newPage) => {
    page.value = Math.max(1, Math.min(newPage, totalPages.value))
  }

  // 处理每页条数变化
  const handleSizeChange = (newSize) => {
    pageSize.value = newSize
    // 切换每页条数后，如果当前页码超出总页数则自动校正
    if (page.value > totalPages.value) {
      page.value = totalPages.value
    }
  }

  // 重置到第一页
  const resetPage = () => {
    page.value = 1
  }

  return {
    page,
    pageSize,
    pageSizeOptions,
    total,
    totalPages,
    paginatedData,
    rangeText,
    handlePageChange,
    handleSizeChange,
    resetPage
  }
}
