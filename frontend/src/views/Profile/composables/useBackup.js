/**
 * useBackup.js - 系统备份/恢复业务逻辑 composable
 *
 * 功能说明：
 * - 业务逻辑与 UI 组件解耦（本 composable 由 BackupPanel.vue 消费）
 * - 状态：备份中/恢复中/已选文件/成功消息/错误消息/自动备份配置/备份历史
 * - 提供：handleDownloadBackup / handleFileChange / handleRestore / 自动备份开关与策略
 */
import { ref, computed } from 'vue'
import { ElMessage } from 'element-plus'
import { backupApi } from '../api/backupApi'

export function useBackup() {
  // ========== 状态 ==========
  const backuping = ref(false)          // 备份进行中
  const restoring = ref(false)          // 恢复进行中
  const selectedFile = ref(null)        // 待恢复的备份文件
  const selectedFileName = ref('')      // 待恢复文件名（展示用）
  const lastBackupResult = ref(null)    // 最近一次备份结果
  const lastRestoreResult = ref(null)   // 最近一次恢复结果

  // ========== 自动备份设置（前端本地状态，后端暂不持久化）==========
  const autoBackupEnabled = ref(false)              // 自动备份开关
  const backupFrequency = ref('weekly')             // daily / weekly / monthly
  const backupRetain = ref(5)                       // 保留份数（3/5/10/0=不限制）

  // ========== 备份历史（前端本地状态；当前后端暂无历史表，前端留接口位）==========
  const backupHistory = ref([])                     // 历史记录列表
  const lastBackupSummary = computed(() => {
    if (lastBackupResult.value) {
      const at = lastBackupResult.value.at
      const ymd = `${at.getFullYear()}-${String(at.getMonth() + 1).padStart(2, '0')}-${String(at.getDate()).padStart(2, '0')}`
      const hms = `${String(at.getHours()).padStart(2, '0')}:${String(at.getMinutes()).padStart(2, '0')}:${String(at.getSeconds()).padStart(2, '0')}`
      return { time: `${ymd} ${hms}`, source: '手动' }
    }
    return null
  })

  // ========== 立即备份 ==========
  /**
   * 触发浏览器下载备份文件
   * 实现：先 fetch 拿 JSON，再用 Blob + a.download 触发下载
   */
  const handleDownloadBackup = async () => {
    if (backuping.value) return
    backuping.value = true
    try {
      // 通过 fetch + blob 拿到文件流（含 Content-Disposition 头）
      const response = await fetch('/api/backup/download', {
        method: 'GET',
        headers: { 'Authorization': `Bearer ${localStorage.getItem('token') || ''}` }
      })
      if (!response.ok) {
        const err = await response.json().catch(() => ({ detail: '备份失败' }))
        throw new Error(err.detail || '备份失败')
      }
      const blob = await response.blob()
      const sizeKb = (blob.size / 1024).toFixed(1)

      // 从响应头提取文件名（如果后端有设置）
      const dispo = response.headers.get('Content-Disposition') || ''
      const match = dispo.match(/filename=([^;]+)/)
      const filename = match ? match[1] : `figurebox_backup_${new Date().toISOString().replace(/[:.]/g, '-').slice(0, 19)}.json`

      // 创建下载链接
      const url = window.URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = filename
      document.body.appendChild(a)
      a.click()
      document.body.removeChild(a)
      window.URL.revokeObjectURL(url)

      lastBackupResult.value = {
        filename,
        size: blob.size,
        sizeKb,
        at: new Date()
      }
      // 将本次备份记录到历史表（前端本地）
      const at = lastBackupResult.value.at
      const pad = (n) => String(n).padStart(2, '0')
      backupHistory.value.unshift({
        time: `${at.getFullYear()}-${pad(at.getMonth() + 1)}-${pad(at.getDate())} ${pad(at.getHours())}:${pad(at.getMinutes())}:${pad(at.getSeconds())}`,
        type: '手动',
        size: `${sizeKb} KB`,
        filename
      })
      ElMessage.success(`备份完成：${filename}（${sizeKb} KB）`)
    } catch (error) {
      console.error('备份失败:', error)
      ElMessage.error(error.message || '备份失败，请稍后重试')
    } finally {
      backuping.value = false
    }
  }

  // ========== 选择恢复文件 ==========
  const handleFileChange = (event) => {
    const file = event.target.files?.[0] || null
    if (!file) {
      selectedFile.value = null
      selectedFileName.value = ''
      return
    }
    if (!file.name.toLowerCase().endsWith('.json')) {
      ElMessage.warning('请选择 .json 格式的备份文件')
      event.target.value = ''
      return
    }
    if (file.size > 50 * 1024 * 1024) {
      ElMessage.warning('备份文件大小不能超过 50 MB')
      event.target.value = ''
      return
    }
    selectedFile.value = file
    selectedFileName.value = file.name
  }

  // ========== 触发恢复 ==========
  const handleRestore = async () => {
    if (restoring.value) return
    if (!selectedFile.value) {
      ElMessage.warning('请先选择备份文件')
      return
    }
    restoring.value = true
    try {
      const result = await backupApi.restoreBackup(selectedFile.value)
      lastRestoreResult.value = result
      if (result.success) {
        ElMessage.success(result.message || '数据恢复完成，3 秒后自动刷新')
        // 3 秒后刷新页面，让用户看到全新数据
        setTimeout(() => {
          window.location.reload()
        }, 3000)
      } else {
        ElMessage.error(result.message || '数据恢复失败')
      }
    } catch (error) {
      console.error('恢复失败:', error)
      const detail = error.response?.data?.detail || error.message || '恢复失败，请稍后重试'
      ElMessage.error(detail)
    } finally {
      restoring.value = false
    }
  }

  // ========== 清除已选文件 ==========
  const clearSelectedFile = () => {
    selectedFile.value = null
    selectedFileName.value = ''
  }

  // ========== 切换自动备份 ==========
  const toggleAutoBackup = () => {
    autoBackupEnabled.value = !autoBackupEnabled.value
  }

  // ========== 保存备份设置 ==========
  const saveBackupSettings = () => {
    // 当前仅在前端记录设置项；后端暂不持久化自动备份策略
    // 留作后续接入自动备份任务时使用
    const summary = {
      enabled: autoBackupEnabled.value,
      frequency: backupFrequency.value,
      retain: backupRetain.value
    }
    ElMessage.success(
      autoBackupEnabled.value
        ? `自动备份设置已保存（${frequencyLabel(backupFrequency.value)} / ${retainLabel(backupRetain.value)}）`
        : '自动备份已关闭'
    )
    return summary
  }

  const frequencyLabel = (v) => ({ daily: '每天', weekly: '每周', monthly: '每月' })[v] || v
  const retainLabel = (v) => v === 0 ? '不限制' : `保留最近 ${v} 份`

  return {
    // state
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
    // actions
    handleDownloadBackup,
    handleFileChange,
    handleRestore,
    clearSelectedFile,
    toggleAutoBackup,
    saveBackupSettings,
    frequencyLabel,
    retainLabel
  }
}
