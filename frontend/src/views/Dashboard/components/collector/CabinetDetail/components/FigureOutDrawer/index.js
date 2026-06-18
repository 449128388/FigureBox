/**
 * index.js - FigureOutDrawer 组件核心逻辑
 *
 * 职责：
 * - 定义组件的数据、计算属性、方法
 * - 处理业务逻辑和事件
 * - 与模板和样式分离，便于维护
 */

import { props } from './props'
import {
  DRAWER_TITLE,
  CLOSE_BUTTON_TEXT,
  CANCEL_BUTTON_TEXT,
  CONFIRM_BUTTON_TEXT,
  SUBMITTING_BUTTON_TEXT,
  INFO_BLOCK_TITLE,
  INFO_LABELS,
  INFO_VALUES,
  OPTION_SECTION_TITLE,
  OUT_OPTIONS,
  WARNING_TEXT,
  DEFAULT_FIGURE_NAME,
  DEFAULT_SELECTED_OPTION,
  DRAWER_SIZE
} from './constants'
import {
  formatHoldingDaysHint,
  formatOutOptionDesc,
  safeGet,
  validateOutParams
} from './utils'

/**
 * 组件名称
 */
export const name = 'FigureOutDrawer'

/**
 * Props 定义
 */
export { props }

/**
 * 组件数据
 * @returns {Object} 组件初始数据
 */
export function data() {
  return {
    // 抽屉显示状态
    drawerVisible: this.visible,

    // 选中的移出选项
    selectedOption: DEFAULT_SELECTED_OPTION,

    // 提交中状态
    submitting: false
  }
}

/**
 * 计算属性
 */
export const computed = {
  /**
   * 藏品数据（代理）
   */
  figureData() {
    return this.figure
  },

  /**
   * 抽屉标题
   */
  drawerTitle() {
    return DRAWER_TITLE
  },

  /**
   * 关闭按钮文本
   */
  closeButtonText() {
    return CLOSE_BUTTON_TEXT
  },

  /**
   * 取消按钮文本
   */
  cancelButtonText() {
    return CANCEL_BUTTON_TEXT
  },

  /**
   * 确认按钮文本（根据提交状态动态变化）
   */
  confirmButtonText() {
    return this.submitting ? SUBMITTING_BUTTON_TEXT : CONFIRM_BUTTON_TEXT
  },

  /**
   * 出柜说明区块标题
   */
  infoBlockTitle() {
    return INFO_BLOCK_TITLE
  },

  /**
   * 出柜说明字段标签
   */
  infoLabels() {
    return INFO_LABELS
  },

  /**
   * 出柜说明字段值
   */
  infoValues() {
    return INFO_VALUES
  },

  /**
   * 选项区域标题
   */
  optionSectionTitle() {
    return OPTION_SECTION_TITLE
  },

  /**
   * 移出选项标签
   */
  outOptionLabel() {
    return OUT_OPTIONS.default.label
  },

  /**
   * 移出选项描述（动态填充收藏柜名称）
   */
  outOptionDesc() {
    return formatOutOptionDesc(this.cabinetName)
  },

  /**
   * 警告提示内容
   */
  warningText() {
    return WARNING_TEXT
  },

  /**
   * 陪伴天数提示文本
   */
  holdingDaysHint() {
    const days = safeGet(this.figureData, 'holding_days', 0)
    return formatHoldingDaysHint(days)
  },

  /**
   * 抽屉尺寸
   */
  drawerSize() {
    return DRAWER_SIZE
  }
}

/**
 * 监听器
 */
export const watch = {
  /**
   * 监听 visible prop 变化
   * @param {boolean} val - 新的可见状态
   */
  visible(val) {
    this.drawerVisible = val
    if (val) {
      // 打开抽屉时重置状态
      this.resetState()
    }
  }
}

/**
 * 方法定义
 */
export const methods = {
  /**
   * 重置组件状态
   */
  resetState() {
    this.selectedOption = DEFAULT_SELECTED_OPTION
    this.submitting = false
  },

  /**
   * 处理关闭抽屉
   */
  handleClose() {
    this.drawerVisible = false
    this.$emit('close')
  },

  /**
   * 处理确认出柜
   * 验证参数并触发 confirm 事件
   */
  async handleConfirm() {
    if (this.submitting) return

    // 验证参数
    const params = {
      figureId: safeGet(this.figureData, 'id', null),
      cabinetKey: this.cabinetKey
    }

    if (!validateOutParams(params)) {
      console.error('出柜参数无效:', params)
      return
    }

    this.submitting = true
    try {
      this.$emit('confirm', params)
    } finally {
      // 注意：提交成功后由父组件关闭抽屉
      // 如果失败，保持 submitting 状态直到父组件处理完毕
    }
  },

  /**
   * 处理选项选择
   * @param {string} option - 选项值
   */
  handleSelectOption(option) {
    this.selectedOption = option
  }
}

/**
 * 组件选项合并
 * 用于 Vue 选项式 API
 */
export const componentOptions = {
  name,
  props,
  data,
  computed,
  watch,
  methods
}

export default componentOptions
