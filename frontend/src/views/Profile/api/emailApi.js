/**
 * emailApi.js - 邮箱设置（SMTP 发件配置）API 调用层
 *
 * 功能说明：
 * - 封装个人中心-系统备份-邮箱设置模块的 HTTP 请求
 * - 与业务逻辑（composables）和 UI 组件（vue）解耦
 * - 端点：
 *   - GET    /api/email/config        读取 SMTP 配置
 *   - PUT    /api/email/config        更新 SMTP 配置
 *   - POST   /api/email/test          测试 SMTP 连接
 *   - POST   /api/email/test-send     发送测试邮件
 */
import axios from '../../../axios'

export const emailApi = {
  /**
   * 读取当前用户 SMTP 邮箱配置（密码不回传，smtp_password_set 表示是否已设置）
   * @returns {Promise<Object>}
   */
  async getConfig() {
    return await axios.get('/email/config')
  },

  /**
   * 更新当前用户 SMTP 邮箱配置
   * @param {Object} payload 配置项（只传需要更新的字段）
   * @param {string} [payload.smtp_host]
   * @param {number} [payload.smtp_port]
   * @param {string} [payload.smtp_from_email]
   * @param {string} [payload.smtp_from_name]
   * @param {string} [payload.smtp_password]
   * @param {string} [payload.smtp_secure_mode] - ssl / starttls / none
   * @returns {Promise<Object>}
   */
  async updateConfig(payload) {
    return await axios.put('/email/config', payload)
  },

  /**
   * 测试 SMTP 连接（仅 login，不发邮件）
   * @returns {Promise<{success: boolean, message: string}>}
   */
  async testConnection() {
    return await axios.post('/email/test')
  },

  /**
   * 发送测试邮件到指定收件邮箱
   * @param {string} testTo - 测试收件邮箱
   * @returns {Promise<{success: boolean, message: string}>}
   */
  async sendTestEmail(testTo) {
    return await axios.post('/email/test-send', { test_to: testTo })
  }
}
