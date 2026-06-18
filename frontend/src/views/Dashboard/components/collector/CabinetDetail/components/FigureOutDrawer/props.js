/**
 * props.js - FigureOutDrawer 组件 Props 和 Events 定义
 *
 * 职责：
 * - 定义组件的所有 Props 类型和默认值
 * - 定义组件对外暴露的 Events
 * - 提供 Props 验证和类型安全
 */

/**
 * Props 定义
 */
export const props = {
  /**
   * 是否显示抽屉
   */
  visible: {
    type: Boolean,
    default: false
  },

  /**
   * 藏品数据
   */
  figure: {
    type: Object,
    default: () => ({})
  },

  /**
   * 当前收藏柜 key
   */
  cabinetKey: {
    type: String,
    default: ''
  },

  /**
   * 当前收藏柜名称
   */
  cabinetName: {
    type: String,
    default: ''
  },

  /**
   * 收藏柜图标
   */
  cabinetIcon: {
    type: String,
    default: '📦'
  }
}

/**
 * Events 定义（文档说明用）
 */
export const events = {
  /**
   * 关闭抽屉时触发
   */
  close: 'close',

  /**
   * 确认出柜时触发
   * 参数: { figureId, cabinetKey }
   */
  confirm: 'confirm'
}

/**
 * 默认选项配置
 */
export const DEFAULT_OPTION = 'default'

/**
 * 抽屉尺寸配置
 */
export const DRAWER_SIZE = 520
