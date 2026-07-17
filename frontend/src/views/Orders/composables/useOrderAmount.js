/**
 * useOrderAmount - 订单金额逻辑
 *
 * 提供定金/尾款金额的步进调整函数与币种选项
 */
export function useOrderAmount() {
  const currencyOptions = [
    { value: 'CNY', label: '人民币' },
    { value: 'JPY', label: '日元' },
    { value: 'USD', label: '美元' },
    { value: 'EUR', label: '欧元' }
  ]

  /**
   * 步进调整金额
   * @param {Object} target - 目标对象（newOrder）
   * @param {string} field - 字段名
   * @param {number} delta - 增减量
   */
  function adjustAmount(target, field, delta) {
    const val = Number(target[field]) || 0
    target[field] = Math.max(0, val + delta)
  }

  return { currencyOptions, adjustAmount }
}
