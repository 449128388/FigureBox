/**
 * privacyApi.js - 隐私设置 API 接口
 */
import axios from '@/axios'

/**
 * 获取隐私设置
 * @returns {Promise<Object>} 隐私设置对象
 */
export function fetchPrivacySettings() {
  return axios.get('/collector/privacy')
}

/**
 * 更新隐私设置
 * @param {Object} settings - 要更新的字段
 * @returns {Promise<Object>} 操作结果
 */
export function updatePrivacySettings(settings) {
  return axios.put('/collector/privacy', settings)
}
