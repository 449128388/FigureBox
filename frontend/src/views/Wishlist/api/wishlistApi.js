/**
 * wishlistApi.js - 愿望清单 API 客户端
 */
import axios from '../../../axios'

const BASE = '/wishlist'

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

  // 厂商列表
  manufacturers() {
    return axios.get(`${BASE}/manufacturers`)
  }
}

export default wishlistApi
