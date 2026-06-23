/**
 * cabinetApi.js - 收藏柜相关 API 接口
 *
 * 功能说明：
 * - 提供收藏柜相关的后端接口调用
 * - 包含出柜登记、评分更新等操作
 */

import request from '@/utils/request'

/**
 * 将藏品从展示分类中排除（软出柜）
 * @param {number} figureId - 藏品ID
 * @param {string} cabinetType - 分类标识
 * @param {string} [sourceCabinet] - 源分类（可选）
 * @param {string} [excludeReason] - 移出原因（可选）
 * @returns {Promise<Object>} 操作结果
 */
export async function excludeFigureFromCabinet(figureId, cabinetType, sourceCabinet, excludeReason) {
  try {
    const response = await request({
      url: `/collector/cabinets/figures/${figureId}/exclude`,
      method: 'POST',
      data: {
        cabinet_type: cabinetType,
        source_cabinet: sourceCabinet,
        exclude_reason: excludeReason
      }
    })
    return response
  } catch (error) {
    console.error('出柜登记失败:', error)
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
