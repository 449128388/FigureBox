import { ref, computed } from 'vue'
import { useFigureStore, useUserStore, useTagStore } from '../../../store'
import axios from '../../../axios'
import { ElMessage } from 'element-plus'

export function useFigureManagement() {
  const figureStore = useFigureStore()
  const userStore = useUserStore()
  const tagStore = useTagStore()

  // 表单显示状态
  const showAddForm = ref(false)
  const isEditing = ref(false)
  const currentEditFigureId = ref(null)
  const activeTab = ref('basic')

  // 图片预览
  const showImagePreview = ref(false)
  const previewImage = ref('')

  // 删除确认对话框
  const showDeleteConfirmDialog = ref(false)
  const figureToDelete = ref(null)
  const figureToDeleteOrderCount = ref(0)

  // 分页
  const currentPage = ref(1)
  const pageSize = ref(15)
  const pageSizes = [15, 30, 45, 60]

  // 搜索
  const searchName = ref('')
  const searchPurchaseDateRange = ref([])
  const searchPurchaseType = ref('')
  const searchTagIds = ref([])

  // 表单错误
  const nameError = ref('')
  const japaneseNameError = ref('')
  const purchaseMethodError = ref('')
  const paintingError = ref('')
  const originalArtError = ref('')
  const workError = ref('')
  const manufacturerError = ref('')
  const scaleError = ref('')
  const materialError = ref('')
  const sizeError = ref('')

  // 默认表单数据
  const defaultFigure = {
    name: '',
    japanese_name: '',
    manufacturer: '',
    price: 0,
    currency: 'CNY',
    market_price: 0,
    market_currency: 'CNY',
    purchase_price: 0,
    purchase_currency: 'CNY',
    release_date: null,
    purchase_date: null,
    purchase_method: '',
    purchase_type: 'OTHER',
    quantity: 1,
    painting: '',
    original_art: '',
    work: '',
    scale: '',
    material: '',
    size: '',
    images: [],
    tag_ids: []
  }

  const newFigure = ref({ ...defaultFigure })

  // 计算属性
  const totalFigures = computed(() => figureStore.totalCount)

  const paginatedFigures = computed(() => {
    return figureStore.figures
  })

  // 方法
  const resetForm = () => {
    newFigure.value = { ...defaultFigure }
    isEditing.value = false
    currentEditFigureId.value = null
    activeTab.value = 'basic'
    resetErrors()
  }

  const resetErrors = () => {
    nameError.value = ''
    japaneseNameError.value = ''
    purchaseMethodError.value = ''
    paintingError.value = ''
    originalArtError.value = ''
    workError.value = ''
    manufacturerError.value = ''
    scaleError.value = ''
    materialError.value = ''
    sizeError.value = ''
  }

  const validateName = () => {
    if (!newFigure.value.name || newFigure.value.name.trim() === '') {
      nameError.value = '请输入名称'
      return false
    }
    nameError.value = ''
    return true
  }

  const validateNameOnInput = () => {
    if (nameError.value) {
      validateName()
    }
  }

  const validateJapaneseNameOnInput = () => {
    // 日文名验证逻辑
  }

  const validatePurchaseMethodOnInput = () => {
    // 入手途径验证逻辑
  }

  const validatePaintingOnInput = () => {
    // 涂装验证逻辑
  }

  const validateOriginalArtOnInput = () => {
    // 原画验证逻辑
  }

  const validateWorkOnInput = () => {
    // 作品验证逻辑
  }

  const validateManufacturerOnInput = () => {
    // 制造商验证逻辑
  }

  const validateScaleOnInput = () => {
    // 比例验证逻辑
  }

  const validateMaterialOnInput = () => {
    // 材质验证逻辑
  }

  const validateSizeOnInput = () => {
    // 尺寸验证逻辑
  }

  const formatDate = (date) => {
    if (!date) return null
    const d = new Date(date)
    const year = d.getFullYear()
    const month = String(d.getMonth() + 1).padStart(2, '0')
    const day = String(d.getDate()).padStart(2, '0')
    return `${year}-${month}-${day}`
  }

  const openAddForm = () => {
    resetForm()
    showAddForm.value = true
  }

  const handleTagChange = (value) => {
    // 标签变更处理
  }

  const addFigure = async () => {
    if (!validateName()) {
      activeTab.value = 'basic'
      return
    }

    try {
      const existingTagIds = []
      const newTagNames = []

      for (const item of newFigure.value.tag_ids) {
        if (typeof item === 'number') {
          existingTagIds.push(item)
        } else if (typeof item === 'string') {
          newTagNames.push(item)
        }
      }

      for (const tagName of newTagNames) {
        try {
          const newTag = await tagStore.createTag({ name: tagName })
          existingTagIds.push(newTag.id)
        } catch (error) {
          const existingTag = tagStore.tags.find(t => t.name === tagName)
          if (existingTag) {
            existingTagIds.push(existingTag.id)
          }
        }
      }

      const figureData = {
        ...newFigure.value,
        release_date: formatDate(newFigure.value.release_date),
        purchase_date: formatDate(newFigure.value.purchase_date),
        currency: newFigure.value.currency || 'CNY',
        market_currency: newFigure.value.market_currency || 'CNY',
        purchase_currency: newFigure.value.purchase_currency || 'CNY',
        tag_ids: existingTagIds
      }

      if (isEditing.value) {
        await figureStore.updateFigure(currentEditFigureId.value, figureData)
      } else {
        await figureStore.createFigure(figureData)
      }

      showAddForm.value = false
      resetForm()
      await fetchFiguresWithSearch()
    } catch (error) {
    }
  }

  // 打开删除确认对话框
  const openDeleteConfirmDialog = async (figure) => {
    figureToDelete.value = figure
    showDeleteConfirmDialog.value = true

    // 获取手办关联的订单数量
    try {
      const response = await axios.get(`/figures/${figure.id}/orders/count`)
      figureToDeleteOrderCount.value = response.count || 0
    } catch (error) {
      figureToDeleteOrderCount.value = 0
    }
  }

  // 取消删除
  const cancelDelete = () => {
    showDeleteConfirmDialog.value = false
    figureToDelete.value = null
    figureToDeleteOrderCount.value = 0
  }

  // 确认删除
  const confirmDelete = async () => {
    if (!figureToDelete.value) return

    try {
      await figureStore.deleteFigure(figureToDelete.value.id)
      showDeleteConfirmDialog.value = false
      figureToDelete.value = null
      figureToDeleteOrderCount.value = 0
      ElMessage.success('手办删除成功')
    } catch (error) {
      if (error.response && error.response.status === 400) {
        ElMessage.error('无法删除有关联尾款的手办')
      } else {
        ElMessage.error('删除失败，请稍后重试')
      }
    }
  }

  const editFigure = async (figure) => {
    showAddForm.value = true
    isEditing.value = true
    currentEditFigureId.value = figure.id

    try {
      const response = await axios.get(`/figures/${figure.id}`)
      const fullFigure = response

      newFigure.value = {
        ...fullFigure,
        tag_ids: fullFigure.tags ? fullFigure.tags.map(tag => tag.id) : [],
        price: fullFigure.price || 0,
        currency: fullFigure.currency || 'CNY',
        market_price: fullFigure.market_price || 0,
        market_currency: fullFigure.market_currency || 'CNY',
        purchase_price: fullFigure.purchase_price || 0,
        purchase_currency: fullFigure.purchase_currency || 'CNY',
        images: fullFigure.images || [],
        quantity: fullFigure.quantity || 1
      }
    } catch (error) {
      newFigure.value = {
        ...figure,
        tag_ids: figure.tags ? figure.tags.map(tag => tag.id) : [],
        price: figure.price || 0,
        currency: figure.currency || 'CNY',
        market_price: figure.market_price || 0,
        market_currency: figure.market_currency || 'CNY',
        purchase_price: figure.purchase_price || 0,
        purchase_currency: figure.purchase_currency || 'CNY',
        images: figure.image ? [figure.image] : []
      }
    }

    resetErrors()
  }

  const getCurrencySymbol = (currency) => {
    switch(currency) {
      case 'CNY': return '元'
      case 'JPY': return '日元'
      case 'USD': return '美元'
      case 'EUR': return '欧元'
      default: return '元'
    }
  }

  const handleSizeChange = async (val) => {
    pageSize.value = val
    currentPage.value = 1
    await fetchFiguresWithSearch()
  }

  const handleCurrentChange = async (val) => {
    currentPage.value = val
    await fetchFiguresWithSearch()
  }

  const fetchFigures = async () => {
    await fetchFiguresWithSearch()
  }

  const handleSearch = async () => {
    currentPage.value = 1
    await fetchFiguresWithSearch()
  }

  const resetSearch = async () => {
    searchName.value = ''
    searchPurchaseDateRange.value = []
    searchPurchaseType.value = ''
    searchTagIds.value = []
    currentPage.value = 1
    await fetchFiguresWithSearch()
  }

  const filterByTag = async (tagId) => {
    if (searchTagIds.value.includes(tagId)) {
      searchTagIds.value = searchTagIds.value.filter(id => id !== tagId)
    } else {
      searchTagIds.value.push(tagId)
    }
    currentPage.value = 1
    await fetchFiguresWithSearch()
  }

  const getTagNameById = (tagId) => {
    const tag = tagStore.tags.find(t => t.id === tagId)
    return tag ? tag.name : ''
  }

  const getSortedTags = (tags) => {
    if (!tags || !Array.isArray(tags)) return []
    return [...tags].sort((a, b) => a.id - b.id)
  }

  const fetchFiguresWithSearch = async () => {
    const params = {
      skip: (currentPage.value - 1) * pageSize.value,
      limit: pageSize.value
    }

    if (searchName.value) {
      params.name = searchName.value
    }
    if (searchPurchaseType.value) {
      params.purchase_type = searchPurchaseType.value
    }
    if (searchPurchaseDateRange.value && searchPurchaseDateRange.value.length === 2) {
      params.purchase_date_start = formatDate(searchPurchaseDateRange.value[0])
      params.purchase_date_end = formatDate(searchPurchaseDateRange.value[1])
    }
    if (searchTagIds.value && searchTagIds.value.length > 0) {
      params.tag_ids = searchTagIds.value
    }

    await figureStore.fetchFigures(params)
  }

  const downloadFigures = async () => {
    try {
      const token = localStorage.getItem('token')
      const response = await fetch('/api/figures/download', {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      })

      if (!response.ok) {
        throw new Error('下载失败')
      }

      const jsonText = await response.text()
      const blob = new Blob([jsonText], { type: 'application/json' })
      const url = URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = `figures_${new Date().toISOString().split('T')[0]}.json`
      document.body.appendChild(a)
      a.click()
      document.body.removeChild(a)
      URL.revokeObjectURL(url)

      return { success: true }
    } catch (error) {
      return { success: false, error }
    }
  }

  const viewImage = (image) => {
    previewImage.value = image
    showImagePreview.value = true
  }

  const closeImagePreview = () => {
    showImagePreview.value = false
    previewImage.value = ''
  }

  const removeImage = (index) => {
    newFigure.value.images.splice(index, 1)
  }

  const handleFileUpload = (event) => {
    const files = event.target.files
    if (!files) return

    for (const file of files) {
      if (newFigure.value.images.length >= 10) break

      const reader = new FileReader()
      reader.onload = (e) => {
        newFigure.value.images.push(e.target.result)
      }
      reader.readAsDataURL(file)
    }
  }

  return {
    // stores
    figureStore,
    userStore,
    tagStore,
    // refs
    showAddForm,
    isEditing,
    currentEditFigureId,
    activeTab,
    showImagePreview,
    previewImage,
    showDeleteConfirmDialog,
    figureToDelete,
    figureToDeleteOrderCount,
    currentPage,
    pageSize,
    pageSizes,
    searchName,
    searchPurchaseDateRange,
    searchPurchaseType,
    searchTagIds,
    nameError,
    japaneseNameError,
    purchaseMethodError,
    paintingError,
    originalArtError,
    workError,
    manufacturerError,
    scaleError,
    materialError,
    sizeError,
    newFigure,
    // computed
    totalFigures,
    paginatedFigures,
    // methods
    resetForm,
    resetErrors,
    validateName,
    validateNameOnInput,
    validateJapaneseNameOnInput,
    validatePurchaseMethodOnInput,
    validatePaintingOnInput,
    validateOriginalArtOnInput,
    validateWorkOnInput,
    validateManufacturerOnInput,
    validateScaleOnInput,
    validateMaterialOnInput,
    validateSizeOnInput,
    formatDate,
    openAddForm,
    handleTagChange,
    addFigure,
    openDeleteConfirmDialog,
    cancelDelete,
    confirmDelete,
    editFigure,
    getCurrencySymbol,
    handleSizeChange,
    handleCurrentChange,
    fetchFigures,
    handleSearch,
    resetSearch,
    filterByTag,
    getTagNameById,
    getSortedTags,
    fetchFiguresWithSearch,
    downloadFigures,
    viewImage,
    closeImagePreview,
    removeImage,
    handleFileUpload
  }
}
