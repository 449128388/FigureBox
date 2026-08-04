/**
 * backupApi.js - 系统备份/恢复 API 调用层
 *
 * 功能说明：
 * - 封装个人中心-系统备份模块的 HTTP 请求
 * - 与业务逻辑（composables）和 UI 组件（vue）解耦
 * - 端点：
 *   - GET  /api/backup/download                立即备份下载
 *   - POST /api/backup/restore                 数据恢复
 *   - GET  /api/backup/settings                读取自动备份配置
 *   - PUT  /api/backup/settings                更新自动备份配置
 *   - GET  /api/backup/records?page=&page_size= 备份历史分页
 *   - DELETE /api/backup/records/{id}          删除某条历史
 *   - GET  /api/backup/records/{id}/download   按 ID 重新下载
 */
import axios from '../../../axios'

export const backupApi = {
  // ===== 备份 / 恢复 =====

  /**
   * 立即备份：下载全量手办数据为 JSON
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
  },

  // ===== 自动备份配置 =====

  /**
   * 读取当前用户的自动备份配置
   * @returns {Promise<{enabled, frequency, retain, last_auto_backup_at}>}
   */
  async getSettings() {
    return await axios.get('/backup/settings')
  },

  /**
   * 更新当前用户的自动备份配置
   * @param {{enabled?: boolean, frequency?: string, retain?: number}} payload
   * @returns {Promise<{enabled, frequency, retain, last_auto_backup_at}>}
   */
  async updateSettings(payload) {
    return await axios.put('/backup/settings', payload)
  },

  // ===== 备份历史 =====

  /**
   * 分页拉取当前用户的备份历史
   * @param {number} page - 页码（从 1 开始）
   * @param {number} pageSize - 每页条数
   * @returns {Promise<{total, page, page_size, items: Array}>}
   */
  async listRecords(page = 1, pageSize = 10) {
    return await axios.get('/backup/records', {
      params: { page, page_size: pageSize }
    })
  },

  /**
   * 删除某条备份历史（同时删磁盘文件）
   * @param {number} id - 备份记录 ID
   * @returns {Promise<{success, message, file_deleted?}>}
   */
  async deleteRecord(id) {
    return await axios.delete(`/backup/records/${id}`)
  }
}
