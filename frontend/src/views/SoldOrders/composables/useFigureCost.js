/**
 * useFigureCost.js - 手办成本价获取 composable
 *
 * 功能说明：
 * - 提供获取手办实际剩余持仓成本价的功能
 * - 与持仓列表使用相同的计算逻辑
 * - 业务逻辑与UI层分离
 *
 * 维护提示：
 * - 成本价从后端 API /api/assets/figures/{figure_id}/cost 获取
 * - 计算逻辑基于 AssetTransaction 库存账
 */

import { ref } from 'vue'
import { ElMessage } from 'element-plus'
import axios from '../../../axios'

export function useFigureCost() {
  const loading = ref(false)
  const error = ref(null)

  /**
   * 获取手办实际剩余持仓成本价
   *
   * @param {number} figureId - 手办ID
   * @returns {Promise<Object|null>} 成本信息对象，包含 cost_price, stock, currency
   */
  const fetchFigureCost = async (figureId) => {
    if (!figureId) {
      return null
    }

    loading.value = true
    error.value = null

    try {
      const response = await axios.get(`/api/assets/figures/${figureId}/cost`)
      return response.data
    } catch (err) {
      error.value = err.response?.data?.detail || err.message || '获取成本价失败'
      console.error('获取手办成本价失败:', err)
      return null
    } finally {
      loading.value = false
    }
  }

  /**
   * 获取成本价并自动填充到订单对象
   *
   * @param {number} figureId - 手办ID
   * @param {Object} order - 订单对象
   * @returns {Promise<boolean>} 是否成功获取并填充
   */
  const fillOrderCostPrice = async (figureId, order) => {
    const costInfo = await fetchFigureCost(figureId)

    if (costInfo && costInfo.cost_price !== undefined) {
      order.cost_price = costInfo.cost_price
      order.cost_price_currency = costInfo.currency || 'CNY'
      return true
    } else {
      // 如果获取失败，显示错误信息
      if (error.value) {
        ElMessage.warning(error.value)
      }
      // 重置成本价
      order.cost_price = 0
      order.cost_price_currency = 'CNY'
      return false
    }
  }

  return {
    loading,
    error,
    fetchFigureCost,
    fillOrderCostPrice
  }
}
