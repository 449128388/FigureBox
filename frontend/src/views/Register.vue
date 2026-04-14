<!--
  Register.vue - 用户注册页面

  功能说明：
  - 提供用户注册表单，包含用户名、邮箱、密码输入
  - 表单验证：用户名必填、邮箱格式、密码必填
  - 注册成功后自动登录并跳转到首页
  - 提供登录入口链接
  - 注册失败时显示错误提示

  维护提示：
  - 使用 userStore.register() 处理注册逻辑
  - 注册成功后使用 Vue Router 导航到首页
  - 表单使用 @submit.prevent 阻止默认提交行为
  - 可扩展密码强度验证功能
-->
<template>
  <div class="register-container">
    <h2>注册</h2>
    <form @submit.prevent="handleRegister">
      <div class="form-group">
        <label for="username">用户名</label>
        <input type="text" id="username" v-model="username" required>
      </div>
      <div class="form-group">
        <label for="email">邮箱</label>
        <input type="email" id="email" v-model="email" required>
      </div>
      <div class="form-group">
        <label for="password">密码</label>
        <input type="password" id="password" v-model="password" required>
      </div>
      <button type="submit" class="btn">注册</button>
      <p class="login-link">已有账号？<router-link to="/login">立即登录</router-link></p>
    </form>
  </div>
</template>

<script>
import { useUserStore } from '../store'

export default {
  name: 'Register',
  data() {
    return {
      username: '',
      email: '',
      password: ''
    }
  },
  methods: {
    async handleRegister() {
      const userStore = useUserStore()
      try {
        await userStore.register(this.username, this.email, this.password)
        this.$router.push('/')
      } catch (error) {
        alert('注册失败，请检查输入信息')
      }
    }
  }
}
</script>

<style scoped>
.register-container {
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

.login-link {
  margin-top: 15px;
  text-align: center;
}

.login-link a {
  color: #4CAF50;
  text-decoration: none;
}

.login-link a:hover {
  text-decoration: underline;
}
</style>