/**
 * useFigureOut.js - 出柜登记业务逻辑组合式函数
 *
 * 功能说明：
 * - 管理出柜抽屉的显示状态
 * - 处理出柜确认提交
 * - 提供出柜相关的计算属性和方法
 *
 * 使用方式：
 * const { outDrawerVisible, selectedFigure, openOutDrawer, closeOutDrawer, handleOutConfirm } = useFigureOut(cabinetKey, cabinetName, cabinetIcon, fetchData)
 */

import { ref, computed } from 'vue'
import { removeFigureFromCabinet } from '../api/cabinetApi'

export default function useFigureOut(cabinetKey, cabinetName, cabinetIcon, fetchData) {
  // 出柜抽屉显示状态
  const outDrawerVisible = ref(false)

  // 当前选中的藏品
  const selectedFigure = ref(null)

  // 提交中状态
  const submitting = ref(false)

  // 当前收藏柜信息（计算属性）
  const currentCabinetKey = computed(() => cabinetKey.value || '')
  const currentCabinetName = computed(() => cabinetName.value || '')
  const currentCabinetIcon = computed(() => cabinetIcon.value || '📦')

  /**
   * 打开出柜登记抽屉
   * @param {Object} figure - 藏品数据
   */
  const openOutDrawer = (figure) => {
    selectedFigure.value = figure
    outDrawerVisible.value = true
  }

  /**
   * 关闭出柜登记抽屉
   */
  const closeOutDrawer = () => {
    outDrawerVisible.value = false
    selectedFigure.value = null
  }

  /**
   * 处理出柜确认
   * @param {Object} payload - 出柜参数 { figureId, cabinetKey }
   */
  const handleOutConfirm = async (payload) => {
    if (submitting.value) return

    submitting.value = true
    try {
      const result = await removeFigureFromCabinet(payload.figureId, payload.cabinetKey)

      if (result.success) {
        // 关闭抽屉
        closeOutDrawer()
        // 刷新数据
        if (typeof fetchData === 'function') {
          await fetchData()
        }
        return { success: true, message: result.message || '出柜成功' }
      } else {
        return { success: false, message: result.message || '出柜失败' }
      }
    } catch (error) {
      console.error('出柜登记失败:', error)
      return { success: false, message: error.message || '出柜登记失败，请稍后重试' }
    } finally {
      submitting.value = false
    }
  }

  return {
    // 状态
    outDrawerVisible,
    selectedFigure,
    submitting,

    // 计算属性
    currentCabinetKey,
    currentCabinetName,
    currentCabinetIcon,

    // 方法
    openOutDrawer,
    closeOutDrawer,
    handleOutConfirm
  }
}
