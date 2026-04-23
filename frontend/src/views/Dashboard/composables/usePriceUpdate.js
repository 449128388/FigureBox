/**
 * 价格更新 composable
 * 提供修改市场价相关的业务逻辑，与UI层分离
 */
import { ref, computed } from 'vue'
import axios from '../../../axios'
import { ElMessage } from 'element-plus'

export function usePriceUpdate() {
  // 状态
  const dialogVisible = ref(false)
  const loading = ref(false)
  const currentFigure = ref(null)
  const priceInfo = ref(null)
  const newPrice = ref(0)

  // 计算属性 - 影响预览
  const impactPreview = computed(() => {
    if (!priceInfo.value || !newPrice.value) return null
    
    const oldPrice = priceInfo.value.current_price
    const costPrice = priceInfo.value.cost_price || 0
    const quantity = priceInfo.value.quantity
    const oldTotalAssets = priceInfo.value.total_assets
    
    // 计算价格差异
    const priceDiff = (newPrice.value - oldPrice) * quantity
    const newTotalAssets = oldTotalAssets + priceDiff
    
    // 计算单个手办盈亏比例变化（基于成本价，与持仓列表一致）
    const oldProfitPercentage = priceInfo.value.profit_percentage
    // 新的盈亏比例 = (新市场价 - 成本价) / 成本价 * 100%
    let newProfitPercentage = 0
    if (costPrice > 0) {
      newProfitPercentage = ((newPrice.value - costPrice) / costPrice) * 100
    }
    
    // 计算整体盈亏比例变化
    const oldTotalProfitPercentage = priceInfo.value.total_profit_percentage || 0
    // 整体盈亏比例 = (新总资产 - 总成本) / 总成本 * 100%
    // 简化计算：新整体盈亏比例 = 旧整体盈亏比例 + (价格差异 / 旧总资产 * 100%)
    let newTotalProfitPercentage = oldTotalProfitPercentage
    if (oldTotalAssets > 0) {
      newTotalProfitPercentage = oldTotalProfitPercentage + (priceDiff / oldTotalAssets * 100)
    }
    
    return {
      oldTotalAssets,
      newTotalAssets,
      oldProfitPercentage,
      newProfitPercentage,
      oldTotalProfitPercentage,
      newTotalProfitPercentage,
      priceDiff
    }
  })

  // 计算属性 - 格式化日期
  const lastUpdatedText = computed(() => {
    if (!priceInfo.value?.last_updated) return '未知'
    
    const lastUpdated = new Date(priceInfo.value.last_updated)
    const now = new Date()
    const diffDays = Math.floor((now - lastUpdated) / (1000 * 60 * 60 * 24))
    
    if (diffDays === 0) return '今天'
    if (diffDays === 1) return '昨天'
    return `${diffDays}天前`
  })

  /**
   * 打开修改市场价对话框
   * @param {Object} figure - 手办信息
   */
  const openDialog = async (figure) => {
    if (!figure) return
    
    currentFigure.value = figure
    dialogVisible.value = true
    loading.value = true
    
    try {
      const response = await axios.get(`/assets/figures/${figure.figure_id}/price-info`)
      priceInfo.value = response
      newPrice.value = response.current_price
    } catch (error) {
      ElMessage.error('获取价格信息失败')
      dialogVisible.value = false
    } finally {
      loading.value = false
    }
  }

  /**
   * 关闭对话框
   */
  const closeDialog = () => {
    dialogVisible.value = false
    currentFigure.value = null
    priceInfo.value = null
    newPrice.value = 0
  }

  /**
   * 使用闲鱼参考价格
   */
  const useXianyuPrice = () => {
    // TODO: 接入闲鱼价格API
    ElMessage.info('闲鱼参考价格功能开发中')
  }

  /**
   * 使用均价
   */
  const useAveragePrice = () => {
    // TODO: 计算历史均价
    ElMessage.info('均价功能开发中')
  }

  /**
   * 确认修改价格
   */
  const confirmUpdate = async () => {
    if (!currentFigure.value || !newPrice.value) return null
    
    loading.value = true
    
    try {
      const response = await axios.post(`/assets/figures/${currentFigure.value.figure_id}/update-price`, {
        new_price: Number(newPrice.value)
      })
      
      ElMessage.success('价格修改成功')
      
      // 先返回结果，再关闭对话框
      const result = response
      closeDialog()
      
      // 返回结果供外部处理
      return result
    } catch (error) {
      ElMessage.error(error.response?.data?.detail || '价格修改失败')
      return null
    } finally {
      loading.value = false
    }
  }

  /**
   * 格式化金额
   */
  const formatMoney = (value) => {
    if (!value && value !== 0) return '¥0'
    return '¥' + Number(value).toLocaleString('zh-CN', {
      minimumFractionDigits: 0,
      maximumFractionDigits: 0
    })
  }

  /**
   * 格式化百分比
   */
  const formatPercentage = (value) => {
    if (!value && value !== 0) return '0%'
    return (value > 0 ? '+' : '') + Number(value).toFixed(1) + '%'
  }

  return {
    // 状态
    dialogVisible,
    loading,
    currentFigure,
    priceInfo,
    newPrice,
    
    // 计算属性
    impactPreview,
    lastUpdatedText,
    
    // 方法
    openDialog,
    closeDialog,
    useXianyuPrice,
    useAveragePrice,
    confirmUpdate,
    formatMoney,
    formatPercentage
  }
}