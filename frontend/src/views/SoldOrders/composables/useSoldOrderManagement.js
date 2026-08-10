import { ref, computed, watch } from 'vue'
import { useSoldOrderStore, useUserStore, useFigureStore } from '../../../store'
import { ElMessage } from 'element-plus'
import { useBatchSelection } from './useBatchSelection'

export function useSoldOrderManagement() {
  // 状态管理
  const soldOrderStore = useSoldOrderStore()
  const userStore = useUserStore()
  const figureStore = useFigureStore()

  // 批量选择功能
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
  const pageSize = ref(15)
  const pageSizes = ref([15, 30, 45, 60])
  const currentStatus = ref('all')

  // 【新增】搜索相关状态
  const searchFigureName = ref('')
  const searchOrderNumber = ref('')
  const searchSellPlatform = ref('')

  const newOrder = ref({
    figure_id: '',
    sell_price: 0,
    cost_price: 0,
    shipping_fee: 0,
    platform_fee: 0,
    sell_platform: '',
    order_number: '',
    quantity: 1,
    payment_method: '',
    sell_date: '',
    buyer_phone: '',
    tracking_number: '',
    logistics_company: '',
    status: '待发货'
  })

  // 删除确认对话框状态
  const showDeleteConfirmDialog = ref(false)
  const orderToDelete = ref(null)

  // 检查是否全选本页
  const isAllSelected = computed(() => {
    if (paginatedOrders.value.length === 0) return false
    return paginatedOrders.value.every(order => selectedIds.value.has(order.id))
  })

  // 切换批量选择模式
  const toggleBatchMode = () => {
    if (isBatchMode.value) {
      exitBatchMode()
    } else {
      enterBatchMode()
    }
  }

  // 处理切换选择
  const handleToggleSelection = (orderId, selected) => {
    setSelection(orderId, selected)
  }

  // 处理全选/取消全选
  const handleSelectAll = () => {
    if (isAllSelected.value) {
      paginatedOrders.value.forEach(order => {
        if (selectedIds.value.has(order.id)) {
          setSelection(order.id, false)
        }
      })
    } else {
      paginatedOrders.value.forEach(order => {
        setSelection(order.id, true)
      })
    }
  }

  // 处理批量删除
  const handleBatchDelete = async () => {
    if (!hasSelection.value) return

    try {
      const response = await soldOrderStore.batchDeleteSoldOrders(selectedIdsArray.value)

      if (response.failed_count === 0) {
        ElMessage.success(`成功删除 ${response.success_count} 个订单`)
      } else if (response.success_count === 0) {
        ElMessage.warning(`删除失败：${response.errors.join('；')}`)
      } else {
        ElMessage.info(`删除完成：成功 ${response.success_count} 个，失败 ${response.failed_count} 个`)
      }

      exitBatchMode()
      await soldOrderStore.fetchSoldOrders()
    } catch (error) {
      console.error('批量删除失败:', error)
      ElMessage.error('批量删除失败，请稍后重试')
    }
  }
  
  // 2026-08-06 修复：删除客户端 searchFilteredOrders 计算属性，
  // 搜索条件仅在用户点击「搜索」按钮（或按 Enter）时通过后端接口生效，
  // 不再在用户输入时实时触发前端过滤。filteredOrders / statusCounts / totalNetProfit
  // 改为直接消费 soldOrderStore.soldOrders（后端最近一次返回的数据，已包含搜索过滤结果）

  // 计算属性
  const filteredOrders = computed(() => {
    // 2026-08-06 修复：直接取 store 数据，不再叠加客户端搜索过滤（搜索由后端完成）
    let orders = soldOrderStore.soldOrders

    if (currentStatus.value !== 'all') {
      orders = orders.filter(order => order.status === currentStatus.value)
    }

    return orders.sort((a, b) => {
      const statusOrder = { '待发货': 0, '已发货': 1, '已完成': 2, '退款/纠纷': 3 }
      return (statusOrder[a.status] || 99) - (statusOrder[b.status] || 99)
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
    // 2026-08-06 修复：状态计数直接取 store 数据（已含搜索过滤结果），不再依赖客户端 searchFilteredOrders
    const orders = soldOrderStore.soldOrders
    const counts = {
      all: orders.length,
      '待发货': 0,
      '已发货': 0,
      '已完成': 0,
      '退款/纠纷': 0
    }

    orders.forEach(order => {
      if (counts[order.status] !== undefined) {
        counts[order.status]++
      }
    })

    return counts
  })
  const availableFigures = computed(() => {
    const figures = figureStore.figures
    if (isEditing.value && newOrder.value && newOrder.value.figure_id) {
      const figureId = Number(newOrder.value.figure_id)
      const exists = figures.some(f => Number(f.id) === figureId)
      if (!exists) {
        return [
          ...figures,
          {
            id: figureId,
            name: newOrder.value.figure_name || `手办#${figureId}`,
            quantity: 1,
            average_purchase_price: 0
          }
        ]
      }
    }
    return figures
  })

  // 2026-08-06 修复：累计净利润直接基于 store 数据计算（已含搜索过滤结果）
  const totalNetProfit = computed(() => {
    return soldOrderStore.soldOrders.reduce((sum, order) => sum + (order.net_profit || 0), 0)
  })
  
  // 方法
  const resetForm = () => {
    isEditing.value = false
    currentEditOrderId.value = null

    newOrder.value = {
      figure_id: '',
      sell_price: 0,
      cost_price: 0,
      shipping_fee: 0,
      platform_fee: 0,
      sell_platform: '',
      order_number: '',
      quantity: 1,
      payment_method: '',
      sell_date: '',
      buyer_phone: '',
      tracking_number: '',
      logistics_company: '',
      status: '待发货'
    }
  }
  
  const openAddForm = () => {
    resetForm()
    // 懒加载有库存的手办列表（仅在打开表单时按需拉取，避免进入页面就预加载浪费请求）
    ensureFiguresWithStockLoaded()
    showAddForm.value = true
  }

  /**
   * 懒加载有库存的手办列表：仅在 figureStore.figures 为空时才请求 /api/figures/with-stock，避免重复请求
   * 解决「已出订单页进入即预加载手办列表」造成的冗余接口调用
   */
  const ensureFiguresWithStockLoaded = async () => {
    if (figureStore.figures.length === 0) {
      await figureStore.fetchFiguresWithStock()
    }
  }

  const handleCancelForm = () => {
    showAddForm.value = false
    resetForm()
  }

  const handleSaveOrder = async (orderData) => {
    try {
      if (isEditing.value) {
        await soldOrderStore.updateSoldOrder(currentEditOrderId.value, orderData)
        ElMessage.success('订单编辑成功')
      } else {
        await soldOrderStore.createSoldOrder(orderData)
        ElMessage.success('订单创建成功')
      }

      showAddForm.value = false
      resetForm()
    } catch (error) {
      const errorMsg = error.response?.data?.detail || error.message || '保存失败，请稍后重试'
      ElMessage.error("保存失败:" + errorMsg)
    }
  }

  // 处理平台手续费计算
  const handleCalculatePlatformFee = async (params) => {
    const { platform, sellPrice, orderId, callback } = params
    
    try {
      // 获取当月闲鱼订单统计
      const monthlyStats = await soldOrderStore.fetchXianyuMonthlyStats(orderId)
      
      // 调用回调函数返回计算结果
      if (callback && typeof callback === 'function') {
        callback(monthlyStats)
      }
    } catch (error) {
      console.error('获取闲鱼月度统计失败:', error)
      // 如果获取失败，返回空统计让前端按默认费率计算
      if (callback && typeof callback === 'function') {
        callback({ order_count: 0, total_amount: 0 })
      }
    }
  }
  
  const openDeleteConfirmDialog = (order) => {
    orderToDelete.value = order
    showDeleteConfirmDialog.value = true
  }

  const cancelDelete = () => {
    showDeleteConfirmDialog.value = false
    orderToDelete.value = null
  }

  const confirmDelete = async () => {
    if (!orderToDelete.value) return

    try {
      await soldOrderStore.deleteSoldOrder(orderToDelete.value.id)
      showDeleteConfirmDialog.value = false
      orderToDelete.value = null
      ElMessage.success('订单删除成功')
    } catch (error) {
      ElMessage.error('删除失败，请稍后重试')
    }
  }
  
  const handleEditOrder = (order) => {
    // 懒加载有库存的手办列表（编辑表单同样需要 availableFigures，编辑时虽然不可改手办，但下拉框仍要展示）
    ensureFiguresWithStockLoaded()
    showAddForm.value = true
    isEditing.value = true
    currentEditOrderId.value = order.id

    newOrder.value = {
      ...order,
      figure_id: order.figure_id
    }
  }
  
  const handleSizeChange = (val) => {
    pageSize.value = val
    currentPage.value = 1
  }
  
  const handleCurrentChange = (val) => {
    currentPage.value = val
  }
  
  const handleStatusChange = (status) => {
    currentStatus.value = status
    currentPage.value = 1
  }
  
  const handleLogout = () => {
    userStore.logout()
  }
  
  const initializeData = () => {
    soldOrderStore.fetchSoldOrders()
    // 2026-08-06 修复：移除 figureStore.fetchFiguresWithStock() 预加载，
    // 改为懒加载（在 openAddForm / handleEditOrder 时按需加载），避免进入页面就请求 /api/figures/with-stock
    if (localStorage.getItem('token') && !userStore.currentUser) {
      userStore.fetchUser()
    }
  }

  // 【新增】处理搜索 - 2026-08-06 修复：调用后端按条件查询（之前只改 currentPage 不发请求）
  const handleSearch = async () => {
    currentPage.value = 1 // 搜索时重置到第一页
    const params = {}
    if (searchFigureName.value && searchFigureName.value.trim()) {
      params.figure_name = searchFigureName.value.trim()
    }
    if (searchOrderNumber.value && searchOrderNumber.value.trim()) {
      params.order_number = searchOrderNumber.value.trim()
    }
    if (searchSellPlatform.value) {
      params.sell_platform = searchSellPlatform.value
    }
    await soldOrderStore.fetchSoldOrders(params)
  }

  // 【新增】处理回车键搜索 - 2026-08-06 新增：搜索输入框按 Enter 触发搜索（与点击搜索按钮等价）
  const handleEnterSearch = () => {
    return handleSearch()
  }

  // 【新增】处理重置 - 2026-08-06 修复：清空搜索条件后重新拉取全量订单（之前只改 ref）
  const handleReset = async () => {
    searchFigureName.value = ''
    searchOrderNumber.value = ''
    searchSellPlatform.value = ''
    currentPage.value = 1 // 重置时回到第一页
    await soldOrderStore.fetchSoldOrders()
  }

  return {
    showAddForm,
    isEditing,
    currentPage,
    pageSize,
    pageSizes,
    currentStatus,
    newOrder,

    showDeleteConfirmDialog,
    orderToDelete,

    isBatchMode,
    selectedIds,
    selectedCount,
    hasSelection,
    isAllSelected,

    // 【新增】搜索相关状态
    searchFigureName,
    searchOrderNumber,
    searchSellPlatform,

    filteredOrders,
    paginatedOrders,
    totalOrders,
    statusCounts,
    availableFigures,
    totalNetProfit,

    resetForm,
  openAddForm,
  handleSaveOrder,
  handleCancelForm,
  handleCalculatePlatformFee,
    openDeleteConfirmDialog,
    cancelDelete,
    confirmDelete,
    handleEditOrder,
    handleSizeChange,
    handleCurrentChange,
    handleStatusChange,
    handleLogout,
    initializeData,

    toggleBatchMode,
    handleToggleSelection,
    handleSelectAll,
    handleBatchDelete,
    exitBatchMode,
    isSelected,

    // 【新增】搜索方法
    handleSearch,
    handleEnterSearch,
    handleReset
  }
}