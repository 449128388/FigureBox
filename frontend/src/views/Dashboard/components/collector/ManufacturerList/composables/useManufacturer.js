/**
 * useManufacturer.js - 本命厂商业务逻辑组合式函数
 *
 * 功能说明：
 * - 管理本命厂商的列表查询、新增、编辑、删除
 * - 管理厂商详情及手办列表查询
 * - 管理弹窗显隐状态
 */

import { ref, reactive } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  getManufacturers,
  getManufacturerDetail,
  createManufacturer,
  updateManufacturer,
  deleteManufacturer
} from '../manufacturerApi'

export function useManufacturer() {
  // ====== 状态 ======
  const manufacturers = ref([])
  const manufacturerCount = ref(0)
  // 全局统计（独立于 filter_type，仅受 keyword 影响）
  const manufacturerStats = ref({ all: 0, in: 0, out: 0 })
  const loading = ref(false)

  // 当前选中的厂商详情
  const currentManufacturer = ref(null)
  const detailLoading = ref(false)

  // 弹窗状态
  const formDialogVisible = ref(false)
  const isEditing = ref(false)
  const editingId = ref(null)
  const formData = reactive({
    name: '',
    name_jp: '',
    description: '',
    logo_url: '',
    website_url: '',
    twitter_url: ''
  })

  // 当前视图: 'list' | 'detail'
  const currentView = ref('list')

  // ====== 搜索 / 筛选状态 ======
  const searchKeyword = ref('')
  const filterType = ref('') // '' | 'in' | 'out'

  // ====== 方法 ======

  /**
   * 获取本命厂商列表（支持搜索 + 筛选）
   * @param {Object} [params] - 搜索/筛选参数
   */
  const fetchManufacturers = async (params = {}) => {
    loading.value = true
    try {
      // 外部传入参数优先，否则使用本地状态
      const keyword = params.keyword !== undefined ? params.keyword : searchKeyword.value
      const filter_type = params.filter_type !== undefined ? params.filter_type : filterType.value

      const response = await getManufacturers({ keyword, filter_type })
      manufacturers.value = response.manufacturers || []
      manufacturerCount.value = response.total || 0
      // 兼容后端未返回 stats 的情况（保底置零）
      manufacturerStats.value = response.stats || { all: 0, in: 0, out: 0 }
    } catch (error) {
      manufacturers.value = []
      manufacturerCount.value = 0
      manufacturerStats.value = { all: 0, in: 0, out: 0 }
    } finally {
      loading.value = false
    }
  }

  /**
   * 触发搜索
   * @param {string} keyword - 搜索关键词
   */
  const handleSearch = async (keyword) => {
    searchKeyword.value = keyword || ''
    await fetchManufacturers()
  }

  /**
   * 切换筛选类型
   * @param {string} type - 筛选类型（'' 全部 / 'in' 有在柜 / 'out' 无在柜）
   */
  const handleFilterChange = async (type) => {
    filterType.value = type || ''
    await fetchManufacturers()
  }

  /**
   * 重置搜索 / 筛选
   */
  const handleResetSearch = async () => {
    searchKeyword.value = ''
    filterType.value = ''
    await fetchManufacturers()
  }

  /**
   * 获取厂商详情
   * @param {number} id - 厂商ID
   */
  const fetchManufacturerDetail = async (id) => {
    detailLoading.value = true
    try {
      const response = await getManufacturerDetail(id)
      currentManufacturer.value = response
      currentView.value = 'detail'
    } catch (error) {
      ElMessage.error('获取厂商详情失败')
      currentManufacturer.value = null
    } finally {
      detailLoading.value = false
    }
  }

  /**
   * 打开新增弹窗
   */
  const openAddDialog = () => {
    isEditing.value = false
    editingId.value = null
    formData.name = ''
    formData.name_jp = ''
    formData.description = ''
    formData.logo_url = ''
    formData.website_url = ''
    formData.twitter_url = ''
    formDialogVisible.value = true
  }

  /**
   * 打开编辑弹窗
   * @param {Object} manufacturer - 厂商数据
   */
  const openEditDialog = (manufacturer) => {
    isEditing.value = true
    editingId.value = manufacturer.id
    formData.name = manufacturer.name || ''
    formData.name_jp = manufacturer.name_jp || ''
    formData.description = manufacturer.description || ''
    formData.logo_url = manufacturer.logo_url || ''
    formData.website_url = manufacturer.website_url || ''
    formData.twitter_url = manufacturer.twitter_url || ''
    formDialogVisible.value = true
  }

  /**
   * 保存厂商（新增或更新）
   * 编辑保存后：若当前在详情页，刷新该详情以实时反映修改
   */
  const saveManufacturer = async () => {
    if (!formData.name || !formData.name.trim()) {
      ElMessage.warning('请填写厂商名称')
      return false
    }

    try {
      if (isEditing.value && editingId.value) {
        await updateManufacturer(editingId.value, formData)
        ElMessage.success('厂商信息已更新')
      } else {
        await createManufacturer(formData)
        ElMessage.success('本命厂商已添加')
      }
      formDialogVisible.value = false
      await fetchManufacturers()
      // 当前在详情页且编辑的就是当前厂商 → 重新拉取详情以实时反映修改
      if (
        currentView.value === 'detail' &&
        currentManufacturer.value &&
        editingId.value === currentManufacturer.value.id
      ) {
        await fetchManufacturerDetail(editingId.value)
      }
      return true
    } catch (error) {
      ElMessage.error('保存失败')
      return false
    }
  }

  /**
   * 删除厂商
   * @param {number} id - 厂商ID
   */
  const removeManufacturer = async (id) => {
    try {
      await ElMessageBox.confirm(
        '确定要删除该本命厂商吗？该厂商下的手办记录不会被删除。',
        '确认删除',
        { confirmButtonText: '确定', cancelButtonText: '取消', type: 'warning' }
      )
      await deleteManufacturer(id)
      ElMessage.success('已删除')
      await fetchManufacturers()
    } catch (error) {
      // 取消删除不处理
    }
  }

  /**
   * 返回列表页
   */
  const backToList = () => {
    currentView.value = 'list'
    currentManufacturer.value = null
  }

  return {
    // 状态
    manufacturers,
    manufacturerCount,
    manufacturerStats,
    loading,
    currentManufacturer,
    detailLoading,
    formDialogVisible,
    isEditing,
    formData,
    currentView,
    searchKeyword,
    filterType,

    // 方法
    fetchManufacturers,
    fetchManufacturerDetail,
    openAddDialog,
    openEditDialog,
    saveManufacturer,
    removeManufacturer,
    backToList,
    handleSearch,
    handleFilterChange,
    handleResetSearch
  }
}
