<!--
  PanelEmail.vue - 邮箱设置（SMTP 发件配置）面板
  用途：个人中心-系统备份-邮箱设置子面板，配置 SMTP 发件服务器
  业务背景：用于明确告知此配置用于发送密码重置邮件、尾款到期提醒、资产周报等系统通知
  复刻自 profile_settings_v8_email.html 行 1771-1876 的 panel-email 区块（UI 100% 1:1 还原）
  字段 / 状态卡 / 按钮 / 交互均与 HTML 原版一致，区别仅在于：
    1) 状态卡走响应式状态（success/error/warning 三态），HTML 原版只有 2 态（gray 初始 / green 成功）
    2) 授权码 input 多了「已配置」提示（后端 password_set 反馈）
    3) 字段值由 v-model 双向绑定，HTML 原版靠 value="..." 硬编码默认值
  props: active / emailConfig / passwordVisible / testRecipient / savingConfig / testingConnection / sendingTestEmail
        / emailStatusText / emailStatusDetail / emailStatusClass / emailStatusIconColor
  emits: save / test / send-test / toggle-pwd / update:testRecipient
-->
<template>
  <div class="panel" :class="{ active: active }">
    <div class="panel-header">邮箱设置（SMTP 发件配置）</div>
    <div class="panel-body">

      <!-- 功能说明卡片（与 HTML 原版 1:1） -->
      <div class="timeout-info-card" style="background:#f0f9ff;border-color:#bae6fd;">
        <svg class="timeout-info-icon" style="color:#0ea5e9;" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M4 4h16c1.1 0 2 .9 2 2v12c0 1.1-.9 2-2 2H4c-1.1 0-2-.9-2-2V6c0-1.1.9-2 2-2z"/>
          <polyline points="22,6 12,13 2,6"/>
        </svg>
        <div class="timeout-info-text">
          <strong>功能说明</strong>：配置 SMTP 发件服务器后，系统将能够通过该邮箱向用户发送
          <strong>密码重置邮件、尾款到期提醒、资产周报</strong>等系统通知。
          授权码通常可在邮箱服务商的「设置 → 账户安全 → 授权码」中获取。
        </div>
      </div>

      <!-- 连接状态卡片（与 HTML 原版 1:1，状态色由后端 last_test_status 驱动） -->
      <div class="minio-status-card" :class="emailStatusClass" style="margin-top:20px;">
        <svg v-if="emailStatusClass === 'warning'" class="status-icon" viewBox="0 0 24 24" fill="none" stroke-width="2">
          <circle cx="12" cy="12" r="10" :stroke="emailStatusIconColor"/>
          <line x1="12" y1="8" x2="12" y2="12" :stroke="emailStatusIconColor" stroke-linecap="round"/>
          <line x1="12" y1="16" x2="12.01" y2="16" :stroke="emailStatusIconColor" stroke-linecap="round"/>
        </svg>
        <svg v-else class="status-icon" viewBox="0 0 24 24" fill="none" stroke-width="2">
          <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14" :stroke="emailStatusIconColor"/>
          <polyline points="22 4 12 14.01 9 11.01" :stroke="emailStatusIconColor"/>
        </svg>
        <div class="status-text">
          <div>{{ emailStatusText }}</div>
          <div class="detail">{{ emailStatusDetail }}</div>
        </div>
      </div>

      <!-- SMTP 服务器（与 HTML 原版 1:1） -->
      <div class="form-row" style="margin-top:24px;">
        <label class="form-label">SMTP 服务器</label>
        <div class="form-control">
          <div class="input-wrap medium">
            <input
              type="text"
              v-model="emailConfig.smtp_host"
              placeholder="如 smtp.163.com"
            >
          </div>
          <div class="form-hint">发件服务器地址，常见：smtp.163.com / smtp.qq.com / smtp.gmail.com</div>
        </div>
      </div>

      <!-- 发件端口（与 HTML 原版 1:1） -->
      <div class="form-row">
        <label class="form-label">发件端口</label>
        <div class="form-control">
          <div class="input-wrap small">
            <input
              type="number"
              v-model.number="emailConfig.smtp_port"
              placeholder="465"
            >
          </div>
          <div class="form-hint">SSL 通常为 465，STARTTLS 通常为 587，无加密为 25</div>
        </div>
      </div>

      <!-- 发件人邮箱（与 HTML 原版 1:1） -->
      <div class="form-row">
        <label class="form-label">发件人邮箱</label>
        <div class="form-control">
          <div class="input-wrap medium">
            <input
              type="email"
              v-model="emailConfig.smtp_from_email"
              placeholder="noreply@figurebox.com"
            >
          </div>
          <div class="form-hint">系统发件时显示的发件人邮箱地址</div>
        </div>
      </div>

      <!-- 发件人昵称（与 HTML 原版 1:1） -->
      <div class="form-row">
        <label class="form-label">发件人昵称</label>
        <div class="form-control">
          <div class="input-wrap medium">
            <input
              type="text"
              v-model="emailConfig.smtp_from_name"
              placeholder="FigureBox"
            >
          </div>
          <div class="form-hint">邮件中显示的发件人名称，如「FigureBox 系统通知」</div>
        </div>
      </div>

      <!-- 授权码 / 密码（与 HTML 原版 1:1，含明文切换眼睛图标） -->
      <div class="form-row">
        <label class="form-label">授权码 / 密码</label>
        <div class="form-control">
          <div class="input-wrap medium" style="position:relative;">
            <input
              :type="passwordVisible ? 'text' : 'password'"
              v-model="emailConfig.smtp_password"
              :placeholder="emailConfig.smtp_password_set ? '已配置授权码（••••••••），如需更换请输入新授权码' : '请输入邮箱授权码'"
              style="padding-right:36px;"
            >
            <span
              @click="$emit('toggle-pwd')"
              :style="{
                position: 'absolute',
                right: '10px',
                top: '9px',
                cursor: 'pointer',
                color: passwordVisible ? 'var(--primary)' : 'var(--text-tertiary)'
              }"
            >
              <svg v-if="!passwordVisible" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/>
                <circle cx="12" cy="12" r="3"/>
              </svg>
              <svg v-else width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M17.94 17.94A10.07 10.07 0 0 1 12 20c-7 0-11-8-11-8a18.45 18.45 0 0 1 5.06-5.94M9.9 4.24A9.12 9.12 0 0 1 12 4c7 0 11 8 11 8a18.5 18.5 0 0 1-2.16 3.19m-6.72-1.07a3 3 0 1 1-4.24-4.24"/>
                <line x1="1" y1="1" x2="23" y2="23"/>
              </svg>
            </span>
          </div>
          <div class="form-hint">
            建议使用邮箱服务商提供的「授权码」而非登录密码，安全性更高
            <span v-if="emailConfig.smtp_password_set" style="color:var(--success);"> · 已配置</span>
          </div>
        </div>
      </div>

      <!-- 安全连接（与 HTML 原版 1:1） -->
      <div class="form-row">
        <label class="form-label">安全连接</label>
        <div class="form-control">
          <div class="radio-group">
            <label class="radio-item">
              <input type="radio" v-model="emailConfig.smtp_secure_mode" value="ssl"> SSL / TLS
            </label>
            <label class="radio-item">
              <input type="radio" v-model="emailConfig.smtp_secure_mode" value="starttls"> STARTTLS
            </label>
            <label class="radio-item">
              <input type="radio" v-model="emailConfig.smtp_secure_mode" value="none"> 无加密
            </label>
          </div>
        </div>
      </div>

      <!-- 测试收件人 + 发送测试邮件（与 HTML 原版 1:1） -->
      <div class="form-row">
        <label class="form-label">测试收件人</label>
        <div class="form-control">
          <div class="input-group-inline" style="display:flex;gap:10px;align-items:flex-start;">
            <div class="input-wrap" style="flex:1;max-width:360px;">
              <input
                type="email"
                :value="testRecipient"
                @input="$emit('update:testRecipient', $event.target.value)"
                placeholder="输入测试收件邮箱"
              >
            </div>
            <button
              class="btn btn-success btn-sm"
              :disabled="sendingTestEmail"
              @click="$emit('send-test')"
            >
              <span
                v-if="sendingTestEmail"
                style="display:inline-block;width:14px;height:14px;border:2px solid #fff;border-top-color:transparent;border-radius:50%;animation:spin 0.8s linear infinite;vertical-align:middle;margin-right:6px;"
              />
              <svg v-else width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" style="display:inline-block;vertical-align:middle;margin-right:4px;">
                <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/>
                <polyline points="22 4 12 14.01 9 11.01"/>
              </svg>
              {{ sendingTestEmail ? '发送中...' : '发送测试邮件' }}
            </button>
          </div>
          <div class="form-hint">向指定邮箱发送一封测试邮件，验证 SMTP 配置是否正确</div>
        </div>
      </div>

      <!-- 操作按钮区（与 HTML 原版 1:1：仅「保存配置」一个主按钮，「测试连接」由发送测试邮件代替） -->
      <div class="form-actions">
        <button
          class="btn btn-primary"
          :disabled="savingConfig"
          @click="$emit('save')"
        >
          {{ savingConfig ? '保存中...' : '保存配置' }}
        </button>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'PanelEmail',
  props: {
    active: { type: Boolean, default: false },
    emailConfig: { type: Object, required: true },
    passwordVisible: { type: Boolean, default: false },
    testRecipient: { type: String, default: '' },
    savingConfig: { type: Boolean, default: false },
    testingConnection: { type: Boolean, default: false },
    sendingTestEmail: { type: Boolean, default: false },
    emailStatusText: { type: String, default: '尚未验证' },
    emailStatusDetail: { type: String, default: '请填写下方配置并点击「测试连接」验证发件功能是否正常' },
    emailStatusClass: { type: String, default: '' },
    emailStatusIconColor: { type: String, default: '#9499a0' }
  },
  emits: ['save', 'test', 'send-test', 'toggle-pwd', 'update:testRecipient']
}
</script>

<style scoped>
/*
  PanelEmail.vue 独立 scoped 样式：之前没写 <style scoped>，导致 .panel { display: none } 不生效，
  邮箱设置内容会在「基本资料 / 头像设置 / 隐私设置 / 推送设置 / 账号安全 / MinIO 设置 / 超时登出 / 系统备份 / 账号注销」
  9 个面板下方"穿透"出来（Vue 3 scoped CSS 不会跨组件继承 .panel 样式，必须在本组件内独立声明）。
  视觉规范 100% 对齐 profile_settings_v8_email.html 的 panel-email 区块。
*/
.panel {
  background: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.06);
  overflow: hidden;
  display: none;
}
.panel.active {
  display: block;
  animation: fadeIn 0.3s ease;
}
@keyframes fadeIn {
  from { opacity: 0; transform: translateY(8px); }
  to { opacity: 1; transform: translateY(0); }
}
@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}
.panel-header {
  padding: 20px 24px;
  border-bottom: 1px solid #e3e5e7;
  font-size: 18px;
  font-weight: 700;
  color: #18191c;
}
.panel-body { padding: 24px 32px 32px; }

.form-row {
  display: flex;
  align-items: flex-start;
  max-width: 640px;
  margin: 0 auto 24px;
}
.form-label {
  width: 110px;
  text-align: right;
  padding-right: 20px;
  padding-top: 9px;
  font-size: 14px;
  color: #61666d;
  flex-shrink: 0;
  white-space: nowrap;
}
.form-control { flex: 1; min-width: 0; }
.input-wrap { position: relative; max-width: 480px; }
.input-wrap.medium { max-width: 360px; }  /* 与 HTML 原版 .input-wrap.medium { max-width: 360px } 一致 */
.input-wrap.small { max-width: 200px; }
.form-hint { margin-top: 6px; font-size: 12px; color: #9499a0; }

input[type="text"], input[type="email"], input[type="number"], input[type="password"] {
  width: 100%;
  padding: 9px 12px;
  border: 1px solid #e3e5e7;
  border-radius: 6px;
  background: #fff;
  font-size: 14px;
  color: #18191c;
  outline: none;
  transition: all 0.2s;
  font-family: inherit;
}
input:focus { border-color: #00a1d6; box-shadow: 0 0 0 3px rgba(0, 161, 214, 0.15); }
input::placeholder { color: #9499a0; }

.radio-group { display: flex; gap: 24px; padding-top: 6px; flex-wrap: wrap; }
.radio-item {
  display: flex; align-items: center; gap: 6px; font-size: 14px; color: #18191c; cursor: pointer; user-select: none;
}
.radio-item input[type="radio"] {
  appearance: none; width: 16px; height: 16px; border: 2px solid #c9cdd4; border-radius: 50%;
  outline: none; cursor: pointer; transition: all 0.2s; position: relative; padding: 0; margin: 0;
}
.radio-item input[type="radio"]:checked { border-color: #00a1d6; }
.radio-item input[type="radio"]:checked::after {
  content: ""; position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%);
  width: 8px; height: 8px; background: #00a1d6; border-radius: 50%;
}

.timeout-info-card {
  display: flex;
  align-items: flex-start;
  gap: 12px;
  padding: 16px 20px;
  border-radius: 8px;
  background: #f6f7f8;
  border: 1px solid #e3e5e7;
  max-width: 640px;
  margin: 0 auto 24px;
}
.timeout-info-icon {
  width: 20px; height: 20px;
  color: #00a1d6;
  flex-shrink: 0;
  margin-top: 1px;
}
.timeout-info-text {
  font-size: 13px;
  color: #61666d;
  line-height: 1.7;
}
.timeout-info-text strong { color: #18191c; }

.minio-status-card {
  display: flex; align-items: center; gap: 16px; padding: 16px 20px;
  background: #f6ffed; border: 1px solid #b7eb8f; border-radius: 8px;
  max-width: 640px; margin: 0 auto 24px;
}
.minio-status-card.warning { background: #fffbe6; border-color: #ffe58f; }
.minio-status-card.error { background: #fff2f0; border-color: #ffccc7; }
.status-icon { width: 32px; height: 32px; flex-shrink: 0; }
.status-text { font-size: 14px; color: #52c41a; font-weight: 500; }
.minio-status-card.warning .status-text { color: #faad14; }
.minio-status-card.error .status-text { color: #f25d8e; }
.status-text .detail { font-size: 12px; font-weight: normal; color: #9499a0; margin-top: 2px; }

.btn {
  display: inline-flex; align-items: center; justify-content: center; gap: 6px;
  padding: 9px 24px; border-radius: 6px; font-size: 14px; font-weight: 500;
  cursor: pointer; border: none; outline: none; transition: all 0.2s;
}
.btn-primary { background: #00a1d6; color: #fff; }
.btn-primary:hover { background: #008db1; }
.btn-success { background: #52c41a; color: #fff; }
.btn-success:hover { background: #389e0d; }
.btn-sm { padding: 6px 16px; font-size: 13px; }
.btn:disabled { opacity: 0.5; cursor: not-allowed; }
.form-actions { margin-top: 8px; display: flex; justify-content: center; gap: 16px; }

@media (max-width: 900px) {
  .form-row { flex-direction: column; }
  .form-label { text-align: left; width: auto; padding: 0 0 6px; }
  .form-actions { padding-left: 0; }
}
</style>
