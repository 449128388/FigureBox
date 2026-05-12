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
  const newOrder = ref({
    figure_id: '',
    sell_price: 0,
    cost_price: 0,
    shipping_fee: 0,
    platform_fee: 0,
    sell_platform: '',
    order_number: '',
    buyer_phone: '',
    tracking_number: '',
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
  
  // 计算属性
  const filteredOrders = computed(() => {
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
    const counts = {
      all: soldOrderStore.soldOrders.length,
      '待发货': 0,
      '已发货': 0,
      '已完成': 0,
      '退款/纠纷': 0
    }

    soldOrderStore.soldOrders.forEach(order => {
      if (counts[order.status] !== undefined) {
        counts[order.status]++
      }
    })

    return counts
  })
  
  const availableFigures = computed(() => {
    return figureStore.figures
  })
  
  const totalNetProfit = computed(() => soldOrderStore.totalNetProfit)
  
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
      buyer_phone: '',
      tracking_number: '',
      status: '待发货'
    }
  }
  
  const openAddForm = () => {
    resetForm()
    showAddForm.value = true
  }
  
  const handleSaveOrder = async (orderData) => {
    try {
      if (isEditing.value) {
        await soldOrderStore.updateSoldOrder(currentEditOrderId.value, orderData)
      } else {
        await soldOrderStore.createSoldOrder(orderData)
      }
      
      showAddForm.value = false
      resetForm()
    } catch (error) {
      ElMessage.error('保存失败，请稍后重试')
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
    figureStore.fetchFigures()
    if (localStorage.getItem('token') && !userStore.currentUser) {
      userStore.fetchUser()
    }
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

    filteredOrders,
    paginatedOrders,
    totalOrders,
    statusCounts,
    availableFigures,
    totalNetProfit,

    resetForm,
    openAddForm,
    handleSaveOrder,
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
    isSelected
  }
}