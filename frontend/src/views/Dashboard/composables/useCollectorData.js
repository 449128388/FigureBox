import { ref } from 'vue'
import axios from '../../../axios'
import { ElMessage } from 'element-plus'

export function useCollectorData() {
  const collectorData = ref(null)
  const loading = ref(false)

  // 获取收藏家模式数据（拆分后的4个独立接口）
  const fetchCollectorData = async () => {
    loading.value = true
    try {
      // 并行请求4个独立接口
      const [summaryRes, cabinetsRes, tagsRes, timelineRes] = await Promise.all([
        axios.get('/collector/summary'),
        axios.get('/collector/cabinets'),
        axios.get('/collector/tags'),
        axios.get('/collector/timeline')
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
        activities: timelineRes.activities || []
      }
    } catch (error) {
      // 生成模拟数据
      collectorData.value = {
        summary: {
          total_collection: 86,
          unique_works: 12,
          unique_manufacturers: 8,
          this_month_count: 3,
          recent_figures: '初音韶华 / 蕾姆婚纱 / 桐宫美月',
          total_sold_count: 8,
          total_companion_days: 1024
        },
        valuable_items: [
          {
            id: 1,
            name: "初音韶华",
            image: "https://trae-api-cn.mchost.guru/api/ide/v1/text_to_image?prompt=anime%20figure%20Hatsune%20Miku%20with%20colorful%20hair%20and%20modern%20outfit&image_size=square",
            profit: 1200,
            status: "海景房"
          },
          {
            id: 2,
            name: "蕾姆婚纱",
            image: "https://trae-api-cn.mchost.guru/api/ide/v1/text_to_image?prompt=anime%20figure%20Rem%20in%20wedding%20dress%20blue%20hair&image_size=square",
            profit: 800,
            status: "小赚"
          },
          {
            id: 3,
            name: "Saber",
            image: "https://trae-api-cn.mchost.guru/api/ide/v1/text_to_image?prompt=anime%20figure%20Saber%20from%20Fate%20series%20in%20blue%20dress&image_size=square",
            profit: -200,
            status: "破发"
          },
          {
            id: 4,
            name: "艾米莉亚",
            image: "https://trae-api-cn.mchost.guru/api/ide/v1/text_to_image?prompt=anime%20figure%20Emilia%20with%20silver%20hair%20and%20blue%20dress&image_size=square",
            status: "已转卖",
            sold_profit: 500
          }
        ],
        tags: [
          {"name": "海景房", "count": 3},
          {"name": "破发区", "count": 5},
          {"name": "待补款", "count": 2},
          {"name": "已出坑", "count": 8}
        ],
        activities: [
          {
            "date": "2026-03-15",
            "content": "入手初音韶华 180天，估值上涨150%",
            "actions": ["生成分享卡片", "查看详情"]
          },
          {
            "date": "2026-02-20",
            "content": "蕾姆婚纱补款完成，等待发货",
            "actions": ["查看详情"]
          }
        ]
      }
    } finally {
      loading.value = false
    }
  }

  // 分享海报
  const sharePoster = () => {
    ElMessage.info('分享海报功能开发中')
  }

  // 隐私设置
  const privacySettings = () => {
    ElMessage.info('隐私设置功能开发中')
  }

  // 按标签筛选
  const filterByTag = (tagName) => {
    ElMessage.info(`按标签 ${tagName} 筛选`)
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
    sharePoster,
    privacySettings,
    filterByTag,
    handleActivityAction
  }
}
