/**
 * securityApi.js - 账号安全 API 调用层
 *
 * 功能说明：
 * - 封装个人中心-账号安全模块的 HTTP 请求
 * - 与业务逻辑（composables）和 UI 组件（vue）解耦
 * - 端点：
 *   - POST /api/users/me/change-password  修改登录密码
 */
import axios from '../../../axios'

export const securityApi = {
  /**
   * 修改当前登录用户密码
   * @param {string} currentPassword - 当前登录密码
   * @param {string} newPassword - 新密码（8-20 位）
   * @returns {Promise<{success: boolean, message: string}>}
   */
  async changePassword(currentPassword, newPassword) {
    return await axios.post('/users/me/change-password', {
      current_password: currentPassword,
      new_password: newPassword
    })
  }
}
