/**
 * utils.js - FigureOutDrawer 组件通用工具方法
 *
 * 职责：
 * - 提供格式化、计算等通用方法
 * - 与组件逻辑解耦，便于单元测试和复用
 */

import { DEFAULT_FIGURE_META, CURRENT_CABINET_TEMPLATE } from './constants'

/**
 * 格式化藏品元信息
 * 将藏品的 IP、比例、厂商、库存等信息拼接成字符串
 *
 * @param {Object} figure - 藏品数据对象
 * @param {string} figure.ip - IP/作品名称
 * @param {string} figure.scale - 比例
 * @param {string} figure.manufacturer - 厂商
 * @param {number} figure.quantity - 库存数量
 * @returns {string} 格式化后的元信息字符串
 *
 * @example
 * formatFigureMeta({ ip: '原创', scale: '1/7', manufacturer: 'Native', quantity: 3 })
 * // 返回: '原创 · 1/7 · Native · 库存 3 体'
 */
export function formatFigureMeta(figure) {
  if (!figure || typeof figure !== 'object') {
    return DEFAULT_FIGURE_META
  }

  const parts = []

  if (figure.ip) {
    parts.push(figure.ip)
  }

  if (figure.scale) {
    parts.push(figure.scale)
  }

  if (figure.manufacturer) {
    parts.push(figure.manufacturer)
  }

  if (figure.quantity) {
    parts.push(`库存 ${figure.quantity} 体`)
  }

  return parts.join(' · ') || DEFAULT_FIGURE_META
}

/**
 * 生成当前所在收藏柜标签文本
 *
 * @param {string} cabinetName - 收藏柜名称
 * @returns {string} 格式化后的标签文本
 *
 * @example
 * formatCabinetTag('海景房专区')
 * // 返回: '📂 当前所在：海景房专区'
 */
export function formatCabinetTag(cabinetName) {
  if (!cabinetName) {
    return CURRENT_CABINET_TEMPLATE.replace('{cabinetName}', '未知')
  }
  return CURRENT_CABINET_TEMPLATE.replace('{cabinetName}', cabinetName)
}

/**
 * 生成陪伴天数提示文本
 *
 * @param {number} days - 陪伴天数
 * @returns {string|null} 格式化后的提示文本，如果天数无效则返回 null
 *
 * @example
 * formatHoldingDaysHint(392)
 * // 返回: '陪伴 392 天 · 感谢这段收藏时光'
 */
export function formatHoldingDaysHint(days) {
  if (!days || days <= 0) {
    return null
  }
  return `陪伴 ${days} 天 · 感谢这段收藏时光`
}

/**
 * 生成移出选项描述文本
 *
 * @param {string} cabinetName - 收藏柜名称
 * @returns {string} 格式化后的描述文本
 *
 * @example
 * formatOutOptionDesc('海景房专区')
 * // 返回: '仅移出「海景房专区」，从当前专区消失，不进行展示'
 */
export function formatOutOptionDesc(cabinetName) {
  const template = '仅移出「{cabinetName}」，从当前专区消失，不进行展示'
  return template.replace('{cabinetName}', cabinetName || '当前收藏柜')
}

/**
 * 安全获取藏品属性
 * 防止访问 undefined 属性导致报错
 *
 * @param {Object} figure - 藏品数据对象
 * @param {string} key - 属性名
 * @param {*} defaultValue - 默认值
 * @returns {*} 属性值或默认值
 *
 * @example
 * safeGet(figure, 'name', '未知手办')
 * // 如果 figure.name 不存在，返回 '未知手办'
 */
export function safeGet(figure, key, defaultValue = '') {
  if (!figure || typeof figure !== 'object') {
    return defaultValue
  }
  return figure[key] !== undefined && figure[key] !== null
    ? figure[key]
    : defaultValue
}

/**
 * 验证出柜参数是否有效
 *
 * @param {Object} params - 出柜参数
 * @param {number} params.figureId - 藏品ID
 * @param {string} params.cabinetKey - 收藏柜key
 * @returns {boolean} 参数是否有效
 */
export function validateOutParams(params) {
  if (!params || typeof params !== 'object') {
    return false
  }

  const { figureId, cabinetKey } = params

  if (!figureId || typeof figureId !== 'number') {
    return false
  }

  if (!cabinetKey || typeof cabinetKey !== 'string') {
    return false
  }

  return true
}
