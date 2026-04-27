/**
 * 补仓 composable
 * 提供补仓相关的业务逻辑，与UI层分离
 */
import { ref, computed } from 'vue'
import axios from '../../../axios'
import { ElMessage } from 'element-plus'

export function useAddPosition() {
  // 状态
  const dialogVisible = ref(false)
  const loading = ref(false)
  const currentFigure = ref(null)

  // 补仓表单数据
  const addPositionForm = ref({
    quantity: 1,      // 补仓数量
    price: 0          // 补仓价格
  })

  // 计算属性 - 补仓后预览
  const positionPreview = computed(() => {
    if (!currentFigure.value || !addPositionForm.value.price) return null

    const currentStock = currentFigure.value.stock || 1
    const currentCostPrice = currentFigure.value.cost_price || 0
    const addQuantity = addPositionForm.value.quantity || 0
    const addPrice = addPositionForm.value.price || 0

    // 计算新的库存
    const newStock = currentStock + addQuantity

    // 计算加权平均成本
    // 加权平均成本 = (原持仓成本总额 + 新买入成本总额) / 总数量
    const currentTotalCost = currentCostPrice * currentStock
    const addTotalCost = addPrice * addQuantity
    const newCostPrice = newStock > 0 ? (currentTotalCost + addTotalCost) / newStock : 0

    return {
      currentStock,
      currentCostPrice,
      addQuantity,
      addPrice,
      newStock,
      newCostPrice,
      currentTotalCost,
      addTotalCost
    }
  })

  /**
   * 打开补仓对话框
   * @param {Object} figure - 手办信息
   */
  const openDialog = (figure) => {
    if (!figure) return

    currentFigure.value = figure
    addPositionForm.value = {
      quantity: 1,
      price: figure.current_price || figure.cost_price || 0
    }
    dialogVisible.value = true
  }

  /**
   * 关闭对话框
   */
  const closeDialog = () => {
    dialogVisible.value = false
    currentFigure.value = null
    addPositionForm.value = {
      quantity: 1,
      price: 0
    }
  }

  /**
   * 确认补仓
   */
  const confirmAddPosition = async () => {
    if (!currentFigure.value || !addPositionForm.value.quantity || !addPositionForm.value.price) {
      ElMessage.warning('请填写完整的补仓信息')
      return null
    }

    loading.value = true

    try {
      const response = await axios.post(`/assets/figures/${currentFigure.value.figure_id}/add-position`, {
        quantity: Number(addPositionForm.value.quantity),
        price: Number(addPositionForm.value.price)
      })

      ElMessage.success('补仓成功')

      // 返回结果
      const result = response
      closeDialog()

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
    addPositionForm,

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
