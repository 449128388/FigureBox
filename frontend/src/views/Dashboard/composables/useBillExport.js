/**
 * 账单导出 composable
 * 提供账单导出相关的业务逻辑，与UI层分离
 */
import { ref } from 'vue'
import axios from '../../../axios'
import { ElMessage } from 'element-plus'

export function useBillExport() {
  const dialogVisible = ref(false)
  const loading = ref(false)

  const openDialog = () => {
    dialogVisible.value = true
  }

  const closeDialog = () => {
    dialogVisible.value = false
  }

  const exportBill = async (exportOptions) => {
    const { range, format, year, month } = exportOptions

    loading.value = true
    try {
      const params = {
        format,
        range
      }

      if (range === 'current') {
        params.year = year
        params.month = month
      }

      const response = await axios.get('/trade_records/export', {
        params,
        responseType: 'blob'
      })

      const blob = new Blob([response], {
        type: format === 'xlsx'
          ? 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
          : 'text/csv;charset=utf-8'
      })

      const url = window.URL.createObjectURL(blob)
      const link = document.createElement('a')
      link.href = url

      const filename = range === 'current'
        ? `交易账单_${year}年${month}月.${format}`
        : `交易账单_全部历史.${format}`

      link.setAttribute('download', filename)
      document.body.appendChild(link)
      link.click()
      document.body.removeChild(link)
      window.URL.revokeObjectURL(url)

      ElMessage.success('账单导出成功')
      closeDialog()
    } catch (error) {
      ElMessage.error('账单导出失败')
    } finally {
      loading.value = false
    }
  }

  return {
    dialogVisible,
    loading,
    openDialog,
    closeDialog,
    exportBill
  }
}
