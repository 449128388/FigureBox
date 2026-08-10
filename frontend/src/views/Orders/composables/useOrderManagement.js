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
  // 2026-08-06 翻页重构：状态计数由后端 status_counts 提供，前端不再用 orderStore.orders 全量聚合
  // 此处保留 searchFilteredOrders computed 是为了在搜索条件下统计「未支付」的尾款总额
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

  // 2026-08-06 翻页重构：paginatedOrders 改为直接取 orderStore.orders（后端已按 skip/limit 切好页）
  // 旧的客户端 slice 逻辑删除，避免翻页"哑铃"（UI 可点但不发请求）
  const paginatedOrders = computed(() => orderStore.orders)

  // 2026-08-06 翻页重构：totalOrders 改为取后端返回的 totalCount
  const totalOrders = computed(() => orderStore.totalCount)
  
  // 2026-08-06 翻页重构：statusCounts 改为取后端返回的 statusCounts
  // 后端应用 figure_name / due_date_range 过滤但不应用 status 过滤，确保 4 个状态 Tab 计数一致
  const statusCounts = computed(() => orderStore.statusCounts)
  
  // 【修复】基于搜索过滤后的订单计算待补款总额
  const totalUnpaidBalance = computed(() => {
    const orders = searchFilteredOrders.value
    return orders
      .filter(order => order.status === '未支付')
      .reduce((sum, order) => sum + (order.balance || 0), 0)
  })

  // 2026-08-06 翻页重构：availableFigures 改用 figure.order_count（手办列表本身已带），
  // 不再从 orderStore.orders 聚合（受分页影响只拿到当前页数据，会误判手办可下单性）
  const availableFigures = computed(() => {
    return figureStore.figures.filter(figure => {
      // 如果是编辑模式且是当前订单的手办，则保留
      if (isEditing.value && newOrder.value.figure_id === figure.id) {
        return true
      }

      // 检查手办是否已有订单（order_count 来自手办列表 API，与分页无关，是全量统计）
      const orderCount = figure.order_count || 0
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
    // 懒加载手办列表（仅在打开表单时按需拉取，避免进入页面就预加载浪费请求）
    ensureFiguresLoaded()
    // 显示表单
    showAddForm.value = true
  }

  /**
   * 懒加载手办列表：仅在手办 store 为空时才请求 /api/figures/，避免重复请求
   * 解决「尾款管理页进入即预加载全量手办」造成的冗余接口调用
   */
  const ensureFiguresLoaded = async () => {
    if (figureStore.figures.length === 0) {
      await figureStore.fetchFigures()
    }
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
    // 懒加载手办列表（编辑表单同样需要 availableFigures，编辑时虽然不可改手办，但下拉框仍要展示）
    ensureFiguresLoaded()
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
  
  // 2026-08-06 翻页重构：统一的订单加载入口，构建所有过滤 + 分页参数，调用后端 store
  // 任何状态变化（搜索 / 状态 Tab / 页码 / 每页条数 / 重置）都通过 loadOrders 触发后端请求
  const loadOrders = async () => {
    const params = {
      skip: (currentPage.value - 1) * pageSize.value,
      limit: pageSize.value
    }
    if (currentStatus.value && currentStatus.value !== 'all') {
      params.status = currentStatus.value
    }
    if (searchFigureName.value && searchFigureName.value.trim()) {
      params.figure_name = searchFigureName.value.trim()
    }
    if (searchDueDateRange.value && searchDueDateRange.value.length === 2) {
      // 2026-08-06 修复：formatDate 必须存在或新增；这里直接读日期对象的 YYYY-MM-DD
      const formatDate = (d) => {
        if (!d) return null
        const dt = new Date(d)
        const yyyy = dt.getFullYear()
        const mm = String(dt.getMonth() + 1).padStart(2, '0')
        const dd = String(dt.getDate()).padStart(2, '0')
        return `${yyyy}-${mm}-${dd}`
      }
      if (searchDueDateRange.value[0]) {
        params.due_date_start = formatDate(searchDueDateRange.value[0])
      }
      if (searchDueDateRange.value[1]) {
        params.due_date_end = formatDate(searchDueDateRange.value[1])
      }
    }
    await orderStore.fetchOrders(params)
  }

  // 2026-08-06 翻页重构：handleSizeChange 走服务端，切换每页条数 → 重新查询后端
  const handleSizeChange = (val) => {
    pageSize.value = val
    currentPage.value = 1
    loadOrders()
  }

  // 2026-08-06 翻页重构：handleCurrentChange 走服务端，页码切换 → 重新查询后端
  const handleCurrentChange = (val) => {
    currentPage.value = val
    loadOrders()
  }
  
  // 2026-08-06 翻页重构：handleStatusChange 切换状态时调后端（旧的纯改 ref 不发请求）
  const handleStatusChange = (status) => {
    currentStatus.value = status
    currentPage.value = 1 // 切换状态时重置页码
    loadOrders()
  }
  
  const handleLogout = () => {
    userStore.logout()
    // 导航到登录页面的逻辑由父组件处理
  }
  
  // 生命周期
  const initializeData = () => {
    // 2026-08-06 翻页重构：进入页面时走 loadOrders()，带上分页参数（默认 page 1, pageSize 10）
    loadOrders()
    // 2026-08-06 修复：移除 figureStore.fetchFigures() 预加载，
    // 改为懒加载（在 openAddForm / handleEditOrder 时按需加载），避免进入页面就请求 /api/figures/
    // 如果有token但用户信息为空，获取用户信息
    if (localStorage.getItem('token') && !userStore.currentUser) {
      userStore.fetchUser()
    }
  }

  // 【新增】处理搜索 - 2026-08-06 翻页重构：走 loadOrders() 统一入口，自动带分页参数
  const handleSearch = async () => {
    currentPage.value = 1 // 搜索时重置到第一页
    await loadOrders()
  }

  // 【新增】处理回车键搜索 - 2026-08-06 新增：搜索输入框按 Enter 触发搜索（与点击搜索按钮等价）
  const handleEnterSearch = () => {
    return handleSearch()
  }

  // 【新增】处理重置 - 2026-08-06 翻页重构：清空搜索条件后走 loadOrders() 拉取全量订单
  const handleReset = async () => {
    searchFigureName.value = ''
    searchDueDateRange.value = []
    currentPage.value = 1
    await loadOrders()
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
    handleEnterSearch,
    handleReset
  }
}