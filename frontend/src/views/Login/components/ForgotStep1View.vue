<!--
  ForgotStep1View.vue - 忘记密码 - 验证邮箱（步骤 1）
  props:  stepState / forgotForm / forgotErrors / sendingCode / verifyingCode / sendCooldown
  emits: back / send-code / next
-->
<template>
  <div class="view active">
    <div class="back-link" @click="$emit('back')">
      <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
        <polyline points="15 18 9 12 15 6"/>
      </svg>
      返回登录
    </div>
    <div class="auth-title" style="margin-bottom: 20px;">重置密码</div>

    <div class="step-bar">
      <div :class="['step-item', stepState.step1]">
        <div class="step-num">
          <svg v-if="stepState.step1 === 'completed'" width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="#fff" stroke-width="3">
            <polyline points="20 6 9 17 4 12"/>
          </svg>
          <span v-else>1</span>
        </div>
        <span>验证邮箱</span>
      </div>
      <div :class="['step-line', stepState.line1]"></div>
      <div :class="['step-item', stepState.step2]">
        <div class="step-num">2</div>
        <span>设置新密码</span>
      </div>
    </div>

    <div class="form-group">
      <label class="form-label">邮箱地址</label>
      <input
        type="email"
        class="form-input"
        :class="{ error: forgotErrors.email }"
        v-model="forgotForm.email"
        placeholder="请输入注册时绑定的邮箱"
        :disabled="sendingCode"
      >
      <div :class="['form-hint', { error: forgotErrors.email }]">
        {{ forgotErrors.email || '验证码将发送至该邮箱' }}
      </div>
    </div>
    <div class="form-group">
      <label class="form-label">验证码</label>
      <div class="code-group">
        <div class="input-wrap" style="flex:1;">
          <input
            type="text"
            class="form-input"
            :class="{ error: forgotErrors.code }"
            v-model="forgotForm.code"
            placeholder="6位验证码"
            maxlength="6"
            style="text-align:center;letter-spacing:4px;"
            @keyup.enter="$emit('next')"
          >
        </div>
        <button
          class="btn btn-outline btn-sm"
          :disabled="sendingCode || sendCooldown > 0"
          @click="$emit('send-code')"
        >
          <span v-if="sendingCode">发送中...</span>
          <span v-else-if="sendCooldown > 0">{{ sendCooldown }}s 后重发</span>
          <span v-else>获取验证码</span>
        </button>
      </div>
      <div :class="['form-hint', { error: forgotErrors.code }]" v-if="forgotErrors.code">
        {{ forgotErrors.code }}
      </div>
    </div>
    <button class="btn btn-primary" :disabled="verifyingCode" @click="$emit('next')">
      <span v-if="verifyingCode" class="spinner"></span>
      <span>下一步</span>
    </button>
  </div>
</template>

<script>
export default {
  name: 'ForgotStep1View',
  props: {
    stepState: { type: Object, required: true },
    forgotForm: { type: Object, required: true },
    forgotErrors: { type: Object, required: true },
    sendingCode: { type: Boolean, default: false },
    verifyingCode: { type: Boolean, default: false },
    sendCooldown: { type: Number, default: 0 }
  },
  emits: ['back', 'send-code', 'next']
}
</script>
