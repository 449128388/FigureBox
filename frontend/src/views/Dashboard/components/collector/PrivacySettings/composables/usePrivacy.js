import { ref, reactive } from 'vue'
import { ElMessage } from 'element-plus'
import { fetchPrivacySettings, updatePrivacySettings } from '../api/privacyApi.js'

const PRIVACY_SELECTORS = {
  home_visibility: {
    title: '个人主页可见性',
    options: [
      { value: 'public', label: '公开', desc: '任何人都可以查看你的收藏主页' },
      { value: 'friends_only', label: '仅好友', desc: '仅互相关注的用户可以查看', disabled: true, disabledTip: '即将支持' },
      { value: 'private', label: '私密', desc: '仅自己可见' }
    ]
  },
  poster_level: {
    title: '海报展示数据',
    options: [
      { value: 'full', label: '完整数据', desc: '展示统计、藏品名、金额等全部信息' },
      { value: 'stats_only', label: '仅统计', desc: '只展示藏品数量等统计数据，不展示具体名称' },
      { value: 'names_only', label: '仅藏品名', desc: '只展示藏品名称，不展示金额等敏感数据' }
    ]
  }
}

export function usePrivacy() {
  const loading = ref(false)
  const saving = ref(false)

  // 默认值
  const settings = reactive({
    home_visibility: 'public',
    show_total: true,
    show_figures: false,
    show_asset: false,
    show_tags: true,
    show_feed: false,
    poster_level: 'stats_only',
    share_domain: ''
  })

  /** 加载隐私设置 */
  async function loadSettings() {
    loading.value = true
    try {
      const res = await fetchPrivacySettings()
      Object.assign(settings, res)
    } catch (e) {
      ElMessage.error('加载隐私设置失败')
    } finally {
      loading.value = false
    }
  }

  /** 保存隐私设置 */
  async function saveSettings() {
    saving.value = true
    try {
      await updatePrivacySettings({ ...settings })
      ElMessage.success('隐私设置已保存')
      return true
    } catch (e) {
      ElMessage.error('保存失败: ' + (e.response?.data?.detail || e.message))
      return false
    } finally {
      saving.value = false
    }
  }

  /** 更新单个字段 */
  function updateField(key, value) {
    settings[key] = value
  }

  /** 获取选择器配置 */
  function getSelector(key) {
    return PRIVACY_SELECTORS[key]
  }

  /** 获取选项显示文本 */
  function getOptionLabel(key) {
    const config = PRIVACY_SELECTORS[key]
    if (!config) return ''
    const opt = config.options.find(o => o.value === settings[key])
    return opt ? opt.label : ''
  }

  return {
    loading,
    saving,
    settings,
    loadSettings,
    saveSettings,
    updateField,
    getSelector,
    getOptionLabel
  }
}
