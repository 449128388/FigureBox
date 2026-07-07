/**
 * useSectorRanking - 板块涨幅排行业务逻辑组合式函数
 *
 * 功能说明：
 * - 拉取用户在投资复盘视角下的板块涨幅排行
 * - 支持多维度切换：作品 / 制造商 / 材质 / 原画作者
 * - 支持板块行的二级展开：点击板块行加载该板块下所有手办明细与汇总
 * - 数据按 |板块收益率| 降序排列
 * - 与 SectorRanking.vue 组件配合使用
 *
 * 数据来源：
 * - props.marketData.sectors（HPIDetail 通过 /market/dashboard 一次性带回，默认 work 维度）
 * - 切换维度时回源到 GET /api/market/sector-ranking?dimension=...
 * - 展开板块时回源到 GET /api/market/sector-figures?dimension=...&sector_name=...
 *
 * 使用示例：
 * const {
 *   sectors, loading, hasData,
 *   activeDimension, setDimension, dimensions,
 *   expandedSector, toggleSector, isExpanded, getSectorDetail
 * } = useSectorRanking(props)
 */

import { ref, computed, watch } from 'vue'
import axios from '../../../axios'

// 维度配置（与后端 DIMENSION_CONFIG 保持一致）
const DEFAULT_DIMENSIONS = [
  { code: 'work', name: '按作品' },
  { code: 'manufacturer', name: '按制造商' },
  { code: 'material', name: '按材质' },
  { code: 'original_art', name: '按原画作者' }
]

export function useSectorRanking(props) {
  const sectors = ref([])
  const loading = ref(false)
  const activeDimension = ref('work')
  const dimensions = ref([...DEFAULT_DIMENSIONS])

  // 板块二级展开相关状态
  const expandedSector = ref('')           // 当前展开的板块名
  const sectorDetailCache = ref({})        // sector_name -> detail
  const detailLoading = ref(false)         // 当前展开板块详情是否在加载
  const detailKey = (dim, name) => `${dim}::${name}`

  const hasData = computed(() => sectors.value.length > 0)
  const isExpanded = (sector) => sector && expandedSector.value === sector.name

  /**
   * 从 marketData 提取板块数据（仅当维度一致时采用）
   */
  const syncFromProps = () => {
    const incoming = props?.marketData?.sectors
    const incomingDim = props?.marketData?.sectors?.[0]?.dimension
    if (Array.isArray(incoming) && incoming.length > 0 && incomingDim === activeDimension.value) {
      sectors.value = incoming
    }
  }

  /**
   * 独立拉取板块排行
   */
  const fetchSectors = async (dimension = activeDimension.value, limit = 5) => {
    loading.value = true
    try {
      const res = await axios.get(`/market/sector-ranking?dimension=${dimension}&limit=${limit}`)
      const data = res?.sectors || []
      sectors.value = data
      // 同步后端返回的当前维度
      if (res?.dimension && res.dimension !== activeDimension.value) {
        activeDimension.value = res.dimension
      }
      // 维度切换时清空已展开板块与缓存
      expandedSector.value = ''
      sectorDetailCache.value = {}
    } catch (e) {
      sectors.value = []
    } finally {
      loading.value = false
    }
  }

  /**
   * 切换维度
   */
  const setDimension = async (dimension) => {
    if (!dimension || dimension === activeDimension.value) return
    activeDimension.value = dimension
    await fetchSectors(dimension, 5)
  }

  /**
   * 拉取支持的维度列表
   */
  const fetchDimensions = async () => {
    try {
      const res = await axios.get('/market/sector-dimensions')
      const list = res?.dimensions
      if (Array.isArray(list) && list.length > 0) {
        dimensions.value = list.map(d => ({ code: d.code, name: `按${d.name}` }))
      }
    } catch (e) {
      // 失败时使用默认维度列表
    }
  }

  /**
   * 拉取板块下手办明细（带缓存）
   */
  const fetchSectorDetail = async (sector) => {
    if (!sector || !sector.name) return null
    const key = detailKey(activeDimension.value, sector.name)
    // 命中缓存直接返回
    if (sectorDetailCache.value[key]) {
      return sectorDetailCache.value[key]
    }
    detailLoading.value = true
    try {
      const res = await axios.get(
        `/market/sector-figures?dimension=${activeDimension.value}&sector_name=${encodeURIComponent(sector.name)}`
      )
      const detail = res || null
      if (detail) {
        sectorDetailCache.value = { ...sectorDetailCache.value, [key]: detail }
      }
      return detail
    } catch (e) {
      return null
    } finally {
      detailLoading.value = false
    }
  }

  /**
   * 切换板块的展开/收起（手风琴：同时只展开一个）
   */
  const toggleSector = async (sector) => {
    if (!sector || !sector.name) return
    if (expandedSector.value === sector.name) {
      // 再次点击收起
      expandedSector.value = ''
      return
    }
    expandedSector.value = sector.name
    await fetchSectorDetail(sector)
  }

  /**
   * 获取板块的详情（响应式）
   */
  const getSectorDetail = (sector) => {
    if (!sector || !sector.name) return null
    const key = detailKey(activeDimension.value, sector.name)
    return sectorDetailCache.value[key] || null
  }

  /**
   * 优先使用 props 已有数据，缺失时再请求接口
   */
  const ensureSectors = async (limit = 5) => {
    syncFromProps()
    if (sectors.value.length > 0) return
    await fetchSectors(activeDimension.value, limit)
  }

  // 监听 props.marketData.sectors 变化，自动同步
  watch(
    () => props?.marketData?.sectors,
    () => syncFromProps(),
    { deep: true }
  )

  return {
    sectors,
    loading,
    hasData,
    activeDimension,
    setDimension,
    dimensions,
    fetchDimensions,
    ensureSectors,
    // 二级展开
    expandedSector,
    detailLoading,
    toggleSector,
    isExpanded,
    fetchSectorDetail,
    getSectorDetail
  }
}
