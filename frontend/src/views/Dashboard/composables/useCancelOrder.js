/**
 * useCancelOrder - 撤单业务逻辑组合式函数
 *
 * 功能说明：
 * - 管理撤单相关的状态和行为
 * - 提供两步撤单流程：选择订单 -> 确认取消
 * - 与 CancelOrderListDialog 和 CancelOrderConfirmDialog 组件配合使用
 *
 * 使用示例：
 * const {
 *   cancelOrderListVisible,
 *   cancelOrderConfirmVisible,
 *   selectedCancelOrder,
 *   openCancelOrderList,
 *   selectCancelOrder,
 *   closeCancelOrderConfirm
 * } = useCancelOrder({
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

export function useCancelOrder(options = {}) {
  // 撤单订单列表弹窗可见性
  const cancelOrderListVisible = ref(false)
  // 撤单确认弹窗可见性
  const cancelOrderConfirmVisible = ref(false)
  // 当前选中的撤单订单
  const selectedCancelOrder = ref(null)

  /**
   * 打开撤单订单列表弹窗
   */
  const openCancelOrderList = () => {
    cancelOrderListVisible.value = true
  }

  /**
   * 关闭撤单订单列表弹窗
   */
  const closeCancelOrderList = () => {
    cancelOrderListVisible.value = false
  }

  /**
   * 打开撤单确认弹窗
   */
  const openCancelOrderConfirm = () => {
    cancelOrderConfirmVisible.value = true
  }

  /**
   * 关闭撤单确认弹窗
   */
  const closeCancelOrderConfirm = () => {
    cancelOrderConfirmVisible.value = false
    selectedCancelOrder.value = null
  }

  /**
   * 选择撤单订单
   * @param {Object} order - 选中的订单
   */
  const selectCancelOrder = (order) => {
    selectedCancelOrder.value = order
    cancelOrderListVisible.value = false
    cancelOrderConfirmVisible.value = true
  }

  /**
   * 处理取消成功
   */
  const handleCancelSuccess = () => {
    cancelOrderConfirmVisible.value = false
    selectedCancelOrder.value = null
    ElMessage.success('订单取消成功')
    // 调用外部传入的成功回调
    if (options.onSuccess) {
      options.onSuccess()
    }
  }

  return {
    // 状态
    cancelOrderListVisible,
    cancelOrderConfirmVisible,
    selectedCancelOrder,
    // 方法
    openCancelOrderList,
    closeCancelOrderList,
    openCancelOrderConfirm,
    closeCancelOrderConfirm,
    selectCancelOrder,
    handleCancelSuccess
  }
}
