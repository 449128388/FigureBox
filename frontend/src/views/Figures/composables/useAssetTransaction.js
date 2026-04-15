/**
 * useAssetTransaction.js - 资产交易业务逻辑 Composable
 *
 * 功能说明：
 * - 提供资产交易相关的业务逻辑处理
 * - 包括获取交易记录、创建买入/卖出交易、计算平均成本、盈亏分析等
 * - 支持股票式补仓功能
 *
 * 使用场景：
 * - 手办详情页显示交易记录
 * - 补仓操作
 * - 卖出操作
 * - 资产分析
 *
 * 依赖：
 * - axios: HTTP 请求
 */

import { ref, computed } from 'vue'
import axios from '../../../axios'

export function useAssetTransaction() {
  // 状态
  const transactions = ref([])
  const averageCost = ref(null)
  const profitAnalysis = ref(null)
  const loading = ref(false)
  const error = ref(null)

  // 计算属性
  const totalBuyQuantity = computed(() => {
    return transactions.value
      .filter(t => t.transaction_type === 'buy')
      .reduce((sum, t) => sum + t.quantity, 0)
  })

  const totalSellQuantity = computed(() => {
    return transactions.value
      .filter(t => t.transaction_type === 'sell')
      .reduce((sum, t) => sum + t.quantity, 0)
  })

  const currentHolding = computed(() => {
    return totalBuyQuantity.value - totalSellQuantity.value
  })

  const totalInvestment = computed(() => {
    return transactions.value
      .filter(t => t.transaction_type === 'buy')
      .reduce((sum, t) => sum + t.total_amount, 0)
  })

  const totalRevenue = computed(() => {
    return transactions.value
      .filter(t => t.transaction_type === 'sell')
      .reduce((sum, t) => sum + t.total_amount, 0)
  })

  /**
   * 获取手办的交易记录
   * @param {number} figureId - 手办ID
   */
  const fetchTransactions = async (figureId) => {
    loading.value = true
    error.value = null
    try {
      const response = await axios.get(`/api/asset-transactions/figure/${figureId}`)
      transactions.value = response.data
      return response.data
    } catch (err) {
      error.value = err.response?.data?.detail || '获取交易记录失败'
      throw err
    } finally {
      loading.value = false
    }
  }

  /**
   * 获取当前用户的所有交易记录
   * @param {Object} params - 查询参数
   */
  const fetchAllTransactions = async (params = {}) => {
    loading.value = true
    error.value = null
    try {
      const response = await axios.get('/api/asset-transactions/my', { params })
      transactions.value = response.data
      return response.data
    } catch (err) {
      error.value = err.response?.data?.detail || '获取交易记录失败'
      throw err
    } finally {
      loading.value = false
    }
  }

  /**
   * 创建买入交易（补仓）
   * @param {Object} data - 交易数据
   */
  const createBuyTransaction = async (data) => {
    loading.value = true
    error.value = null
    try {
      const response = await axios.post('/api/asset-transactions/buy', {
        ...data,
        transaction_type: 'buy'
      })
      // 添加到本地列表
      transactions.value.unshift(response.data)
      return response.data
    } catch (err) {
      error.value = err.response?.data?.detail || '创建买入交易失败'
      throw err
    } finally {
      loading.value = false
    }
  }

  /**
   * 创建卖出交易
   * @param {Object} data - 交易数据
   */
  const createSellTransaction = async (data) => {
    loading.value = true
    error.value = null
    try {
      const response = await axios.post('/api/asset-transactions/sell', data)
      // 添加到本地列表
      transactions.value.unshift(response.data)
      return response.data
    } catch (err) {
      error.value = err.response?.data?.detail || '创建卖出交易失败'
      throw err
    } finally {
      loading.value = false
    }
  }

  /**
   * 获取平均成本
   * @param {number} figureId - 手办ID
   */
  const fetchAverageCost = async (figureId) => {
    loading.value = true
    error.value = null
    try {
      const response = await axios.get(`/api/asset-transactions/figure/${figureId}/average-cost`)
      averageCost.value = response.data
      return response.data
    } catch (err) {
      error.value = err.response?.data?.detail || '获取平均成本失败'
      throw err
    } finally {
      loading.value = false
    }
  }

  /**
   * 获取盈亏分析
   * @param {number} figureId - 手办ID
   * @param {number} currentMarketPrice - 当前市场价格
   */
  const fetchProfitAnalysis = async (figureId, currentMarketPrice = null) => {
    loading.value = true
    error.value = null
    try {
      const params = currentMarketPrice ? { current_market_price: currentMarketPrice } : {}
      const response = await axios.get(`/api/asset-transactions/figure/${figureId}/profit`, { params })
      profitAnalysis.value = response.data
      return response.data
    } catch (err) {
      error.value = err.response?.data?.detail || '获取盈亏分析失败'
      throw err
    } finally {
      loading.value = false
    }
  }

  /**
   * 删除交易记录
   * @param {number} transactionId - 交易记录ID
   */
  const deleteTransaction = async (transactionId) => {
    loading.value = true
    error.value = null
    try {
      await axios.delete(`/api/asset-transactions/${transactionId}`)
      // 从本地列表移除
      transactions.value = transactions.value.filter(t => t.id !== transactionId)
      return true
    } catch (err) {
      error.value = err.response?.data?.detail || '删除交易记录失败'
      throw err
    } finally {
      loading.value = false
    }
  }

  /**
   * 重置状态
   */
  const resetState = () => {
    transactions.value = []
    averageCost.value = null
    profitAnalysis.value = null
    loading.value = false
    error.value = null
  }

  return {
    // 状态
    transactions,
    averageCost,
    profitAnalysis,
    loading,
    error,
    // 计算属性
    totalBuyQuantity,
    totalSellQuantity,
    currentHolding,
    totalInvestment,
    totalRevenue,
    // 方法
    fetchTransactions,
    fetchAllTransactions,
    createBuyTransaction,
    createSellTransaction,
    fetchAverageCost,
    fetchProfitAnalysis,
    deleteTransaction,
    resetState
  }
}
