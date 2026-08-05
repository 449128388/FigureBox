<!--
  LoginView.vue - 登录视图（步骤 0）
  props:  serverError / submitting / submittingText / passwordVisible
  emits: submit / toggle-pwd
-->
<template>
  <div class="view active">
    <div class="auth-title">登录</div>
    <div class="form-group">
      <label class="form-label">邮箱</label>
      <input
        type="email"
        class="form-input"
        v-model="loginForm.email"
        placeholder="请输入邮箱地址"
        @keyup.enter="$emit('submit')"
      >
    </div>
    <div class="form-group">
      <label class="form-label">密码</label>
      <div class="input-wrap">
        <input
          :type="passwordVisible ? 'text' : 'password'"
          class="form-input"
          v-model="loginForm.password"
          placeholder="请输入密码"
          style="padding-right:40px;"
          @keyup.enter="$emit('submit')"
        >
        <span class="input-suffix" @click="$emit('toggle-pwd')">
          <!-- 闭眼图标（密文态） -->
          <svg v-if="!passwordVisible" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/><circle cx="12" cy="12" r="3"/>
          </svg>
          <!-- 睁眼图标（明文态） -->
          <svg v-else width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M17.94 17.94A10.07 10.07 0 0 1 12 20c-7 0-11-8-11-8a18.45 18.45 0 0 1 5.06-5.94M9.9 4.24A9.12 9.12 0 0 1 12 4c7 0 11 8 11 8a18.5 18.5 0 0 1-2.16 3.19m-6.72-1.07a3 3 0 1 1-4.24-4.24"/>
            <line x1="1" y1="1" x2="23" y2="23"/>
          </svg>
        </span>
      </div>
    </div>
    <div v-if="serverError" class="form-hint error" style="margin-bottom: 16px; margin-top: -10px;">{{ serverError }}</div>
    <div class="forgot-link">
      <a @click="$emit('forgot')">忘记密码？</a>
    </div>
    <button class="btn btn-primary" :disabled="submitting" @click="$emit('submit')">
      <span v-if="submitting" class="spinner"></span>
      <span>{{ submittingText }}</span>
    </button>
    <div class="auth-footer">
      还没有账号？ <a @click="$emit('register')">立即注册</a>
    </div>
  </div>
</template>

<script>
export default {
  name: 'LoginView',
  props: {
    loginForm: { type: Object, required: true },
    serverError: { type: String, default: '' },
    submitting: { type: Boolean, default: false },
    submittingText: { type: String, default: '登录' },
    passwordVisible: { type: Boolean, default: false }
  },
  emits: ['submit', 'toggle-pwd', 'forgot', 'register']
}
</script>
