/**
 * manufacturerApi.js - 本命厂商 API 接口
 *
 * 功能说明：
 * - 提供本命厂商的 CRUD 接口调用
 * - 获取厂商列表、详情、新增、编辑、删除
 */

import axios from '@/axios'

/**
 * 获取所有本命厂商列表（支持搜索 / 筛选）
 * @param {Object} [params] - 查询参数
 * @param {string} [params.keyword] - 搜索关键词
 * @param {string} [params.filter_type] - 筛选类型 ("in" | "out" | "")
 * @returns {Promise<Object>} { manufacturers, total }
 */
export async function getManufacturers(params = {}) {
  try {
    const response = await axios.get('/collector/manufacturers', {
      params: {
        keyword: params.keyword || '',
        filter_type: params.filter_type || ''
      }
    })
    return response
  } catch (error) {
    console.error('获取本命厂商列表失败:', error)
    throw error
  }
}

/**
 * 获取单个本命厂商详情（含手办列表）
 * @param {number} id - 厂商ID
 * @returns {Promise<Object>} 厂商详情
 */
export async function getManufacturerDetail(id) {
  try {
    const response = await axios.get(`/collector/manufacturers/${id}`)
    return response
  } catch (error) {
    console.error('获取本命厂商详情失败:', error)
    throw error
  }
}

/**
 * 新增本命厂商
 * @param {Object} data - 厂商数据
 * @param {string} data.name - 厂商中文名称
 * @param {string} [data.name_jp] - 厂商日文/原文名称
 * @param {string} [data.description] - 厂商描述
 * @param {string} [data.logo_url] - Logo URL
 * @param {string} [data.website_url] - 官网链接
 * @param {string} [data.twitter_url] - 推特/X 链接
 * @returns {Promise<Object>} 操作结果
 */
export async function createManufacturer(data) {
  try {
    const response = await axios.post('/collector/manufacturers', data)
    return response
  } catch (error) {
    console.error('新增本命厂商失败:', error)
    throw error
  }
}

/**
 * 更新本命厂商
 * @param {number} id - 厂商ID
 * @param {Object} data - 要更新的字段
 * @returns {Promise<Object>} 操作结果
 */
export async function updateManufacturer(id, data) {
  try {
    const response = await axios.put(`/collector/manufacturers/${id}`, data)
    return response
  } catch (error) {
    console.error('更新本命厂商失败:', error)
    throw error
  }
}

/**
 * 删除本命厂商
 * @param {number} id - 厂商ID
 * @returns {Promise<Object>} 操作结果
 */
export async function deleteManufacturer(id) {
  try {
    const response = await axios.delete(`/collector/manufacturers/${id}`)
    return response
  } catch (error) {
    console.error('删除本命厂商失败:', error)
    throw error
  }
}
