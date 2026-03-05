<template>
  <div class="orders-container">
    <div class="header">
      <h2>订单管理</h2>
      <div class="header-actions">
        <button class="btn btn-add">添加订单</button>
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
        <button class="btn btn-edit">编辑</button>
        <button class="btn btn-delete">删除</button>
      </div>
    </div>
  </div>
</template>

<script>
import { useOrderStore, useUserStore } from '../store'

export default {
  name: 'Orders',
  computed: {
    orderStore() {
      return useOrderStore()
    },
    userStore() {
      return useUserStore()
    }
  },
  mounted() {
    this.orderStore.fetchOrders()
    // 如果有token但用户信息为空，获取用户信息
    if (localStorage.getItem('token') && !this.userStore.currentUser) {
      this.userStore.fetchUser()
    }
  },
  methods: {
    logout() {
      this.userStore.logout()
      this.$router.push('/login')
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
</style>