/**
 * useQuickActions - 快速操作业务逻辑组合式函数
 *
 * 功能说明：
 * - 管理快速操作相关的状态和行为
 * - 提供买入、卖出、补款、撤单四个快速操作的对话框控制
 * - 与 QuickActions.vue 组件配合使用
 *
 * 使用示例：
 * const {
 *   buyDialogVisible,
 *   sellDialogVisible,
 *   paymentDialogVisible,
 *   cancelDialogVisible,
 *   openBuyDialog,
 *   openSellDialog,
 *   openPaymentDialog,
 *   openCancelDialog,
 *   closeAllDialogs
 * } = useQuickActions()
 *
 * 维护提示：
 * - 所有对话框状态通过 ref 管理
 * - 提供打开和关闭方法供组件调用
 */

import { ref } from 'vue'

export function useQuickActions() {
  // 买入对话框可见性
  const buyDialogVisible = ref(false)
  // 卖出对话框可见性
  const sellDialogVisible = ref(false)
  // 补款对话框可见性
  const paymentDialogVisible = ref(false)
  // 撤单对话框可见性
  const cancelDialogVisible = ref(false)

  /**
   * 打开买入对话框
   */
  const openBuyDialog = () => {
    buyDialogVisible.value = true
  }

  /**
   * 关闭买入对话框
   */
  const closeBuyDialog = () => {
    buyDialogVisible.value = false
  }

  /**
   * 打开卖出对话框
   */
  const openSellDialog = () => {
    sellDialogVisible.value = true
  }

  /**
   * 关闭卖出对话框
   */
  const closeSellDialog = () => {
    sellDialogVisible.value = false
  }

  /**
   * 打开补款对话框
   */
  const openPaymentDialog = () => {
    paymentDialogVisible.value = true
  }

  /**
   * 关闭补款对话框
   */
  const closePaymentDialog = () => {
    paymentDialogVisible.value = false
  }

  /**
   * 打开撤单对话框
   */
  const openCancelDialog = () => {
    cancelDialogVisible.value = true
  }

  /**
   * 关闭撤单对话框
   */
  const closeCancelDialog = () => {
    cancelDialogVisible.value = false
  }

  /**
   * 关闭所有对话框
   */
  const closeAllDialogs = () => {
    buyDialogVisible.value = false
    sellDialogVisible.value = false
    paymentDialogVisible.value = false
    cancelDialogVisible.value = false
  }

  return {
    // 状态
    buyDialogVisible,
    sellDialogVisible,
    paymentDialogVisible,
    cancelDialogVisible,
    // 方法
    openBuyDialog,
    closeBuyDialog,
    openSellDialog,
    closeSellDialog,
    openPaymentDialog,
    closePaymentDialog,
    openCancelDialog,
    closeCancelDialog,
    closeAllDialogs
  }
}
