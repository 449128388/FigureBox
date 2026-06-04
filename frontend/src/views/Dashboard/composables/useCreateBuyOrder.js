/**
 * useCreateBuyOrder - 创建买入订单业务逻辑组合式函数
 *
 * 功能说明：
 * - 管理创建买入订单抽屉的显示/隐藏状态
 * - 提供打开抽屉的方法
 * - 处理订单创建成功后的回调
 *
 * 使用示例：
 * const {
 *   drawerVisible,
 *   openDrawer,
 *   closeDrawer,
 *   handleSuccess
 * } = useCreateBuyOrder({
 *   onSuccess: () => refreshOrderList()
 * })
 *
 * 维护提示：
 * - 抽屉状态通过 ref 管理
 * - 成功回调可用于刷新订单列表
 */

import { ref } from 'vue'

/**
 * @param {Object} options - 配置选项
 * @param {Function} options.onSuccess - 订单创建成功后的回调函数
 * @returns {Object} 抽屉状态和控制方法
 */
export function useCreateBuyOrder(options = {}) {
  // 抽屉可见性状态
  const drawerVisible = ref(false)

  /**
   * 打开创建订单抽屉
   */
  const openDrawer = () => {
    drawerVisible.value = true
  }

  /**
   * 关闭创建订单抽屉
   */
  const closeDrawer = () => {
    drawerVisible.value = false
  }

  /**
   * 处理订单创建成功
   * - 关闭抽屉
   *  - 执行成功回调
   */
  const handleSuccess = () => {
    closeDrawer()
    if (typeof options.onSuccess === 'function') {
      options.onSuccess()
    }
  }

  return {
    // 状态
    drawerVisible,
    // 方法
    openDrawer,
    closeDrawer,
    handleSuccess
  }
}
