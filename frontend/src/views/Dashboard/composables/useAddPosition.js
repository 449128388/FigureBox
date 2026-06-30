/**
 * 补仓 composable
 * 提供补仓相关的业务逻辑，与UI层分离
 * 汇率通过统一 composable useExchangeRates 获取
 */
import { ref, computed } from 'vue'
import axios from '../../../axios'
import { ElMessage } from 'element-plus'
import { exchangeUtils } from '../../../composables/useExchangeRates'

// 兜底默认汇率（API 不可用时使用）
const FALLBACK_RATES = {
  CNY: 1.0,
  JPY: 1 / 23,
  USD: 7.0,
  EUR: 8.0
}

export function useAddPosition() {
  const dialogVisible = ref(false)
  const loading = ref(false)
  const currentFigure = ref(null)
  const rates = ref({ ...FALLBACK_RATES })

  // 补仓表单数据
  const addQuantity = ref(1)         // 补仓数量
  const addPrice = ref(0)            // 补仓价格
  const addCurrency = ref('CNY')     // 补仓币种，默认为人民币

  // 补仓预览（同步计算，使用缓存的汇率）
  const positionPreview = computed(() => {
    if (!currentFigure.value || !addQuantity.value || !addPrice.value) return null
    const currentStock = currentFigure.value.stock || 1
    const currentCostPrice = currentFigure.value.cost_price || 0
    const r = rates.value[addCurrency.value] ?? FALLBACK_RATES[addCurrency.value] ?? 1.0
    const addPriceInCNY = addPrice.value * r
    const totalCost = (currentCostPrice * currentStock) + (addPriceInCNY * addQuantity.value)
    const totalQuantity = currentStock + addQuantity.value
    const newCostPrice = totalQuantity > 0 ? totalCost / totalQuantity : 0
    return {
      currentStock, currentCostPrice,
      addQuantity: addQuantity.value, addPrice: addPrice.value,
      addCurrency: addCurrency.value, addPriceInCNY, newCostPrice,
      newStock: totalQuantity, totalCost
    }
  })

  const openDialog = async (figure) => {
    if (!figure) return
    currentFigure.value = figure
    dialogVisible.value = true
    addQuantity.value = 1
    addPrice.value = figure.current_price || figure.cost_price || 0
    try { rates.value = await exchangeUtils.fetchRates() } catch { rates.value = { ...FALLBACK_RATES } }
  }

  const closeDialog = () => {
    dialogVisible.value = false
    currentFigure.value = null
    addQuantity.value = 1
    addPrice.value = 0
    addCurrency.value = 'CNY'
    rates.value = { ...FALLBACK_RATES }
  }

  const confirmAddPosition = async () => {
    if (!currentFigure.value || !addQuantity.value || !addPrice.value) {
      ElMessage.warning('请填写完整的补仓信息')
      return null
    }
    if (addQuantity.value <= 0) { ElMessage.warning('补仓数量必须大于0'); return null }
    if (addPrice.value <= 0) { ElMessage.warning('补仓价格必须大于0'); return null }
    loading.value = true
    try {
      const r = rates.value[addCurrency.value] ?? FALLBACK_RATES[addCurrency.value] ?? 1.0
      const priceInCNY = Number(addPrice.value) * r
      const response = await axios.post(`/assets/figures/${currentFigure.value.figure_id}/add-position`, {
        quantity: Number(addQuantity.value), price: priceInCNY, currency: addCurrency.value
      })
      ElMessage.success('补仓成功')
      const result = response
      closeDialog()
      return result
    } catch (error) {
      ElMessage.error(error.response?.data?.detail || '补仓失败')
      return null
    } finally { loading.value = false }
  }

  const formatMoney = (value) => {
    if (!value && value !== 0) return '¥0'
    return '¥' + Number(value).toLocaleString('zh-CN', { minimumFractionDigits: 2, maximumFractionDigits: 2 })
  }
  const formatNumber = (value) => {
    if (!value && value !== 0) return '0'
    return Number(value).toLocaleString('zh-CN')
  }

  return {
    dialogVisible, loading, currentFigure, addQuantity, addPrice, addCurrency,
    positionPreview, openDialog, closeDialog, confirmAddPosition, formatMoney, formatNumber
  }
}
