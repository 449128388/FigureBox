<!--
  Login.vue - 用户登录页面（高保真 + 忘记密码重置密码流程）

  功能说明：
  - 4 个视图（与 login_with_forgot_password.html 高保真 1:1）：
    1. login        登录
    2. forgot-1     忘记密码-验证邮箱（输入邮箱 + 6 位验证码）
    3. forgot-2     忘记密码-设置新密码（密码强度 + 确认密码）
    4. success      密码重置成功
  - 业务逻辑全部走 useLoginFlow composable
  - 4 个子视图为纯展示组件，UI 与 login_with_forgot_password.html 1:1
  - 输入框回车直接触发表单提交
-->
<template>
  <div class="auth-page">
    <div class="auth-card">
      <transition name="view-fade" mode="out-in">
        <LoginView
          v-if="currentView === 'login'"
          key="login"
          :login-form="loginForm"
          :server-error="serverError"
          :submitting="submittingLogin"
          :submitting-text="submittingText"
          :password-visible="loginPasswordVisible"
          @submit="handleLogin"
          @toggle-pwd="loginPasswordVisible = !loginPasswordVisible"
          @forgot="goToForgot"
          @register="onRegisterClick"
        />
        <ForgotStep1View
          v-else-if="currentView === 'forgot-1'"
          key="forgot-1"
          :step-state="stepState"
          :forgot-form="forgotForm"
          :forgot-errors="forgotErrors"
          :sending-code="sendingCode"
          :verifying-code="verifyingCode"
          :send-cooldown="sendCooldown"
          @back="goToLogin"
          @send-code="sendForgotCode"
          @next="goToForgotStep2"
        />
        <ForgotStep2View
          v-else-if="currentView === 'forgot-2'"
          key="forgot-2"
          :step-state="stepState"
          :reset-form="resetForm"
          :reset-errors="resetErrors"
          :password-visible="resetPasswordVisible"
          :submitting="submittingReset"
          :submitting-text="submittingResetText"
          :strength-score="strengthScore"
          :strength-label="strengthLabel"
          :strength-color="strengthColor"
          :strength-segments="strengthSegments"
          :strength-shown="strengthShown"
          @back="goToForgotStep1"
          @submit="submitResetPwd"
          @toggle-pwd="toggleResetPwdVisible"
        />
        <ResetSuccessView
          v-else-if="currentView === 'success'"
          key="success"
          @back="goToLogin"
        />
      </transition>
    </div>
  </div>
</template>

<script>
import LoginView from './Login/components/LoginView.vue'
import ForgotStep1View from './Login/components/ForgotStep1View.vue'
import ForgotStep2View from './Login/components/ForgotStep2View.vue'
import ResetSuccessView from './Login/components/ResetSuccessView.vue'
import { useLoginFlow } from './Login/composables/useLoginFlow'

export default {
  name: 'Login',
  components: { LoginView, ForgotStep1View, ForgotStep2View, ResetSuccessView },
  setup() {
    const flow = useLoginFlow()
    const toggleResetPwdVisible = (key) => {
      flow.resetPasswordVisible.value[key] = !flow.resetPasswordVisible.value[key]
    }
    return { ...flow, toggleResetPwdVisible }
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
  position: relative;
  overflow: hidden;
  transition: box-shadow 0.3s;
}
.auth-card:hover {
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.12);
}

/* ===== 视图过渡动画 ===== */
.view-fade-enter-active,
.view-fade-leave-active {
  transition: all 0.35s ease;
}
.view-fade-enter-from {
  opacity: 0;
  transform: translateY(12px);
}
.view-fade-leave-to {
  opacity: 0;
  transform: translateY(-8px);
}

/* ===== 子组件样式共享（与 HTML 高保真 1:1）===== */
:deep(.view) {
  animation: fadeSlideIn 0.35s ease;
}
@keyframes fadeSlideIn {
  from { opacity: 0; transform: translateY(12px); }
  to { opacity: 1; transform: translateY(0); }
}

:deep(.auth-title) {
  font-size: 24px;
  font-weight: 700;
  color: #333;
  text-align: center;
  margin-bottom: 32px;
}

:deep(.form-group) {
  margin-bottom: 20px;
}
:deep(.form-label) {
  display: block;
  font-size: 14px;
  font-weight: 600;
  color: #333;
  margin-bottom: 8px;
}
:deep(.form-input) {
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
}
:deep(.form-input:focus) {
  border-color: #4caf50;
  box-shadow: 0 0 0 3px rgba(76, 175, 80, 0.15);
}
:deep(.form-input::placeholder) {
  color: #999;
}
:deep(.form-input.error) {
  border-color: #f25d8e;
  box-shadow: 0 0 0 3px rgba(242, 93, 142, 0.1);
}
:deep(.form-input:disabled) {
  background: #f5f5f5;
  color: #999;
  cursor: not-allowed;
}

:deep(.input-wrap) {
  position: relative;
}
:deep(.input-suffix) {
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
:deep(.input-suffix:hover) {
  color: #666;
}

:deep(.form-hint) {
  margin-top: 6px;
  font-size: 12px;
  color: #999;
  transition: opacity 0.2s;
}
:deep(.form-hint.error) {
  color: #f25d8e;
}
:deep(.form-hint.success) {
  color: #52c41a;
}

:deep(.btn) {
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
:deep(.btn-primary) {
  background: #4caf50;
  color: #fff;
}
:deep(.btn-primary:hover) {
  background: #43a047;
}
:deep(.btn-primary:disabled) {
  opacity: 0.7;
  cursor: not-allowed;
}
:deep(.btn-outline) {
  background: #fff;
  color: #666;
  border: 1px solid #bdbdbd;
}
:deep(.btn-outline:hover:not(:disabled)) {
  border-color: #4caf50;
  color: #4caf50;
}
:deep(.btn-outline:disabled) {
  opacity: 0.6;
  cursor: not-allowed;
  background: #fafafa;
}
:deep(.btn-sm) {
  padding: 8px 16px;
  font-size: 13px;
  width: auto;
  white-space: nowrap;
}

:deep(.auth-footer) {
  text-align: center;
  margin-top: 20px;
  font-size: 14px;
  color: #666;
}
:deep(.auth-footer a) {
  color: #4caf50;
  text-decoration: none;
  cursor: pointer;
  font-weight: 500;
}
:deep(.auth-footer a:hover) {
  text-decoration: underline;
}

:deep(.forgot-link) {
  text-align: right;
  margin-top: -10px;
  margin-bottom: 20px;
  font-size: 13px;
}
:deep(.forgot-link a) {
  color: #999;
  text-decoration: none;
  cursor: pointer;
  transition: color 0.2s;
}
:deep(.forgot-link a:hover) {
  color: #4caf50;
}

/* Step indicator */
:deep(.step-bar) {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 12px;
  margin-bottom: 28px;
}
:deep(.step-item) {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 13px;
  font-weight: 500;
  color: #999;
  transition: all 0.3s;
}
:deep(.step-item.active) {
  color: #4caf50;
}
:deep(.step-item.completed) {
  color: #52c41a;
}
:deep(.step-num) {
  width: 24px;
  height: 24px;
  border-radius: 50%;
  background: #e8e8e8;
  color: #999;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 12px;
  font-weight: 600;
  transition: all 0.3s;
}
:deep(.step-item.active .step-num) {
  background: #4caf50;
  color: #fff;
}
:deep(.step-item.completed .step-num) {
  background: #52c41a;
  color: #fff;
}
:deep(.step-line) {
  width: 40px;
  height: 2px;
  background: #e8e8e8;
  border-radius: 1px;
  transition: background 0.3s;
}
:deep(.step-line.active) {
  background: #4caf50;
}

/* Code input */
:deep(.code-group) {
  display: flex;
  gap: 10px;
  align-items: flex-start;
}
:deep(.code-group .form-input) {
  text-align: center;
  letter-spacing: 4px;
  font-size: 16px;
  font-weight: 600;
}

/* Password strength */
:deep(.strength-bar) {
  display: flex;
  gap: 4px;
  margin-top: 8px;
  transition: opacity 0.3s;
}
:deep(.strength-segment) {
  flex: 1;
  height: 4px;
  border-radius: 2px;
  background: #e8e8e8;
  transition: background 0.3s;
}
:deep(.strength-text) {
  font-size: 12px;
  color: #999;
  margin-top: 4px;
  transition: opacity 0.3s;
}

/* Success state */
:deep(.success-icon) {
  width: 64px;
  height: 64px;
  margin: 0 auto 20px;
  background: rgba(76, 175, 80, 0.08);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
}
:deep(.success-title) {
  font-size: 20px;
  font-weight: 700;
  color: #333;
  text-align: center;
  margin-bottom: 8px;
}
:deep(.success-desc) {
  font-size: 14px;
  color: #666;
  text-align: center;
  margin-bottom: 24px;
  line-height: 1.6;
}

/* Back link */
:deep(.back-link) {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 13px;
  color: #999;
  cursor: pointer;
  margin-bottom: 16px;
  transition: color 0.2s;
  width: fit-content;
}
:deep(.back-link:hover) {
  color: #4caf50;
}

/* Spinner */
:deep(.spinner) {
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
