import { ref, onMounted } from 'vue'
import axios from '../../../axios'
import { ElMessage } from 'element-plus'

export function useCollectorData() {
  const collectorData = ref(null)
  const loading = ref(false)

  // 获取收藏家模式数据
  const fetchCollectorData = async () => {
    loading.value = true
    try {
      const res = await axios.get('/assets/collector/dashboard')
      collectorData.value = res
    } catch (error) {
      // 生成模拟数据
      collectorData.value = {
        summary: {
          total_investment: 50000,
          total_valuation: 80000,
          blood_money: 12000
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

  // 组件挂载时获取数据
  onMounted(() => {
    fetchCollectorData()
  })

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
