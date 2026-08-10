<!--
  PanelLicense.vue - 许可管理面板（个人中心-邮箱设置-许可管理）

  复刻自 profile_settings_v9_license.html 行 1883-2015 的 panel-license 区块
  字段 / 状态卡 / 按钮 / 交互均与 HTML 原版 1:1 对齐
  区别：
    1) 状态卡走响应式状态（active / inactive / expired / revoked 四态）
    2) 按钮 loading 态由 composable 透传 prop 控制
    3) 删除/吊销用 ElMessageBox.confirm 替代 confirm() 原生弹窗
    4) .req 导出走真实后端 /api/license/machine-fingerprint
    5) .lic 导入走真实后端 /api/license/import（FileReader 读文本）
    6) 历史表格数据从后端 /api/license/history 动态加载

  props 全部由 Profile.vue 通过 useLicense() 注入
  emits: activate / import / revoke / delete-history / export-req / export-lic / file-change
-->
<template>
  <div class="panel" :class="{ active }">
    <div class="panel-header">许可管理</div>
    <div class="panel-body">

      <!-- 功能说明卡片（与 HTML 原版 1:1） -->
      <div class="timeout-info-card" style="background:#f0f9ff;border-color:#bae6fd;">
        <svg class="timeout-info-icon" style="color:#0ea5e9;" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <rect x="3" y="3" width="18" height="18" rx="2" ry="2"/>
          <path d="M9 12l2 2 4-4"/>
          <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/>
        </svg>
        <div class="timeout-info-text">
          <strong>许可管理</strong>：FigureBox 采用许可证授权机制。你可以通过导入 .lic 许可文件或在线激活来解锁系统功能。
          如需离线激活，请先导出 .req 请求文件，在授权服务器上生成 .lic 文件后再导入。
        </div>
      </div>

      <!-- 当前许可状态（响应式状态卡：4 态） -->
      <div class="form-row" style="margin-top:24px;">
        <label class="form-label">当前状态</label>
        <div class="form-control">
          <div
            id="license-status-card"
            :class="['minio-status-card', statusCardClass]"
            style="max-width:640px;"
          >
            <svg
              v-if="statusCardClass === 'warning' || statusCardClass === 'error'"
              class="status-icon"
              viewBox="0 0 24 24"
              fill="none"
              stroke-width="2"
            >
              <circle cx="12" cy="12" r="10" :stroke="statusCardIconColor"/>
              <line x1="12" y1="8" x2="12" y2="12" :stroke="statusCardIconColor" stroke-linecap="round"/>
              <line x1="12" y1="16" x2="12.01" y2="16" :stroke="statusCardIconColor" stroke-linecap="round"/>
            </svg>
            <svg
              v-else
              class="status-icon"
              viewBox="0 0 24 24"
              fill="none"
              stroke-width="2"
            >
              <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14" :stroke="statusCardIconColor"/>
              <polyline points="22 4 12 14.01 9 11.01" :stroke="statusCardIconColor"/>
            </svg>
            <div class="status-text">
              <div>{{ statusCardText }}</div>
              <div class="detail">{{ statusCardDetail || '点击下方按钮导入 .lic 许可文件或在线激活' }}</div>
            </div>
          </div>
          <div class="form-hint" style="margin-top:6px;">
            许可证由 FigureBox 官方授权服务器签发，与当前设备硬件绑定
          </div>
        </div>
      </div>

      <!-- 在线激活 -->
      <div class="form-row">
        <label class="form-label">在线激活</label>
        <div class="form-control">
          <div style="display:flex;gap:10px;align-items:flex-start;max-width:640px;">
            <div class="input-wrap" style="flex:1;">
              <input
                type="text"
                :value="onlineKey"
                @input="$emit('update:onlineKey', $event.target.value)"
                placeholder="请输入 32 位许可密钥，如 XXXX-XXXX-XXXX-XXXX"
                maxlength="39"
                @keyup.enter="$emit('activate')"
              >
            </div>
            <button
              class="btn btn-primary btn-sm"
              :disabled="activating"
              @click="$emit('activate')"
              style="white-space:nowrap;padding:9px 18px;"
            >
              <span
                v-if="activating"
                style="display:inline-block;width:12px;height:12px;border:2px solid #fff;border-top-color:transparent;border-radius:50%;animation:spin 0.8s linear infinite;vertical-align:middle;margin-right:4px;"
              />
              {{ activating ? '激活中...' : '在线激活' }}
            </button>
          </div>
          <div class="form-hint">联网状态下直接输入密钥激活，无需手动导入许可文件</div>
        </div>
      </div>

      <!-- 离线导入 -->
      <div class="form-row">
        <label class="form-label">离线导入</label>
        <div class="form-control">
          <div
            class="license-dropzone"
            :class="{ dragging: isDragging }"
            @click="triggerFileInput"
            @dragover.prevent="isDragging = true"
            @dragleave.prevent="isDragging = false"
            @drop.prevent="onDrop"
          >
            <div class="license-dropzone-inner">
              <svg class="license-dropzone-icon" viewBox="0 0 24 24" fill="none" stroke="#c0c4cc" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">
                <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>
                <polyline points="14 2 14 8 20 8"/>
                <path d="M12 18v-6"/>
                <path d="M9 15l3-3 3 3"/>
              </svg>
              <div class="license-dropzone-text">点击上传或拖拽 .lic 许可文件至此处</div>
              <div class="license-dropzone-hint">支持 .lic 格式，文件大小不超过 1 MB</div>
            </div>
            <input
              ref="fileInput"
              type="file"
              accept=".lic"
              style="display:none"
              @change="onFileChange"
            >
          </div>
          <div
            v-if="offlineFilename"
            class="license-imported-info"
          >
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#52c41a" stroke-width="2">
              <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/>
              <polyline points="22 4 12 14.01 9 11.01"/>
            </svg>
            <span>{{ offlineFilename }}</span>
            <span style="margin-left:auto;font-size:12px;color:#666;">已验证通过</span>
          </div>
        </div>
      </div>

      <!-- 许可历史 -->
      <div class="form-row">
        <label class="form-label">许可历史</label>
        <div class="form-control">
          <div class="license-table-wrap">
            <table class="license-table">
              <colgroup>
                <col style="width:32%;">
                <col style="width:12%;">
                <col style="width:26%;">
                <col style="width:12%;">
                <col style="width:18%;">
              </colgroup>
              <thead>
                <tr>
                  <th>许可文件</th>
                  <th>授权类型</th>
                  <th>有效期</th>
                  <th>状态</th>
                  <th style="text-align:right;">操作</th>
                </tr>
              </thead>
              <tbody>
                <tr v-if="!history.items || history.items.length === 0">
                  <td colspan="5" class="license-empty">暂无许可记录</td>
                </tr>
                <tr
                  v-for="item in history.items"
                  :key="item.id"
                  :class="{ 'is-current': item.is_current }"
                >
                  <td class="filename-cell">
                    {{ item.filename || item.license_key }}
                    <span v-if="item.is_current" class="current-tag">当前</span>
                  </td>
                  <td>
                    <span :class="['plan-tag', `plan-${item.plan}`]">{{ item.plan_label }}</span>
                  </td>
                  <td class="muted-cell">
                    {{ formatDate(item.issued_at) }} 至 {{ formatDate(item.expires_at) }}
                  </td>
                  <td>
                    <span :class="['status-tag', `status-${item.status}`]">
                      <svg v-if="item.status === 'active'" width="10" height="10" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3">
                        <polyline points="20 6 9 17 4 12"/>
                      </svg>
                      {{ statusLabel(item.status) }}
                    </span>
                  </td>
                  <td style="text-align:right;white-space:nowrap;">
                    <button
                      class="btn btn-outline btn-sm"
                      style="padding:4px 10px;font-size:12px;"
                      @click="$emit('export-lic', item)"
                    >导出</button>
                    <button
                      v-if="item.status === 'active' && !item.is_current"
                      class="btn btn-outline btn-sm"
                      style="padding:4px 10px;font-size:12px;margin-left:6px;color:var(--danger);border-color:#ffd6d6;"
                      @click="$emit('revoke')"
                    >吊销</button>
                    <button
                      v-if="item.is_current && item.status === 'active'"
                      class="btn btn-outline btn-sm"
                      style="padding:4px 10px;font-size:12px;margin-left:6px;color:var(--danger);border-color:#ffd6d6;"
                      :disabled="revoking"
                      @click="$emit('revoke')"
                    >吊销</button>
                    <button
                      v-if="item.status === 'expired' || item.status === 'revoked'"
                      class="btn btn-outline btn-sm"
                      style="padding:4px 10px;font-size:12px;margin-left:6px;color:var(--danger);border-color:#ffd6d6;"
                      :disabled="deleting"
                      @click="$emit('delete-history')"
                    >删除</button>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
          <div class="form-hint" style="margin-top:8px;">
            共 {{ history.total }} 条许可记录{{ history.total > 0 ? '，当前生效 ' + (history.items.filter(i => i.is_current).length) + ' 条' : '' }}
          </div>
        </div>
      </div>

      <!-- .req 请求文件导出 -->
      <div class="form-row">
        <label class="form-label">请求文件</label>
        <div class="form-control">
          <div class="req-info-box">
            <div style="display:flex;align-items:center;gap:10px;margin-bottom:8px;">
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#d46b08" stroke-width="2">
                <circle cx="12" cy="12" r="10"/>
                <line x1="12" y1="8" x2="12" y2="12"/>
                <line x1="12" y1="16" x2="12.01" y2="16"/>
              </svg>
              <span style="font-size:14px;font-weight:600;color:#d46b08;">离线激活流程</span>
            </div>
            <div style="font-size:13px;color:#666;line-height:1.8;padding-left:28px;">
              1. 点击下方按钮导出 <strong>.req</strong> 请求文件（包含当前设备硬件指纹）<br>
              2. 将 .req 文件提交至 FigureBox 授权服务器或发送给管理员<br>
              3. 获取返回的 <strong>.lic</strong> 许可文件后，通过上方「离线导入」导入系统
            </div>
            <div style="margin-top:12px;padding-left:28px;">
              <button
                class="btn btn-primary btn-sm"
                :disabled="exportingReq"
                @click="$emit('export-req')"
              >
                <span
                  v-if="exportingReq"
                  style="display:inline-block;width:12px;height:12px;border:2px solid #fff;border-top-color:transparent;border-radius:50%;animation:spin 0.8s linear infinite;vertical-align:middle;margin-right:4px;"
                />
                <svg v-else width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" style="display:inline-block;vertical-align:middle;margin-right:4px;">
                  <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/>
                  <polyline points="7 10 12 15 17 10"/>
                  <line x1="12" y1="15" x2="12" y2="3"/>
                </svg>
                {{ exportingReq ? '生成中...' : '导出 .req 请求文件' }}
              </button>
            </div>
          </div>
          <div class="form-hint" style="margin-top:8px;">
            .req 文件仅包含设备硬件信息（CPU ID、主板序列号等），不含任何个人隐私数据
          </div>
        </div>
      </div>

      <!-- 保存设置按钮（与 HTML 原版 1:1） -->
      <div class="form-actions">
        <button
          class="btn btn-primary"
          @click="$emit('save')"
        >保存设置</button>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'PanelLicense',
  props: {
    active: { type: Boolean, default: false },
    licenseStatus: { type: Object, required: true },
    history: { type: Object, required: true },
    onlineKey: { type: String, default: '' },
    offlineFilename: { type: String, default: '' },
    activating: { type: Boolean, default: false },
    importing: { type: Boolean, default: false },
    revoking: { type: Boolean, default: false },
    deleting: { type: Boolean, default: false },
    exportingReq: { type: Boolean, default: false },
    statusCardText: { type: String, default: '未激活' },
    statusCardClass: { type: String, default: 'warning' },
    statusCardIconColor: { type: String, default: '#9499a0' },
    statusCardDetail: { type: String, default: '' }
  },
  emits: [
    'update:onlineKey',
    'activate',
    'import',
    'revoke',
    'delete-history',
    'export-req',
    'export-lic',
    'file-change',
    'save'
  ],
  data() {
    return {
      isDragging: false
    }
  },
  methods: {
    triggerFileInput() {
      this.$refs.fileInput.click()
    },
    onFileChange(e) {
      const file = e.target.files[0]
      if (file) this.$emit('file-change', file)
    },
    onDrop(e) {
      this.isDragging = false
      const file = e.dataTransfer.files[0]
      if (file) this.$emit('file-change', file)
    },
    formatDate(iso) {
      if (!iso) return '-'
      const d = new Date(iso)
      const pad = (n) => String(n).padStart(2, '0')
      return `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())}`
    },
    statusLabel(s) {
      return { active: '有效', expired: '已过期', revoked: '已吊销', inactive: '未激活' }[s] || s
    }
  }
}
</script>

<style scoped>
/* 复刻自 PanelEmail.vue 的独立 scoped 样式规范 */
.panel {
  background: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.06);
  overflow: hidden;
  display: none;
}
.panel.active { display: block; animation: fadeIn 0.3s ease; }
@keyframes fadeIn { from { opacity: 0; transform: translateY(8px); } to { opacity: 1; transform: translateY(0); } }
@keyframes spin { from { transform: rotate(0deg); } to { transform: rotate(360deg); } }

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
  max-width: 920px;
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
.form-hint { margin-top: 6px; font-size: 12px; color: #9499a0; }

input[type="text"] {
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
input[type="text"]:focus { border-color: #00a1d6; box-shadow: 0 0 0 3px rgba(0, 161, 214, 0.15); }
input[type="text"]::placeholder { color: #9499a0; }

.timeout-info-card {
  display: flex;
  align-items: flex-start;
  gap: 12px;
  padding: 16px 20px;
  border-radius: 8px;
  background: #f6f7f8;
  border: 1px solid #e3e5e7;
  max-width: 920px;
  margin: 0 auto 24px;
}
.timeout-info-icon { width: 20px; height: 20px; color: #00a1d6; flex-shrink: 0; margin-top: 1px; }
.timeout-info-text { font-size: 13px; color: #61666d; line-height: 1.7; }
.timeout-info-text strong { color: #18191c; }

.minio-status-card {
  display: flex; align-items: center; gap: 16px; padding: 16px 20px;
  background: #f6ffed; border: 1px solid #b7eb8f; border-radius: 8px;
  max-width: 920px;
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
.btn-outline { background: #fff; color: #61666d; border: 1px solid #c9cdd4; }
.btn-outline:hover { border-color: #00a1d6; color: #00a1d6; }
.btn-sm { padding: 6px 16px; font-size: 13px; }
.btn:disabled { opacity: 0.5; cursor: not-allowed; }
.form-actions { margin-top: 8px; display: flex; justify-content: center; gap: 16px; }

/* 拖拽上传区 */
.license-dropzone {
  padding: 24px;
  border: 2px dashed #e3e5e7;
  border-radius: 8px;
  background: #fafafa;
  max-width: 920px;
  transition: all 0.2s;
  cursor: pointer;
  position: relative;
  /* 用 grid 实现内容严格上下左右居中 */
  display: grid;
  place-items: center;
  min-height: 160px;
}
.license-dropzone-inner {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  text-align: center;
  width: 100%;
}
.license-dropzone-icon {
  width: 44px;
  height: 44px;
  display: block;
  margin: 0 auto 12px;
  flex-shrink: 0;
}
.license-dropzone-text {
  font-size: 14px;
  color: #18191c;
  font-weight: 500;
  line-height: 1.5;
  text-align: center;
}
.license-dropzone-hint {
  font-size: 12px;
  color: #9499a0;
  margin-top: 6px;
  line-height: 1.5;
  text-align: center;
}
.license-dropzone:hover, .license-dropzone.dragging {
  border-color: #00a1d6;
  background: rgba(0, 161, 214, 0.08);
}

.license-imported-info {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-top: 12px;
  padding: 12px 16px;
  background: #f6ffed;
  border: 1px solid #b7eb8f;
  border-radius: 6px;
  font-size: 13px;
  color: #389e0d;
  max-width: 920px;
}

/* 历史表格 */
.license-table-wrap {
  border: 1px solid #e3e5e7;
  border-radius: 8px;
  overflow: hidden;
  max-width: 920px;
}
.license-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 13px;
  table-layout: fixed;
}
.license-table thead tr { background: #f8f9fa; border-bottom: 1px solid #e3e5e7; }
.license-table th {
  padding: 10px 16px;
  text-align: left;
  font-weight: 600;
  color: #61666d;
  font-size: 12px;
  white-space: nowrap;
}
.license-table td {
  padding: 12px 16px;
  border-bottom: 1px solid #f0f0f0;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
.license-table tr:last-child td { border-bottom: none; }
.license-table tr.is-current { background: rgba(0, 161, 214, 0.04); }
.license-table .filename-cell { color: #18191c; font-weight: 500; display: flex; align-items: center; gap: 6px; }
.license-table .muted-cell { color: #61666d; }
.license-table .license-empty { text-align: center; color: #9499a0; padding: 32px 16px; }

/* 标签 */
.current-tag {
  display: inline-block;
  padding: 1px 6px;
  border-radius: 3px;
  background: #e6f7ff;
  color: #096dd9;
  font-size: 11px;
  font-weight: 500;
}
.plan-tag {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  padding: 2px 8px;
  border-radius: 4px;
  font-size: 12px;
}
.plan-tag.plan-trial { background: #f0f0f0; color: #61666d; }
.plan-tag.plan-personal { background: #e6f7ff; color: #096dd9; }
.plan-tag.plan-pro { background: #fff7e6; color: #d46b08; }
.plan-tag.plan-enterprise { background: #f9f0ff; color: #722ed1; }
.status-tag {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  padding: 2px 8px;
  border-radius: 4px;
  font-size: 12px;
}
.status-tag.status-active { background: #f6ffed; color: #389e0d; }
.status-tag.status-expired { background: #f5f5f5; color: #999; }
.status-tag.status-revoked { background: #fff2f0; color: #f25d8e; }
.status-tag.status-inactive { background: #f5f5f5; color: #999; }

/* .req 信息盒 */
.req-info-box {
  padding: 16px 20px;
  border-radius: 8px;
  background: #fff7e6;
  border: 1px solid #ffd591;
  max-width: 920px;
}

@media (max-width: 900px) {
  .form-row { flex-direction: column; }
  .form-label { text-align: left; width: auto; padding: 0 0 6px; }
  .form-actions { padding-left: 0; }
}
</style>
