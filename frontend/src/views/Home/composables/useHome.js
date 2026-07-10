import { ref, onMounted } from 'vue'
import axios from '../../../axios'

export function useHome() {
  const loading = ref(true)
  const summary = ref(null)
  const activities = ref([])
  const topHoldings = ref([])

  const loadSummary = async () => {
    try {
      const res = await axios.get('/home/summary')
      summary.value = res
    } catch { 
      summary.value = null 
    }
  }

  const loadActivities = async () => {
    try {
      const res = await axios.get('/home/activities')
      activities.value = res || []
    } catch { 
      activities.value = [] 
    }
  }

  const loadTopHoldings = async () => {
    try {
      const res = await axios.get('/home/top-holdings')
      topHoldings.value = res || []
    } catch { 
      topHoldings.value = [] 
    }
  }

  const loadAll = async () => {
    loading.value = true
    await Promise.all([loadSummary(), loadActivities(), loadTopHoldings()])
    loading.value = false
  }

  onMounted(loadAll)

  return { loading, summary, activities, topHoldings, loadAll }
}
