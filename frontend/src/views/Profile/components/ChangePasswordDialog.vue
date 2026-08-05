<!--
  ChangePasswordDialog.vue - 修改登录密码弹窗（个人中心-账号安全）

  功能说明：
  - UI 结构对齐 profile_settings_v6_backup.html「修改密码 Modal」（当前密码/新密码+强度条/确认密码+不一致提示）
  - 纯展示组件：表单值 / 错误 / 密码可见性 / 强度 / 提交中状态均由父组件透传，本组件仅做 v-model 绑定与事件抛出
  - emits: close（关闭弹窗）/ submit（点击确认修改）
-->
<template>
  <el-dialog
    :model-value="visible"
    title="修改密码"
    width="460px"
    :close-on-click-modal="false"
    @close="$emit('close')"
  >
    <div class="pwd-body">
      <!-- 服务端错误（内联展示，如当前密码不正确） -->
      <div v-if="errors.server" class="form-hint server-error">
        {{ errors.server }}
      </div>

      <!-- 当前密码 -->
      <div class="form-row">
        <label class="form-label">当前密码</label>
        <div class="form-control">
          <div class="input-wrap">
            <input
              v-model="form.current"
              :type="passwordVisible.current ? 'text' : 'password'"
              placeholder="请输入当前登录密码"
            >
            <span class="pwd-eye" @click="passwordVisible.current = !passwordVisible.current">
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/><circle cx="12" cy="12" r="3"/>
              </svg>
            </span>
          </div>
          <div v-if="errors.current" class="form-hint field-error">{{ errors.current }}</div>
        </div>
      </div>

      <!-- 新密码 -->
      <div class="form-row">
        <label class="form-label">新密码</label>
        <div class="form-control">
          <div class="input-wrap">
            <input
              v-model="form.new"
              :type="passwordVisible.new ? 'text' : 'password'"
              placeholder="8-20位，建议包含字母与数字"
            >
            <span class="pwd-eye" @click="passwordVisible.new = !passwordVisible.new">
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/><circle cx="12" cy="12" r="3"/>
              </svg>
            </span>
          </div>
          <!-- 密码强度条 -->
          <div class="strength-bar" :class="{ shown: strengthShown }">
            <div
              v-for="(active, idx) in strengthSegments"
              :key="idx"
              class="strength-seg"
              :style="{ background: active ? strengthColor : '#e3e5e7' }"
            ></div>
          </div>
          <div
            class="strength-text"
            :class="{ shown: strengthShown }"
            :style="{ color: strengthColor }"
          >
            密码强度：{{ strengthLabel }}
          </div>
          <div v-if="errors.new" class="form-hint field-error">{{ errors.new }}</div>
        </div>
      </div>

      <!-- 确认密码 -->
      <div class="form-row">
        <label class="form-label">确认密码</label>
        <div class="form-control">
          <div class="input-wrap">
            <input
              v-model="form.confirm"
              :type="passwordVisible.confirm ? 'text' : 'password'"
              placeholder="请再次输入新密码"
            >
            <span class="pwd-eye" @click="passwordVisible.confirm = !passwordVisible.confirm">
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/><circle cx="12" cy="12" r="3"/>
              </svg>
            </span>
          </div>
          <div v-if="errors.confirm" class="form-hint field-error">{{ errors.confirm }}</div>
        </div>
      </div>
    </div>

    <template #footer>
      <button class="btn btn-outline" @click="$emit('close')">取消</button>
      <button class="btn btn-primary" :disabled="submitting" @click="$emit('submit')">
        {{ submitting ? '修改中...' : '确认修改' }}
      </button>
    </template>
  </el-dialog>
</template>

<script>
export default {
  name: 'ChangePasswordDialog',
  props: {
    visible: { type: Boolean, default: false },
    form: { type: Object, default: () => ({ current: '', new: '', confirm: '' }) },
    errors: { type: Object, default: () => ({ current: '', new: '', confirm: '', server: '' }) },
    passwordVisible: { type: Object, default: () => ({ current: false, new: false, confirm: false }) },
    strengthSegments: { type: Array, default: () => [] },
    strengthLabel: { type: String, default: '未输入' },
    strengthColor: { type: String, default: '#e3e5e7' },
    strengthShown: { type: Boolean, default: false },
    submitting: { type: Boolean, default: false }
  },
  emits: ['close', 'submit']
}
</script>

<style scoped>
.pwd-body { padding-top: 4px; }

.form-row {
  display: flex;
  align-items: flex-start;
  margin-bottom: 18px;
}
.form-row:last-child { margin-bottom: 0; }
.form-label {
  width: 90px;
  text-align: right;
  padding-right: 16px;
  padding-top: 9px;
  font-size: 14px;
  color: #61666d;
  flex-shrink: 0;
  white-space: nowrap;
}
.form-control { flex: 1; min-width: 0; }

.input-wrap {
  position: relative;
}
.input-wrap input {
  width: 100%;
  box-sizing: border-box;
  padding: 8px 36px 8px 12px;
  font-size: 14px;
  border: 1px solid #e3e5e7;
  border-radius: 6px;
  background-color: #fff;
  color: #18191c;
  transition: border-color 0.2s;
  outline: none;
}
.input-wrap input:hover { border-color: #c9cdd4; }
.input-wrap input:focus { border-color: #00a1d6; }
.pwd-eye {
  position: absolute;
  right: 10px;
  top: 9px;
  cursor: pointer;
  color: #9499a0;
  display: inline-flex;
}
.pwd-eye:hover { color: #00a1d6; }

/* 密码强度条 */
.strength-bar {
  display: flex;
  gap: 4px;
  margin-top: 8px;
  opacity: 0;
  transition: opacity 0.3s;
}
.strength-bar.shown { opacity: 1; }
.strength-seg {
  flex: 1;
  height: 4px;
  border-radius: 2px;
  transition: background 0.3s;
}
.strength-text {
  font-size: 12px;
  margin-top: 4px;
  opacity: 0;
  transition: opacity 0.3s;
}
.strength-text.shown { opacity: 1; }

/* 内联错误提示 */
.form-hint { margin-top: 6px; font-size: 12px; }
.field-error { color: #ff4d4f; }
.server-error {
  color: #ff4d4f;
  padding: 8px 12px;
  background: #fff2f0;
  border: 1px solid #ffccc7;
  border-radius: 6px;
  margin-bottom: 18px;
}

/* 按钮 */
.btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
  padding: 8px 20px;
  border-radius: 6px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  border: none;
  outline: none;
  transition: all 0.2s;
}
.btn-primary { background: #00a1d6; color: #fff; }
.btn-primary:hover { background: #008db1; }
.btn-primary:disabled { opacity: 0.5; cursor: not-allowed; }
.btn-outline {
  background: #fff;
  color: #61666d;
  border: 1px solid #c9cdd4;
}
.btn-outline:hover { border-color: #00a1d6; color: #00a1d6; }
.btn + .btn { margin-left: 12px; }
</style>
