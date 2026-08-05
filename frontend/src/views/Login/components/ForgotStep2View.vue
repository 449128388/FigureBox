<!--
  ForgotStep2View.vue - 忘记密码 - 设置新密码（步骤 2）
  props:  stepState / resetForm / resetErrors / passwordVisible / submitting / submittingText
          / strengthScore / strengthLabel / strengthColor / strengthSegments / strengthShown
  emits: back / submit / toggle-pwd
-->
<template>
  <div class="view active">
    <div class="back-link" @click="$emit('back')">
      <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
        <polyline points="15 18 9 12 15 6"/>
      </svg>
      上一步
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
      <label class="form-label">新密码</label>
      <div class="input-wrap">
        <input
          :type="passwordVisible.pwd ? 'text' : 'password'"
          class="form-input"
          :class="{ error: resetErrors.pwd }"
          v-model="resetForm.pwd"
          placeholder="8-20位，建议包含字母与数字"
          style="padding-right:40px;"
          @keyup.enter="$emit('submit')"
        >
        <span class="input-suffix" @click="$emit('toggle-pwd', 'pwd')">
          <svg v-if="!passwordVisible.pwd" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
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
      <div v-if="resetErrors.pwd" class="form-hint error">{{ resetErrors.pwd }}</div>
    </div>
    <div class="form-group">
      <label class="form-label">确认密码</label>
      <div class="input-wrap">
        <input
          :type="passwordVisible.confirm ? 'text' : 'password'"
          class="form-input"
          :class="{ error: resetErrors.confirm || resetErrors.match }"
          v-model="resetForm.confirm"
          placeholder="请再次输入新密码"
          style="padding-right:40px;"
          @keyup.enter="$emit('submit')"
        >
        <span class="input-suffix" @click="$emit('toggle-pwd', 'confirm')">
          <svg v-if="!passwordVisible.confirm" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/><circle cx="12" cy="12" r="3"/>
          </svg>
          <svg v-else width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M17.94 17.94A10.07 10.07 0 0 1 12 20c-7 0-11-8-11-8a18.45 18.45 0 0 1 5.06-5.94M9.9 4.24A9.12 9.12 0 0 1 12 4c7 0 11 8 11 8a18.5 18.5 0 0 1-2.16 3.19m-6.72-1.07a3 3 0 1 1-4.24-4.24"/>
            <line x1="1" y1="1" x2="23" y2="23"/>
          </svg>
        </span>
      </div>
      <div class="form-hint error" :style="{ opacity: resetErrors.confirm || resetErrors.match ? 1 : 0 }">
        {{ resetErrors.confirm || resetErrors.match || '两次输入的密码不一致' }}
      </div>
    </div>
    <button class="btn btn-primary" :disabled="submitting" @click="$emit('submit')">
      <span v-if="submitting" class="spinner"></span>
      <span>{{ submittingText }}</span>
    </button>
  </div>
</template>

<script>
export default {
  name: 'ForgotStep2View',
  props: {
    stepState: { type: Object, required: true },
    resetForm: { type: Object, required: true },
    resetErrors: { type: Object, required: true },
    passwordVisible: { type: Object, required: true },
    submitting: { type: Boolean, default: false },
    submittingText: { type: String, default: '确认重置' },
    strengthScore: { type: Number, default: 0 },
    strengthLabel: { type: String, default: '未输入' },
    strengthColor: { type: String, default: '#e8e8e8' },
    strengthSegments: { type: Array, required: true },
    strengthShown: { type: Boolean, default: false }
  },
  emits: ['back', 'submit', 'toggle-pwd']
}
</script>
