import { ref, computed, watch } from 'vue'
import { useOrderStore, useUserStore, useFigureStore } from '../../../store'
import { ElMessage } from 'element-plus'
import { useBatchSelection } from './useBatchSelection'

export function useOrderManagement() {
  // 状态管理
  const orderStore = useOrderStore()
  const userStore = useUserStore()
  const figureStore = useFigureStore()

  // 【新增】批量选择功能
  const {
    selectedIds,
    isBatchMode,
    selectedCount,
    hasSelection,
    selectedIdsArray,
    setSelection,
    isSelected,
    selectAll,
    deselectAll,
    enterBatchMode,
    exitBatchMode,
    clearAll
  } = useBatchSelection()

  // 响应式数据
  const showAddForm = ref(false)
  const isEditing = ref(false)
  const currentEditOrderId = ref(null)
  const currentPage = ref(1)
  const pageSize = ref(10)
  const pageSizes = ref([10, 20, 30, 40, 50])
  const currentStatus = ref('未支付') // 当前筛选状态：all, 未支付, 已支付, 已取消；默认显示未支付
  const figureError = ref('')
  const dueDateError = ref('')
  
  // 【新增】搜索相关状态
  const searchFigureName = ref('')
  const searchDueDateRange = ref([])
  
  const newOrder = ref({
    figure_id: '',
    order_type: '定金预定',
    deposit: 0,
    deposit_currency: 'CNY',
    balance: 0,
    balance_currency: 'CNY',
    due_date: '',
    status: '未支付',
    shop_name: '',
    shop_contact: '',
    tracking_number: '',
    logistics_company: '',
    payment_method: '',
    payment_time: '',
    balance_payment_method: '',
    balance_payment_time: ''
  })

  // 删除确认对话框状态
  const showDeleteConfirmDialog = ref(false)
  const orderToDelete = ref(null)

  // 【新增】检查是否全选本页
  const isAllSelected = computed(() => {
    if (paginatedOrders.value.length === 0) return false
    return paginatedOrders.value.every(order => selectedIds.value.has(order.id))
  })

  // 【新增】切换批量选择模式
  const toggleBatchMode = () => {
    if (isBatchMode.value) {
      exitBatchMode()
    } else {
      enterBatchMode()
    }
  }

  // 【新增】处理切换选择
  const handleToggleSelection = (orderId, selected) => {
    setSelection(orderId, selected)
  }

  // 【新增】处理全选/取消全选
  const handleSelectAll = () => {
    if (isAllSelected.value) {
      // 取消全选本页
      paginatedOrders.value.forEach(order => {
        if (selectedIds.value.has(order.id)) {
          setSelection(order.id, false)
        }
      })
    } else {
      // 全选本页
      paginatedOrders.value.forEach(order => {
        setSelection(order.id, true)
      })
    }
  }

  // 【新增】处理批量删除
  const handleBatchDelete = async () => {
    if (!hasSelection.value) return

    try {
      const response = await orderStore.batchDeleteOrders(selectedIdsArray.value)

      // 显示删除结果
      if (response.failed_count === 0) {
        ElMessage.success(`成功删除 ${response.success_count} 个订单`)
      } else if (response.success_count === 0) {
        ElMessage.warning(`删除失败：${response.errors.join('；')}`)
      } else {
        ElMessage.info(`删除完成：成功 ${response.success_count} 个，失败 ${response.failed_count} 个`)
      }

      // 退出批量选择模式
      exitBatchMode()
      // 刷新订单列表
      await orderStore.fetchOrders()
    } catch (error) {
      console.error('批量删除失败:', error)
      ElMessage.error('批量删除失败，请稍后重试')
    }
  }
  
  // 【新增】搜索过滤后的订单（不包含状态筛选，用于状态栏计数）
  const searchFilteredOrders = computed(() => {
    let orders = orderStore.orders

    // 按手办名称模糊搜索
    if (searchFigureName.value) {
      const keyword = searchFigureName.value.toLowerCase()
      orders = orders.filter(order =>
        order.figure_name && order.figure_name.toLowerCase().includes(keyword)
      )
    }

    // 按出荷日期范围筛选
    if (searchDueDateRange.value && searchDueDateRange.value.length === 2) {
      const startDate = searchDueDateRange.value[0] ? new Date(searchDueDateRange.value[0]) : null
      const endDate = searchDueDateRange.value[1] ? new Date(searchDueDateRange.value[1]) : null

      orders = orders.filter(order => {
        if (!order.due_date) return false
        const dueDate = new Date(order.due_date)

        if (startDate && dueDate < startDate) return false
        if (endDate && dueDate > endDate) return false
        return true
      })
    }

    return orders
  })

  // 计算属性
  const filteredOrders = computed(() => {
    let orders = searchFilteredOrders.value

    // 按状态筛选
    if (currentStatus.value !== 'all') {
      orders = orders.filter(order => order.status === currentStatus.value)
    }

    // 按出荷日期排序
    return orders.sort((a, b) => {
      const today = new Date()
      today.setHours(0, 0, 0, 0)

      const dueA = a.due_date ? new Date(a.due_date) : new Date('9999-12-31')
      const dueB = b.due_date ? new Date(b.due_date) : new Date('9999-12-31')
      dueA.setHours(0, 0, 0, 0)
      dueB.setHours(0, 0, 0, 0)

      // 当筛选状态为"全部"时，已完成和已取消的订单放在最后，并按出荷日期降序排列
      if (currentStatus.value === 'all') {
        const isACompletedOrCancelled = a.status === '已完成' || a.status === '已取消'
        const isBCompletedOrCancelled = b.status === '已完成' || b.status === '已取消'

        // 如果一个是已完成/已取消，另一个不是
        if (isACompletedOrCancelled && !isBCompletedOrCancelled) {
          return 1 // a 排在后面
        }
        if (!isACompletedOrCancelled && isBCompletedOrCancelled) {
          return -1 // b 排在后面
        }

        // 如果都是已完成/已取消，按出荷日期降序排列（最新的在前面）
        if (isACompletedOrCancelled && isBCompletedOrCancelled) {
          return dueB - dueA
        }
      }

      // 已完成单独筛选时按出荷日期降序排序（最新完成排前面）
      if (currentStatus.value === '已完成') {
        return dueB - dueA
      }

      // 其他情况按出荷日期升序排序（即将出荷的排在前面）
      return dueA - dueB
    })
  })
  
  const paginatedOrders = computed(() => {
    const startIndex = (currentPage.value - 1) * pageSize.value
    const endIndex = startIndex + pageSize.value
    return filteredOrders.value.slice(startIndex, endIndex)
  })
  
  const totalOrders = computed(() => {
    return filteredOrders.value.length
  })
  
  const statusCounts = computed(() => {
    // 【修复】使用搜索过滤后的订单计算状态数量
    const orders = searchFilteredOrders.value
    const counts = {
      all: orders.length,
      '未支付': 0,
      '已支付': 0,
      '已取消': 0,
      '已完成': 0
    }

    orders.forEach(order => {
      if (counts[order.status] !== undefined) {
        counts[order.status]++
      }
    })

    return counts
  })
  
  // 【修复】基于搜索过滤后的订单计算待补款总额
  const totalUnpaidBalance = computed(() => {
    const orders = searchFilteredOrders.value
    return orders
      .filter(order => order.status === '未支付')
      .reduce((sum, order) => sum + (order.balance || 0), 0)
  })

  const availableFigures = computed(() => {
    // 获取已有订单的手办ID列表及其订单数量
    const figureOrderCounts = {}
    orderStore.orders.forEach(order => {
      if (!figureOrderCounts[order.figure_id]) {
        figureOrderCounts[order.figure_id] = 0
      }
      figureOrderCounts[order.figure_id]++
    })
    
    // 过滤出符合条件的手办
    return figureStore.figures.filter(figure => {
      // 如果是编辑模式且是当前订单的手办，则保留
      if (isEditing.value && newOrder.value.figure_id === figure.id) {
        return true
      }
      
      // 检查手办是否已有订单
      const orderCount = figureOrderCounts[figure.id] || 0
      // 检查手办数量限制
      const figureQuantity = figure.quantity || 1
      
      // 只有当订单数量小于手办数量时才显示
      return orderCount < figureQuantity
    })
  })
  
  // 方法
  const resetForm = () => {
    // 重置编辑状态
    isEditing.value = false
    currentEditOrderId.value = null

    // 重置错误状态
    figureError.value = ''
    dueDateError.value = ''

    // 重置表单数据
    newOrder.value = {
      figure_id: '',
      order_type: '定金预定',
      deposit: 0,
      deposit_currency: 'CNY',
      balance: 0,
      balance_currency: 'CNY',
      due_date: '',
      status: '未支付',
      shop_name: '',
      shop_contact: '',
      tracking_number: '',
      logistics_company: '',
      payment_method: '',
      payment_time: '',
      balance_payment_method: '',
      balance_payment_time: ''
    }
  }
  
  const openAddForm = () => {
    // 重置表单
    resetForm()
    // 显示表单
    showAddForm.value = true
  }
  
  const validateForm = () => {
    let isValid = true

    // 验证手办
    if (!newOrder.value.figure_id) {
      figureError.value = '请选择手办'
      isValid = false
    } else {
      figureError.value = ''
    }

    // 【修复】验证出荷日期 - 已取消状态的订单不需要填写出荷日期
    const isCancelled = newOrder.value.status === '已取消'
    if (!isCancelled && !newOrder.value.due_date) {
      dueDateError.value = '请选择出荷日期'
      isValid = false
    } else {
      dueDateError.value = ''
    }

    return isValid
  }
  
  const formatDate = (date) => {
    if (!date) return null
    if (typeof date === 'string') return date
    // 转换为YYYY-MM-DD格式，使用本地时间避免时区问题
    const d = new Date(date)
    const year = d.getFullYear()
    const month = String(d.getMonth() + 1).padStart(2, '0')
    const day = String(d.getDate()).padStart(2, '0')
    return `${year}-${month}-${day}`
  }
  
  const handleSaveOrder = async (orderData) => {
    try {
      // 先验证表单
      if (!validateForm()) {
        return
      }

      // 规范化空值:把 undefined / 空字符串统一转为 null,确保 el-select × 清空后能正确提交到后端
      // 避免 exclude_unset=True 时字段未传导致后端保留旧值
      const normalizedData = Object.fromEntries(
        Object.entries(orderData).map(([k, v]) => [
          k,
          v === '' || v === undefined ? null : v
        ])
      )

      const formattedOrderData = {
        ...normalizedData,
        due_date: formatDate(normalizedData.due_date)
      }
      
      if (isEditing.value) {
        // 编辑模式
        await orderStore.updateOrder(currentEditOrderId.value, formattedOrderData)
        ElMessage.success('订单编辑成功')
      } else {
        // 添加模式
        await orderStore.createOrder(formattedOrderData)
        ElMessage.success('订单添加成功')
      }
      
      showAddForm.value = false
      // 重置表单
      resetForm()
    } catch (error) {
      const errorMsg = error.response?.data?.detail || error.message || '保存失败，请稍后重试'
      ElMessage.error('保存失败: ' + errorMsg)
    }
  }
  
  // 打开删除确认对话框
  const openDeleteConfirmDialog = (order) => {
    orderToDelete.value = order
    showDeleteConfirmDialog.value = true
  }

  // 取消删除
  const cancelDelete = () => {
    showDeleteConfirmDialog.value = false
    orderToDelete.value = null
  }

  // 确认删除
  const confirmDelete = async () => {
    if (!orderToDelete.value) return

    try {
      await orderStore.deleteOrder(orderToDelete.value.id)
      showDeleteConfirmDialog.value = false
      orderToDelete.value = null
      ElMessage.success('订单删除成功')
    } catch (error) {
      ElMessage.error('删除失败，请稍后重试')
    }
  }

  const handleReceiveOrder = async (order) => {
    if (confirm('确认已收到货物？')) {
      try {
        await orderStore.updateOrder(order.id, { status: '已完成' })
        ElMessage.success('确认收货成功')
      } catch (error) {
        ElMessage.error('操作失败，请稍后重试')
      }
    }
  }
  
  const handleEditOrder = (order) => {
    // 先重置表单到初始状态,避免上次编辑/新增的数据残留
    resetForm()
    // 打开编辑表单
    showAddForm.value = true
    isEditing.value = true
    currentEditOrderId.value = order.id

    // 填充表单数据（覆盖重置后的默认值）
    newOrder.value = {
      ...newOrder.value,
      ...order,
      figure_id: order.figure_id
    }
  }
  
  const handleSizeChange = (val) => {
    pageSize.value = val
    currentPage.value = 1 // 重置为第一页
  }
  
  const handleCurrentChange = (val) => {
    currentPage.value = val
  }
  
  const handleStatusChange = (status) => {
    currentStatus.value = status
    currentPage.value = 1 // 切换状态时重置页码
  }
  
  const handleLogout = () => {
    userStore.logout()
    // 导航到登录页面的逻辑由父组件处理
  }
  
  // 生命周期
  const initializeData = () => {
    orderStore.fetchOrders()
    figureStore.fetchFigures()
    // 如果有token但用户信息为空，获取用户信息
    if (localStorage.getItem('token') && !userStore.currentUser) {
      userStore.fetchUser()
    }
  }
  
  // 【新增】处理搜索
  const handleSearch = () => {
    currentPage.value = 1 // 搜索时重置到第一页
  }
  
  // 【新增】处理重置
  const handleReset = () => {
    searchFigureName.value = ''
    searchDueDateRange.value = []
    currentPage.value = 1 // 重置时回到第一页
  }
  
  return {
    // 状态
    showAddForm,
    isEditing,
    currentPage,
    pageSize,
    pageSizes,
    currentStatus,
    figureError,
    dueDateError,
    newOrder,

    // 删除确认对话框状态
    showDeleteConfirmDialog,
    orderToDelete,

    // 【新增】批量选择状态
    isBatchMode,
    selectedIds,
    selectedCount,
    hasSelection,
    isAllSelected,

    // 【新增】搜索相关状态
    searchFigureName,
    searchDueDateRange,

    // 计算属性
    filteredOrders,
    paginatedOrders,
    totalOrders,
    statusCounts,
    availableFigures,
    totalUnpaidBalance,

    // 方法
    resetForm,
    openAddForm,
    validateForm,
    handleSaveOrder,
    openDeleteConfirmDialog,
    cancelDelete,
    confirmDelete,
    handleReceiveOrder,
    handleEditOrder,
    handleSizeChange,
    handleCurrentChange,
    handleStatusChange,
    handleLogout,
    initializeData,

    // 【新增】批量选择方法
    toggleBatchMode,
    handleToggleSelection,
    handleSelectAll,
    handleBatchDelete,
    exitBatchMode,
    isSelected,

    // 【新增】搜索方法
    handleSearch,
    handleReset
  }
}