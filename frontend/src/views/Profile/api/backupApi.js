/**
 * backupApi.js - 系统备份/恢复 API 调用层
 *
 * 功能说明：
 * - 封装个人中心-系统备份模块的 HTTP 请求
 * - 与业务逻辑（composables）和 UI 组件（vue）解耦
 * - 端点：GET /api/backup/download · POST /api/backup/restore
 */
import axios from '../../../axios'

export const backupApi = {
  /**
   * 立即备份：下载全量手办数据为 JSON
   * @param {string} token - 鉴权 token（默认从 store 读取）
   * @returns {Promise<{json_str: string, filename: string, count: number}>}
   */
  async downloadBackup() {
    const response = await axios.get('/backup/download', {
      responseType: 'json'
    })
    return response
  },

  /**
   * 数据恢复：上传 JSON 文件进行数据恢复
   * @param {File} file - 备份文件
   * @returns {Promise<{success, imported_figures, updated_figures, imported_orders, errors, message}>}
   */
  async restoreBackup(file) {
    const formData = new FormData()
    formData.append('file', file)
    const response = await axios.post('/backup/restore', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })
    return response
  }
}
