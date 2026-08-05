<!--
  PanelTimeout.vue - 超时登出设置面板
  props: active / timeoutConfig / savingTimeout
  emits: select-timeout（minutes）/ save
-->
<template>
  <div class="panel" :class="{ active: active }">
    <div class="panel-header">超时登出设置</div>
    <div class="panel-body">
      <div class="timeout-info-card">
        <svg class="timeout-info-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <circle cx="12" cy="12" r="10"/>
          <line x1="12" y1="16" x2="12" y2="12"/>
          <line x1="12" y1="8" x2="12.01" y2="8"/>
        </svg>
        <div class="timeout-info-text">
          <strong>安全提示</strong>：当页面在设定时间内无任何操作（鼠标移动、点击、键盘输入），系统将自动退出登录状态，防止他人未经授权访问你的资产数据。该设置仅对当前设备生效，建议公共场合使用较短时长。
        </div>
      </div>

      <div class="form-row">
        <label class="form-label">超时时间</label>
        <div class="form-control">
          <div class="timeout-options">
            <label
              class="timeout-option"
              :class="{ selected: timeoutConfig.timeout_minutes === 30 }"
              @click="$emit('select-timeout', 30)"
            >
              <input type="radio" name="timeout" :value="30" :checked="timeoutConfig.timeout_minutes === 30">
              <div class="timeout-option-text">
                <div class="timeout-option-label">30分钟</div>
                <div class="timeout-option-desc">适合公共场所或多人共用设备</div>
              </div>
            </label>
            <label
              class="timeout-option"
              :class="{ selected: timeoutConfig.timeout_minutes === 60 }"
              @click="$emit('select-timeout', 60)"
            >
              <input type="radio" name="timeout" :value="60" :checked="timeoutConfig.timeout_minutes === 60">
              <div class="timeout-option-text">
                <div class="timeout-option-label">1小时</div>
                <div class="timeout-option-desc">兼顾安全与便利的推荐设置</div>
              </div>
            </label>
            <label
              class="timeout-option"
              :class="{ selected: timeoutConfig.timeout_minutes === 120 }"
              @click="$emit('select-timeout', 120)"
            >
              <input type="radio" name="timeout" :value="120" :checked="timeoutConfig.timeout_minutes === 120">
              <div class="timeout-option-text">
                <div class="timeout-option-label">2小时</div>
                <div class="timeout-option-desc">适合办公室等相对安全的环境</div>
              </div>
            </label>
            <label
              class="timeout-option"
              :class="{ selected: timeoutConfig.timeout_minutes === 180 }"
              @click="$emit('select-timeout', 180)"
            >
              <input type="radio" name="timeout" :value="180" :checked="timeoutConfig.timeout_minutes === 180">
              <div class="timeout-option-text">
                <div class="timeout-option-label">3 小时</div>
                <div class="timeout-option-desc">适合家庭个人电脑等私密环境</div>
              </div>
            </label>
            <label
              class="timeout-option"
              :class="{ selected: timeoutConfig.timeout_minutes === 0 }"
              @click="$emit('select-timeout', 0)"
            >
              <input type="radio" name="timeout" :value="0" :checked="timeoutConfig.timeout_minutes === 0">
              <div class="timeout-option-text">
                <div class="timeout-option-label">从不超时 <span class="not-recommend">（不推荐）</span></div>
                <div class="timeout-option-desc">保持永久登录，仅在手动退出时失效（不推荐）</div>
              </div>
            </label>
          </div>
        </div>
      </div>

      <div class="form-row">
        <label class="form-label">倒计时提醒</label>
        <div class="form-control">
          <div class="radio-group">
            <label class="radio-item"><input type="radio" v-model="timeoutConfig.timeout_warning" :value="true"> 超时前 30 秒弹窗提醒</label>
            <label class="radio-item"><input type="radio" v-model="timeoutConfig.timeout_warning" :value="false"> 直接登出，不提醒</label>
          </div>
          <div class="form-hint">开启提醒后可在弹窗中点击"保持登录"延长当前会话</div>
        </div>
      </div>

      <div class="form-actions">
        <button class="btn btn-primary" @click="$emit('save')" :disabled="savingTimeout">
          <span v-if="savingTimeout">保存中...</span>
          <span v-else>保存设置</span>
        </button>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'PanelTimeout',
  props: {
    active: { type: Boolean, default: false },
    timeoutConfig: { type: Object, required: true },
    savingTimeout: { type: Boolean, default: false }
  },
  emits: ['select-timeout', 'save']
}
</script>

<style scoped>
.panel { background: #fff; border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.06); overflow: hidden; display: none; }
.panel.active { display: block; animation: fadeIn 0.3s ease; }
@keyframes fadeIn { from { opacity: 0; transform: translateY(8px); } to { opacity: 1; transform: translateY(0); } }
.panel-header { padding: 20px 24px; border-bottom: 1px solid #e3e5e7; font-size: 18px; font-weight: 700; color: #18191c; }
.panel-body { padding: 24px 32px 32px; }

.timeout-info-card {
  display: flex; align-items: flex-start; gap: 12px; padding: 16px 20px;
  border-radius: 8px; background: #f6f7f8; border: 1px solid #e3e5e7;
  max-width: 640px; margin: 0 auto 24px;
}
.timeout-info-icon { width: 20px; height: 20px; color: #00a1d6; flex-shrink: 0; margin-top: 1px; }
.timeout-info-text { font-size: 13px; color: #61666d; line-height: 1.7; }
.timeout-info-text strong { color: #18191c; }

.form-row { display: flex; align-items: flex-start; max-width: 640px; margin: 0 auto 24px; }
.form-label { width: 110px; text-align: right; padding-right: 20px; padding-top: 9px; font-size: 14px; color: #61666d; flex-shrink: 0; white-space: nowrap; }
.form-control { flex: 1; min-width: 0; }
.form-hint { margin-top: 6px; font-size: 12px; color: #9499a0; }

.timeout-options { display: flex; flex-direction: column; gap: 12px; max-width: 480px; }
.timeout-option {
  display: flex; align-items: center; gap: 12px; padding: 14px 16px;
  border: 1px solid #e3e5e7; border-radius: 8px; cursor: pointer; transition: all 0.2s; background: #fff;
}
.timeout-option:hover { border-color: #00a1d6; background: rgba(0, 161, 214, 0.04); }
.timeout-option.selected { border-color: #00a1d6; background: rgba(0, 161, 214, 0.06); box-shadow: 0 0 0 3px rgba(0, 161, 214, 0.1); }
.timeout-option input[type="radio"] {
  appearance: none; width: 18px; height: 18px; border: 2px solid #c9ccd0; border-radius: 50%;
  outline: none; cursor: pointer; transition: all 0.2s; position: relative; flex-shrink: 0;
}
.timeout-option input[type="radio"]:checked { border-color: #00a1d6; }
.timeout-option input[type="radio"]:checked::after {
  content: ""; position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%);
  width: 9px; height: 9px; background: #00a1d6; border-radius: 50%;
}
.timeout-option-text { display: flex; flex-direction: column; gap: 2px; }
.timeout-option-label { font-size: 14px; font-weight: 500; color: #18191c; }
.timeout-option-desc { font-size: 12px; color: #9499a0; }
.not-recommend { color: #ff4d4f; font-size: 12px; font-weight: 400; }

.radio-group { display: flex; gap: 24px; padding-top: 6px; }
.radio-item { display: flex; align-items: center; gap: 6px; font-size: 14px; color: #18191c; cursor: pointer; user-select: none; }
.radio-item input[type="radio"] {
  appearance: none; width: 16px; height: 16px; border: 2px solid #c9cdd4; border-radius: 50%;
  outline: none; cursor: pointer; transition: all 0.2s; position: relative; padding: 0;
}
.radio-item input[type="radio"]:checked { border-color: #00a1d6; }
.radio-item input[type="radio"]:checked::after {
  content: ""; position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%);
  width: 8px; height: 8px; background: #00a1d6; border-radius: 50%;
}

.btn {
  display: inline-flex; align-items: center; justify-content: center; gap: 6px;
  padding: 9px 24px; border-radius: 6px; font-size: 14px; font-weight: 500;
  cursor: pointer; border: none; outline: none; transition: all 0.2s;
}
.btn-primary { background: #00a1d6; color: #fff; }
.btn-primary:hover { background: #008db1; }
.btn-primary:disabled { opacity: 0.7; cursor: not-allowed; }
.form-actions { margin-top: 8px; display: flex; justify-content: center; gap: 16px; }

@media (max-width: 900px) {
  .form-row { flex-direction: column; }
  .form-label { text-align: left; width: auto; padding: 0 0 6px; }
  .form-actions { padding-left: 0; }
}
</style>
