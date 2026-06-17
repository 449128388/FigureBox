/**
 * 收藏柜配置常量
 * 包含状态文本、样式类、副标题等常量定义
 */

// 收藏柜类型对应的副标题
export const CABINET_SUBTITLES = {
  star: '你最珍视的藏品，陪伴最久的塑料小人',
  new: '30天内加入收藏室的新成员',
  fix: '正在补件、补色或返厂中的病号',
  out: '已经找到新主人的藏品，感谢陪伴',
  air: '空气谷 — 已下单但尚未入库的藏品',
  dup: '同一手办持有2体以上的复数库存',
  wait: '已付清全款或尾款，等待工厂出荷',
  role: '你最钟爱的角色全收集'
}

// 收藏柜类型对应的状态样式类
export const STATUS_CLASSES = {
  star: 'st-in',
  new: 'st-in',
  fix: 'st-fix',
  out: 'st-out',
  air: 'st-air',
  dup: 'st-in',
  wait: 'st-air',
  role: 'st-in'
}

// 收藏柜类型对应的状态文本
export const STATUS_TEXTS = {
  star: '在柜',
  new: '在柜',
  fix: '修复中',
  out: '已出',
  air: '预定中',
  dup: '复数',
  wait: '待出荷',
  role: '本命'
}

// 排序选项配置
export const SORT_OPTIONS = [
  { field: 'transaction_date', label: '入库时间' },
  { field: 'name', label: '名称' },
  { field: 'rating', label: '喜爱度' },
  { field: 'holding_days', label: '收藏天数' }
]

// 视图模式选项
export const VIEW_MODES = [
  { mode: 'grid', label: '⊞ 网格' },
  { mode: 'list', label: '☰ 列表' }
]

// 默认收藏柜数据
export const DEFAULT_CABINET = {
  key: '',
  name: '',
  description: '',
  icon: '📦',
  icon_bg: '#F5F5F5',
  count: 0,
  companion_days: 0,
  meta: '',
  items: []
}

// 不显示陪伴天数的收藏柜类型
export const HIDE_COMPANION_DAYS_TYPES = ['air', 'wait']
