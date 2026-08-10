/**
 * licenseApi.js - 许可管理 API 调用层
 *
 * 功能说明：
 * - 封装个人中心-邮箱设置-许可管理面板的 HTTP 请求
 * - 与业务逻辑（composables）和 UI 组件（vue）解耦
 * - 端点（全部需要登录）：
 *   - GET    /api/license/status                  读取许可状态
 *   - GET    /api/license/machine-fingerprint     获取本机机器指纹
 *   - POST   /api/license/activate                在线激活
 *   - POST   /api/license/import                  离线导入 .lic
 *   - GET    /api/license/history                 许可历史
 *   - POST   /api/license/revoke                  吊销
 *   - POST   /api/license/delete                  删除记录
 */
import axios from '../../../axios'

export const licenseApi = {
  /**
   * 获取当前许可状态
   * @returns {Promise<Object>} 详见 LicenseResponse
   */
  async getStatus() {
    return await axios.get('/license/status')
  },

  /**
   * 获取本机机器指纹
   * @returns {Promise<{fingerprint, hostname, platform, generated_at}>}
   */
  async getMachineFingerprint() {
    return await axios.get('/license/machine-fingerprint')
  },

  /**
   * 在线激活
   * @param {string} licenseKey
   * @returns {Promise<{success, message, data?}>}
   */
  async activate(licenseKey) {
    return await axios.post('/license/activate', { license_key: licenseKey })
  },

  /**
   * 离线导入 .lic 文件
   * @param {string} filename
   * @param {string} content 文件原始内容（前端用 FileReader 读取为文本）
   * @returns {Promise<{success, message, data?}>}
   */
  async importFile(filename, content) {
    return await axios.post('/license/import', { filename, content })
  },

  /**
   * 获取许可历史
   * @returns {Promise<{items, total}>}
   */
  async getHistory() {
    return await axios.get('/license/history')
  },

  /**
   * 吊销当前许可
   * @returns {Promise<{success, message, data?}>}
   */
  async revoke() {
    return await axios.post('/license/revoke')
  },

  /**
   * 删除许可记录
   * @returns {Promise<{success, message, data?}>}
   */
  async delete() {
    return await axios.post('/license/delete')
  }
}
