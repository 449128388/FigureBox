/**
 * 藏品详情抽屉工具函数
 * 包含状态计算、收藏历程生成等逻辑
 */

import {
  STATUS_CLASSES,
  STATUS_TEXTS,
  STATUS_COLORS,
  STATUS_LABELS
} from '../constants/figureDetailConfig'

/**
 * 获取状态样式类
 * @param {string} cabinetKey - 收藏柜类型key
 * @returns {string} 状态样式类
 */
export function getStatusClass(cabinetKey) {
  return STATUS_CLASSES[cabinetKey] || 'st-in'
}

/**
 * 获取状态文本
 * @param {string} cabinetKey - 收藏柜类型key
 * @returns {string} 状态文本
 */
export function getStatusText(cabinetKey) {
  return STATUS_TEXTS[cabinetKey] || '在柜'
}

/**
 * 获取状态颜色
 * @param {string} statusClass - 状态样式类
 * @returns {string} 状态颜色
 */
export function getStatusColor(statusClass) {
  return STATUS_COLORS[statusClass] || '#7EB8A2'
}

/**
 * 获取状态标签
 * @param {string} cabinetKey - 收藏柜类型key
 * @returns {string} 状态标签文本
 */
export function getStatusLabel(cabinetKey) {
  return STATUS_LABELS[cabinetKey] || '✅ 在柜 · 完好'
}

/**
 * 获取完整状态信息
 * @param {string} cabinetKey - 收藏柜类型key
 * @returns {Object} 包含class、text、color、label的状态对象
 */
export function getStatusInfo(cabinetKey) {
  const statusClass = getStatusClass(cabinetKey)
  return {
    class: statusClass,
    text: getStatusText(cabinetKey),
    color: getStatusColor(statusClass),
    label: getStatusLabel(cabinetKey)
  }
}

/**
 * 生成收藏历程列表
 * @param {Object} figure - 藏品数据
 * @returns {Array} 收藏历程列表
 */
export function generateHistoryList(figure) {
  const list = []
  if (figure?.transaction_date) {
    const costText = figure.purchase_price ? `，成本 ¥${Number(figure.purchase_price).toLocaleString()}` : ''
    list.push({
      date: figure.transaction_date,
      text: `首次入库 · 买入 <strong>1 体</strong>${costText}`
    })
  }
  return list
}

/**
 * 判断是否为镇柜之宝
 * @param {string} cabinetKey - 收藏柜类型key
 * @param {number} rating - 评分值
 * @returns {boolean}
 */
export function isStarFigure(cabinetKey, rating) {
  return cabinetKey === 'star' || rating === 5
}
