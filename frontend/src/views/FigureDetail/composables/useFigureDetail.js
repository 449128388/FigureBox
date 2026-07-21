/**
 * useFigureDetail.js - 手办详情业务逻辑
 *
 * 职责划分：
 * - 数据拉取：fetchFigureDetail / fetchOrders / getRelatedOrders
 * - 业务格式化：formatPrice / formatDate / formatQuantity / getStatusBadge
 * - 订单业务：getOrderDisplayInfo / getPaymentDisplay（订单支付信息智能展示）
 *
 * 所有业务函数以纯函数导出（无需响应式），组件按需导入解构使用
 */

import { useFigureStore, useOrderStore } from '../../../store'
import axios from '../../../axios'

// ============== 数据拉取 ==============

/**
 * 获取手办详情（后端已包含订单均价等计算字段）
 */
const fetchFigureDetail = async (figureId) => {
  try {
    // axios 拦截器已解包 response.data
    return await axios.get(`/figures/${figureId}`)
  } catch (error) {
    // 失败兜底：从 store 中查找
    const figureStore = useFigureStore()
    const figure = figureStore.figures.find(f => f.id == figureId)
    return figure || {}
  }
}

/**
 * 获取当前用户所有订单
 */
const fetchOrders = async () => {
  const orderStore = useOrderStore()
  return orderStore.fetchOrders()
}

/**
 * 从全量订单中筛选关联订单
 */
const getRelatedOrders = (figureId, orders) => {
  return orders.filter(order => order.figure_id === parseInt(figureId))
}

// ============== 业务格式化 ==============

/**
 * 货币符号映射
 */
const getCurrencySymbol = (currency) => {
  const map = {
    CNY: '元',
    JPY: '日元',
    USD: '美元',
    EUR: '欧元'
  }
  return map[currency] || '元'
}

/**
 * 格式化金额（统一用 ¥ + 数字，金额字段下显示货币后缀）
 */
const formatPrice = (value, currency) => {
  if (value === null || value === undefined) return '—'
  const num = Number(value)
  if (Number.isNaN(num)) return '—'
  const fixed = num % 1 === 0 ? num.toString() : num.toFixed(2)
  return `¥${fixed}`
}

/**
 * 格式化数量（数字 + 体）
 */
const formatQuantity = (value) => {
  if (value === null || value === undefined) return '—'
  return `${value} 体`
}

/**
 * 格式化日期（截取 YYYY-MM-DD）
 */
const formatDate = (value) => {
  if (!value) return '—'
  const str = String(value)
  return str.length >= 10 ? str.substring(0, 10) : str
}

/**
 * 格式化支付时间（截取 YYYY-MM-DD）
 */
const formatPaymentDate = formatDate

/**
 * 截取字符串首字（用于作者头像占位）
 */
const getAuthorInitial = (name) => {
  if (!name) return '?'
  return String(name).trim().charAt(0).toUpperCase()
}

// ============== 状态徽章 ==============

/**
 * 手办状态徽章 class（用于基本信息卡片右上角徽章）
 */
const getFigureStatusBadge = (figure) => {
  // 根据 purchase_type + 库存计算
  if (figure.purchase_type === 'wishlist') {
    return { class: 'badge-orange', text: '愿望中' }
  }
  if (figure.average_purchase_price > 0) {
    return { class: 'badge-green', text: '已入手' }
  }
  return { class: 'badge-blue', text: '在库' }
}

/**
 * 订单状态 class（用于订单徽章 / value 文本着色）
 */
const getOrderStatusClass = (status) => {
  const map = {
    '未支付': 'status-unpaid',
    '已支付': 'status-paid',
    '已完成': 'status-paid',
    '已取消': 'status-cancelled'
  }
  return map[status] || ''
}

/**
 * 订单状态徽章 class
 */
const getOrderStatusBadge = (status) => {
  const map = {
    '未支付': 'badge-orange',
    '已支付': 'badge-blue',
    '已完成': 'badge-green',
    '已取消': 'badge-red'
  }
  return map[status] || 'badge-blue'
}

// ============== 订单业务 ==============

/**
 * 智能计算订单要展示的「支付方式 / 支付时间」
 *
 * 业务规则：
 * - 已完成订单：优先展示尾款支付（balance_payment_*），回退到定金支付
 * - 已支付订单（未完成尾款）：展示定金支付（payment_*）
 * - 未支付订单：均为空
 * - 已取消订单：均为空
 *
 * Returns: { method: string, time: string }
 */
const getPaymentDisplay = (order) => {
  if (!order || order.status === '未支付' || order.status === '已取消') {
    return { method: '—', time: '—' }
  }
  // 已完成：优先尾款支付
  if (order.status === '已完成') {
    return {
      method: order.balance_payment_method || order.payment_method || '—',
      time: formatPaymentDate(order.balance_payment_time || order.payment_time)
    }
  }
  // 已支付：展示定金支付
  return {
    method: order.payment_method || '—',
    time: formatPaymentDate(order.payment_time)
  }
}

/**
 * 构造订单副标题（japanese_name · manufacturer · scale）
 */
const getPageSubtitle = (figure) => {
  const parts = []
  if (figure.japanese_name) parts.push(figure.japanese_name)
  if (figure.manufacturer) parts.push(figure.manufacturer)
  if (figure.scale) parts.push(figure.scale)
  return parts.join(' · ') || ''
}

// ============== 主入口 ==============

export function useFigureDetail() {
  return {
    // 数据
    fetchFigureDetail,
    fetchOrders,
    getRelatedOrders,
    // 格式化
    getCurrencySymbol,
    formatPrice,
    formatQuantity,
    formatDate,
    formatPaymentDate,
    getAuthorInitial,
    getPageSubtitle,
    // 状态
    getFigureStatusBadge,
    getOrderStatusClass,
    getOrderStatusBadge,
    getPaymentDisplay
  }
}
