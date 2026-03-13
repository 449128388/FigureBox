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
    <div class="orders-list">
      <div v-if="orderStore.orders.length === 0" class="empty-state">
        <p>暂无数据</p>
      </div>
      <div v-else class="order-item" v-for="order in orderStore.orders" :key="order.id">
        <h3>{{ order.figure.name }}</h3>
        <p>定金: ¥{{ order.deposit }}</p>
        <p>尾款: ¥{{ order.balance }}</p>
        <p>到期日期: {{ order.due_date }}</p>
        <p>状态: {{ order.status }}</p>
        <button class="btn btn-edit" @click="editOrder(order)">编辑</button>
        <button class="btn btn-delete" @click="deleteOrder(order.id)">删除</button>
      </div>
    </div>
    
    <!-- 添加订单表单 -->
    <div class="form-overlay" v-if="showAddForm">
      <div class="form-container">
        <h3>{{ isEditing ? '编辑订单' : '添加订单' }}</h3>
        <form @submit.prevent="addOrder">
          <div class="form-grid">
            <div class="form-group">
              <label>手办</label>
              <el-select v-model="newOrder.figure_id" placeholder="请选择手办" style="width: 100%;">
                <el-option 
                  v-for="figure in figureStore.figures" 
                  :key="figure.id" 
                  :label="figure.name" 
                  :value="figure.id" 
                />
              </el-select>
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
              <label>到期日期</label>
              <el-date-picker v-model="newOrder.due_date" type="date" placeholder="选择到期日期" style="width: 100%;"></el-date-picker>
            </div>
            <div class="form-group">
              <label>状态</label>
              <el-select v-model="newOrder.status" placeholder="请选择状态" style="width: 100%;">
                <el-option value="未支付" label="未支付" />
                <el-option value="已支付" label="已支付" />
                <el-option value="已取消" label="已取消" />
              </el-select>
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
      newOrder: {
        figure_id: '',
        deposit: 0,
        balance: 0,
        due_date: '',
        status: '未支付'
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
      
      // 重置表单数据
      this.newOrder = {
        figure_id: '',
        deposit: 0,
        balance: 0,
        due_date: '',
        status: '未支付'
      }
    },
    // 打开添加订单表单
    openAddForm() {
      // 重置表单
      this.resetForm()
      // 显示表单
      this.showAddForm = true
    },
    async addOrder() {
      try {
        // 处理空的日期字段
        const formatDate = (date) => {
          if (!date) return null
          if (typeof date === 'string') return date
          // 转换为YYYY-MM-DD格式
          return date.toISOString().split('T')[0]
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

@media (max-width: 768px) {
  .form-grid {
    grid-template-columns: 1fr;
  }
  
  .form-container {
    width: 95%;
    padding: 20px;
  }
}
</style>