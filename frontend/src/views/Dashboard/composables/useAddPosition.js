/**
 * 补仓 composable
 * 提供补仓相关的业务逻辑，与UI层分离
 */
import { ref, computed } from 'vue'
import axios from '../../../axios'
import { ElMessage } from 'element-plus'

// 汇率配置：相对人民币的汇率
const EXCHANGE_RATES = {
  'CNY': 1.0,    // 人民币
  'JPY': 1 / 23, // 日元：1人民币 = 23日元
  'USD': 7.0,    // 美元：1美元 = 7人民币
  'EUR': 8.0     // 欧元：1欧元 = 8人民币
}

/**
 * 将指定币种金额转换为人民币
 * @param {number} amount - 金额
 * @param {string} currency - 币种代码
 * @returns {number} 人民币金额
 */
const convertToCNY = (amount, currency) => {
  const rate = EXCHANGE_RATES[currency] || 1.0
  return amount * rate
}

export function useAddPosition() {
  // 状态
  const dialogVisible = ref(false)
  const loading = ref(false)
  const currentFigure = ref(null)

  // 补仓表单数据
  const addQuantity = ref(1)      // 补仓数量
  const addPrice = ref(0)         // 补仓价格
  const addCurrency = ref('CNY')  // 补仓币种，默认为人民币

  // 计算属性 - 补仓预览
  const positionPreview = computed(() => {
    if (!currentFigure.value || !addQuantity.value || !addPrice.value) {
      return null
    }

    const currentStock = currentFigure.value.stock || 1
    const currentCostPrice = currentFigure.value.cost_price || 0

    // 将补仓价格转换为人民币
    const addPriceInCNY = convertToCNY(addPrice.value, addCurrency.value)

    // 计算新的加权平均成本价
    // 新成本价 = (原成本 * 原数量 + 补仓价格(人民币) * 补仓数量) / (原数量 + 补仓数量)
    const totalCost = (currentCostPrice * currentStock) + (addPriceInCNY * addQuantity.value)
    const totalQuantity = currentStock + addQuantity.value
    const newCostPrice = totalQuantity > 0 ? totalCost / totalQuantity : 0

    // 新的库存数量
    const newStock = totalQuantity

    return {
      currentStock,
      currentCostPrice,
      addQuantity: addQuantity.value,
      addPrice: addPrice.value,
      addCurrency: addCurrency.value,
      addPriceInCNY,
      newCostPrice,
      newStock,
      totalCost
    }
  })

  /**
   * 打开补仓对话框
   * @param {Object} figure - 手办信息
   */
  const openDialog = (figure) => {
    if (!figure) return

    currentFigure.value = figure
    dialogVisible.value = true

    // 初始化默认值
    addQuantity.value = 1
    // 默认补仓价格为当前市场价或成本价
    addPrice.value = figure.current_price || figure.cost_price || 0
  }

  /**
   * 关闭对话框
   */
  const closeDialog = () => {
    dialogVisible.value = false
    currentFigure.value = null
    addQuantity.value = 1
    addPrice.value = 0
    addCurrency.value = 'CNY'
  }

  /**
   * 确认补仓
   */
  const confirmAddPosition = async () => {
    if (!currentFigure.value || !addQuantity.value || !addPrice.value) {
      ElMessage.warning('请填写完整的补仓信息')
      return null
    }

    if (addQuantity.value <= 0) {
      ElMessage.warning('补仓数量必须大于0')
      return null
    }

    if (addPrice.value <= 0) {
      ElMessage.warning('补仓价格必须大于0')
      return null
    }

    loading.value = true

    try {
      // 将补仓价格转换为人民币后发送给后端
      const priceInCNY = convertToCNY(Number(addPrice.value), addCurrency.value)

      const response = await axios.post(`/assets/figures/${currentFigure.value.figure_id}/add-position`, {
        quantity: Number(addQuantity.value),
        price: priceInCNY,
        currency: addCurrency.value
      })

      ElMessage.success('补仓成功')

      // 先返回结果，再关闭对话框
      const result = response
      closeDialog()

      // 返回结果供外部处理
      return result
    } catch (error) {
      ElMessage.error(error.response?.data?.detail || '补仓失败')
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
    loading,
    currentFigure,
    addQuantity,
    addPrice,
    addCurrency,

    // 计算属性
    positionPreview,

    // 方法
    openDialog,
    closeDialog,
    confirmAddPosition,
    formatMoney,
    formatNumber
  }
}
