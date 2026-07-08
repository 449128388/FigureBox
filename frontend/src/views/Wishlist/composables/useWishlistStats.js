/**
 * useWishlistStats.js - 愿望清单统计 composable
 */
import { ref, onMounted } from 'vue'
import { wishlistApi } from '../api/wishlistApi'

const defaultStats = () => ({
  total: 0,
  releasing_this_month: 0,
  budget_total: 0,
  pending_purchase: 0,
  status_distribution: {},
  top_manufacturers: []
})

export function useWishlistStats() {
  const stats = ref(defaultStats())
  const loading = ref(false)

  const load = async () => {
    loading.value = true
    try {
      const data = await wishlistApi.stats()
      stats.value = data || defaultStats()
    } catch (e) {
      stats.value = defaultStats()
    } finally {
      loading.value = false
    }
  }

  return { stats, loading, load }
}
