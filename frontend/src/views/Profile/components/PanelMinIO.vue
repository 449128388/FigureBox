<!--
  PanelMinIO.vue - MinIO 图床设置面板
  props: active / minioConfig / minioStatusText / minioStatusDetail / minioStatusClass / minioStatusIconColor / testingConnection / resettingMinIO
  emits: test / save / reset
-->
<template>
  <div class="panel" :class="{ active: active }">
    <div class="panel-header">MinIO 图床设置</div>
    <div class="panel-body">
      <div class="minio-status-card" :class="minioStatusClass">
        <!-- 未知状态：圆形感叹号 -->
        <svg v-if="minioStatusClass === 'warning'" class="status-icon" viewBox="0 0 24 24" fill="none" stroke-width="2">
          <circle cx="12" cy="12" r="10" :stroke="minioStatusIconColor"/>
          <line x1="12" y1="8" x2="12" y2="13" :stroke="minioStatusIconColor" stroke-linecap="round"/>
          <circle cx="12" cy="16.5" r="1" :fill="minioStatusIconColor"/>
        </svg>
        <!-- 成功/失败状态：对勾 -->
        <svg v-else class="status-icon" viewBox="0 0 24 24" fill="none" stroke-width="2">
          <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14" :stroke="minioStatusIconColor"/>
          <polyline points="22 4 12 14.01 9 11.01" :stroke="minioStatusIconColor"/>
        </svg>
        <div class="status-text">
          <div>{{ minioStatusText }}</div>
          <div class="detail">{{ minioStatusDetail }}</div>
        </div>
      </div>

      <div class="form-row">
        <label class="form-label">服务器地址</label>
        <div class="form-control">
          <div class="input-wrap medium">
            <input type="url" v-model="minioConfig.endpoint" placeholder="http://localhost:9000">
          </div>
          <div class="form-hint">MinIO API 端点地址，包含协议与端口</div>
        </div>
      </div>

      <div class="form-row">
        <label class="form-label">Access Key</label>
        <div class="form-control">
          <div class="input-wrap medium">
            <input type="text" v-model="minioConfig.access_key" placeholder="Access Key">
          </div>
        </div>
      </div>

      <div class="form-row">
        <label class="form-label">Secret Key</label>
        <div class="form-control">
          <div class="input-wrap medium">
            <input type="text" v-model="minioConfig.secret_key" placeholder="Secret Key">
          </div>
          <div class="form-hint">密钥仅保存在本地浏览器，不会上传至 FigureBox 服务器</div>
        </div>
      </div>

      <div class="form-row">
        <label class="form-label">Bucket 名称</label>
        <div class="form-control">
          <div class="input-wrap medium">
            <input type="text" v-model="minioConfig.bucket" placeholder="Bucket 名称">
          </div>
        </div>
      </div>

      <div class="form-row">
        <label class="form-label">图片访问域名</label>
        <div class="form-control">
          <div class="input-wrap medium">
            <input type="url" v-model="minioConfig.public_url" placeholder="http://localhost:25620/figurebox-images">
          </div>
          <div class="form-hint">前端拼接图片 URL 的基地址，通常与服务器地址一致</div>
        </div>
      </div>

      <div class="form-row">
        <label class="form-label">安全连接</label>
        <div class="form-control">
          <div class="radio-group">
            <label class="radio-item"><input type="radio" v-model="minioConfig.secure" :value="false"> HTTP（内网）</label>
            <label class="radio-item"><input type="radio" v-model="minioConfig.secure" :value="true"> HTTPS（公网）</label>
          </div>
        </div>
      </div>

      <div class="form-actions" style="margin-top:24px;">
        <button class="btn btn-success" @click="$emit('test')" :disabled="testingConnection">
          <span v-if="testingConnection">测试中...</span>
          <span v-else>测试连接</span>
        </button>
        <button class="btn btn-primary" @click="$emit('save')">保存配置</button>
        <button class="btn btn-outline" @click="$emit('reset')" :disabled="resettingMinIO">
          <span v-if="resettingMinIO">恢复中...</span>
          <span v-else>恢复默认</span>
        </button>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'PanelMinIO',
  props: {
    active: { type: Boolean, default: false },
    minioConfig: { type: Object, required: true },
    minioStatusText: { type: String, default: '' },
    minioStatusDetail: { type: String, default: '' },
    minioStatusClass: { type: String, default: 'warning' },
    minioStatusIconColor: { type: String, default: '#faad14' },
    testingConnection: { type: Boolean, default: false },
    resettingMinIO: { type: Boolean, default: false }
  },
  emits: ['test', 'save', 'reset']
}
</script>

<style scoped>
.panel { background: #fff; border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.06); overflow: hidden; display: none; }
.panel.active { display: block; animation: fadeIn 0.3s ease; }
@keyframes fadeIn { from { opacity: 0; transform: translateY(8px); } to { opacity: 1; transform: translateY(0); } }
.panel-header { padding: 20px 24px; border-bottom: 1px solid #e3e5e7; font-size: 18px; font-weight: 700; color: #18191c; }
.panel-body { padding: 24px 32px 32px; }

.minio-status-card {
  display: flex; align-items: center; gap: 16px; padding: 16px 20px;
  background: #f6ffed; border: 1px solid #b7eb8f; border-radius: 8px; margin-bottom: 24px;
}
.minio-status-card.warning { background: #fffbe6; border-color: #ffe58f; }
.minio-status-card.error { background: #fff2f0; border-color: #ffccc7; }
.status-icon { width: 32px; height: 32px; flex-shrink: 0; }
.status-text { font-size: 14px; color: #52c41a; font-weight: 500; }
.minio-status-card.warning .status-text { color: #faad14; }
.minio-status-card.error .status-text { color: #ff4d4f; }
.status-text .detail { font-size: 12px; font-weight: normal; color: #9499a0; margin-top: 2px; }

.form-row { display: flex; align-items: flex-start; margin-bottom: 24px; }
.form-label { width: 110px; text-align: right; padding-right: 20px; padding-top: 9px; font-size: 14px; color: #61666d; flex-shrink: 0; white-space: nowrap; }
.form-control { flex: 1; min-width: 0; }
.input-wrap { position: relative; max-width: 480px; }
.input-wrap.medium { max-width: 400px; }
.form-hint { margin-top: 6px; font-size: 12px; color: #9499a0; }

input[type="url"], input[type="text"] {
  width: 100%; padding: 9px 12px; border: 1px solid #e3e5e7; border-radius: 6px;
  background: #fff; font-size: 14px; color: #18191c; outline: none; transition: all 0.2s; font-family: inherit;
}
input:focus { border-color: #00a1d6; box-shadow: 0 0 0 3px rgba(0, 161, 214, 0.15); }
input::placeholder { color: #9499a0; }

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
.btn-outline { background: #fff; color: #61666d; border: 1px solid #c9cdd4; }
.btn-outline:hover { border-color: #00a1d6; color: #00a1d6; }
.btn-success { background: #52c41a; color: #fff; }
.btn-success:hover { background: #389e0d; }
.btn-success:disabled { background: #a3d987; cursor: not-allowed; }
.btn:disabled { opacity: 0.5; cursor: not-allowed; }
.form-actions { margin-top: 8px; padding-left: 130px; display: flex; gap: 16px; }

@media (max-width: 900px) {
  .form-row { flex-direction: column; }
  .form-label { text-align: left; width: auto; padding: 0 0 6px; }
  .form-actions { padding-left: 0; }
}
</style>
