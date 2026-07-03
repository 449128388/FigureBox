import { ref, computed, onMounted } from 'vue'
import { useUserStore } from '../../../store'
import { ElMessage } from 'element-plus'
import axios from '../../../axios'

export function useProfile() {
  const userStore = useUserStore()

  // 当前激活的面板
  const activePanel = ref('panel-basic')

  // 表单数据
  const basicForm = ref({
    nickname: '',
    signature: '',
    gender: 'secret',
    birthday: { year: '', month: '', day: '' },
    bio: ''
  })

  // 开关设置
  const toggles = ref({
    privacy_cabinet: true,
    privacy_profit: false,
    privacy_follow: true,
    push_balance_remind: true,
    push_price_alert: true,
    push_system_notice: true,
    push_weekly_report: false
  })

  // 隐私设置（从 collector_privacy 表读取）
  const privacySettings = ref({
    home_visibility: 'public',
    show_total: true,
    show_figures: false,
    show_asset: false,
    show_tags: true,
    show_feed: false
  })

  // 个人主页可见性中文文本
  const homeVisibilityText = computed(() => {
    const map = {
      public: '公开',
      friends_only: '仅好友可见',
      private: '仅自己可见'
    }
    return map[privacySettings.value.home_visibility] || '公开'
  })

  // 字符计数
  const nicknameLen = computed(() => basicForm.value.nickname.length)
  const signatureLen = computed(() => basicForm.value.signature.length)
  const bioLen = computed(() => basicForm.value.bio.length)

  // 切换面板
  const switchPanel = (panelId) => {
    activePanel.value = panelId
  }

  // 切换开关
  const toggleSwitch = (key) => {
    toggles.value[key] = !toggles.value[key]
  }

  // 切换隐私设置开关
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

  // 加载隐私设置
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

  // 显示主页可见性设置弹窗
  const showHomeVisibility = () => {
    ElMessage.info('进入可见性设置')
  }

  // 加载个人资料
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

  // 保存基本资料
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

  // 保存设置
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

  // 退出登录
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
  })

  return {
    activePanel,
    basicForm,
    toggles,
    privacySettings,
    homeVisibilityText,
    nicknameLen,
    signatureLen,
    bioLen,
    switchPanel,
    toggleSwitch,
    togglePrivacy,
    showHomeVisibility,
    saveBasic,
    saveSettings,
    logout,
    userStore
  }
}
