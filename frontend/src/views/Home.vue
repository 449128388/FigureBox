<template>
  <div class="home-container">
    <h1>欢迎来到 FigureBox</h1>
    <p>手办管理系统</p>
    <div class="nav-buttons">
      <router-link to="/login" class="btn" v-if="!userStore.isAuthenticated">登录</router-link>
      <router-link to="/register" class="btn" v-if="!userStore.isAuthenticated">注册</router-link>
      <router-link to="/figures" class="btn" v-if="userStore.isAuthenticated">手办管理</router-link>
      <router-link to="/orders" class="btn" v-if="userStore.isAuthenticated">订单管理</router-link>
      <router-link to="/profile" class="btn" v-if="userStore.isAuthenticated">个人资料</router-link>
      <button class="btn btn-logout" v-if="userStore.isAuthenticated" @click="userStore.logout()">退出登录</button>
    </div>
  </div>
</template>

<script>
import { useUserStore } from '../store'

export default {
  name: 'Home',
  computed: {
    userStore() {
      return useUserStore()
    }
  }
}
</script>

<style scoped>
.home-container {
  text-align: center;
  margin-top: 100px;
}

h1 {
  font-size: 36px;
  margin-bottom: 20px;
  color: #333;
}

p {
  font-size: 18px;
  margin-bottom: 40px;
  color: #666;
}

.nav-buttons {
  display: flex;
  justify-content: center;
  gap: 20px;
  flex-wrap: wrap;
}

.btn {
  padding: 10px 20px;
  background-color: #4CAF50;
  color: white;
  text-decoration: none;
  border-radius: 4px;
  font-size: 16px;
  transition: background-color 0.3s;
}

.btn:hover {
  background-color: #45a049;
}

.btn-logout {
  background-color: #f44336;
  border: none;
  cursor: pointer;
}

.btn-logout:hover {
  background-color: #da190b;
}
</style>