/**
 * 藏品详情抽屉常量配置
 * 包含状态文本、颜色映射、评分标签等常量
 */

// 状态样式类映射
export const STATUS_CLASSES = {
  'star': 'st-in',
  'new': 'st-in',
  'fix': 'st-fix',
  'out': 'st-out',
  'air': 'st-air',
  'dup': 'st-in',
  'pre': 'st-air',
  'wait': 'st-air',
  'fav': 'st-in'
}

// 状态文本映射
export const STATUS_TEXTS = {
  'star': '在柜',
  'new': '在柜',
  'fix': '待修复',
  'out': '已出坑',
  'air': '预定中',
  'dup': '在柜',
  'pre': '待出荷',
  'wait': '待出荷',
  'fav': '在柜'
}

// 状态颜色映射
export const STATUS_COLORS = {
  'st-in': '#7EB8A2',
  'st-air': '#9B7ED8',
  'st-fix': '#E6A23C',
  'st-out': '#999999'
}

// 状态标签映射
export const STATUS_LABELS = {
  'star': '✅ 在柜 · 镇柜之宝',
  'new': '✅ 在柜 · 新欢',
  'fix': '🔧 待修复',
  'out': '📦 已出坑',
  'air': '☁️ 预定中',
  'dup': '✅ 在柜 · 复数',
  'pre': '🚚 待出荷',
  'wait': '🚚 待出荷',
  'fav': '✅ 在柜 · 本命'
}

// 评分标签映射
export const STAR_LABELS = [
  '未设置',
  '1星 - 一般',
  '2星 - 还行',
  '3星 - 喜欢',
  '4星 - 很爱',
  '5星 - 镇柜之宝'
]

// 默认状态
export const DEFAULT_STATUS = {
  class: 'st-in',
  text: '在柜',
  color: '#7EB8A2',
  label: '✅ 在柜 · 完好'
}
