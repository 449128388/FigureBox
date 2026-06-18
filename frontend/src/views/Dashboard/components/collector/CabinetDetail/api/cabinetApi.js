/**
 * cabinetApi.js - 收藏柜相关 API 接口
 *
 * 功能说明：
 * - 提供收藏柜相关的后端接口调用
 * - 包含出柜登记、评分更新等操作
 */

import request from '@/utils/request'

/**
 * 将藏品从收藏柜移出
 * @param {number} figureId - 藏品ID
 * @param {string} cabinetKey - 收藏柜key
 * @returns {Promise<Object>} 操作结果
 */
export async function removeFigureFromCabinet(figureId, cabinetKey) {
  try {
    const response = await request({
      url: '/api/v1/cabinets/remove-figure',
      method: 'POST',
      data: {
        figure_id: figureId,
        cabinet_key: cabinetKey
      }
    })
    return response
  } catch (error) {
    console.error('移出藏品失败:', error)
    throw error
  }
}

/**
 * 更新藏品评分
 * @param {number} figureId - 藏品ID
 * @param {number} rating - 评分值 (1-5)
 * @returns {Promise<Object>} 操作结果
 */
export async function updateFigureRating(figureId, rating) {
  try {
    const response = await request({
      url: `/api/v1/cabinets/figures/${figureId}/rating`,
      method: 'PUT',
      data: { rating }
    })
    return response
  } catch (error) {
    console.error('更新评分失败:', error)
    throw error
  }
}
