<!--
  BackupPanel.vue - 个人中心 / 系统备份 面板

  功能说明：
  - 立即备份按钮：调用 GET /api/backup/download，触发浏览器下载 JSON 备份文件
  - 自动备份开关：本地状态切换（暂未接入后端定时任务）
  - 备份历史：本地状态列表（当前会话内累计，待后端提供历史表后接入）
  - 数据恢复区：拖拽 / 点击上传 .json 备份文件，调用 POST /api/backup/restore 进行数据恢复
  - 业务逻辑全部抽离到 useBackup composable，本组件只负责 UI 渲染
  - 视觉与字段结构对齐 profile_settings_v5.html 中「系统备份」面板
-->
<template>
  <div class="panel" :class="{ active: activePanel === 'panel-backup' }">
    <div class="panel-header">系统备份</div>
    <div class="panel-body">

      <!-- 备份范围说明卡片 -->
      <div class="timeout-info-card" style="background: #f0f9ff; border-color: #bae6fd;">
        <svg class="timeout-info-icon" style="color: #0ea5e9;" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z" />
          <path d="M12 8v4" />
          <path d="M12 16h.01" />
        </svg>
        <div class="timeout-info-text">
          <strong>备份范围</strong>：备份将包含你的全部手办数据、交易流水、尾款订单、资产收益记录、收藏柜配置、个人资料及系统设置。备份文件为 JSON 格式，可通过本系统的「数据恢复」功能导入。
        </div>
      </div>

      <!-- 手动备份 -->
      <div class="form-row" style="margin-top: 24px;">
        <label class="form-label">手动备份</label>
        <div class="form-control">
          <div style="display: flex; gap: 12px; align-items: flex-start; flex-wrap: wrap;">
            <button
              class="btn btn-primary"
              :disabled="backuping"
              @click="handleDownloadBackup"
            >
              <span
                v-if="backuping"
                style="display: inline-block; width: 14px; height: 14px; border: 2px solid #fff; border-top-color: transparent; border-radius: 50%; animation: spin 0.8s linear infinite; vertical-align: middle; margin-right: 6px;"
              />
              <svg v-else width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" style="display: inline-block; vertical-align: middle; margin-right: 4px;">
                <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" />
                <polyline points="7 10 12 15 17 10" />
                <line x1="12" y1="15" x2="12" y2="3" />
              </svg>
              {{ backuping ? '正在打包数据…' : '立即备份' }}
            </button>
            <div
              v-if="lastBackupResult"
              style="display: flex; align-items: center; gap: 8px; padding: 8px 14px; background: #f6ffed; border: 1px solid #b7eb8f; border-radius: 6px; font-size: 13px; color: #389e0d;"
            >
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#52c41a" stroke-width="2">
                <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14" />
                <polyline points="22 4 12 14.01 9 11.01" />
              </svg>
              备份完成：{{ lastBackupResult.filename }}（{{ lastBackupResult.sizeKb }} KB）
            </div>
          </div>
          <div v-if="lastBackupSummary" class="form-hint">
            上次备份：{{ lastBackupSummary.time }} · {{ lastBackupSummary.source }}备份
          </div>
          <div v-else class="form-hint">
            备份过程可能需要 1-3 秒，建议每月月底或重要操作前执行一次手动备份
          </div>
        </div>
      </div>

      <!-- 自动备份 -->
      <div class="form-row">
        <label class="form-label">自动备份</label>
        <div class="form-control">
          <div style="display: flex; align-items: center; gap: 16px; margin-bottom: 12px;">
            <div
              class="toggle-v2"
              :class="{ active: autoBackupEnabled }"
              @click="toggleAutoBackup"
            ></div>
            <span style="font-size: 14px; color: #61666d;">
              {{ autoBackupEnabled ? '已开启' : '已关闭' }}
            </span>
          </div>
          <div v-if="autoBackupEnabled" style="max-width: 480px;">
            <div class="select-group" style="margin-bottom: 10px;">
              <select v-model="backupFrequency" style="min-width: 140px;">
                <option value="daily">每天</option>
                <option value="weekly">每周</option>
                <option value="monthly">每月</option>
              </select>
              <select v-model.number="backupRetain">
                <option :value="3">保留最近 3 份</option>
                <option :value="5">保留最近 5 份</option>
                <option :value="10">保留最近 10 份</option>
                <option :value="0">不限制</option>
              </select>
            </div>
            <div class="form-hint">
              自动备份将在设定周期内执行，超出保留份数的历史备份将被自动清理
            </div>
          </div>
        </div>
      </div>

      <!-- 备份历史 -->
      <div class="form-row">
        <label class="form-label">备份历史</label>
        <div class="form-control">
          <div style="border: 1px solid #e3e5e7; border-radius: 8px; overflow: hidden; max-width: 720px;">
            <table style="width: 100%; border-collapse: collapse; font-size: 13px;">
              <thead>
                <tr style="background: #f8f9fa; border-bottom: 1px solid #e3e5e7;">
                  <th style="padding: 10px 16px; text-align: left; font-weight: 600; color: #61666d; font-size: 12px;">备份时间</th>
                  <th style="padding: 10px 16px; text-align: left; font-weight: 600; color: #61666d; font-size: 12px;">类型</th>
                  <th style="padding: 10px 16px; text-align: left; font-weight: 600; color: #61666d; font-size: 12px;">大小</th>
                  <th style="padding: 10px 16px; text-align: right; font-weight: 600; color: #61666d; font-size: 12px;">操作</th>
                </tr>
              </thead>
              <tbody>
                <tr v-if="backupHistory.length === 0">
                  <td colspan="4" style="padding: 20px 16px; text-align: center; color: #9499a0; font-size: 13px;">
                    暂无备份记录，点击「立即备份」生成第一条记录
                  </td>
                </tr>
                <tr
                  v-for="(item, idx) in backupHistory"
                  :key="idx"
                  style="border-bottom: 1px solid #f0f0f0;"
                >
                  <td style="padding: 12px 16px; color: #18191c;">{{ item.time }}</td>
                  <td style="padding: 12px 16px;">
                    <span
                      :style="{
                        display: 'inline-flex',
                        alignItems: 'center',
                        gap: '4px',
                        padding: '2px 8px',
                        borderRadius: '4px',
                        fontSize: '12px',
                        background: item.type === '自动' ? '#e6f7ff' : '#fff7e6',
                        color: item.type === '自动' ? '#096dd9' : '#d46b08'
                      }"
                    >
                      <svg v-if="item.type === '自动'" width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <rect x="3" y="4" width="18" height="18" rx="2" ry="2" />
                        <line x1="16" y1="2" x2="16" y2="6" />
                        <line x1="8" y1="2" x2="8" y2="6" />
                        <line x1="3" y1="10" x2="21" y2="10" />
                      </svg>
                      <svg v-else width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2" />
                        <circle cx="12" cy="7" r="4" />
                      </svg>
                      {{ item.type }}
                    </span>
                  </td>
                  <td style="padding: 12px 16px; color: #61666d;">{{ item.size }}</td>
                  <td style="padding: 12px 16px; text-align: right;">
                    <button class="btn btn-outline btn-sm" style="padding: 4px 10px; font-size: 12px;" @click="handleDownloadFromHistory(item)">下载</button>
                    <button
                      class="btn btn-outline btn-sm"
                      style="padding: 4px 10px; font-size: 12px; margin-left: 6px; color: #f25d8e; border-color: #ffd6d6;"
                      @click="handleDeleteFromHistory(idx)"
                    >删除</button>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
          <div v-if="backupHistory.length > 0" class="form-hint" style="margin-top: 8px;">
            共 {{ backupHistory.length }} 条备份记录
          </div>
        </div>
      </div>

      <!-- 数据恢复 -->
      <div class="form-row">
        <label class="form-label">数据恢复</label>
        <div class="form-control">
          <div
            style="padding: 20px; border: 2px dashed var(--border, #e3e5e7); border-radius: 8px; text-align: center; background: #fafafa; max-width: 480px; transition: all 0.2s; cursor: pointer;"
            :style="dragOver ? 'border-color: #00a1d6; background: #e6f7ff;' : ''"
            @dragover.prevent="dragOver = true"
            @dragleave.prevent="dragOver = false"
            @drop.prevent="handleDrop"
            @click="triggerFileInput"
          >
            <svg width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="#9499a0" stroke-width="1.5" style="margin-bottom: 8px;">
              <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" />
              <polyline points="17 8 12 3 7 8" />
              <line x1="12" y1="3" x2="12" y2="15" />
            </svg>
            <div style="font-size: 14px; color: #61666d; font-weight: 500;">
              点击上传或拖拽备份文件至此处
            </div>
            <div style="font-size: 12px; color: #9499a0; margin-top: 4px;">
              支持 .json 格式，文件大小不超过 50 MB
            </div>
            <input
              ref="fileInputRef"
              type="file"
              accept=".json"
              style="display: none"
              @change="handleFileChange"
            />
          </div>

          <!-- 已选文件信息 -->
          <div
            v-if="selectedFile"
            style="margin-top: 12px; padding: 12px 16px; background: #fff7e6; border: 1px solid #ffd591; border-radius: 6px; font-size: 13px; color: #d46b08; display: flex; align-items: center; justify-content: space-between; max-width: 480px;"
          >
            <div style="display: flex; align-items: center; gap: 8px;">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#d46b08" stroke-width="2">
                <path d="M13 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V9z" />
                <polyline points="13 2 13 9 20 9" />
              </svg>
              <span>{{ selectedFileName }}</span>
            </div>
            <div style="display: flex; gap: 8px;">
              <button class="btn btn-primary btn-sm" :disabled="restoring" @click="handleRestore">
                <span v-if="restoring">恢复中…</span>
                <span v-else>开始恢复</span>
              </button>
              <button class="btn btn-outline btn-sm" @click="clearSelectedFile">取消</button>
            </div>
          </div>

          <div class="form-hint" style="margin-top: 8px;">
            ⚠️ 警告：数据恢复会向当前数据库插入/更新手办、订单、售出单、库存账、资金账记录。建议恢复前先执行一次「立即备份」保留当前数据快照。
          </div>

          <!-- 恢复结果展示 -->
          <div
            v-if="lastRestoreResult && lastRestoreResult.success"
            style="margin-top: 12px; padding: 12px 16px; background: #f6ffed; border: 1px solid #b7eb8f; border-radius: 6px; font-size: 13px; color: #389e0d;"
          >
            ✓ {{ lastRestoreResult.message }}（页面将在 3 秒后自动刷新）
          </div>
          <div
            v-else-if="lastRestoreResult && !lastRestoreResult.success"
            style="margin-top: 12px; padding: 12px 16px; background: #fff2f0; border: 1px solid #ffccc7; border-radius: 6px; font-size: 13px; color: #cf1322;"
          >
            ✗ {{ lastRestoreResult.message }}
          </div>
        </div>
      </div>

      <div class="form-actions">
        <button class="btn btn-primary" @click="saveBackupSettings">保存设置</button>
      </div>
    </div>
  </div>
</template>

<script>
import { ref } from 'vue'
import { ElMessage } from 'element-plus'
import { useBackup } from '../composables/useBackup'

export default {
  name: 'BackupPanel',
  props: {
    activePanel: {
      type: String,
      default: ''
    }
  },
  setup() {
    const fileInputRef = ref(null)
    const dragOver = ref(false)

    const {
      backuping,
      restoring,
      selectedFile,
      selectedFileName,
      lastBackupResult,
      lastRestoreResult,
      autoBackupEnabled,
      backupFrequency,
      backupRetain,
      backupHistory,
      lastBackupSummary,
      handleDownloadBackup,
      handleFileChange,
      handleRestore,
      clearSelectedFile,
      toggleAutoBackup,
      saveBackupSettings
    } = useBackup()

    const triggerFileInput = () => {
      fileInputRef.value?.click()
    }

    const handleDrop = (event) => {
      dragOver.value = false
      const file = event.dataTransfer?.files?.[0]
      if (file) {
        const fakeInput = { files: [file], target: { value: '' } }
        handleFileChange(fakeInput)
      }
    }

    const handleDownloadFromHistory = (item) => {
      // 历史记录中的「下载」按钮：当前阶段历史为前端本地记录，
      // 仅做提示并复用即时下载逻辑（保留同一份文件流）。
      ElMessage.info(`开始下载备份文件：${item.filename || item.time}`)
      handleDownloadBackup()
    }

    const handleDeleteFromHistory = (idx) => {
      backupHistory.value.splice(idx, 1)
    }

    return {
      fileInputRef,
      dragOver,
      backuping,
      restoring,
      selectedFile,
      selectedFileName,
      lastBackupResult,
      lastRestoreResult,
      autoBackupEnabled,
      backupFrequency,
      backupRetain,
      backupHistory,
      lastBackupSummary,
      handleDownloadBackup,
      handleFileChange,
      handleRestore,
      clearSelectedFile,
      toggleAutoBackup,
      saveBackupSettings,
      triggerFileInput,
      handleDrop,
      handleDownloadFromHistory,
      handleDeleteFromHistory
    }
  }
}
</script>

<style scoped>
/*
  Profile.vue 父组件的 <style scoped> 不会作用到本子组件元素上。
  系统备份面板用到的所有类样式（.panel / .toggle-v2 / .select-group / .form-actions / 表格等），
  全部在本组件内独立注入，与 profile_settings_v5.html 视觉规范保持一致。
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
  margin-bottom: 24px;
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
.form-hint { margin-top: 6px; font-size: 12px; color: #9499a0; }

.form-actions {
  margin-top: 8px;
  padding-left: 130px;
}
.form-actions .btn + .btn { margin-left: 12px; }

.btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
  padding: 9px 24px;
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
.btn-outline {
  background: #fff;
  color: #61666d;
  border: 1px solid #c9cdd4;
}
.btn-outline:hover { border-color: #00a1d6; color: #00a1d6; }
.btn-sm { padding: 6px 16px; font-size: 13px; }
.btn:disabled { opacity: 0.5; cursor: not-allowed; }

.timeout-info-card {
  display: flex;
  align-items: flex-start;
  gap: 12px;
  padding: 16px 20px;
  border-radius: 8px;
  background: #f6f7f8;
  border: 1px solid #e3e5e7;
  margin-bottom: 24px;
  max-width: 640px;
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

/* Toggle Switch v2 (与 HTML 一致) */
.toggle-v2 {
  position: relative;
  width: 44px;
  height: 24px;
  background: #e3e5e7;
  border-radius: 12px;
  cursor: pointer;
  transition: background 0.3s;
  flex-shrink: 0;
  -webkit-tap-highlight-color: transparent;
}
.toggle-v2::after {
  content: "";
  position: absolute;
  top: 2px; left: 2px;
  width: 20px; height: 20px;
  background: #fff;
  border-radius: 50%;
  transition: transform 0.3s;
  box-shadow: 0 1px 3px rgba(0,0,0,0.2);
}
.toggle-v2.active {
  background: #00a1d6;
}
.toggle-v2.active::after {
  transform: translateX(20px);
}

/* Select Group (与 HTML 一致) */
.select-group {
  display: flex;
  gap: 10px;
}
.select-group select {
  width: auto;
  min-width: 100px;
  padding: 8px 28px 8px 12px;
  font-size: 14px;
  border: 1px solid #e3e5e7;
  border-radius: 6px;
  background-color: #fff;
  color: #18191c;
  cursor: pointer;
  appearance: none;
  background-image: url("data:image/svg+xml,%3Csvg width='10' height='6' viewBox='0 0 10 6' xmlns='http://www.w3.org/2000/svg'%3E%3Cpath d='M1 1l4 4 4-4' stroke='%239499a0' stroke-width='1.5' fill='none' fill-rule='evenodd'/%3E%3C/svg%3E");
  background-repeat: no-repeat;
  background-position: right 10px center;
  transition: border-color 0.2s;
}
.select-group select:hover { border-color: #00a1d6; }
.select-group select:focus { outline: none; border-color: #00a1d6; }

@media (max-width: 900px) {
  .form-row { flex-direction: column; }
  .form-label { text-align: left; width: auto; padding: 0 0 6px; }
  .form-actions { padding-left: 0; }
}
</style>
