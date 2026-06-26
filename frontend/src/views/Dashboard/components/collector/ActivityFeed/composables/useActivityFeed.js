/**
 * useActivityFeed.js - 动态流业务逻辑 composable
 *
 * 功能说明：
 * - 管理动态流数据的加载、筛选、分页
 * - 提供事件详情弹窗的数据
 */

import { ref } from 'vue'
import { ElMessage } from 'element-plus'
import { fetchTimeline, fetchEventDetail, INITIAL_PAGE_SIZE, LOAD_MORE_PAGE_SIZE } from '../api/activityApi.js'

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
   * 获取格式化时间（从ISO字符串中提取 HH:mm:ss）
   */
  function formatTime(isoStr) {
    if (!isoStr) return ''
    try {
      const parts = isoStr.split('T')
      if (parts.length > 1) {
        return parts[1].substring(0, 8)
      }
      return ''
    } catch {
      return ''
    }
  }

  /**
   * 格式化事件标题（为关键字段添加HTML颜色高亮）
   *
   * 规则：
   * - 手办名称「...」→ highlight（主题色）
   * - 价格 ¥数字 → price（红色）
   * - 盈利文本 → profit（红色）
   * - 亏损文本 → loss（绿色）
   * - 标签 #tagname → tag-badge（红色）
   * - 出柜分类 → highlight（主题色）
   */
  function formatEventTitle(item, showAsset = true) {
    if (!item || !item.event_title) return ''
    const type = item.event_type || ''
    const detail = item.detail_data || {}
    let title = item.event_title

    // 0. show_asset = false 时，掩码所有价格敏感数据
    if (!showAsset) {
      title = title.replace(/((?:JP\s+)?[¥$€£])(\d+(?:\.\d+)?)/g, '¥***')
      title = title.replace(/(盈利\s*)¥[\d.]+/g, '$1¥***')
      title = title.replace(/(亏损\s*)¥[\d.]+/g, '$1¥***')
      return title
    }

    // 1. 包裹手办名称（全部类型）
    title = title.replace(/「([^」]*)」/g, '<span class="highlight">「$1」</span>')

    // 2. 卖出事件：价格和盈亏
    if (type === 'sell') {
      title = title.replace(/¥(\d+(?:\.\d+)?)/g, '<span class="price">¥$1</span>')
      title = title.replace(/(盈利\s*¥[\d.]+)/g, '<span class="profit">$1</span>')
      title = title.replace(/(亏损\s*¥[\d.]+)/g, '<span class="loss">$1</span>')
    }

    // 3. 标签事件：#标签名 — 统一使用红色
    if (type === 'tag_add') {
      title = title.replace(/(#[^\s,、，」]+)/g, '<span class="tag-badge" style="background:#FFEBEE;color:#D66A6A">$1</span>')
    }

    // 4. 出柜事件：移出分类名称使用 highlight 高亮
    if (type === 'out') {
      title = title.replace(/已移出(.+)$/, '已移出<span class="highlight">$1</span>')
    }

    // 5. BUY 事件：金额数字高亮
    if (type === 'buy') {
      // 金额数字带币种符号（如 $800.0、¥900.0、JP ¥800.0）
      title = title.replace(/((?:JP\s+)?[¥$€£])(\d+(?:\.\d+)?)/g, '<span class="price">$1$2</span>')
    }

    // 6. 市场价更新事件：价格数字高亮（红色）
    if (type === 'price_update') {
      title = title.replace(/([¥$€£])(\d+(?:\.\d+)?)/g, '<span class="price">$1$2</span>')
    }

    return title
  }

  /**
   * 加载动态流数据
   * @param {string} eventType - 事件类型
   * @param {boolean} append - 是否追加模式
   * @param {number} pageLimit - 每页条数（默认首次加载 20）
   */
  async function loadActivities(eventType, append = false, pageLimit = INITIAL_PAGE_SIZE) {
    loading.value = true
    try {
      if (!append) {
        currentOffset.value = 0
      }
      currentFilter.value = eventType || 'all'

      const res = await fetchTimeline({
        event_type: currentFilter.value,
        offset: currentOffset.value,
        limit: pageLimit
      })

      const newGroups = res.activities || []

      if (append) {
        // 追加模式：合并到现有分组中
        activityGroups.value = mergeActivityGroups(activityGroups.value, newGroups)
      } else {
        activityGroups.value = newGroups
      }

      hasMore.value = res.has_more || false
      currentOffset.value += pageLimit
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
   * 加载更多（每次加载 10 条）
   */
  async function loadMore() {
    await loadActivities(currentFilter.value, true, LOAD_MORE_PAGE_SIZE)
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
    formatTime,
    formatEventTitle
  }
}
