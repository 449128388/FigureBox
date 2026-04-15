import { ref, computed, watch } from 'vue'
import { useOrderStore, useUserStore, useFigureStore } from '../../../store'

export function useOrderManagement() {
  // 状态管理
  const orderStore = useOrderStore()
  const userStore = useUserStore()
  const figureStore = useFigureStore()
  
  // 响应式数据
  const showAddForm = ref(false)
  const isEditing = ref(false)
  const currentEditOrderId = ref(null)
  const currentPage = ref(1)
  const pageSize = ref(15)
  const pageSizes = ref([15, 30, 45, 60])
  const currentStatus = ref('未支付') // 当前筛选状态：all, 未支付, 已支付, 已取消；默认显示未支付
  const figureError = ref('')
  const dueDateError = ref('')
  const newOrder = ref({
    figure_id: '',
    deposit: 0,
    balance: 0,
    due_date: '',
    status: '未支付',
    shop_name: '',
    shop_contact: ''
  })
  
  // 计算属性
  const filteredOrders = computed(() => {
    let orders = orderStore.orders

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
    const counts = {
      all: orderStore.orders.length,
      '未支付': 0,
      '已支付': 0,
      '已取消': 0,
      '已完成': 0
    }

    orderStore.orders.forEach(order => {
      if (counts[order.status] !== undefined) {
        counts[order.status]++
      }
    })

    return counts
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
      deposit: 0,
      balance: 0,
      due_date: '',
      status: '未支付',
      shop_name: '',
      shop_contact: '',
      tracking_number: ''
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
      
      const formattedOrderData = {
        ...orderData,
        due_date: formatDate(orderData.due_date)
      }
      
      if (isEditing.value) {
        // 编辑模式
        await orderStore.updateOrder(currentEditOrderId.value, formattedOrderData)
      } else {
        // 添加模式
        await orderStore.createOrder(formattedOrderData)
      }
      
      showAddForm.value = false
      // 重置表单
      resetForm()
    } catch (error) {
    }
  }
  
  const handleDeleteOrder = async (id) => {
    if (confirm('确定要删除这个订单吗？')) {
      try {
        await orderStore.deleteOrder(id)
      } catch (error) {
      }
    }
  }
  
  const handleReceiveOrder = async (order) => {
    if (confirm('确认已收到货物？')) {
      try {
        await orderStore.updateOrder(order.id, { status: '已完成' })
      } catch (error) {
      }
    }
  }
  
  const handleEditOrder = (order) => {
    // 打开编辑表单
    showAddForm.value = true
    isEditing.value = true
    currentEditOrderId.value = order.id
    
    // 填充表单数据
    newOrder.value = {
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
    
    // 计算属性
    filteredOrders,
    paginatedOrders,
    totalOrders,
    statusCounts,
    availableFigures,
    totalUnpaidBalance: computed(() => orderStore.totalUnpaidBalance),
    
    // 方法
    resetForm,
    openAddForm,
    validateForm,
    handleSaveOrder,
    handleDeleteOrder,
    handleReceiveOrder,
    handleEditOrder,
    handleSizeChange,
    handleCurrentChange,
    handleStatusChange,
    handleLogout,
    initializeData
  }
}