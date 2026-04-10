<template>
  <div class="figures-container">
    <FiguresHeader
      :user-store="userStore"
      @open-add-form="openAddForm"
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
      @delete="deleteFigure"
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
  </div>
</template>

<script>
import FiguresHeader from './Figures/components/FiguresHeader.vue'
import FiguresSearch from './Figures/components/FiguresSearch.vue'
import FiguresList from './Figures/components/FiguresList.vue'
import FiguresPagination from './Figures/components/FiguresPagination.vue'
import FigureForm from './Figures/components/FigureForm.vue'
import ImagePreview from './Figures/components/ImagePreview.vue'
import { useFigureManagement } from './Figures/composables/useFigureManagement'

export default {
  name: 'Figures',
  components: {
    FiguresHeader,
    FiguresSearch,
    FiguresList,
    FiguresPagination,
    FigureForm,
    ImagePreview
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
      deleteFigure,
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
      deleteFigure,
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
      handleFileUpload
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
