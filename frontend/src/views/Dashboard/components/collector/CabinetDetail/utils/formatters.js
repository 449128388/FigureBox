/**
 * 格式化工具函数
 * 包含日期、藏品信息、陪伴天数等格式化函数
 */

/**
 * 格式化作品·比例·制造商信息
 * @param {Object} item - 藏品对象
 * @returns {string} 格式化后的字符串
 */
export function formatFigureInfo(item) {
  const work = item?.work || '未知'
  const scale = item?.scale || '未知'
  const manufacturer = item?.manufacturer || '未知'
  return `${work} · ${scale} · ${manufacturer}`
}

/**
 * 格式化入库时间·陪伴时间信息
 * @param {Object} item - 藏品对象
 * @returns {string} 格式化后的字符串
 */
export function formatDateInfo(item) {
  const date = item?.transaction_date || '未知'
  const days = item?.holding_days
  if (days && days > 0) {
    return `入库时间 ${date} · 陪伴 ${days} 天`
  }
  return `入库时间 ${date}`
}

/**
 * 格式化陪伴天数（带千分位）
 * @param {number} days - 天数
 * @returns {string} 格式化后的字符串
 */
export function formatCompanionDays(days) {
  if (!days || days === 0) return '-'
  return days.toLocaleString()
}

/**
 * 格式化数字为千分位
 * @param {number} num - 数字
 * @returns {string} 格式化后的字符串
 */
export function formatNumber(num) {
  if (!num && num !== 0) return '-'
  return num.toLocaleString()
}
