/**
 * useLicense.js - 许可管理业务逻辑 composable
 *
 * 功能说明：
 * - 业务逻辑与 UI 组件解耦（由 Profile.vue 消费，透传给 PanelLicense.vue）
 * - 状态：当前许可状态 / 历史记录 / 表单输入 / 操作中态
 * - 操作：在线激活 / 离线导入 / 吊销 / 删除 / 导出 .req
 * - 错误反馈偏好：服务端错误以 ElMessage.error 展示；表单内操作均含 loading 态
 * - 业务背景：详见 docs/license-system-design.md
 */
import { ref, computed } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { licenseApi } from '../api/licenseApi'

/**
 * 生成稳定的浏览器指纹（用于 DEVICE_ID）
 * 基于多种浏览器特征生成唯一且稳定的哈希值
 * 同一浏览器/同一机器上指纹保持不变
 */
function _generateBrowserFingerprint() {
  try {
    const parts = []

    // 1. User Agent
    parts.push(navigator.userAgent || '')

    // 2. 屏幕信息
    parts.push(`${screen.width}x${screen.height}x${screen.colorDepth}`)

    // 3. 时区
    parts.push(Intl.DateTimeFormat().resolvedOptions().timeZone || '')

    // 4. 语言
    parts.push(navigator.language || '')

    // 5. 平台
    parts.push(navigator.platform || '')

    // 6. CPU 核心数（如果可用）
    if (navigator.hardwareConcurrency) {
      parts.push(`cpu:${navigator.hardwareConcurrency}`)
    }

    // 7. 设备内存（如果可用）
    if (navigator.deviceMemory) {
      parts.push(`mem:${navigator.deviceMemory}`)
    }

    // 8. Canvas 指纹（可选，增加唯一性）
    try {
      const canvas = document.createElement('canvas')
      canvas.width = 200
      canvas.height = 50
      const ctx = canvas.getContext('2d')
      ctx.textBaseline = 'top'
      ctx.font = '14px Arial'
      ctx.fillStyle = '#f60'
      ctx.fillRect(125, 1, 62, 20)
      ctx.fillStyle = '#069'
      ctx.fillText('FigureBox License', 2, 15)
      ctx.strokeStyle = 'rgba(102, 204, 0, 0.7)'
      ctx.strokeText('FigureBox License', 4, 17)
      parts.push(`canvas:${canvas.toDataURL().slice(-50)}`)
    } catch {
      parts.push('canvas:unavailable')
    }

    // 拼接并做简单哈希
    const raw = parts.join('|')
    let hash = 0
    for (let i = 0; i < raw.length; i++) {
      const char = raw.charCodeAt(i)
      hash = ((hash << 5) - hash) + char
      hash = hash & hash // Convert to 32bit integer
    }
    // 转为 32 位十六进制，固定长度
    return Math.abs(hash).toString(16).padStart(8, '0') +
           Math.abs(hash >>> 0).toString(16).padStart(8, '0') +
           (raw.length * 31).toString(16).padStart(8, '0') +
           raw.length.toString(16).padStart(8, '0')
  } catch {
    // 兜底：使用时间戳+随机数生成不太稳定但可用的 ID
    return `fallback_${Date.now().toString(16)}_${Math.random().toString(36).slice(2, 10)}`
  }
}

export function useLicense() {
  // ========== 状态：当前许可 ==========
  const licenseStatus = ref({
    license_key: '',
    plan: 'trial',
    plan_label: '试用版',
    features: [],
    issued_at: null,
    expires_at: null,
    activated_at: null,
    status: 'inactive',
    source: '',
    filename: '',
    machine_fingerprint: '',
    machine_hostname: ''
  })

  // ========== 状态：历史记录 ==========
  const history = ref({ items: [], total: 0 })

  // ========== 状态：表单 ==========
  const onlineKey = ref('')        // 在线激活密钥
  const offlineFilename = ref('')  // 离线导入文件名

  // ========== 状态：操作中 ==========
  const loadingStatus = ref(false)  // 拉取状态中
  const activating = ref(false)     // 在线激活中
  const importing = ref(false)     // 离线导入中
  const revoking = ref(false)      // 吊销中
  const deleting = ref(false)      // 删除中
  const exportingReq = ref(false)  // 导出 .req 中

  // ========== 计算属性：状态卡展示 ==========
  const isActive = computed(() => licenseStatus.value.status === 'active')
  const isInactive = computed(() => licenseStatus.value.status === 'inactive')
  const isExpired = computed(() => licenseStatus.value.status === 'expired')
  const isRevoked = computed(() => licenseStatus.value.status === 'revoked')

  // 状态卡文字 / 样式 / 图标色（与 HTML 原版配色一致）
  const statusCardText = computed(() => {
    if (isActive.value) return '已授权'
    if (isExpired.value) return '已过期'
    if (isRevoked.value) return '已吊销'
    return '未激活'
  })

  const statusCardClass = computed(() => {
    if (isActive.value) return ''
    if (isExpired.value || isRevoked.value) return 'warning'
    return 'warning'
  })

  const statusCardIconColor = computed(() => {
    if (isActive.value) return '#52c41a'
    if (isExpired.value) return '#faad14'
    if (isRevoked.value) return '#f25d8e'
    return '#9499a0'
  })

  // 状态卡详情：有效期至 X / 设备绑定: XXX
  const statusCardDetail = computed(() => {
    const s = licenseStatus.value
    const parts = []
    if (s.expires_at) {
      const d = new Date(s.expires_at)
      const pad = (n) => String(n).padStart(2, '0')
      parts.push(`有效期至 ${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())}`)
    }
    if (s.plan_label) parts.push(s.plan_label)
    if (s.machine_hostname) parts.push(`设备绑定: ${s.machine_hostname}`)
    return parts.join(' · ')
  })

  // ========== 操作：拉取状态 ==========
  const loadLicenseStatus = async () => {
    loadingStatus.value = true
    try {
      licenseStatus.value = await licenseApi.getStatus()
    } catch (error) {
      console.error('读取许可状态失败:', error)
      ElMessage.error('读取许可状态失败')
    } finally {
      loadingStatus.value = false
    }
  }

  // ========== 操作：拉取历史 ==========
  const loadHistory = async () => {
    try {
      history.value = await licenseApi.getHistory()
    } catch (error) {
      console.error('读取许可历史失败:', error)
      ElMessage.error('读取许可历史失败')
    }
  }

  // ========== 操作：在线激活 ==========
  const activateOnline = async () => {
    if (activating.value) return
    if (!onlineKey.value || onlineKey.value.trim().length < 16) {
      ElMessage.warning('请输入有效的许可密钥（至少 16 位）')
      return
    }
    activating.value = true
    try {
      const result = await licenseApi.activate(onlineKey.value)
      if (result.success) {
        ElMessage.success(result.message || '在线激活成功')
        onlineKey.value = ''
        await loadLicenseStatus()
        await loadHistory()
      } else {
        ElMessage.error(result.message || '在线激活失败')
      }
    } catch (error) {
      console.error('在线激活失败:', error)
      const detail = error.response?.data?.detail || '激活失败，请稍后重试'
      ElMessage.error(typeof detail === 'string' ? detail : JSON.stringify(detail))
    } finally {
      activating.value = false
    }
  }

  // ========== 操作：离线导入 ==========
  // 接收 File 对象（从 <input type="file"> change 事件获取）
  const importOffline = async (file) => {
    if (importing.value) return
    if (!file) return
    if (!file.name.toLowerCase().endsWith('.lic')) {
      ElMessage.warning('仅支持 .lic 格式的许可文件')
      return
    }
    if (file.size > 1024 * 1024) {
      ElMessage.warning('许可文件大小不能超过 1 MB')
      return
    }

    importing.value = true
    try {
      const content = await file.text()
      const result = await licenseApi.importFile(file.name, content)
      if (result.success) {
        ElMessage.success(result.message || '许可导入成功')
        offlineFilename.value = file.name
        await loadLicenseStatus()
        await loadHistory()
      } else {
        ElMessage.error(result.message || '许可导入失败')
      }
    } catch (error) {
      console.error('许可导入失败:', error)
      const detail = error.response?.data?.detail || '导入失败，请稍后重试'
      ElMessage.error(typeof detail === 'string' ? detail : JSON.stringify(detail))
    } finally {
      importing.value = false
    }
  }

  // ========== 操作：吊销 ==========
  const revokeLicense = async () => {
    if (revoking.value) return
    try {
      await ElMessageBox.confirm(
        '确定要吊销该许可证吗？吊销后相关功能将立即失效。',
        '吊销许可',
        { confirmButtonText: '确认吊销', cancelButtonText: '取消', type: 'warning' }
      )
    } catch {
      return
    }
    revoking.value = true
    try {
      const result = await licenseApi.revoke()
      if (result.success) {
        ElMessage.success(result.message || '许可已吊销')
        await loadLicenseStatus()
        await loadHistory()
      } else {
        ElMessage.error(result.message || '吊销失败')
      }
    } catch (error) {
      console.error('吊销失败:', error)
      const detail = error.response?.data?.detail || '吊销失败，请稍后重试'
      ElMessage.error(typeof detail === 'string' ? detail : JSON.stringify(detail))
    } finally {
      revoking.value = false
    }
  }

  // ========== 操作：删除记录 ==========
  const deleteLicense = async () => {
    if (deleting.value) return
    try {
      await ElMessageBox.confirm(
        '确定要删除该许可记录吗？此操作不可恢复。',
        '删除许可记录',
        { confirmButtonText: '确认删除', cancelButtonText: '取消', type: 'warning' }
      )
    } catch {
      return
    }
    deleting.value = true
    try {
      const result = await licenseApi.delete()
      if (result.success) {
        ElMessage.success(result.message || '许可记录已删除')
        await loadLicenseStatus()
        await loadHistory()
      } else {
        ElMessage.error(result.message || '删除失败')
      }
    } catch (error) {
      console.error('删除失败:', error)
      const detail = error.response?.data?.detail || '删除失败，请稍后重试'
      ElMessage.error(typeof detail === 'string' ? detail : JSON.stringify(detail))
    } finally {
      deleting.value = false
    }
  }

  // ========== 操作：导出 .req 请求文件 ==========
  const exportReqFile = async () => {
    if (exportingReq.value) return
    exportingReq.value = true
    try {
      // 使用前端浏览器特征生成稳定的 DEVICE_ID（同一浏览器/机器保持不变）
      const deviceId = _generateBrowserFingerprint()

      const data = await licenseApi.getMachineFingerprint()
      const content = [
        'FIGUREBOX_LICENSE_REQUEST_V1',
        `DEVICE_ID=${deviceId}`,
        `HOSTNAME=${data.hostname}`,
        `PLATFORM=${data.platform}`,
        `GENERATED_AT=${data.generated_at}`,
        'SIGNATURE=PENDING'
      ].join('\n')

      const blob = new Blob([content], { type: 'text/plain' })
      const url = URL.createObjectURL(blob)
      const a = document.createElement('a')
      const date = new Date().toISOString().slice(0, 10).replace(/-/g, '')
      a.href = url
      a.download = `figurebox_request_${date}.req`
      document.body.appendChild(a)
      a.click()
      document.body.removeChild(a)
      URL.revokeObjectURL(url)
      ElMessage.success('.req 请求文件已导出')
    } catch (error) {
      console.error('导出 .req 失败:', error)
      ElMessage.error('导出 .req 失败')
    } finally {
      exportingReq.value = false
    }
  }

  // ========== 操作：导出 .lic 文件（仅展示已激活许可的元信息，不导出真签） ==========
  const exportLicenseFile = (item) => {
    const content = JSON.stringify({
      license_key: item.license_key,
      plan: item.plan,
      features: [],
      issued_at: item.issued_at,
      expires_at: item.expires_at,
      exported_at: new Date().toISOString(),
      note: '备份导出（仅元信息，不含数字签名）'
    }, null, 2)
    const blob = new Blob([content], { type: 'text/plain' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `${item.license_key || 'license'}.lic`
    document.body.appendChild(a)
    a.click()
    document.body.removeChild(a)
    URL.revokeObjectURL(url)
    ElMessage.success('许可文件已导出')
  }

  return {
    // state
    licenseStatus,
    history,
    onlineKey,
    offlineFilename,
    loadingStatus,
    activating,
    importing,
    revoking,
    deleting,
    exportingReq,
    // computed
    isActive,
    isInactive,
    isExpired,
    isRevoked,
    statusCardText,
    statusCardClass,
    statusCardIconColor,
    statusCardDetail,
    // actions
    loadLicenseStatus,
    loadHistory,
    activateOnline,
    importOffline,
    revokeLicense,
    deleteLicense,
    exportReqFile,
    exportLicenseFile
  }
}
