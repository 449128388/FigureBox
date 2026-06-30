/**
 * 价格更新 composable
 * 提供修改市场价相关的业务逻辑，与UI层分离
 * 汇率通过统一 composable useExchangeRates 获取
 */
import { ref, computed } from 'vue'
import axios from '../../../axios'
import { ElMessage } from 'element-plus'
import { exchangeUtils } from '../../../composables/useExchangeRates'

// 兜底默认汇率（API 不可用时使用）
const FALLBACK_RATES = { CNY: 1.0, JPY: 1 / 23, USD: 7.0, EUR: 8.0 }

// 币种选项
const CURRENCY_OPTIONS = [
  { value: 'CNY', label: '人民币' },
  { value: 'JPY', label: '日元' },
  { value: 'USD', label: '美元' },
  { value: 'EUR', label: '欧元' }
]

export function usePriceUpdate() {
  const dialogVisible = ref(false)
  const loading = ref(false)
  const currentFigure = ref(null)
  const priceInfo = ref(null)
  const newPrice = ref(0)
  const selectedCurrency = ref('CNY')
  const rates = ref({ ...FALLBACK_RATES })

  // 影响预览（同步计算，使用缓存的汇率）
  const impactPreview = computed(() => {
    if (!priceInfo.value || !newPrice.value) return null
    const oldPrice = priceInfo.value.current_price
    const costPrice = priceInfo.value.cost_price || 0
    const quantity = priceInfo.value.quantity
    const oldTotalAssets = priceInfo.value.total_assets
    const exchangeRate = rates.value[selectedCurrency.value] ?? FALLBACK_RATES[selectedCurrency.value] ?? 1.0
    const newPriceInCNY = newPrice.value * exchangeRate
    const priceDiff = (newPriceInCNY - oldPrice) * quantity
    const newTotalAssets = oldTotalAssets + priceDiff
    let newProfitPercentage = 0
    if (costPrice > 0) newProfitPercentage = ((newPriceInCNY - costPrice) / costPrice) * 100
    let newTotalProfitPercentage = priceInfo.value.total_profit_percentage || 0
    if (oldTotalAssets > 0) newTotalProfitPercentage = newTotalProfitPercentage + (priceDiff / oldTotalAssets * 100)
    const displayExchangeRate = selectedCurrency.value === 'JPY' ? exchangeRate.toFixed(4) : exchangeRate
    return {
      oldTotalAssets, newTotalAssets,
      oldProfitPercentage: priceInfo.value.profit_percentage, newProfitPercentage,
      oldTotalProfitPercentage: priceInfo.value.total_profit_percentage || 0, newTotalProfitPercentage,
      priceDiff, newPriceInCNY, exchangeRate: displayExchangeRate
    }
  })

  const lastUpdatedText = computed(() => {
    if (!priceInfo.value?.last_updated) return '未知'
    const lastUpdated = new Date(priceInfo.value.last_updated)
    const now = new Date()
    const diffDays = Math.floor((now - lastUpdated) / (1000 * 60 * 60 * 24))
    if (diffDays === 0) return '今天'
    if (diffDays === 1) return '昨天'
    return `${diffDays}天前`
  })

  const openDialog = async (figure) => {
    if (!figure) return
    currentFigure.value = figure
    dialogVisible.value = true
    loading.value = true
    try {
      const response = await axios.get(`/assets/figures/${figure.figure_id}/price-info`)
      priceInfo.value = response
      newPrice.value = response.current_price
      rates.value = await exchangeUtils.fetchRates()
    } catch (error) {
      ElMessage.error('获取价格信息失败')
      dialogVisible.value = false
    } finally { loading.value = false }
  }

  const closeDialog = () => {
    dialogVisible.value = false
    currentFigure.value = null
    priceInfo.value = null
    newPrice.value = 0
    selectedCurrency.value = 'CNY'
    rates.value = { ...FALLBACK_RATES }
  }

  const useXianyuPrice = () => { ElMessage.info('闲鱼参考价格功能开发中') }
  const useAveragePrice = () => {
    if (priceInfo.value?.cost_price) {
      newPrice.value = priceInfo.value.cost_price
      ElMessage.success('已填充成本价')
    } else {
      ElMessage.info('暂无成本数据')
    }
  }

  const confirmUpdate = async () => {
    if (!currentFigure.value || !newPrice.value) return null
    loading.value = true
    try {
      const exchangeRate = rates.value[selectedCurrency.value] ?? FALLBACK_RATES[selectedCurrency.value] ?? 1.0
      const newPriceInCNY = Number(newPrice.value) * exchangeRate
      const response = await axios.post(`/assets/figures/${currentFigure.value.figure_id}/update-price`, {
        new_price: newPriceInCNY, currency: selectedCurrency.value
      })
      ElMessage.success('价格修改成功')
      const result = response
      closeDialog()
      return result
    } catch (error) {
      ElMessage.error(error.response?.data?.detail || '价格修改失败')
      return null
    } finally { loading.value = false }
  }

  const formatMoney = (value) => {
    if (!value && value !== 0) return '¥0'
    return '¥' + Number(value).toLocaleString('zh-CN', { minimumFractionDigits: 0, maximumFractionDigits: 0 })
  }
  const formatPercentage = (value) => {
    if (!value && value !== 0) return '0%'
    return (value > 0 ? '+' : '') + Number(value).toFixed(1) + '%'
  }

  return {
    dialogVisible, loading, currentFigure, priceInfo, newPrice, selectedCurrency,
    CURRENCY_OPTIONS, impactPreview, lastUpdatedText,
    openDialog, closeDialog, useXianyuPrice, useAveragePrice, confirmUpdate, formatMoney, formatPercentage
  }
}
