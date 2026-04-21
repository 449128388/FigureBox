<!--
  Figures.vue - 手办管理主页面

  功能说明：
  - 手办CRUD完整功能：添加、编辑、删除手办
  - 数据导入导出：支持JSON格式批量导入和下载
  - 多维度搜索：按名称、购买类型、购买日期范围、标签筛选
  - 分页展示：支持自定义每页显示数量
  - 图片管理：支持多图上传、预览、删除
  - 标签管理：支持多标签关联和筛选
  - 【新增】批量选择功能：支持多选手办进行批量操作

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
  - 【新增】使用 useBatchSelection composable 管理批量选择功能
  - 表单验证在提交时统一处理
  - 搜索条件变化自动触发重新查询
  - 批量选择模式下，手办卡片显示复选框
  - 有关联订单的手办在批量选择模式下会被禁用
-->
<template>
  <div class="figures-container">
    <FiguresHeader
      :user-store="userStore"
      :is-batch-mode="isBatchMode"
      :selected-count="selectedCount"
      @open-add-form="openAddForm"
      @import-figures="openImportDialog"
      @download-figures="handleDownload"
      @refresh-figures="fetchFigures"
      @logout="logout($router)"
      @toggle-batch-mode="toggleBatchMode"
      @batch-delete="handleBatchDelete"
      @select-all="handleSelectAll"
    />

    <!-- 【新增】批量选择工具栏 -->
    <div v-if="isBatchMode" class="batch-toolbar">
      <div class="batch-info">
        <span class="batch-count">已选择 {{ selectedCount }} 项</span>
        <el-button
          type="primary"
          size="small"
          :disabled="paginatedFigures.length === 0"
          @click="handleSelectAll"
        >
          {{ isAllSelected ? '取消全选' : '全选本页' }}
        </el-button>
      </div>
      <div class="batch-actions">
        <el-button
          type="danger"
          size="small"
          :disabled="!hasSelection"
          @click="handleBatchDelete"
        >
          批量删除
        </el-button>
        <el-button
          size="small"
          @click="exitBatchMode"
        >
          退出选择
        </el-button>
      </div>
    </div>

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
      :is-batch-mode="isBatchMode"
      :selected-ids="selectedIds"
      :disabled-ids="disabledIds"
      @edit="editFigure"
      @delete="openDeleteConfirmDialog"
      @filter-by-tag="filterByTag"
      @toggle-selection="handleToggleSelection"
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
import { useBatchSelection } from './Figures/composables/useBatchSelection'
import { computed } from 'vue'

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
    // 【新增】批量选择功能
    const {
      selectedIds,
      disabledIds,
      isBatchMode,
      selectedCount,
      hasSelection,
      selectedIdsArray,
      toggleSelection,
      setSelection,
      selectAll,
      deselectAll,
      enterBatchMode,
      exitBatchMode,
      clearAll
    } = useBatchSelection()

    // 【新增】检查是否全选本页
    const isAllSelected = computed(() => {
      const selectableFigures = paginatedFigures.value.filter(
        f => !f.has_incomplete_orders && !disabledIds.value.has(f.id)
      )
      if (selectableFigures.length === 0) return false
      return selectableFigures.every(f => selectedIds.value.has(f.id))
    })

    // 【新增】切换批量选择模式
    const toggleBatchMode = () => {
      if (isBatchMode.value) {
        exitBatchMode()
      } else {
        enterBatchMode()
      }
    }

    // 【新增】处理切换选择
    const handleToggleSelection = (figureId, selected) => {
      // 检查手办是否有未完成订单
      const figure = paginatedFigures.value.find(f => f.id === figureId)
      if (figure && figure.has_incomplete_orders) {
        return // 有未完成订单的手办不能选择
      }
      // 使用 setSelection 直接设置选中状态，而不是 toggle
      setSelection(figureId, selected)
    }

    // 【新增】处理全选/取消全选
    const handleSelectAll = () => {
      if (isAllSelected.value) {
        // 取消全选本页
        paginatedFigures.value.forEach(figure => {
          if (selectedIds.value.has(figure.id)) {
            setSelection(figure.id, false)
          }
        })
      } else {
        // 全选本页（排除有未完成订单的）
        paginatedFigures.value.forEach(figure => {
          if (!figure.has_incomplete_orders && !disabledIds.value.has(figure.id)) {
            setSelection(figure.id, true)
          }
        })
      }
    }

    // 【新增】处理批量删除
    const handleBatchDelete = () => {
      if (!hasSelection.value) return
      // TODO: 实现批量删除逻辑
      console.log('批量删除选中的手办:', selectedIdsArray.value)
    }

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
      handleImport,
      // 【新增】批量选择相关
      selectedIds,
      disabledIds,
      isBatchMode,
      selectedCount,
      hasSelection,
      isAllSelected,
      toggleBatchMode,
      handleToggleSelection,
      handleSelectAll,
      handleBatchDelete,
      exitBatchMode
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

/* 【新增】批量选择工具栏样式 */
.batch-toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: white;
  padding: 12px 20px;
  margin-bottom: 15px;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  border-left: 4px solid #3B82F6;
}

.batch-info {
  display: flex;
  align-items: center;
  gap: 15px;
}

.batch-count {
  font-size: 14px;
  font-weight: 500;
  color: #333;
}

.batch-actions {
  display: flex;
  gap: 10px;
}

@media (max-width: 768px) {
  .figures-container {
    margin-left: 20px;
    margin-right: 20px;
  }

  .batch-toolbar {
    flex-direction: column;
    gap: 10px;
    align-items: flex-start;
  }

  .batch-actions {
    width: 100%;
    justify-content: flex-end;
  }
}
</style>
