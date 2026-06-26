import { ref } from 'vue'
import axios from '../../../axios'
import { ElMessage } from 'element-plus'

export function useCollectorData() {
  const collectorData = ref(null)
  const loading = ref(false)
  const tagFilterResults = ref(null)
  const tagFilterName = ref('')

  // 获取收藏家模式数据（拆分后的4个独立接口）
  const fetchCollectorData = async () => {
    loading.value = true
    try {
      // 并行请求3个独立接口（动态流由 ActivityFeed 组件独立加载）
      const [summaryRes, cabinetsRes, tagsRes] = await Promise.all([
        axios.get('/collector/summary'),
        axios.get('/collector/cabinets'),
        axios.get('/collector/tags')
      ])

      // 合并数据为统一格式
      collectorData.value = {
        summary: summaryRes,
        cabinets: cabinetsRes.cabinets || [
          { key: 'star', name: '海景房专区', description: '镇柜之宝', icon: '🖼️', icon_bg: '#E8F4F8', count: 3, meta: '3 体 · 入柜 180+ 天', items: [{ id: 1, name: '初音韶华', image: '' }, { id: 2, name: '蕾姆婚纱', image: '' }, { id: 3, name: 'Saber', image: '' }] },
          { key: 'new', name: '最近入柜', description: '新欢', icon: '✨', icon_bg: '#F0F5E8', count: 5, meta: '5 体 · 30 天内新成员', items: [] },
          { key: 'fix', name: '修复工坊', description: '待修复', icon: '🔧', icon_bg: '#FDF6EE', count: 2, meta: '2 体 · 补件/补色中', items: [] },
          { key: 'out', name: '已出藏品', description: '已出坑', icon: '📦', icon_bg: '#F5F5F5', count: 8, meta: '8 体 · 找到新主人', items: [] },
          { key: 'air', name: '预定中', description: '空气谷', icon: '☁️', icon_bg: '#F3E8FF', count: 12, meta: '12 体 · 待付尾款/待出荷', items: [] },
          { key: 'dup', name: '复数专区', description: '复数', icon: '👯', icon_bg: '#FFF2F0', count: 6, meta: '6 体 · 同一手办多体', items: [] },
          { key: 'wait', name: '待出荷', description: '待出荷', icon: '📅', icon_bg: '#E6F7FF', count: 4, meta: '4 体 · 已付清等工厂', items: [] },
          { key: 'role', name: '本命厂商', description: '本命', icon: '🏭', icon_bg: '#E8F4F8', count: 0, meta: '暂无本命厂商', items: [] }
        ],
        tags: tagsRes.tags || [],
        system_tags: tagsRes.system_tags || [],
        user_tags: tagsRes.user_tags || []
      }
    } catch (error) {
      console.error('获取收藏家数据失败:', error)
      ElMessage.error('获取收藏家数据失败: ' + (error.response?.data?.detail || error.message))
      collectorData.value = null
    } finally {
      loading.value = false
    }
  }

  // 按标签筛选 - 调用后端接口获取匹配手办列表
  const filterByTag = async (tagName) => {
    try {
      const res = await axios.get('/collector/tags/figures', {
        params: { tag_name: tagName }
      })
      tagFilterName.value = tagName
      tagFilterResults.value = res.figures || []
      ElMessage.success(`找到 ${tagFilterResults.value.length} 个匹配"${tagName}"的手办`)
    } catch (e) {
      ElMessage.error('标签筛选失败: ' + (e.response?.data?.detail || e.message))
    }
  }

  // 清除标签筛选结果
  const clearTagFilter = () => {
    tagFilterResults.value = null
    tagFilterName.value = ''
  }

  // 处理动态流操作
  const handleActivityAction = (action, activity) => {
    ElMessage.info(`执行操作: ${action}`)
  }

  // 【修复】移除 onMounted 自动获取数据
  // 现在由 Dashboard.vue 在切换到收藏家模式时手动调用 fetchCollectorData

  return {
    collectorData,
    loading,
    fetchCollectorData,
    filterByTag,
    clearTagFilter,
    tagFilterResults,
    tagFilterName,
    handleActivityAction
  }
}
