<template>
  <div class="header">
    <h2>尾款管理</h2>
    <div class="header-actions">
      <button class="btn btn-add" @click="$emit('openAddForm')">添加订单</button>
      <div class="user-info">
        <span v-if="userStore.isAuthenticated">当前用户：</span>
        <span v-if="userStore.isAuthenticated" class="username" @click="$emit('navigateToProfile')" style="cursor: pointer; color: #2196F3; text-decoration: underline;">{{ userStore.currentUser?.username }}</span>
        <button v-if="userStore.isAuthenticated" class="btn btn-logout" @click="$emit('logout')">退出</button>
      </div>
    </div>
  </div>
</template>

<script>
import { useUserStore } from '../../../store'

export default {
  name: 'OrderHeader',
  emits: ['openAddForm', 'navigateToProfile', 'logout'],
  computed: {
    userStore() {
      return useUserStore()
    }
  }
}
</script>

<style scoped>
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
</style>