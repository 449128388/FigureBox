/**
 * useLoginFlow.js - 登录 / 忘记密码 业务逻辑 composable
 *
 * 功能说明：
 * - 集中管理 4 个视图（登录 / 忘记密码-步骤1 / 忘记密码-步骤2 / 重置成功）的全部状态与方法
 * - 业务逻辑与 UI 组件解耦（由 Login.vue 消费）
 * - 状态：
 *   - currentView: 当前视图（'login' | 'forgot-1' | 'forgot-2' | 'success'）
 *   - loginForm / forgotForm / resetForm: 三张表单
 *   - 字段级校验错误 / 密码可见性 / 密码强度 / 提交中 / 倒计时
 *   - serverError: 服务端错误
 * - 视图切换：goToLogin / goToForgot / goToForgotStep1 / goToForgotStep2 / goToSuccess
 * - 视图切换 / 计时器 / 全部 axios 请求均在本 composable 内完成
 *
 * 校验规则与 login_with_forgot_password.html 保持一致：
 *   - 邮箱必填，格式 ^[^\s@]+@[^\s@]+\.[^\s@]+$
 *   - 密码 8-20 位
 *   - 验证码 6 位数字
 *   - 两次输入的新密码一致
 *   - 密码强度：长度/字母数字混合/特殊字符/超长
 */
import { ref, computed, onUnmounted } from 'vue'
import { ElMessage } from 'element-plus'
import { authApi } from '../api/authApi'
import { useUserStore } from '../../../store'

const PASSWORD_MASK = '••••••••'

export function useLoginFlow() {
  const userStore = useUserStore()

  // ========== 视图切换 ==========
  const currentView = ref('login')
  const goToLogin = () => {
    currentView.value = 'login'
    loginForm.value.password = ''
    serverError.value = ''
  }
  const goToForgot = () => {
    currentView.value = 'forgot-1'
    resetForgotFlow()
  }
  const goToForgotStep1 = () => {
    currentView.value = 'forgot-1'
    updateStep1UI()
  }
  const goToForgotStep2 = async () => {
    // 字段级校验
    serverError.value = ''
    const email = forgotForm.value.email.trim()
    const code = forgotForm.value.code.trim()
    if (!email || !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
      forgotErrors.value.email = '请输入有效的邮箱地址'
      return
    }
    forgotErrors.value.email = ''
    if (!code || code.length !== 6) {
      forgotErrors.value.code = '请输入6位验证码'
      return
    }
    forgotErrors.value.code = ''

    // 校验验证码（不消费）
    verifyingCode.value = true
    try {
      const response = await authApi.verifyResetCode(email, code)
      if (!response.success) {
        forgotErrors.value.code = response.message || '验证码不正确或已失效'
        return
      }
      currentView.value = 'forgot-2'
      updateStep2UI()
    } catch (error) {
      forgotErrors.value.code = error.response?.data?.detail || '验证码校验失败，请稍后重试'
    } finally {
      verifyingCode.value = false
    }
  }
  const goToSuccess = () => {
    currentView.value = 'success'
  }

  // ========== 登录表单 ==========
  const loginForm = ref({ email: '', password: '' })
  const serverError = ref('')
  const submittingLogin = ref(false)
  const loginPasswordVisible = ref(false)
  const submittingText = ref('登录')

  const handleLogin = async () => {
    serverError.value = ''
    const email = loginForm.value.email.trim()
    const pwd = loginForm.value.password.trim()
    if (!email) {
      ElMessage.warning('请输入邮箱地址')
      return
    }
    if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
      ElMessage.warning('请输入有效的邮箱地址')
      return
    }
    if (!pwd) {
      ElMessage.warning('请输入密码')
      return
    }
    submittingLogin.value = true
    submittingText.value = '登录中...'
    try {
      await userStore.login(email, pwd)
      ElMessage.success('登录成功，正在跳转...')
      // 跳转到首页
      window.location.href = '/home'
    } catch (error) {
      const msg = error.response?.data?.detail || '登录失败，请检查邮箱和密码'
      serverError.value = msg
    } finally {
      submittingLogin.value = false
      submittingText.value = '登录'
    }
  }

  // ========== 忘记密码 - 步骤1 表单 ==========
  const forgotForm = ref({ email: '', code: '' })
  const forgotErrors = ref({ email: '', code: '' })
  const sendingCode = ref(false)
  const verifyingCode = ref(false)
  const sendCooldown = ref(0) // 0 = 可点击，>0 = 倒计时中
  let cooldownTimer = null

  const sendForgotCode = async () => {
    forgotErrors.value.email = ''
    const email = forgotForm.value.email.trim()
    if (!email) {
      forgotErrors.value.email = '请输入邮箱地址'
      return
    }
    if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
      forgotErrors.value.email = '请输入有效的邮箱地址'
      return
    }
    sendingCode.value = true
    try {
      const response = await authApi.forgotPassword(email)
      if (response.success) {
        ElMessage.success(response.message || '验证码已发送，请注意查收')
        startCooldown(60)
      } else {
        forgotErrors.value.email = response.message || '验证码发送失败'
      }
    } catch (error) {
      forgotErrors.value.email = error.response?.data?.detail || '验证码发送失败，请稍后重试'
    } finally {
      sendingCode.value = false
    }
  }

  const startCooldown = (seconds) => {
    sendCooldown.value = seconds
    if (cooldownTimer) clearInterval(cooldownTimer)
    cooldownTimer = setInterval(() => {
      sendCooldown.value--
      if (sendCooldown.value <= 0) {
        clearInterval(cooldownTimer)
        cooldownTimer = null
      }
    }, 1000)
  }

  // ========== 忘记密码 - 步骤2 表单（新密码）==========
  const resetForm = ref({ pwd: '', confirm: '' })
  const resetErrors = ref({ pwd: '', confirm: '', match: '' })
  const resetPasswordVisible = ref({ pwd: false, confirm: false })
  const submittingReset = ref(false)
  const submittingResetText = ref('确认重置')

  // 密码强度（与 HTML checkResetPwdStrength() 算法一致）
  const strengthScore = computed(() => {
    const val = resetForm.value.pwd
    if (!val) return 0
    let score = 0
    if (val.length >= 8) score++
    if (/[a-zA-Z]/.test(val) && /\d/.test(val)) score++
    if (/[^a-zA-Z0-9]/.test(val)) score++
    if (val.length >= 12) score++
    return score
  })
  const strengthLabel = computed(() => ['未输入', '弱', '中', '强', '极强'][strengthScore.value])
  const strengthColor = computed(() => {
    const colors = ['#e8e8e8', '#ff4d4f', '#faad14', '#4caf50', '#4caf50']
    return colors[strengthScore.value]
  })
  const strengthSegments = computed(() => [1, 2, 3, 4].map(i => i <= strengthScore.value))
  const strengthShown = computed(() => resetForm.value.pwd.length > 0)

  const submitResetPwd = async () => {
    resetErrors.value = { pwd: '', confirm: '', match: '' }
    const pwd = resetForm.value.pwd
    const confirm = resetForm.value.confirm
    const email = forgotForm.value.email.trim()
    const code = forgotForm.value.code.trim()

    if (!pwd) {
      resetErrors.value.pwd = '请输入新密码'
      return
    }
    if (pwd.length < 8 || pwd.length > 20) {
      resetErrors.value.pwd = '新密码长度需在 8-20 位之间'
      return
    }
    if (!confirm) {
      resetErrors.value.confirm = '请再次输入新密码'
      return
    }
    if (pwd !== confirm) {
      resetErrors.value.match = '两次输入的密码不一致'
      return
    }

    submittingReset.value = true
    submittingResetText.value = '重置中...'
    try {
      const response = await authApi.resetPassword(email, code, pwd)
      if (response.success) {
        goToSuccess()
        ElMessage.success(response.message || '密码重置成功')
      } else {
        // 业务错误
        if (response.message && response.message.includes('验证码')) {
          // 验证码相关错误 → 退回步骤 1
          ElMessage.error(response.message)
          currentView.value = 'forgot-1'
          updateStep1UI()
          forgotForm.value.code = ''
        } else {
          resetErrors.value.match = response.message || '重置失败'
        }
      }
    } catch (error) {
      const msg = error.response?.data?.detail || '密码重置失败，请稍后重试'
      if (msg.includes('验证码')) {
        ElMessage.error(msg)
        currentView.value = 'forgot-1'
        updateStep1UI()
        forgotForm.value.code = ''
      } else {
        resetErrors.value.match = msg
      }
    } finally {
      submittingReset.value = false
      submittingResetText.value = '确认重置'
    }
  }

  // ========== 步骤指示器状态 ==========
  const stepState = ref({ step1: 'active', line1: '', step2: '' })
  const updateStep1UI = () => {
    stepState.value = { step1: 'active', line1: '', step2: '' }
  }
  const updateStep2UI = () => {
    stepState.value = { step1: 'completed', line1: 'active', step2: 'active' }
  }

  // ========== 注册入口（跳转到独立注册页）==========
  const onRegisterClick = () => {
    window.location.href = '/register'
  }

  // ========== 重置整个忘记密码流程 ==========
  const resetForgotFlow = () => {
    forgotForm.value = { email: '', code: '' }
    forgotErrors.value = { email: '', code: '' }
    resetForm.value = { pwd: '', confirm: '' }
    resetErrors.value = { pwd: '', confirm: '', match: '' }
    sendCooldown.value = 0
    if (cooldownTimer) {
      clearInterval(cooldownTimer)
      cooldownTimer = null
    }
    updateStep1UI()
  }

  // 组件卸载时清理计时器
  onUnmounted(() => {
    if (cooldownTimer) clearInterval(cooldownTimer)
  })

  return {
    // state
    currentView,
    loginForm,
    serverError,
    submittingLogin,
    submittingText,
    loginPasswordVisible,
    forgotForm,
    forgotErrors,
    sendingCode,
    verifyingCode,
    sendCooldown,
    resetForm,
    resetErrors,
    resetPasswordVisible,
    submittingReset,
    submittingResetText,
    strengthScore,
    strengthLabel,
    strengthColor,
    strengthSegments,
    strengthShown,
    stepState,
    // actions
    goToLogin,
    goToForgot,
    goToForgotStep1,
    goToForgotStep2,
    goToSuccess,
    handleLogin,
    sendForgotCode,
    submitResetPwd,
    onRegisterClick,
    PASSWORD_MASK
  }
}
