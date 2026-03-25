<template>
  <div class="orders-container">
    <div class="header">
      <h2>尾款管理</h2>
      <div class="header-actions">
        <button class="btn btn-add" @click="openAddForm">添加订单</button>
        <div class="user-info">
          <span v-if="userStore.isAuthenticated">当前用户：</span>
          <span v-if="userStore.isAuthenticated" class="username" @click="$router.push('/profile')" style="cursor: pointer; color: #2196F3; text-decoration: underline;">{{ userStore.currentUser?.username }}</span>
          <button v-if="userStore.isAuthenticated" class="btn btn-logout" @click="logout">退出</button>
        </div>
      </div>
    </div>
    <!-- 状态筛选 Tab -->
    <div class="status-tabs">
      <div 
        class="status-tab" 
        :class="{ active: currentStatus === 'all' }"
        @click="currentStatus = 'all'"
      >
        全部 ({{ statusCounts.all }})
      </div>
      <div 
        class="status-tab" 
        :class="{ active: currentStatus === '未支付' }"
        @click="currentStatus = '未支付'"
      >
        未支付 ({{ statusCounts['未支付'] }})
      </div>
      <div 
        class="status-tab" 
        :class="{ active: currentStatus === '已支付' }"
        @click="currentStatus = '已支付'"
      >
        已支付 ({{ statusCounts['已支付'] }})
      </div>
      <div 
        class="status-tab" 
        :class="{ active: currentStatus === '已取消' }"
        @click="currentStatus = '已取消'"
      >
        已取消 ({{ statusCounts['已取消'] }})
      </div>
      <div 
        class="status-tab" 
        :class="{ active: currentStatus === '已完成' }"
        @click="currentStatus = '已完成'"
      >
        已完成 ({{ statusCounts['已完成'] }})
      </div>
    </div>

    <div class="orders-list">
      <div v-if="filteredOrders.length === 0" class="empty-state">
        <p>暂无数据</p>
      </div>
      <div v-else class="order-item" v-for="order in paginatedOrders" :key="order.id">
        <h3><router-link :to="`/figures/${order.figure.id}`" class="figure-name-link">{{ order.figure.name }}</router-link><span v-if="order.status !== '已完成' && order.status !== '已取消'" class="countdown-tag" :class="getCountdownClass(order.due_date)">{{ getCountdownText(order.due_date) }}</span></h3>
        <p>定金: ¥{{ order.deposit }}</p>
        <p>尾款: ¥{{ order.balance }}</p>
        <p>出荷日期: {{ order.due_date }}</p>
        <p>尾款状态: {{ order.status }}</p>
        <p v-if="order.shop_name">购买店铺: {{ order.shop_name }}</p>
        <p v-if="order.shop_contact">店铺联系方式: {{ order.shop_contact }}</p>
        <p v-if="order.tracking_number">物流订单: {{ order.tracking_number }}</p>
        <button class="btn btn-edit" @click="editOrder(order)">编辑</button>
        <button v-if="order.status === '已支付'" class="btn btn-receive" @click="receiveOrder(order)">收货</button>
        <button class="btn btn-delete" @click="deleteOrder(order.id)">删除</button>
      </div>
    </div>
    
    <!-- 分页组件 -->
    <div v-if="totalOrders > 0" class="pagination-container">
      <el-pagination
        v-model:current-page="currentPage"
        v-model:page-size="pageSize"
        :page-sizes="pageSizes"
        layout="total, sizes, prev, pager, next, jumper"
        :total="totalOrders"
        @size-change="handleSizeChange"
        @current-change="handleCurrentChange"
      />
    </div>
    
    <!-- 添加订单表单 -->
    <div class="form-overlay" v-if="showAddForm">
      <div class="form-container">
        <h3>{{ isEditing ? '编辑订单' : '添加订单' }}</h3>
        <form @submit.prevent="addOrder">
          <div class="form-grid">
            <div class="form-group">
              <label>手办</label>
              <el-select 
                v-model="newOrder.figure_id" 
                placeholder="请选择手办" 
                style="width: 100%;"
                :class="{ 'error-input': figureError }"
                :disabled="isEditing"
                @change="validateFigureOnChange"
              >
                <el-option 
                  v-for="figure in availableFigures" 
                  :key="figure.id" 
                  :label="figure.name" 
                  :value="figure.id" 
                />
              </el-select>
              <div v-if="figureError" class="error-message">{{ figureError }}</div>
            </div>
            <div class="form-group">
              <label>定金</label>
              <el-input-number v-model="newOrder.deposit" placeholder="请输入定金" :min="0" :step="1" style="width: 100%;"></el-input-number>
            </div>
            <div class="form-group">
              <label>尾款</label>
              <el-input-number v-model="newOrder.balance" placeholder="请输入尾款" :min="0" :step="1" style="width: 100%;"></el-input-number>
            </div>
            <div class="form-group">
              <label>出荷日期</label>
              <el-date-picker 
                v-model="newOrder.due_date" 
                type="date" 
                placeholder="选择出荷日期" 
                style="width: 100%;"
                :class="{ 'error-input': dueDateError }"
                @change="validateDueDateOnChange"
              ></el-date-picker>
              <div v-if="dueDateError" class="error-message">{{ dueDateError }}</div>
            </div>
            <div class="form-group">
              <label>尾款状态</label>
              <el-select v-model="newOrder.status" placeholder="请选择尾款状态" style="width: 100%;">
                <el-option value="未支付" label="未支付" />
                <el-option value="已支付" label="已支付" />
                <el-option value="已取消" label="已取消" />
                <el-option value="已完成" label="已完成" />
              </el-select>
            </div>
            <div class="form-group">
              <label>购买店铺</label>
              <el-input v-model="newOrder.shop_name" placeholder="请输入购买店铺" style="width: 100%;"></el-input>
            </div>
            <div class="form-group">
              <label>店铺联系方式</label>
              <el-input v-model="newOrder.shop_contact" placeholder="请输入店铺联系方式" style="width: 100%;"></el-input>
            </div>
            <div class="form-group" v-if="isEditing">
              <label>物流订单</label>
              <el-input v-model="newOrder.tracking_number" placeholder="请输入物流订单号" style="width: 100%;"></el-input>
            </div>
          </div>

          <div class="form-actions">
            <el-button class="btn-cancel" @click="showAddForm = false">取消</el-button>
            <el-button class="btn-submit" type="primary" native-type="submit">保存</el-button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script>
import { useOrderStore, useUserStore, useFigureStore } from '../store'

export default {
  name: 'Orders',
  data() {
    return {
      showAddForm: false,
      isEditing: false,
      currentEditOrderId: null,
      currentPage: 1,
      pageSize: 15,
      pageSizes: [15, 30, 45, 60],
      currentStatus: '未支付', // 当前筛选状态：all, 未支付, 已支付, 已取消；默认显示未支付
      figureError: '',
      dueDateError: '',
      newOrder: {
        figure_id: '',
        deposit: 0,
        balance: 0,
        due_date: '',
        status: '未支付',
        shop_name: '',
        shop_contact: ''
      }
    }
  },
  computed: {
    orderStore() {
      return useOrderStore()
    },
    userStore() {
      return useUserStore()
    },
    figureStore() {
      return useFigureStore()
    },
    
    // 根据状态筛选订单
    filteredOrders() {
      let orders = this.orderStore.orders

      // 按状态筛选
      if (this.currentStatus !== 'all') {
        orders = orders.filter(order => order.status === this.currentStatus)
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
        if (this.currentStatus === 'all') {
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
    },
    
    // 分页处理
    paginatedOrders() {
      const startIndex = (this.currentPage - 1) * this.pageSize
      const endIndex = startIndex + this.pageSize
      return this.filteredOrders.slice(startIndex, endIndex)
    },
    
    // 总数据量（根据筛选状态）
    totalOrders() {
      return this.filteredOrders.length
    },
    
    // 各状态订单数量统计
    statusCounts() {
      const counts = {
        all: this.orderStore.orders.length,
        '未支付': 0,
        '已支付': 0,
        '已取消': 0,
        '已完成': 0
      }

      this.orderStore.orders.forEach(order => {
        if (counts[order.status] !== undefined) {
          counts[order.status]++
        }
      })

      return counts
    },
    
    // 可选手办列表（过滤掉已有订单的手办，但编辑模式下包含当前订单的手办）
    availableFigures() {
      // 获取已有订单的手办ID列表
      const orderedFigureIds = this.orderStore.orders.map(order => order.figure.id)
      // 过滤掉已有订单的手办，但编辑模式下保留当前订单的手办
      return this.figureStore.figures.filter(figure => {
        // 如果是编辑模式且是当前订单的手办，则保留
        if (this.isEditing && this.newOrder.figure_id === figure.id) {
          return true
        }
        // 否则过滤掉已有订单的手办
        return !orderedFigureIds.includes(figure.id)
      })
    }
  },
  mounted() {
    this.orderStore.fetchOrders()
    this.figureStore.fetchFigures()
    // 如果有token但用户信息为空，获取用户信息
    if (localStorage.getItem('token') && !this.userStore.currentUser) {
      this.userStore.fetchUser()
    }
  },
  methods: {
    logout() {
      this.userStore.logout()
      this.$router.push('/login')
    },
    // 重置表单
    resetForm() {
      // 重置编辑状态
      this.isEditing = false
      this.currentEditOrderId = null

      // 重置错误状态
      this.figureError = ''
      this.dueDateError = ''

      // 重置表单数据
      this.newOrder = {
        figure_id: '',
        deposit: 0,
        balance: 0,
        due_date: '',
        status: '未支付',
        shop_name: '',
        shop_contact: '',
        tracking_number: ''
      }
    },
    // 打开添加订单表单
    openAddForm() {
      // 重置表单
      this.resetForm()
      // 显示表单
      this.showAddForm = true
    },
    // 验证手办字段
    validateFigureOnChange() {
      if (!this.newOrder.figure_id) {
        this.figureError = '请选择手办'
      } else {
        this.figureError = ''
      }
    },
    
    // 验证出荷日期字段
    validateDueDateOnChange() {
      if (!this.newOrder.due_date) {
        this.dueDateError = '请选择出荷日期'
      } else {
        this.dueDateError = ''
      }
    },
    
    // 验证整个表单
    validateForm() {
      let isValid = true
      
      // 验证手办
      if (!this.newOrder.figure_id) {
        this.figureError = '请选择手办'
        isValid = false
      } else {
        this.figureError = ''
      }
      
      // 验证出荷日期
      if (!this.newOrder.due_date) {
        this.dueDateError = '请选择出荷日期'
        isValid = false
      } else {
        this.dueDateError = ''
      }
      
      return isValid
    },
    
    async addOrder() {
      try {
        // 先验证表单
        if (!this.validateForm()) {
          return
        }
        
        // 处理空的日期字段
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
        
        const orderData = {
          ...this.newOrder,
          due_date: formatDate(this.newOrder.due_date)
        }
        
        if (this.isEditing) {
          // 编辑模式
          await this.orderStore.updateOrder(this.currentEditOrderId, orderData)
        } else {
          // 添加模式
          await this.orderStore.createOrder(orderData)
        }
        
        this.showAddForm = false
        // 重置表单
        this.resetForm()
      } catch (error) {
        console.error('Failed to add order:', error)
      }
    },
    async deleteOrder(id) {
      if (confirm('确定要删除这个订单吗？')) {
        try {
          await this.orderStore.deleteOrder(id)
        } catch (error) {
          console.error('Failed to delete order:', error)
        }
      }
    },
    async receiveOrder(order) {
      if (confirm('确认已收到货物？')) {
        try {
          await this.orderStore.updateOrder(order.id, { status: '已完成' })
        } catch (error) {
          console.error('Failed to receive order:', error)
        }
      }
    },
    editOrder(order) {
      // 打开编辑表单
      this.showAddForm = true
      this.isEditing = true
      this.currentEditOrderId = order.id
      
      // 填充表单数据
      this.newOrder = {
        ...order,
        figure_id: order.figure.id
      }
    },
    
    // 处理每页条数变化
    handleSizeChange(val) {
      this.pageSize = val
      this.currentPage = 1 // 重置为第一页
    },
    
    // 处理页码变化
    handleCurrentChange(val) {
      this.currentPage = val
    },
    
    // 获取倒计时文本
    getCountdownText(dueDate) {
      if (!dueDate) return ''
      
      const today = new Date()
      today.setHours(0, 0, 0, 0)
      
      const due = new Date(dueDate)
      due.setHours(0, 0, 0, 0)
      
      const diffTime = due - today
      const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24))
      
      if (diffDays < 0) {
        return `已出荷 ${Math.abs(diffDays)} 天`
      } else if (diffDays === 0) {
        return '今天出荷'
      } else {
        return `还有 ${diffDays} 天`
      }
    },
    
    // 获取倒计时样式类
    getCountdownClass(dueDate) {
      if (!dueDate) return ''
      
      const today = new Date()
      today.setHours(0, 0, 0, 0)
      
      const due = new Date(dueDate)
      due.setHours(0, 0, 0, 0)
      
      const diffTime = due - today
      const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24))
      
      if (diffDays < 0) {
        return 'countdown-overdue'
      } else if (diffDays === 0) {
        return 'countdown-today'
      } else if (diffDays <= 7) {
        return 'countdown-urgent'
      } else if (diffDays <= 30) {
        return 'countdown-warning'
      } else {
        return 'countdown-normal'
      }
    }
  },
  
  watch: {
    // 当切换状态筛选时，重置页码到第一页
    currentStatus() {
      this.currentPage = 1
    }
  }
}
</script>

<style scoped>
.orders-container {
  margin-top: 20px;
  width: 100%;
  max-width: 1650px;
  margin-left: 50px;
  margin-right: 50px;
  padding: 20px;
  background-color: #f9f9f9;
  border-radius: 8px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 30px;
  padding-bottom: 20px;
  border-bottom: 2px solid #e0e0e0;
}

.header h2 {
  margin: 0;
  color: #333;
  font-size: 24px;
  font-weight: 600;
}

.header-actions {
  display: flex;
  align-items: center;
  gap: 20px;
}

/* 状态筛选 Tab 样式 */
.status-tabs {
  display: flex;
  gap: 10px;
  margin-bottom: 20px;
  padding: 10px;
  background-color: white;
  border-radius: 8px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.status-tab {
  padding: 10px 20px;
  border-radius: 6px;
  cursor: pointer;
  font-size: 14px;
  font-weight: 500;
  color: #666;
  background-color: #f5f5f5;
  transition: all 0.3s ease;
  border: 2px solid transparent;
}

.status-tab:hover {
  background-color: #e8e8e8;
  transform: translateY(-1px);
}

.status-tab.active {
  background-color: #2196F3;
  color: white;
  border-color: #1976D2;
  box-shadow: 0 2px 8px rgba(33, 150, 243, 0.3);
}

.status-tab.active:hover {
  background-color: #1976D2;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 15px;
  padding: 10px 15px;
  background-color: white;
  border-radius: 6px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.username {
  font-size: 14px;
  font-weight: 500;
  color: #555;
}

.btn {
  padding: 10px 20px;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-size: 14px;
  font-weight: 500;
  transition: all 0.3s ease;
}

.btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
}

.btn-add {
  background-color: #4CAF50;
  color: white;
  padding: 12px 24px;
  font-size: 16px;
}

.btn-add:hover {
  background-color: #45a049;
}

.btn-logout {
  background-color: #f44336;
  color: white;
  padding: 8px 16px;
  font-size: 14px;
}

.btn-logout:hover {
  background-color: #da190b;
}

.orders-list {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
  gap: 15px;
  margin-bottom: 20px;
}

.empty-state {
  grid-column: 1 / -1;
  text-align: center;
  padding: 60px 20px;
  background-color: white;
  border-radius: 8px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
  color: #999;
  font-size: 16px;
}

.order-item {
  background: white;
  padding: 20px;
  border-radius: 8px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
}

.order-item h3 {
  margin-bottom: 10px;
  color: #333;
}

.order-item p {
  margin-bottom: 5px;
  color: #666;
}

.figure-name-link {
  color: #333;
  text-decoration: none;
  cursor: pointer;
  transition: color 0.3s ease;
}

.figure-name-link:hover {
  color: #2196F3;
}

.countdown-tag {
  display: inline-block;
  margin-left: 10px;
  padding: 4px 12px;
  border-radius: 6px;
  font-size: 14px;
  font-weight: 600;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  border: 2px solid transparent;
}

.countdown-normal {
  background-color: #e8f5e9;
  color: #2e7d32;
  border-color: #4caf50;
}

.countdown-warning {
  background-color: #fff3e0;
  color: #e65100;
  border-color: #ff9800;
}

.countdown-urgent {
  background-color: #ffebee;
  color: #c62828;
  border-color: #f44336;
  animation: pulse 2s infinite;
}

.countdown-today {
  background-color: #e3f2fd;
  color: #1565c0;
  border-color: #2196f3;
  animation: pulse 2s infinite;
}

.countdown-overdue {
  background-color: #f5f5f5;
  color: #616161;
  border-color: #9e9e9e;
}

@keyframes pulse {
  0% {
    box-shadow: 0 0 0 0 rgba(244, 67, 54, 0.4);
  }
  70% {
    box-shadow: 0 0 0 10px rgba(244, 67, 54, 0);
  }
  100% {
    box-shadow: 0 0 0 0 rgba(244, 67, 54, 0);
  }
}

.btn {
  padding: 8px 16px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
  margin-right: 10px;
  margin-top: 10px;
}

.btn-edit {
  background-color: #2196F3;
  color: white;
}

.btn-edit:hover {
  background-color: #0b7dda;
}

.btn-delete {
  background-color: #f44336;
  color: white;
}

.btn-delete:hover {
  background-color: #da190b;
}

.btn-receive {
  background-color: #4CAF50;
  color: white;
}

.btn-receive:hover {
  background-color: #45a049;
}

.btn-add {
  background-color: #4CAF50;
  color: white;
  padding: 10px 20px;
  font-size: 16px;
}

.btn-add:hover {
  background-color: #45a049;
}

/* 表单样式 */
.form-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.form-container {
  background: white;
  padding: 30px;
  border-radius: 8px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);
  width: 90%;
  max-width: 600px;
  max-height: 80vh;
  overflow-y: auto;
}

.form-container h3 {
  margin-top: 0;
  margin-bottom: 20px;
  color: #333;
  font-size: 20px;
  font-weight: 600;
  border-bottom: 1px solid #e0e0e0;
  padding-bottom: 10px;
}

.form-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 15px;
  margin-bottom: 20px;
}

.form-group {
  display: flex;
  flex-direction: column;
}

.form-group label {
  margin-bottom: 8px;
  font-weight: 500;
  color: #333;
}

/* 错误提示样式 */
:deep(.error-input .el-input__wrapper) {
  box-shadow: 0 0 0 1px #f56c6c inset !important;
}

:deep(.error-input .el-input__wrapper:hover) {
  box-shadow: 0 0 0 1px #f56c6c inset !important;
}

:deep(.error-input .el-input__wrapper.is-focus) {
  box-shadow: 0 0 0 1px #f56c6c inset !important;
}

:deep(.error-input .el-select .el-input__wrapper) {
  box-shadow: 0 0 0 1px #f56c6c inset !important;
}

:deep(.error-input .el-select .el-input__wrapper:hover) {
  box-shadow: 0 0 0 1px #f56c6c inset !important;
}

:deep(.error-input .el-select .el-input__wrapper.is-focus) {
  box-shadow: 0 0 0 1px #f56c6c inset !important;
}

.error-message {
  color: #f56c6c;
  font-size: 12px;
  line-height: 1;
  padding-top: 4px;
}

.form-actions {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
  margin-top: 20px;
  padding-top: 20px;
  border-top: 1px solid #e0e0e0;
}

.btn-cancel {
  padding: 10px 20px;
  border: 1px solid #dcdfe6;
  border-radius: 6px;
  background-color: white;
  color: #606266;
  cursor: pointer;
  font-size: 14px;
  font-weight: 500;
  transition: all 0.3s ease;
}

.btn-cancel:hover {
  color: #409eff;
  border-color: #c6e2ff;
  background-color: #ecf5ff;
}

.btn-submit {
  padding: 10px 20px;
  border: none;
  border-radius: 6px;
  background-color: #4CAF50;
  color: white;
  cursor: pointer;
  font-size: 14px;
  font-weight: 500;
  transition: all 0.3s ease;
}

.btn-submit:hover {
  background-color: #45a049;
  transform: translateY(-2px);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
}

.pagination-container {
  display: flex;
  justify-content: flex-end;
  margin-top: 30px;
  padding-top: 20px;
  border-top: 2px solid #e0e0e0;
}

@media (max-width: 768px) {
  .form-grid {
    grid-template-columns: 1fr;
  }
  
  .form-container {
    width: 95%;
    padding: 20px;
  }
  
  .pagination-container {
    justify-content: center;
  }
}
</style>