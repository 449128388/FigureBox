/**
 * usePayBalance - 补款业务逻辑组合式函数
 *
 * 功能说明：
 * - 管理补款相关的状态和行为
 * - 提供两步补款流程：选择订单 -> 确认支付
 * - 与 PayBalanceOrderListDialog 和 PayBalanceConfirmDrawer 组件配合使用
 *
 * 使用示例：
 * const {
 *   payBalanceOrderListVisible,
 *   payBalanceConfirmVisible,
 *   selectedPayBalanceOrder,
 *   openPayBalanceOrderList,
 *   selectPayBalanceOrder,
 *   closePayBalanceConfirm
 * } = usePayBalance({
 *   onSuccess: () => {
 *     // 刷新数据
 *   }
 * })
 *
 * 维护提示：
 * - 所有对话框状态通过 ref 管理
 * - 提供打开和关闭方法供组件调用
 * - 采用两步弹窗设计
 */

import { ref } from 'vue'
import { ElMessage } from 'element-plus'

export function usePayBalance(options = {}) {
  // 补款订单列表弹窗可见性
  const payBalanceOrderListVisible = ref(false)
  // 补款确认抽屉可见性
  const payBalanceConfirmVisible = ref(false)
  // 当前选中的补款订单
  const selectedPayBalanceOrder = ref(null)

  /**
   * 打开补款订单列表弹窗
   */
  const openPayBalanceOrderList = () => {
    payBalanceOrderListVisible.value = true
  }

  /**
   * 关闭补款订单列表弹窗
   */
  const closePayBalanceOrderList = () => {
    payBalanceOrderListVisible.value = false
  }

  /**
   * 打开补款确认抽屉
   */
  const openPayBalanceConfirm = () => {
    payBalanceConfirmVisible.value = true
  }

  /**
   * 关闭补款确认抽屉
   */
  const closePayBalanceConfirm = () => {
    payBalanceConfirmVisible.value = false
    selectedPayBalanceOrder.value = null
  }

  /**
   * 选择补款订单
   * @param {Object} order - 选中的订单
   */
  const selectPayBalanceOrder = (order) => {
    selectedPayBalanceOrder.value = order
    payBalanceOrderListVisible.value = false
    payBalanceConfirmVisible.value = true
  }

  /**
   * 处理支付成功
   */
  const handlePayBalanceSuccess = () => {
    payBalanceConfirmVisible.value = false
    selectedPayBalanceOrder.value = null
    // 调用外部传入的成功回调
    if (options.onSuccess) {
      options.onSuccess()
    }
  }

  return {
    // 状态
    payBalanceOrderListVisible,
    payBalanceConfirmVisible,
    selectedPayBalanceOrder,
    // 方法
    openPayBalanceOrderList,
    closePayBalanceOrderList,
    openPayBalanceConfirm,
    closePayBalanceConfirm,
    selectPayBalanceOrder,
    handlePayBalanceSuccess
  }
}
