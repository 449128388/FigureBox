import { ref, computed, onMounted } from 'vue'
import { useUserStore } from '../../../store'
import { ElMessage, ElMessageBox } from 'element-plus'
import axios from '../../../axios'

/**
 * useProfile.js - 个人中心所有面板的业务逻辑 composable
 *
 * 功能说明：
 * - 集中管理 9 个面板（基本资料 / 头像 / 隐私 / 推送 / 账号安全 / MinIO / 超时登出 / 账号注销）
 *   除「系统备份」外（备份功能由 useBackup.js 独立管理）的全部状态、计算属性与方法
 * - 全部 axios 请求 / ElMessage / ElMessageBox 调用均在本 composable 内完成
 * - 父页面 Profile.vue 调用一次 useProfile()，把返回的 state/actions 透传给子面板
 * - 子面板仅做 UI 渲染，通过 defineProps 接收 state、defineEmits 抛出交互事件
 */
export function useProfile() {
  const userStore = useUserStore()

  // ========== 面板路由 ==========
  const activePanel = ref('panel-basic')
  const switchPanel = (panelId) => {
    activePanel.value = panelId
  }

  // ========== 基本资料 ==========
  const basicForm = ref({
    nickname: '',
    signature: '',
    gender: 'secret',
    birthday: { year: '', month: '', day: '' },
    bio: ''
  })
  const nicknameLen = computed(() => basicForm.value.nickname.length)
  const signatureLen = computed(() => basicForm.value.signature.length)
  const bioLen = computed(() => basicForm.value.bio.length)
  const years = computed(() => {
    const y = new Date().getFullYear()
    return Array.from({ length: 100 }, (_, i) => y - i)
  })

  // ========== 隐私设置 ==========
  const privacySettings = ref({
    home_visibility: 'public',
    show_total: true,
    show_figures: false,
    show_asset: false,
    show_tags: true,
    show_feed: false
  })
  const homeVisibilityText = computed(() => {
    const map = {
      public: '公开',
      friends_only: '仅好友可见',
      private: '仅自己可见'
    }
    return map[privacySettings.value.home_visibility] || '公开'
  })

  // ========== 推送开关 ==========
  const toggles = ref({
    privacy_cabinet: true,
    privacy_profit: false,
    privacy_follow: true,
    push_balance_remind: true,
    push_price_alert: true,
    push_system_notice: true,
    push_weekly_report: false
  })

  // ========== 头像 ==========
  const avatarSrc = ref('')
  const selectedAvatarFile = ref(null)

  // ========== MinIO 配置 ==========
  const minioConfig = ref({
    endpoint: '',
    access_key: '',
    secret_key: '',
    bucket: '',
    public_url: '',
    secure: false
  })
  const minioStatusText = ref('当前连接状态未知')
  const minioStatusDetail = ref('')
  const minioStatusClass = ref('warning')
  const minioStatusIconColor = ref('#faad14')
  const testingConnection = ref(false)
  const resettingMinIO = ref(false)

  // ========== 超时登出 ==========
  const timeoutConfig = ref({
    timeout_minutes: 30,
    timeout_warning: true
  })
  const savingTimeout = ref(false)

  // ========== 切换开关 ==========
  const toggleSwitch = (key) => {
    toggles.value[key] = !toggles.value[key]
  }

  // ========== 切换隐私设置 ==========
  const togglePrivacy = async (key) => {
    privacySettings.value[key] = !privacySettings.value[key]
    try {
      await axios.put('/collector/privacy', { [key]: privacySettings.value[key] })
      ElMessage.success('设置已保存')
    } catch (error) {
      privacySettings.value[key] = !privacySettings.value[key]
      ElMessage.error('保存失败，请稍后重试')
    }
  }

  // ========== 主页可见性弹窗 ==========
  const showHomeVisibility = () => {
    ElMessage.info('进入可见性设置')
  }

  // ========== 加载个人资料 ==========
  const loadProfile = async () => {
    const profile = await userStore.fetchProfile()
    if (!profile) {
      ElMessage.warning('获取个人资料失败')
      return
    }
    basicForm.value.nickname = profile.nickname || ''
    basicForm.value.signature = profile.signature || ''
    basicForm.value.gender = profile.gender || 'secret'
    basicForm.value.bio = profile.bio || ''
    if (profile.birthday) {
      const parts = profile.birthday.split('-')
      basicForm.value.birthday = { year: parts[0] || '', month: parts[1] || '', day: parts[2] || '' }
    }
  }

  // ========== 保存基本资料 ==========
  const saveBasic = async () => {
    const birthday = basicForm.value.birthday
    const birthdayStr = birthday.year && birthday.month && birthday.day
      ? `${birthday.year}-${birthday.month.padStart(2, '0')}-${birthday.day.padStart(2, '0')}`
      : null

    await userStore.updateProfile({
      nickname: basicForm.value.nickname,
      signature: basicForm.value.signature,
      gender: basicForm.value.gender,
      birthday: birthdayStr,
      bio: basicForm.value.bio
    })
    ElMessage.success('基本资料已保存')
  }

  // ========== 保存隐私 / 推送设置 ==========
  const saveSettings = async (type) => {
    const settingsMap = {
      privacy: { privacy_settings: JSON.stringify({
        privacy_cabinet: toggles.value.privacy_cabinet,
        privacy_profit: toggles.value.privacy_profit,
        privacy_follow: toggles.value.privacy_follow
      })},
      push: { push_settings: JSON.stringify({
        push_balance_remind: toggles.value.push_balance_remind,
        push_price_alert: toggles.value.push_price_alert,
        push_system_notice: toggles.value.push_system_notice,
        push_weekly_report: toggles.value.push_weekly_report
      })}
    }
    await userStore.updateSettings(settingsMap[type])
    ElMessage.success('设置已保存')
  }

  // ========== 加载隐私设置 ==========
  const loadPrivacySettings = async () => {
    try {
      const response = await axios.get('/collector/privacy')
      if (response) {
        privacySettings.value = {
          home_visibility: response.home_visibility || 'public',
          show_total: response.show_total || false,
          show_figures: response.show_figures || false,
          show_asset: response.show_asset || false,
          show_tags: response.show_tags || false,
          show_feed: response.show_feed || false
        }
      }
    } catch (error) {
      console.error('加载隐私设置失败:', error)
    }
  }

  // ========== 头像：触发文件选择 / 预览 ==========
  const triggerAvatarInput = (inputRef) => {
    if (inputRef && inputRef.value) {
      inputRef.value.click()
    }
  }
  const previewAvatar = (e) => {
    const file = e.target?.files?.[0]
    if (file) {
      selectedAvatarFile.value = file
      const reader = new FileReader()
      reader.onload = (ev) => { avatarSrc.value = ev.target.result }
      reader.readAsDataURL(file)
    }
  }

  // ========== 头像：保存 ==========
  const saveAvatar = async () => {
    if (!selectedAvatarFile.value) {
      ElMessage.warning('请先选择要上传的头像')
      return
    }
    const formData = new FormData()
    formData.append('file', selectedAvatarFile.value)
    try {
      const uploadResponse = await axios.post('/upload', formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      })
      if (uploadResponse.url) {
        await userStore.updateAvatar(uploadResponse.url)
        ElMessage.success('头像已更新')
      } else {
        ElMessage.error('头像上传失败')
      }
    } catch (error) {
      console.error('头像上传失败:', error)
      ElMessage.error('头像上传失败，请稍后重试')
    }
  }

  // ========== 加载 MinIO 配置 ==========
  const loadMinIOConfig = async () => {
    try {
      const response = await axios.get('/minio/config')
      if (response) {
        minioConfig.value = {
          endpoint: response.endpoint || '',
          access_key: response.access_key || '',
          secret_key: response.secret_key || '',
          bucket: response.bucket || '',
          public_url: response.public_url || '',
          secure: response.secure || false
        }
      }
    } catch (error) {
      console.error('加载 MinIO 配置失败:', error)
    }
  }

  // ========== MinIO 连接测试 ==========
  const testMinIOConnection = async () => {
    testingConnection.value = true
    minioStatusText.value = '正在测试连接...'
    minioStatusDetail.value = ''
    minioStatusClass.value = 'warning'
    minioStatusIconColor.value = '#faad14'

    try {
      const response = await axios.post('/minio/test', {
        endpoint: minioConfig.value.endpoint,
        access_key: minioConfig.value.access_key,
        secret_key: minioConfig.value.secret_key,
        bucket: minioConfig.value.bucket,
        secure: minioConfig.value.secure
      })
      if (response.success) {
        minioStatusText.value = response.message
        minioStatusDetail.value = `延迟 ${response.latency}ms`
        minioStatusClass.value = ''
        minioStatusIconColor.value = '#52c41a'
        ElMessage.success('MinIO 连接测试成功')
      } else {
        minioStatusText.value = '连接失败'
        minioStatusDetail.value = response.message
        minioStatusClass.value = 'error'
        minioStatusIconColor.value = '#ff4d4f'
        ElMessage.error('MinIO 连接测试失败')
      }
    } catch (error) {
      minioStatusText.value = '连接测试异常'
      minioStatusDetail.value = error.response?.data?.detail || '网络错误'
      minioStatusClass.value = 'error'
      minioStatusIconColor.value = '#ff4d4f'
      ElMessage.error('MinIO 连接测试失败，请稍后重试')
    } finally {
      testingConnection.value = false
    }
  }

  // ========== 保存 MinIO 配置 ==========
  const saveMinIOConfig = async () => {
    try {
      await axios.put('/minio/config', {
        endpoint: minioConfig.value.endpoint,
        access_key: minioConfig.value.access_key,
        secret_key: minioConfig.value.secret_key,
        bucket: minioConfig.value.bucket,
        public_url: minioConfig.value.public_url,
        secure: minioConfig.value.secure
      })
      ElMessage.success('MinIO 配置已保存')
    } catch (error) {
      console.error('保存 MinIO 配置失败:', error)
      ElMessage.error('保存失败，请稍后重试')
    }
  }

  // ========== 重置 MinIO 配置 ==========
  const resetMinIOConfig = async () => {
    resettingMinIO.value = true
    try {
      const response = await axios.post('/minio/reset')
      minioConfig.value = {
        endpoint: response.endpoint || '',
        access_key: response.access_key || '',
        secret_key: response.secret_key || '',
        bucket: response.bucket || '',
        public_url: response.public_url || '',
        secure: response.secure || false
      }
      ElMessage.success('已恢复为默认配置')
    } catch (error) {
      console.error('重置 MinIO 配置失败:', error)
      ElMessage.error('重置失败，请稍后重试')
    } finally {
      resettingMinIO.value = false
    }
  }

  // ========== 超时登出：选择时长 ==========
  const selectTimeout = (minutes) => {
    timeoutConfig.value.timeout_minutes = minutes
  }

  // ========== 加载超时配置 ==========
  const loadTimeoutConfig = async () => {
    try {
      const response = await axios.get('/timeout/config')
      if (response) {
        timeoutConfig.value = {
          timeout_minutes: response.timeout_minutes ?? 30,
          timeout_warning: response.timeout_warning ?? true
        }
      }
    } catch (error) {
      console.error('加载超时登出配置失败:', error)
    }
  }

  // ========== 保存超时配置 ==========
  const saveTimeoutConfig = async () => {
    savingTimeout.value = true
    try {
      await axios.put('/timeout/config', {
        timeout_minutes: timeoutConfig.value.timeout_minutes,
        timeout_warning: timeoutConfig.value.timeout_warning
      })
      ElMessage.success('超时登出设置已保存')
    } catch (error) {
      console.error('保存超时登出配置失败:', error)
      ElMessage.error('保存失败，请稍后重试')
    } finally {
      savingTimeout.value = false
    }
  }

  // ========== 账号注销：二次确认弹窗 ==========
  const showDeleteConfirm = () => {
    ElMessageBox.confirm(
      '注销后所有数据将永久删除且无法恢复，确认要注销吗？',
      '确认注销账号',
      { confirmButtonText: '确认注销', cancelButtonText: '取消', type: 'warning' }
    ).then(() => {
      ElMessage.info('请联系管理员完成注销流程')
    }).catch(() => {})
  }

  // ========== 退出登录 ==========
  const logout = () => {
    userStore.logout()
    window.location.href = '/login'
  }

  onMounted(() => {
    if (!userStore.currentUser) {
      userStore.fetchUser()
    }
    loadProfile()
    loadPrivacySettings()
    avatarSrc.value = userStore.currentUser?.avatar_url || userStore.profile?.avatar_url || '/imgs/none.jpg'
    loadMinIOConfig()
    loadTimeoutConfig()
  })

  return {
    // state
    activePanel,
    basicForm,
    nicknameLen,
    signatureLen,
    bioLen,
    years,
    privacySettings,
    homeVisibilityText,
    toggles,
    avatarSrc,
    selectedAvatarFile,
    minioConfig,
    minioStatusText,
    minioStatusDetail,
    minioStatusClass,
    minioStatusIconColor,
    testingConnection,
    resettingMinIO,
    timeoutConfig,
    savingTimeout,
    // actions
    switchPanel,
    toggleSwitch,
    togglePrivacy,
    showHomeVisibility,
    loadProfile,
    saveBasic,
    saveSettings,
    loadPrivacySettings,
    triggerAvatarInput,
    previewAvatar,
    saveAvatar,
    loadMinIOConfig,
    testMinIOConnection,
    saveMinIOConfig,
    resetMinIOConfig,
    selectTimeout,
    loadTimeoutConfig,
    saveTimeoutConfig,
    showDeleteConfirm,
    logout,
    // store
    userStore
  }
}
