<!--
  Register.vue - 用户注册页面（高保真 + 与登录页风格一致）

  功能说明：
  - 与 Login.vue 风格统一：白底卡片 420px + 绿色按钮 + 居中
  - 表单验证：用户名 2-25 位、邮箱格式、密码 8-20 位
  - 密码强度实时显示（弱/中/强/极强，4 段色条）
  - 注册成功后自动登录并跳转到首页
  - 错误提示统一使用 ElMessage（不再用 form-hint error 内联展示）
  - 已有账号提供「立即登录」入口
-->
<template>
  <div class="auth-page">
    <div class="auth-card">
      <div class="auth-title">注册</div>
      <div class="form-group">
        <label class="form-label">用户名</label>
        <input
          type="text"
          class="form-input"
          v-model="username"
          placeholder="2-25 个字符"
          maxlength="25"
          @keyup.enter="handleRegister"
        >
      </div>
      <div class="form-group">
        <label class="form-label">邮箱</label>
        <input
          type="email"
          class="form-input"
          v-model="email"
          placeholder="请输入邮箱地址"
          @keyup.enter="handleRegister"
        >
      </div>
      <div class="form-group">
        <label class="form-label">密码</label>
        <div class="input-wrap">
          <input
            :type="passwordVisible ? 'text' : 'password'"
            class="form-input"
            v-model="password"
            placeholder="8-20 位，建议包含字母与数字"
            style="padding-right: 40px;"
            @keyup.enter="handleRegister"
          >
          <span class="input-suffix" @click="passwordVisible = !passwordVisible">
            <svg v-if="!passwordVisible" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/><circle cx="12" cy="12" r="3"/>
            </svg>
            <svg v-else width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M17.94 17.94A10.07 10.07 0 0 1 12 20c-7 0-11-8-11-8a18.45 18.45 0 0 1 5.06-5.94M9.9 4.24A9.12 9.12 0 0 1 12 4c7 0 11 8 11 8a18.5 18.5 0 0 1-2.16 3.19m-6.72-1.07a3 3 0 1 1-4.24-4.24"/>
              <line x1="1" y1="1" x2="23" y2="23"/>
            </svg>
          </span>
        </div>
        <div class="strength-bar" :style="{ opacity: strengthShown ? 1 : 0 }">
          <div
            v-for="(active, idx) in strengthSegments"
            :key="idx"
            class="strength-segment"
            :style="{ background: active ? strengthColor : '#e8e8e8' }"
          ></div>
        </div>
        <div class="strength-text" :style="{ opacity: strengthShown ? 1 : 0, color: strengthColor }">
          密码强度：{{ strengthLabel }}
        </div>
      </div>
      <button class="btn btn-primary" :disabled="submitting" @click="handleRegister">
        <span v-if="submitting" class="spinner"></span>
        <span>{{ submittingText }}</span>
      </button>
      <div class="auth-footer">
        已有账号？<a @click="goLogin">立即登录</a>
      </div>
    </div>
  </div>
</template>

<script>
import { ElMessage } from 'element-plus'
import { useUserStore } from '../store'

export default {
  name: 'Register',
  data() {
    return {
      username: '',
      email: '',
      password: '',
      submitting: false,
      submittingText: '注册',
      passwordVisible: false
    }
  },
  computed: {
    strengthScore() {
      const val = this.password
      if (!val) return 0
      let score = 0
      if (val.length >= 8) score++
      if (/[a-zA-Z]/.test(val) && /\d/.test(val)) score++
      if (/[^a-zA-Z0-9]/.test(val)) score++
      if (val.length >= 12) score++
      return score
    },
    strengthLabel() {
      return ['未输入', '弱', '中', '强', '极强'][this.strengthScore]
    },
    strengthColor() {
      const colors = ['#e8e8e8', '#ff4d4f', '#faad14', '#4caf50', '#4caf50']
      return colors[this.strengthScore]
    },
    strengthSegments() {
      return [1, 2, 3, 4].map(i => i <= this.strengthScore)
    },
    strengthShown() {
      return this.password.length > 0
    }
  },
  methods: {
    async handleRegister() {
      // 字段级校验（统一使用 ElMessage 提示）
      const username = this.username.trim()
      if (!username) {
        ElMessage.warning('请输入用户名')
        return
      }
      if (username.length < 2 || username.length > 25) {
        ElMessage.warning('用户名长度需在 2-25 位之间')
        return
      }
      const email = this.email.trim()
      if (!email) {
        ElMessage.warning('请输入邮箱地址')
        return
      }
      if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
        ElMessage.warning('请输入有效的邮箱地址')
        return
      }
      if (!this.password) {
        ElMessage.warning('请输入密码')
        return
      }
      if (this.password.length < 8 || this.password.length > 20) {
        ElMessage.warning('密码长度需在 8-20 位之间')
        return
      }

      const userStore = useUserStore()
      this.submitting = true
      this.submittingText = '注册中...'
      try {
        await userStore.register(username, email, this.password)
        ElMessage.success('注册成功，正在跳转...')
        window.location.href = '/home'
      } catch (error) {
        const msg = error.response?.data?.detail || '注册失败，请检查输入信息'
        // 服务端错误统一用 ElMessage.error 提示
        ElMessage.error(msg)
      } finally {
        this.submitting = false
        this.submittingText = '注册'
      }
    },
    goLogin() {
      window.location.href = '/login'
    }
  }
}
</script>

<style scoped>
.auth-page {
  position: fixed;
  inset: 0;
  background: #f5f5f5;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 20px;
  z-index: 100;
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
}
.auth-card {
  background: #fff;
  border-radius: 8px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
  width: 420px;
  max-width: 100%;
  padding: 40px 36px 36px;
  transition: box-shadow 0.3s;
}
.auth-card:hover {
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.12);
}

.auth-title {
  font-size: 24px;
  font-weight: 700;
  color: #333;
  text-align: center;
  margin-bottom: 32px;
}

.form-group {
  margin-bottom: 20px;
}
.form-label {
  display: block;
  font-size: 14px;
  font-weight: 600;
  color: #333;
  margin-bottom: 8px;
}
.form-input {
  width: 100%;
  padding: 11px 14px;
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  background: #fff;
  font-size: 14px;
  color: #333;
  outline: none;
  transition: all 0.2s;
  font-family: inherit;
  box-sizing: border-box;
}
.form-input:focus {
  border-color: #4caf50;
  box-shadow: 0 0 0 3px rgba(76, 175, 80, 0.15);
}
.form-input::placeholder {
  color: #999;
}
.form-input:disabled {
  background: #f5f5f5;
  color: #999;
  cursor: not-allowed;
}

.input-wrap {
  position: relative;
}
.input-suffix {
  position: absolute;
  right: 12px;
  top: 50%;
  transform: translateY(-50%);
  cursor: pointer;
  color: #999;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 4px;
  transition: color 0.2s;
}
.input-suffix:hover {
  color: #666;
}

.btn {
  width: 100%;
  padding: 12px 24px;
  border-radius: 8px;
  font-size: 15px;
  font-weight: 500;
  cursor: pointer;
  border: none;
  outline: none;
  transition: all 0.2s;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  font-family: inherit;
}
.btn-primary {
  background: #4caf50;
  color: #fff;
}
.btn-primary:hover {
  background: #43a047;
}
.btn-primary:disabled {
  opacity: 0.7;
  cursor: not-allowed;
}

.auth-footer {
  text-align: center;
  margin-top: 20px;
  font-size: 14px;
  color: #666;
}
.auth-footer a {
  color: #4caf50;
  text-decoration: none;
  cursor: pointer;
  font-weight: 500;
  margin-left: 4px;
}
.auth-footer a:hover {
  text-decoration: underline;
}

.strength-bar {
  display: flex;
  gap: 4px;
  margin-top: 8px;
  transition: opacity 0.3s;
}
.strength-segment {
  flex: 1;
  height: 4px;
  border-radius: 2px;
  background: #e8e8e8;
  transition: background 0.3s;
}
.strength-text {
  font-size: 12px;
  color: #999;
  margin-top: 4px;
  transition: opacity 0.3s;
}

.spinner {
  width: 16px;
  height: 16px;
  border: 2px solid #fff;
  border-top-color: transparent;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}
@keyframes spin {
  to { transform: rotate(360deg); }
}

@media (max-width: 480px) {
  .auth-card {
    padding: 28px 20px 24px;
  }
}
</style>
