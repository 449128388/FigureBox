<!--
  Figures.vue - 手办管理主页面

  功能说明：
  - 手办CRUD完整功能：添加、编辑、删除手办
  - 数据导入导出：支持JSON格式批量导入和下载
  - 多维度搜索：按名称、购买类型、购买日期范围、标签筛选
  - 分页展示：支持自定义每页显示数量
  - 图片管理：支持多图上传、预览、删除
  - 标签管理：支持多标签关联和筛选

  组件依赖：
  - FiguresHeader.vue - 页面头部（添加、导入、下载、刷新按钮）
  - FiguresSearch.vue - 搜索筛选区域
  - FiguresList.vue - 手办卡片列表
  - FiguresPagination.vue - 分页组件
  - FigureForm.vue - 手办表单（添加/编辑）
  - ImagePreview.vue - 图片预览弹窗
  - ImportFiguresDialog.vue - 数据导入对话框
  - FigureDeleteConfirmDialog.vue - 删除确认对话框

  维护提示：
  - 使用 useFigureManagement composable 管理业务逻辑
  - 使用 useImportFigures composable 管理导入功能
  - 表单验证在提交时统一处理
  - 搜索条件变化自动触发重新查询
-->
<template>
  <div class="figures-container">
    <FiguresHeader
      :user-store="userStore"
      @open-add-form="openAddForm"
      @import-figures="openImportDialog"
      @download-figures="handleDownload"
      @refresh-figures="fetchFigures"
      @logout="logout($router)"
    />
    
    <FiguresSearch
      v-model:search-name="searchName"
      v-model:search-purchase-type="searchPurchaseType"
      v-model:search-purchase-date-range="searchPurchaseDateRange"
      :search-tag-ids="searchTagIds"
      :tag-store="tagStore"
      @search="handleSearch"
      @reset="resetSearch"
      @filter-by-tag="filterByTag"
    />
    
    <FiguresList
      :figures="paginatedFigures"
      :search-tag-ids="searchTagIds"
      @edit="editFigure"
      @delete="openDeleteConfirmDialog"
      @filter-by-tag="filterByTag"
    />
    
    <FiguresPagination
      v-model:current-page="currentPage"
      v-model:page-size="pageSize"
      :page-sizes="pageSizes"
      :total="totalFigures"
      @size-change="handleSizeChange"
      @current-change="handleCurrentChange"
    />
    
    <FigureForm
      v-model:show="showAddForm"
      :is-editing="isEditing"
      v-model:figure="newFigure"
      v-model:active-tab="activeTab"
      :tag-store="tagStore"
      :name-error="nameError"
      :japanese-name-error="japaneseNameError"
      :purchase-method-error="purchaseMethodError"
      :painting-error="paintingError"
      :original-art-error="originalArtError"
      :work-error="workError"
      :manufacturer-error="manufacturerError"
      :scale-error="scaleError"
      :material-error="materialError"
      :size-error="sizeError"
      @close="showAddForm = false"
      @submit="addFigure"
      @validate-name-input="validateNameOnInput"
      @validate-japanese-name-input="validateJapaneseNameOnInput"
      @validate-purchase-method-input="validatePurchaseMethodOnInput"
      @validate-painting-input="validatePaintingOnInput"
      @validate-original-art-input="validateOriginalArtOnInput"
      @validate-work-input="validateWorkOnInput"
      @validate-manufacturer-input="validateManufacturerOnInput"
      @validate-scale-input="validateScaleOnInput"
      @validate-material-input="validateMaterialOnInput"
      @validate-size-input="validateSizeOnInput"
      @view-image="viewImage"
      @remove-image="removeImage"
      @file-upload="handleFileUpload"
      @tag-change="handleTagChange"
    />
    
    <ImagePreview
      :show="showImagePreview"
      :image="previewImage"
      @close="closeImagePreview"
    />

    <ImportFiguresDialog
      :show="showImportDialog"
      @close="closeImportDialog"
      @import="handleImport"
    />

    <FigureDeleteConfirmDialog
      v-model:show="showDeleteConfirmDialog"
      :figure="figureToDelete"
      :order-count="figureToDeleteOrderCount"
      @confirm="confirmDelete"
      @cancel="cancelDelete"
    />
  </div>
</template>

<script>
import FiguresHeader from './Figures/components/FiguresHeader.vue'
import FiguresSearch from './Figures/components/FiguresSearch.vue'
import FiguresList from './Figures/components/FiguresList.vue'
import FiguresPagination from './Figures/components/FiguresPagination.vue'
import FigureForm from './Figures/components/FigureForm.vue'
import ImagePreview from './Figures/components/ImagePreview.vue'
import ImportFiguresDialog from './Figures/components/ImportFiguresDialog.vue'
import FigureDeleteConfirmDialog from './Figures/components/FigureDeleteConfirmDialog.vue'
import { useFigureManagement } from './Figures/composables/useFigureManagement'
import { useImportFigures } from './Figures/composables/useImportFigures'

export default {
  name: 'Figures',
  components: {
    FiguresHeader,
    FiguresSearch,
    FiguresList,
    FiguresPagination,
    FigureForm,
    ImagePreview,
    ImportFiguresDialog,
    FigureDeleteConfirmDialog
  },
  setup() {
    const {
      figureStore,
      userStore,
      tagStore,
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
      totalFigures,
      paginatedFigures,
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
    } = useFigureManagement()

    const logout = (router) => {
      userStore.logout()
      router.push('/login')
    }

    const handleDownload = async () => {
      const result = await downloadFigures()
      if (result.success) {
        // 显示成功消息
      } else {
        // 显示错误消息
      }
    }

    // 导入功能
    const {
      showImportDialog,
      openImportDialog,
      closeImportDialog,
      importFigures
    } = useImportFigures()

    const handleImport = async (data, callback) => {
      const result = await importFigures(data)
      if (result.success) {
        // 刷新手办列表
        await fetchFigures()
      }
      // 如果有回调函数，调用它返回结果
      if (callback && typeof callback === 'function') {
        callback(result)
      }
      return result
    }

    return {
      figureStore,
      userStore,
      tagStore,
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
      totalFigures,
      paginatedFigures,
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
      logout,
      handleDownload,
      viewImage,
      closeImagePreview,
      removeImage,
      handleFileUpload,
      showImportDialog,
      openImportDialog,
      closeImportDialog,
      handleImport
    }
  },
  mounted() {
    this.fetchFigures()
    this.tagStore.fetchTags()
    // 如果已登录但用户信息为空，则获取用户信息
    if (this.userStore.isAuthenticated && !this.userStore.currentUser) {
      this.userStore.fetchUser()
    }
  }
}
</script>

<style scoped>
.figures-container {
  margin-top: 20px;
  width: 100%;
  max-width: 1650px;
  margin-left: 50px;
  margin-right: 50px;
  padding: 20px;
  background-color: #f9f9f9;
  border-radius: 8px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
}

@media (max-width: 768px) {
  .figures-container {
    margin-left: 20px;
    margin-right: 20px;
  }
}
</style>
