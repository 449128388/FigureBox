/**
 * useBackup.js - 系统备份/恢复业务逻辑 composable
 *
 * 功能说明：
 * - 业务逻辑与 UI 组件解耦（本 composable 由 BackupPanel.vue 消费）
 * - 状态：备份中/恢复中/已选文件/成功消息/错误消息/自动备份配置/备份历史
 * - 提供：handleDownloadBackup / handleFileChange / handleRestore / 自动备份开关与策略 / 历史拉取与下载与删除
 *
 * 2026-07-31 升级：所有「自动备份设置 / 备份历史」均改为后端持久化，不再仅存活在前端
 * - loadSettings()        启动时从后端拉配置
 * - saveBackupSettings()  PUT 后端，失败时回滚 UI
 * - loadHistory()         从后端拉分页历史
 * - handleDownloadRecord  按记录 ID 重新下载
 * - handleDeleteRecord    DELETE 后端记录 + 重新拉历史
 */
import { ref, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { backupApi } from '../api/backupApi'

export function useBackup() {
  // ========== 状态 ==========
  const backuping = ref(false)          // 备份进行中
  const restoring = ref(false)          // 恢复进行中
  const selectedFile = ref(null)        // 待恢复的备份文件
  const selectedFileName = ref('')      // 待恢复文件名（展示用）
  const lastBackupResult = ref(null)    // 最近一次备份结果
  const lastRestoreResult = ref(null)   // 最近一次恢复结果

  // ========== 自动备份设置（启动时由后端填充）==========
  const settingsLoaded = ref(false)               // 是否已从后端拉过
  const autoBackupEnabled = ref(false)            // 自动备份开关
  const backupFrequency = ref('weekly')           // daily / weekly / monthly
  const backupRetain = ref(5)                     // 保留份数（3/5/10/0=不限制）
  const lastAutoBackupAt = ref(null)              // 上次自动备份时间

  // ========== 备份历史（后端分页）==========
  const historyLoading = ref(false)
  const historyTotal = ref(0)
  const historyPage = ref(1)
  const historyPageSize = ref(10)
  const backupHistory = ref([])                   // 从后端拉的记录列表

  // 启动时拉取的「上次手动备份摘要」（保留兼容）
  const lastBackupSummary = computed(() => {
    if (lastBackupResult.value) {
      const at = lastBackupResult.value.at
      const ymd = `${at.getFullYear()}-${String(at.getMonth() + 1).padStart(2, '0')}-${String(at.getDate()).padStart(2, '0')}`
      const hms = `${String(at.getHours()).padStart(2, '0')}:${String(at.getMinutes()).padStart(2, '0')}:${String(at.getSeconds()).padStart(2, '0')}`
      return { time: `${ymd} ${hms}`, source: '手动' }
    }
    return null
  })

  // ========== 启动时初始化（拉配置 + 拉历史）==========
  const loadSettings = async () => {
    try {
      const data = await backupApi.getSettings()
      autoBackupEnabled.value = !!data.enabled
      backupFrequency.value = data.frequency || 'weekly'
      backupRetain.value = typeof data.retain === 'number' ? data.retain : 5
      lastAutoBackupAt.value = data.last_auto_backup_at || null
      settingsLoaded.value = true
    } catch (error) {
      console.error('读取自动备份配置失败:', error)
      ElMessage.warning('读取自动备份配置失败，使用默认值')
    }
  }

  const loadHistory = async () => {
    historyLoading.value = true
    try {
      const data = await backupApi.listRecords(historyPage.value, historyPageSize.value)
      historyTotal.value = data.total || 0
      // 把后端 ISO 时间转成中文展示格式
      backupHistory.value = (data.items || []).map((item) => {
        const at = item.created_at ? new Date(item.created_at) : null
        const pad = (n) => String(n).padStart(2, '0')
        const time = at
          ? `${at.getFullYear()}-${pad(at.getMonth() + 1)}-${pad(at.getDate())} ${pad(at.getHours())}:${pad(at.getMinutes())}:${pad(at.getSeconds())}`
          : item.created_at
        return {
          id: item.id,
          time,
          type: item.backup_type === 'auto' ? '自动' : '手动',
          size: `${item.size_kb} KB`,
          recordCount: item.record_count,
          filename: item.filename
        }
      })
    } catch (error) {
      console.error('读取备份历史失败:', error)
      ElMessage.warning('读取备份历史失败')
    } finally {
      historyLoading.value = false
    }
  }

  onMounted(() => {
    loadSettings()
    loadHistory()
  })

  // ========== 立即备份 ==========
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

      // 从响应头提取文件名
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
      ElMessage.success(`备份完成：${filename}（${sizeKb} KB）`)

      // 备份完成后刷新历史列表（让本次记录立刻可见）
      historyPage.value = 1
      await loadHistory()
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

  // ========== 切换自动备份（仅前端 UI 状态，保存时才落库）==========
  const toggleAutoBackup = () => {
    autoBackupEnabled.value = !autoBackupEnabled.value
  }

  // ========== 保存自动备份设置（PUT 后端）==========
  const saveBackupSettings = async () => {
    try {
      const payload = {
        enabled: autoBackupEnabled.value,
        frequency: backupFrequency.value,
        retain: backupRetain.value
      }
      const data = await backupApi.updateSettings(payload)
      // 用后端返回值回填（含校验后的最终值）
      autoBackupEnabled.value = !!data.enabled
      backupFrequency.value = data.frequency || 'weekly'
      backupRetain.value = typeof data.retain === 'number' ? data.retain : 5
      ElMessage.success(
        autoBackupEnabled.value
          ? `自动备份设置已保存（${frequencyLabel(backupFrequency.value)} / ${retainLabel(backupRetain.value)}）`
          : '自动备份设置已保存（已关闭）'
      )
      return data
    } catch (error) {
      console.error('保存自动备份设置失败:', error)
      ElMessage.error('保存失败，请稍后重试')
      // 失败时重新拉一次后端状态回滚 UI
      await loadSettings()
    }
  }

  // ========== 历史操作：下载 / 删除 ==========
  const handleDownloadRecord = async (id) => {
    try {
      const response = await fetch(`/api/backup/records/${id}/download`, {
        method: 'GET',
        headers: { 'Authorization': `Bearer ${localStorage.getItem('token') || ''}` }
      })
      if (!response.ok) {
        const err = await response.json().catch(() => ({ detail: '下载失败' }))
        throw new Error(err.detail || '下载失败')
      }
      const blob = await response.blob()
      const dispo = response.headers.get('Content-Disposition') || ''
      const match = dispo.match(/filename=([^;]+)/)
      const filename = match ? match[1] : `backup_${id}.json`

      const url = window.URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = filename
      document.body.appendChild(a)
      a.click()
      document.body.removeChild(a)
      window.URL.revokeObjectURL(url)
      ElMessage.success(`已下载：${filename}`)
    } catch (error) {
      console.error('下载历史备份失败:', error)
      ElMessage.error(error.message || '下载失败')
    }
  }

  const handleDeleteRecord = async (id) => {
    try {
      await ElMessageBox.confirm(
        '确认删除该备份记录？磁盘上的 JSON 文件也会一并删除，无法恢复。',
        '确认删除',
        { confirmButtonText: '确认删除', cancelButtonText: '取消', type: 'warning' }
      )
    } catch {
      return  // 用户取消
    }
    try {
      const result = await backupApi.deleteRecord(id)
      if (result.success) {
        ElMessage.success(result.message || '已删除')
        await loadHistory()
      } else {
        ElMessage.error(result.message || '删除失败')
      }
    } catch (error) {
      console.error('删除历史备份失败:', error)
      ElMessage.error(error.response?.data?.detail || '删除失败')
    }
  }

  const refreshHistory = async () => {
    historyPage.value = 1
    await loadHistory()
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
    lastAutoBackupAt,
    settingsLoaded,
    backupHistory,
    historyLoading,
    historyTotal,
    historyPage,
    historyPageSize,
    lastBackupSummary,
    // actions
    handleDownloadBackup,
    handleFileChange,
    handleRestore,
    clearSelectedFile,
    toggleAutoBackup,
    saveBackupSettings,
    handleDownloadRecord,
    handleDeleteRecord,
    refreshHistory,
    loadSettings,
    loadHistory,
    frequencyLabel,
    retainLabel
  }
}
