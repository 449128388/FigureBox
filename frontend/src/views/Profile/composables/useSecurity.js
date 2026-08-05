/**
 * useSecurity.js - 账号安全（修改登录密码）业务逻辑 composable
 *
 * 功能说明：
 * - 业务逻辑与 UI 组件解耦（由 Profile.vue 消费，透传给 ChangePasswordDialog.vue）
 * - 状态：弹窗显隐 / 表单三字段 / 字段级校验错误 / 密码可见性 / 密码强度 / 提交中
 * - 校验规则与 profile_settings_v6_backup.html「修改密码」页面保持一致：
 *   - 当前密码必填
 *   - 新密码 8-20 位
 *   - 两次输入的新密码一致
 * - 错误反馈偏好：字段级内联提示（不用 Toast / 弹窗），服务端错误展示在弹窗内联错误区
 * - 密码强度算法与 HTML checkPwdStrength() 完全一致（长度/字母数字混合/特殊字符/超长）
 */
import { ref, computed } from 'vue'
import { ElMessage } from 'element-plus'
import { securityApi } from '../api/securityApi'
import { useUserStore } from '../../../store'

export function useSecurity() {
  const userStore = useUserStore()

  // ========== 弹窗显隐 ==========
  const dialogVisible = ref(false)
  const openDialog = () => {
    resetForm()
    dialogVisible.value = true
  }
  const closeDialog = () => {
    dialogVisible.value = false
  }

  // ========== 表单状态 ==========
  const pwdForm = ref({ current: '', new: '', confirm: '' })
  const errors = ref({ current: '', new: '', confirm: '', server: '' })
  const passwordVisible = ref({ current: false, new: false, confirm: false })
  const submitting = ref(false)

  const resetForm = () => {
    pwdForm.value = { current: '', new: '', confirm: '' }
    errors.value = { current: '', new: '', confirm: '', server: '' }
    passwordVisible.value = { current: false, new: false, confirm: false }
    submitting.value = false
  }

  // ========== 密码强度（与 HTML checkPwdStrength() 算法一致）==========
  const strengthScore = computed(() => {
    const val = pwdForm.value.new
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
    const colors = ['#e3e5e7', '#ff4d4f', '#faad14', '#52c41a', '#52c41a']
    return colors[strengthScore.value]
  })
  const strengthSegments = computed(() => [1, 2, 3, 4].map(i => i <= strengthScore.value))
  const strengthShown = computed(() => pwdForm.value.new.length > 0)

  // ========== 提交修改 ==========
  const submitChangePassword = async () => {
    // 重置本次提交的所有内联错误
    errors.value = { current: '', new: '', confirm: '', server: '' }

    // 字段级校验（内联提示）
    if (!pwdForm.value.current) {
      errors.value.current = '请输入当前密码'
      return
    }
    if (!pwdForm.value.new) {
      errors.value.new = '请输入新密码'
      return
    }
    if (pwdForm.value.new.length < 8 || pwdForm.value.new.length > 20) {
      errors.value.new = '新密码长度需在 8-20 位之间'
      return
    }
    if (pwdForm.value.new !== pwdForm.value.confirm) {
      errors.value.confirm = '两次输入的密码不一致'
      return
    }

    submitting.value = true
    try {
      await securityApi.changePassword(pwdForm.value.current, pwdForm.value.new)
      ElMessage.success('密码修改成功，请使用新密码重新登录')
      dialogVisible.value = false
      resetForm()
      // 修改密码后强制重新登录（旧 token 已失效，需用新密码登录）
      userStore.logout()
      window.location.href = '/login'
    } catch (error) {
      // 服务端错误（当前密码不正确等）内联展示
      errors.value.server = error.response?.data?.detail || '密码修改失败，请稍后重试'
    } finally {
      submitting.value = false
    }
  }

  return {
    dialogVisible,
    openDialog,
    closeDialog,
    pwdForm,
    errors,
    passwordVisible,
    submitting,
    strengthScore,
    strengthLabel,
    strengthColor,
    strengthSegments,
    strengthShown,
    submitChangePassword
  }
}
