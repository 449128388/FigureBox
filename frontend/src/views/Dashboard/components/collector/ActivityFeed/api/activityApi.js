/**
 * activityApi.js - 动态流 API 接口
 *
 * 功能说明：
 * - 提供动态流相关 API 调用
 * - 获取动态流列表、事件详情等
 */

import axios from '../../../../../../axios'

/**
 * 获取动态流列表（按日期分组）
 * @param {Object} params - 查询参数
 * @param {string} params.event_type - 事件类型筛选：all/buy/sell/order/tag/price
 * @param {number} params.offset - 分页偏移
 * @param {number} params.limit - 每页条数
 * @returns {Promise<Object>} { activities: [], has_more: boolean }
 */
export function fetchTimeline(params = {}) {
  const defaults = { event_type: 'all', offset: 0, limit: 20 }
  return axios.get('/collector/timeline', { params: { ...defaults, ...params } })
}

/**
 * 获取单条事件详情
 * @param {number} eventId - 事件ID
 * @returns {Promise<Object>} 事件详情
 */
export function fetchEventDetail(eventId) {
  return axios.get(`/collector/timeline/events/${eventId}`)
}
