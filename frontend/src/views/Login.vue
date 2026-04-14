<!--
  Login.vue - 用户登录页面

  功能说明：
  - 提供用户登录表单，包含邮箱和密码输入
  - 表单验证：邮箱格式、密码必填
  - 登录成功后跳转到首页
  - 提供注册入口链接
  - 登录失败时显示错误提示

  维护提示：
  - 使用 userStore.login() 处理登录逻辑
  - 登录成功后使用 Vue Router 导航到首页
  - 表单使用 @submit.prevent 阻止默认提交行为
-->
<template>
  <div class="login-container">
    <h2>登录</h2>
    <form @submit.prevent="handleLogin">
      <div class="form-group">
        <label for="email">邮箱</label>
        <input type="email" id="email" v-model="email" required>
      </div>
      <div class="form-group">
        <label for="password">密码</label>
        <input type="password" id="password" v-model="password" required>
      </div>
      <button type="submit" class="btn">登录</button>
      <p class="register-link">还没有账号？<router-link to="/register">立即注册</router-link></p>
    </form>
  </div>
</template>

<script>
import { useUserStore } from '../store'

export default {
  name: 'Login',
  data() {
    return {
      email: '',
      password: ''
    }
  },
  methods: {
    async handleLogin() {
      const userStore = useUserStore()
      try {
        await userStore.login(this.email, this.password)
        this.$router.push('/')
      } catch (error) {
        alert('登录失败，请检查邮箱和密码')
      }
    }
  }
}
</script>

<style scoped>
.login-container {
  max-width: 400px;
  margin: 100px auto;
  padding: 20px;
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
}

h2 {
  text-align: center;
  margin-bottom: 20px;
  color: #333;
}

.form-group {
  margin-bottom: 15px;
}

label {
  display: block;
  margin-bottom: 5px;
  font-weight: bold;
}

input {
  width: 100%;
  padding: 10px;
  border: 1px solid #ddd;
  border-radius: 4px;
}

.btn {
  width: 100%;
  padding: 10px;
  background-color: #4CAF50;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 16px;
}

.btn:hover {
  background-color: #45a049;
}

.register-link {
  margin-top: 15px;
  text-align: center;
}

.register-link a {
  color: #4CAF50;
  text-decoration: none;
}

.register-link a:hover {
  text-decoration: underline;
}
</style>