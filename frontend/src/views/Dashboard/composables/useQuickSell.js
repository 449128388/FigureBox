/**
 * 快速卖出 composable
 * 提供快速卖出相关的业务逻辑，与UI层分离
 */
import { ref, computed } from 'vue'
import axios from '../../../axios'
import { ElMessage } from 'element-plus'

export function useQuickSell() {
  // 状态
  const dialogVisible = ref(false)
  const loading = ref(false)
  const currentFigure = ref(null)

  // 卖出表单数据
  const sellQuantity = ref(1)    // 卖出数量
  const sellPrice = ref(0)       // 卖出价格

  // 计算属性 - 弹窗标题
  const dialogTitle = computed(() => {
    if (!currentFigure.value) return '卖出'
    return `卖出${currentFigure.value.figure_name || ''}`
  })

  // 计算属性 - 卖出预览
  const sellPreview = computed(() => {
    if (!currentFigure.value || !sellQuantity.value || !sellPrice.value) {
      return null
    }

    const costPrice = currentFigure.value.cost_price || 0
    const currentPrice = currentFigure.value.current_price || 0
    const quantity = sellQuantity.value
    const price = sellPrice.value

    // 预计收入 = 卖出价格 × 卖出数量
    const totalRevenue = price * quantity

    // 预计盈亏 = (卖出价 - 成本价) × 卖出数量
    const profit = (price - costPrice) * quantity

    // 盈亏百分比 = 盈亏 / (成本价 × 卖出数量) × 100%
    const totalCost = costPrice * quantity
    const profitPercentage = totalCost > 0 ? (profit / totalCost) * 100 : 0

    return {
      totalRevenue,
      profit,
      profitPercentage
    }
  })

  /**
   * 打开卖出对话框
   * @param {Object} figure - 手办信息
   */
  const openDialog = (figure) => {
    if (!figure) return

    currentFigure.value = figure
    dialogVisible.value = true

    // 初始化默认值
    sellQuantity.value = figure.stock || 1
    // 默认卖出价格为当前市场价
    sellPrice.value = figure.current_price || 0
  }

  /**
   * 关闭对话框
   */
  const closeDialog = () => {
    dialogVisible.value = false
    currentFigure.value = null
    sellQuantity.value = 1
    sellPrice.value = 0
  }

  /**
   * 使用当前市价
   */
  const useCurrentMarketPrice = () => {
    if (currentFigure.value && currentFigure.value.current_price) {
      sellPrice.value = currentFigure.value.current_price
    }
  }

  /**
   * 确认卖出
   */
  const confirmSell = async () => {
    if (!currentFigure.value || !sellQuantity.value || !sellPrice.value) {
      ElMessage.warning('请填写完整的卖出信息')
      return null
    }

    if (sellQuantity.value <= 0) {
      ElMessage.warning('卖出数量必须大于0')
      return null
    }

    if (sellPrice.value <= 0) {
      ElMessage.warning('卖出价格必须大于0')
      return null
    }

    const maxStock = currentFigure.value.stock || 0
    if (sellQuantity.value > maxStock) {
      ElMessage.warning(`卖出数量不能超过当前持仓数量(${maxStock}体)`)
      return null
    }

    loading.value = true

    try {
      // 调用快速卖出API
      const response = await axios.post('/sold-orders/quick-sell', {
        figure_id: currentFigure.value.figure_id,
        figure_name: currentFigure.value.figure_name,
        quantity: Number(sellQuantity.value),
        sell_price: Number(sellPrice.value),
        cost_price: currentFigure.value.cost_price || 0
      })

      ElMessage.success('卖出成功')

      // 先返回结果，再关闭对话框
      const result = response
      closeDialog()

      // 返回结果供外部处理
      return result
    } catch (error) {
      ElMessage.error(error.response?.data?.detail || '卖出失败')
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
      minimumFractionDigits: 2,
      maximumFractionDigits: 2
    })
  }

  /**
   * 格式化数字
   */
  const formatNumber = (value) => {
    if (!value && value !== 0) return '0'
    return Number(value).toLocaleString('zh-CN')
  }

  return {
    // 状态
    dialogVisible,
    dialogTitle,
    loading,
    currentFigure,
    sellQuantity,
    sellPrice,

    // 计算属性
    sellPreview,

    // 方法
    openDialog,
    closeDialog,
    confirmSell,
    useCurrentMarketPrice,
    formatMoney,
    formatNumber
  }
}
