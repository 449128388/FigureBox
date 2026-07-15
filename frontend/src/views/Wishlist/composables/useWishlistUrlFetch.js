/**
 * useWishlistUrlFetch.js - URL 抓取 composable
 * 
 * 支持多层抓取引擎：HPOI 使用 Playwright 浏览器引擎，其他站点使用模拟数据。
 * 增加抓取进度和状态反馈。
 */
import { ref } from 'vue'
import { ElMessage } from 'element-plus'
import { wishlistApi } from '../api/wishlistApi'

export function useWishlistUrlFetch() {
  const url = ref('')
  const loading = ref(false)
  const fetching = ref(false)
  const progressText = ref('')
  const result = ref(null)
  const error = ref(null)
  const note = ref('')
  const status = ref('wish')

  const reset = () => {
    url.value = ''
    loading.value = false
    fetching.value = false
    progressText.value = ''
    result.value = null
    error.value = null
    note.value = ''
    status.value = 'wish'
  }

  const fetchFromUrl = async () => {
    if (!url.value.trim()) {
      ElMessage.warning('请输入商品链接')
      return null
    }
    loading.value = true
    fetching.value = true
    progressText.value = '正在解析页面，提取手办信息...'
    result.value = null
    error.value = null
    try {
      const data = await wishlistApi.urlFetch(url.value.trim())
      result.value = data
      if (data._cache_hit) {
        ElMessage.success('使用缓存数据')
      } else if (data._fallback) {
        ElMessage.warning('部分数据未能完整解析，请手动补充')
      }
      return data
    } catch (e) {
      const detail = e?.response?.data?.detail || '抓取失败'
      error.value = detail
      ElMessage.error(detail)
      return null
    } finally {
      loading.value = false
      fetching.value = false
      progressText.value = ''
    }
  }

  const saveFromUrl = async (onCreated) => {
    if (!result.value) {
      ElMessage.warning('请先抓取链接')
      return false
    }
    try {
      // 标准化 release_date：HPOI 可能返回 "2026-12"（仅年月），补成 "2026-12-01"
      let releaseDate = result.value.release_date
      if (releaseDate && /^\d{4}-\d{2}$/.test(releaseDate)) {
        releaseDate = releaseDate + '-01'
      }
      const payload = {
        name: result.value.name,
        japanese_name: result.value.japanese_name,
        manufacturer: result.value.production || result.value.manufacturer,
        scale: result.value.scale,
        painting: result.value.painter,
        original_art: result.value.original_art,
        work: result.value.work,
        material: result.value.material,
        size: result.value.size,
        price: result.value.price,
        currency: result.value.currency,
        release_date: releaseDate,
        source_url: result.value.source_url,
        note: note.value,
        images: result.value.image ? [result.value.image] : [],
        wishlist_status: status.value
      }
      const created = await wishlistApi.create(payload)
      ElMessage.success('已添加到愿望清单')
      onCreated && onCreated(created)
      return true
    } catch (e) {
      ElMessage.error('保存失败')
      return false
    }
  }

  return {
    url, loading, fetching, progressText, result, error, note, status,
    reset, fetchFromUrl, saveFromUrl
  }
}
