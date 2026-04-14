import { ref } from 'vue'
import axios from '../../../axios'

export function useImportFigures() {
  const showImportDialog = ref(false)
  const isImporting = ref(false)
  const importProgress = ref(0)
  const importResult = ref(null)
  const importError = ref(null)

  const openImportDialog = () => {
    showImportDialog.value = true
    importResult.value = null
    importError.value = null
    importProgress.value = 0
  }

  const closeImportDialog = () => {
    showImportDialog.value = false
  }

  const importFigures = async (data) => {
    isImporting.value = true
    importProgress.value = 0
    importError.value = null

    try {
      const response = await axios.post('/figures/import', {
        figures: data
      }, {
        onUploadProgress: (progressEvent) => {
          if (progressEvent.total) {
            importProgress.value = Math.round(
              (progressEvent.loaded * 100) / progressEvent.total
            )
          }
        }
      })

      importResult.value = response
      return {
        success: true,
        imported: response.imported_count || 0,
        orders: response.orders_count || 0,
        message: response.message || '导入成功'
      }
    } catch (error) {
      importError.value = error.response?.data?.detail || error.message || '导入失败'
      return {
        success: false,
        message: importError.value
      }
    } finally {
      isImporting.value = false
      importProgress.value = 100
    }
  }

  return {
    showImportDialog,
    isImporting,
    importProgress,
    importResult,
    importError,
    openImportDialog,
    closeImportDialog,
    importFigures
  }
}
