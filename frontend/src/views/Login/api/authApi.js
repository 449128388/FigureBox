/**
 * authApi.js - 登录/注册/密码重置 API 调用层
 *
 * 功能说明：
 * - 封装个人中心-账号安全模块的 HTTP 请求
 * - 与业务逻辑（composables）和 UI 组件（vue）解耦
 * - 端点：
 *   - POST /api/auth/login            登录
 *   - POST /api/auth/register         注册
 *   - POST /api/auth/forgot-password  请求密码重置验证码
 *   - POST /api/auth/verify-reset-code 校验密码重置验证码（不消费）
 *   - POST /api/auth/reset-password   通过验证码重置密码（消费）
 */
import axios from '../../../axios'

export const authApi = {
  /** 登录 */
  async login(email, password) {
    return await axios.post('/auth/login', { email, password })
  },
  /** 注册 */
  async register(username, email, password) {
    return await axios.post('/auth/register', { username, email, password })
  },
  /** 请求密码重置验证码（公开端点） */
  async forgotPassword(email) {
    return await axios.post('/auth/forgot-password', { email })
  },
  /** 校验密码重置验证码（公开端点，不消费） */
  async verifyResetCode(email, code) {
    return await axios.post('/auth/verify-reset-code', { email, code })
  },
  /** 通过验证码重置密码（公开端点，消费验证码） */
  async resetPassword(email, code, newPassword) {
    return await axios.post('/auth/reset-password', { email, code, new_password: newPassword })
  }
}
