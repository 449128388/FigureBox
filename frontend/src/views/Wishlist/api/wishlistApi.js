/**
 * wishlistApi.js - 愿望清单 API 客户端
 *
 * 2026-08-06 修复：manufacturers / scales 增加模块级 Promise 缓存，
 * 解决「同一页内多个组件 onMounted 同时调用 → 重复请求后端」的问题
 * （典型场景：WishlistFilterBar + WishlistManualModal 都在挂载时拉取同一份厂商列表）
 *
 * 缓存策略：
 * - 首次调用 → 发起请求，并把 Promise 本身缓存（未完成的 Promise 也能去重）
 * - 并发调用 → 全部 await 同一个 in-flight Promise，杜绝瞬时重复请求
 * - 调用成功 → 缓存保持，下次直接复用
 * - 调用失败 → 清空缓存，下次重试不会被「永远失败的 Promise」卡死
 * - 新增/编辑愿望后 → 调用 invalidateOptions() 清空缓存，下次重新拉取最新数据
 */
import axios from '../../../axios'

const BASE = '/wishlist'

// 模块级 Promise 缓存（存放的是 Promise 而非结果数组，方便处理并发场景）
let manufacturersCache = null
let scalesCache = null

export const wishlistApi = {
  // 列表
  list(params) {
    return axios.get(`${BASE}/`, { params })
  },

  // 详情
  detail(id) {
    return axios.get(`${BASE}/${id}`)
  },

  // 创建
  create(data) {
    return axios.post(`${BASE}/`, data)
  },

  // 更新
  update(id, data) {
    return axios.put(`${BASE}/${id}`, data)
  },

  // 软删除
  delete(id) {
    return axios.delete(`${BASE}/${id}`)
  },

  // 状态流转
  changeStatus(id, status) {
    return axios.post(`${BASE}/${id}/status`, { status })
  },

  // 转入手办库
  moveToLibrary(id, purchaseType = 'preorder') {
    return axios.post(`${BASE}/${id}/move-to-library`, { purchase_type: purchaseType })
  },

  // 统计
  stats() {
    return axios.get(`${BASE}/stats`)
  },

  // URL 抓取
  urlFetch(url) {
    return axios.post(`${BASE}/url-fetch`, { url })
  },

  // 厂商列表（带 Promise 缓存，避免同页内多组件重复请求）
  manufacturers(forceRefresh = false) {
    if (forceRefresh) manufacturersCache = null
    if (!manufacturersCache) {
      manufacturersCache = axios.get(`${BASE}/manufacturers`)
        .then(res => res || [])
        .catch(err => {
          // 请求失败时清空缓存，防止「永远失败的 Promise」阻塞后续重试
          manufacturersCache = null
          throw err
        })
    }
    return manufacturersCache
  },

  // 比例列表（带 Promise 缓存，避免同页内多组件重复请求）
  scales(forceRefresh = false) {
    if (forceRefresh) scalesCache = null
    if (!scalesCache) {
      scalesCache = axios.get(`${BASE}/scales`)
        .then(res => res || [])
        .catch(err => {
          scalesCache = null
          throw err
        })
    }
    return scalesCache
  },

  /**
   * 清空「厂商 / 比例」缓存
   * 调用时机：新增 / 编辑愿望成功之后（用户可能新增了厂商或比例，下次打开下拉需拿到最新值）
   */
  invalidateOptions() {
    manufacturersCache = null
    scalesCache = null
  }
}

export default wishlistApi
