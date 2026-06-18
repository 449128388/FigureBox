/**
 * constants.js - FigureOutDrawer 组件常量定义
 *
 * 职责：
 * - 定义组件使用的所有常量
 * - 文案、样式变量、配置项集中管理
 * - 便于国际化和主题定制
 */

/**
 * 抽屉标题文案
 */
export const DRAWER_TITLE = '🏷️ 出柜登记'

/**
 * 关闭按钮文本
 */
export const CLOSE_BUTTON_TEXT = '✕'

/**
 * 取消按钮文本
 */
export const CANCEL_BUTTON_TEXT = '取消'

/**
 * 确认按钮文本
 */
export const CONFIRM_BUTTON_TEXT = '确认出柜'

/**
 * 处理中按钮文本
 */
export const SUBMITTING_BUTTON_TEXT = '处理中...'

/**
 * 出柜说明区块标题
 */
export const INFO_BLOCK_TITLE = '📌 出柜说明'

/**
 * 出柜说明字段
 */
export const INFO_LABELS = {
  operationType: '操作类型',
  financialImpact: '资金影响',
  inventoryImpact: '库存影响'
}

/**
 * 出柜说明值
 */
export const INFO_VALUES = {
  operationType: '移出当前展示柜',
  financialImpact: '无 · 不涉及交易',
  inventoryImpact: '库存数量不变'
}

/**
 * 移出后去向区块标题
 */
export const OPTION_SECTION_TITLE = '移出后去向'

/**
 * 移出选项
 */
export const OUT_OPTIONS = {
  default: {
    label: '移出当前收藏',
    descTemplate: '仅移出「{cabinetName}」，从当前专区消失，不进行展示'
  }
}

/**
 * 警告提示内容
 */
export const WARNING_TEXT = {
  title: '注意：',
  content: '出柜登记仅影响展示柜分类，不会删除藏品信息，也不会产生交易流水。',
  note: '该藏品仍可在「我的收藏」全部列表中查看。'
}

/**
 * 陪伴天数提示模板
 */
export const HOLDING_DAYS_TEMPLATE = '陪伴 {days} 天 · 感谢这段收藏时光'

/**
 * 默认藏品名称
 */
export const DEFAULT_FIGURE_NAME = '未知手办'

/**
 * 默认藏品信息
 */
export const DEFAULT_FIGURE_META = '暂无信息'

/**
 * 当前所在标签模板
 */
export const CURRENT_CABINET_TEMPLATE = '📂 当前所在：{cabinetName}'

/**
 * CSS 变量默认值
 */
export const CSS_VARIABLES = {
  borderColor: '#EBE8E4',
  textPrimary: '#1F1F1F',
  textSecondary: '#666666',
  textTertiary: '#999999',
  accentColor: '#C49A6C',
  accentLight: '#FDF6EE',
  dangerColor: '#D66A6A',
  successColor: '#7EB8A2'
}

/**
 * 抽屉尺寸
 */
export const DRAWER_SIZE = 520

/**
 * 默认选项值
 */
export const DEFAULT_SELECTED_OPTION = 'default'
