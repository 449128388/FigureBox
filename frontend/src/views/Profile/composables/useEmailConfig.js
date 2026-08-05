/**
 * useEmailConfig.js - 邮箱设置（SMTP 发件配置）业务逻辑 composable
 *
 * 功能说明：
 * - 业务逻辑与 UI 组件解耦（由 Profile.vue 消费，透传给 PanelEmail.vue）
 * - 状态：SMTP 配置表单 / 密码可见性 / 测试状态 / 测试邮件发送状态 / 提交中
 * - 错误反馈偏好：服务端错误以 ElMessage.error 展示；表单内操作均含 loading 态
 * - 业务背景：配置 SMTP 后系统可通过此通道发送密码重置 / 尾款到期提醒 / 资产周报
 */
import { ref, computed } from 'vue'
import { ElMessage } from 'element-plus'
import { emailApi } from '../api/emailApi'

// 授权码已配置时的掩码占位（不暴露明文，同时避免输入框显示为空）
const PASSWORD_MASK = '••••••••'

export function useEmailConfig() {
  // ========== 状态：SMTP 配置 ==========
  const emailConfig = ref({
    smtp_host: '',
    smtp_port: 465,
    smtp_from_email: '',
    smtp_from_name: 'FigureBox 系统通知',
    smtp_password: '',
    smtp_password_set: false,    // 后端返回：密码是否已设置（不回传原密码）
    smtp_secure_mode: 'ssl',
    smtp_last_test_at: null,
    smtp_last_test_status: ''
  })
  const passwordVisible = ref(false)   // 控制授权码输入框明文/密文

  // ========== 状态：操作中 ==========
  const loadingConfig = ref(false)     // 拉取配置中
  const savingConfig = ref(false)      // 保存中
  const testingConnection = ref(false) // 测试连接中
  const sendingTestEmail = ref(false)  // 发送测试邮件中

  // ========== 状态：测试收件人 ==========
  const testRecipient = ref('')        // 测试邮件收件邮箱

  // ========== 计算属性：连接状态展示（与 profile_settings_v8_email.html 状态卡 1:1）==========
  // 初始状态无 emailStatusClass（卡片为绿色 success 默认），无测试记录时由面板 prop 兜底
  const emailStatusText = computed(() => {
    const status = emailConfig.value.smtp_last_test_status
    if (!status) return '尚未验证'
    if (status === 'success') return '测试邮件发送成功'
    if (status === 'failed') return '上次测试失败'
    return '连接状态未知'
  })

  const emailStatusDetail = computed(() => {
    const at = emailConfig.value.smtp_last_test_at
    const status = emailConfig.value.smtp_last_test_status
    if (!at) return '请填写下方配置并点击「测试连接」验证发件功能是否正常'
    const date = new Date(at)
    const pad = (n) => String(n).padStart(2, '0')
    const ymd = `${date.getFullYear()}-${pad(date.getMonth() + 1)}-${pad(date.getDate())}`
    const hms = `${pad(date.getHours())}:${pad(date.getMinutes())}:${pad(date.getSeconds())}`
    if (status === 'success') return `最后测试时间：${ymd} ${hms}`
    if (status === 'failed') return `请检查配置后重新测试（${ymd} ${hms}）`
    return `最后测试时间：${ymd} ${hms}`
  })

  const emailStatusClass = computed(() => {
    const status = emailConfig.value.smtp_last_test_status
    // 与 HTML 原版一致：初始无 status 时不挂任何 class（卡片走默认 success 绿底）
    if (!status) return ''
    if (status === 'success') return ''
    if (status === 'failed') return 'error'
    return ''
  })

  const emailStatusIconColor = computed(() => {
    const status = emailConfig.value.smtp_last_test_status
    // 与 HTML 原版一致：初始无 status 时 icon 用 #9499a0 灰色
    if (!status || status === 'success') return '#52c41a'
    if (status === 'failed') return '#f25d8e'
    return '#9499a0'
  })

  // ========== 操作：拉取配置 ==========
  const loadEmailConfig = async () => {
    loadingConfig.value = true
    try {
      const data = await emailApi.getConfig()
      // 后端不回传原密码，仅回传 password_set；已配置时用掩码占位填充输入框（避免显示为空）
      emailConfig.value = {
        ...emailConfig.value,
        smtp_host: data.smtp_host || '',
        smtp_port: data.smtp_port || 465,
        smtp_from_email: data.smtp_from_email || '',
        smtp_from_name: data.smtp_from_name || 'FigureBox 系统通知',
        smtp_password: data.smtp_password_set ? PASSWORD_MASK : '',
        smtp_password_set: !!data.smtp_password_set,
        smtp_secure_mode: data.smtp_secure_mode || 'ssl',
        smtp_last_test_at: data.smtp_last_test_at || null,
        smtp_last_test_status: data.smtp_last_test_status || ''
      }
    } catch (error) {
      console.error('读取 SMTP 配置失败:', error)
      ElMessage.error('读取 SMTP 配置失败')
    } finally {
      loadingConfig.value = false
    }
  }

  // ========== 操作：保存配置 ==========
  const saveEmailConfig = async () => {
    if (savingConfig.value) return
    // 仅当用户输入了新的授权码（且不是掩码占位）时才更新，避免空值/掩码覆盖已存在的密码
    const payload = {
      smtp_host: emailConfig.value.smtp_host,
      smtp_port: Number(emailConfig.value.smtp_port) || 465,
      smtp_from_email: emailConfig.value.smtp_from_email,
      smtp_from_name: emailConfig.value.smtp_from_name,
      smtp_secure_mode: emailConfig.value.smtp_secure_mode
    }
    if (emailConfig.value.smtp_password && emailConfig.value.smtp_password !== PASSWORD_MASK) {
      payload.smtp_password = emailConfig.value.smtp_password
    }

    savingConfig.value = true
    try {
      const data = await emailApi.updateConfig(payload)
      ElMessage.success('SMTP 配置已保存')
      // 回填后端返回；密码不回传，已配置时用掩码占位（避免输入框显示为空）
      emailConfig.value = {
        ...emailConfig.value,
        smtp_host: data.smtp_host || '',
        smtp_port: data.smtp_port || 465,
        smtp_from_email: data.smtp_from_email || '',
        smtp_from_name: data.smtp_from_name || 'FigureBox 系统通知',
        smtp_password: data.smtp_password_set ? PASSWORD_MASK : '',
        smtp_password_set: !!data.smtp_password_set,
        smtp_secure_mode: data.smtp_secure_mode || 'ssl',
        smtp_last_test_at: data.smtp_last_test_at || null,
        smtp_last_test_status: data.smtp_last_test_status || ''
      }
    } catch (error) {
      console.error('保存 SMTP 配置失败:', error)
      const detail = error.response?.data?.detail || '保存失败，请稍后重试'
      ElMessage.error(typeof detail === 'string' ? detail : JSON.stringify(detail))
    } finally {
      savingConfig.value = false
    }
  }

  // ========== 操作：测试连接 ==========
  const testEmailConnection = async () => {
    if (testingConnection.value) return
    testingConnection.value = true
    try {
      const result = await emailApi.testConnection()
      if (result.success) {
        ElMessage.success(result.message || 'SMTP 连接测试成功')
      } else {
        ElMessage.error(result.message || 'SMTP 连接测试失败')
      }
      // 重新拉取后端状态以更新 last_test_at / last_test_status
      await loadEmailConfig()
    } catch (error) {
      console.error('测试 SMTP 连接失败:', error)
      const detail = error.response?.data?.detail || '测试失败，请稍后重试'
      ElMessage.error(typeof detail === 'string' ? detail : JSON.stringify(detail))
      await loadEmailConfig()
    } finally {
      testingConnection.value = false
    }
  }

  // ========== 操作：发送测试邮件 ==========
  const sendTestEmail = async () => {
    if (sendingTestEmail.value) return
    if (!testRecipient.value || !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(testRecipient.value)) {
      ElMessage.warning('请输入有效的测试收件邮箱')
      return
    }
    sendingTestEmail.value = true
    try {
      const result = await emailApi.sendTestEmail(testRecipient.value)
      if (result.success) {
        ElMessage.success(result.message || '测试邮件已发送')
        testRecipient.value = ''
      } else {
        ElMessage.error(result.message || '测试邮件发送失败')
      }
      await loadEmailConfig()
    } catch (error) {
      console.error('发送测试邮件失败:', error)
      const detail = error.response?.data?.detail || '发送失败，请稍后重试'
      ElMessage.error(typeof detail === 'string' ? detail : JSON.stringify(detail))
      await loadEmailConfig()
    } finally {
      sendingTestEmail.value = false
    }
  }

  // ========== 操作：切换密码可见性 ==========
  const togglePasswordVisible = () => {
    passwordVisible.value = !passwordVisible.value
  }

  return {
    // state
    emailConfig,
    passwordVisible,
    testRecipient,
    loadingConfig,
    savingConfig,
    testingConnection,
    sendingTestEmail,
    // computed
    emailStatusText,
    emailStatusDetail,
    emailStatusClass,
    emailStatusIconColor,
    // actions
    loadEmailConfig,
    saveEmailConfig,
    testEmailConnection,
    sendTestEmail,
    togglePasswordVisible
  }
}
