/**
 * useActivityFeed.js - 动态流业务逻辑 composable
 *
 * 功能说明：
 * - 管理动态流数据的加载、筛选、分页
 * - 提供事件详情弹窗的数据
 */

import { ref } from 'vue'
import { ElMessage } from 'element-plus'
import { fetchTimeline, fetchEventDetail } from '../api/activityApi.js'

export function useActivityFeed() {
  /** 动态流分组数据 */
  const activityGroups = ref([])
  /** 是否还有更多数据 */
  const hasMore = ref(true)
  /** 加载状态 */
  const loading = ref(false)
  /** 当前筛选类型 */
  const currentFilter = ref('all')
  /** 当前分页偏移 */
  const currentOffset = ref(0)
  /** 详情弹窗数据 */
  const eventDetail = ref(null)
  /** 详情弹窗可见性 */
  const detailVisible = ref(false)

  /**
   * 获取日期标签（今天/昨天/前天）
   */
  function getDateLabel(dateStr, label) {
    if (label) return label
    return ''
  }

  /**
   * 获取事件类型对应的 CSS 类
   */
  function getEventDotClass(eventType) {
    const classMap = {
      'buy': 'buy',
      'full_pay': 'full_pay',
      'in_stock': 'in_stock',
      'sell': 'sell',
      'out': 'out',
      'tag_add': 'tag_add',
      'fix': 'fix',
      'order_create': 'order_create',
      'order_cancel': 'order_cancel',
      'price_update': 'price_update'
    }
    return classMap[eventType] || 'buy'
  }

  /**
   * 获取格式化时间（从ISO字符串中提取 HH:mm）
   */
  function formatTime(isoStr) {
    if (!isoStr) return ''
    try {
      const parts = isoStr.split('T')
      if (parts.length > 1) {
        return parts[1].substring(0, 5)
      }
      return ''
    } catch {
      return ''
    }
  }

  /**
   * 加载动态流数据
   */
  async function loadActivities(eventType, append = false) {
    loading.value = true
    try {
      if (!append) {
        currentOffset.value = 0
      }
      currentFilter.value = eventType || 'all'

      const res = await fetchTimeline({
        event_type: currentFilter.value,
        offset: currentOffset.value,
        limit: 20
      })

      const newGroups = res.activities || []

      if (append) {
        // 追加模式：合并到现有分组中
        activityGroups.value = mergeActivityGroups(activityGroups.value, newGroups)
      } else {
        activityGroups.value = newGroups
      }

      hasMore.value = res.has_more || false
      currentOffset.value += newGroups.length
    } catch (e) {
      ElMessage.error('加载动态流失败: ' + (e.response?.data?.detail || e.message))
    } finally {
      loading.value = false
    }
  }

  /**
   * 合并新旧分组数据
   */
  function mergeActivityGroups(existing, incoming) {
    const map = {}
    existing.forEach(g => { map[g.date] = g })
    incoming.forEach(g => {
      if (map[g.date]) {
        // 合并同一天的 items（去重）
        const existingIds = new Set(map[g.date].items.map(i => i.id))
        g.items.forEach(item => {
          if (!existingIds.has(item.id)) {
            map[g.date].items.push(item)
          }
        })
      } else {
        map[g.date] = g
      }
    })
    return Object.values(map).sort((a, b) => b.date.localeCompare(a.date))
  }

  /**
   * 加载更多
   */
  async function loadMore() {
    await loadActivities(currentFilter.value, true)
  }

  /**
   * 切换筛选类型
   */
  function switchFilter(eventType) {
    currentFilter.value = eventType || 'all'
    loadActivities(currentFilter.value, false)
  }

  /**
   * 查看事件详情
   */
  async function showDetail(eventId) {
    try {
      const detail = await fetchEventDetail(eventId)
      eventDetail.value = detail
      detailVisible.value = true
    } catch (e) {
      ElMessage.error('获取事件详情失败')
    }
  }

  /**
   * 关闭详情弹窗
   */
  function closeDetail() {
    detailVisible.value = false
    eventDetail.value = null
  }

  return {
    activityGroups,
    hasMore,
    loading,
    currentFilter,
    eventDetail,
    detailVisible,
    loadActivities,
    loadMore,
    switchFilter,
    showDetail,
    closeDetail,
    getDateLabel,
    getEventDotClass,
    formatTime
  }
}
