/**
 * useExchangeRates.js - 统一汇率 composable
 *
 * 提供前端统一的汇率获取和币种转换功能
 * 优先从后端 API 获取实时汇率，兜底使用默认汇率
 */

import { ref } from 'vue'
import axios from '../axios'

// 兜底默认汇率（API 不可用时使用）
const FALLBACK_RATES = {
  CNY: 1.0,
  USD: 7.0,
  JPY: 1 / 23,
  EUR: 8.0,
  HKD: 0.9,
  GBP: 9.0
}

// 缓存
let cachedRates = null
let lastFetchTime = 0
const CACHE_TTL = 5 * 60 * 1000 // 5 分钟

/**
 * 获取汇率映射表
 * 优先从后端 API 获取，带 5 分钟缓存
 */
async function fetchRates() {
  const now = Date.now()
  if (cachedRates && now - lastFetchTime < CACHE_TTL) {
    return cachedRates
  }
  try {
    const res = await axios.get('/assets/exchange-rates')
    cachedRates = res
    lastFetchTime = now
    return res
  } catch {
    return { ...FALLBACK_RATES }
  }
}

/**
 * 将指定币种金额转换为人民币
 */
function convertToCNY(amount, currency, rates) {
  if (!currency || currency === 'CNY') return amount || 0
  const rate = rates?.[currency] || FALLBACK_RATES[currency] || 1.0
  return (amount || 0) * rate
}

export function useExchangeRates() {
  const loading = ref(false)
  const rates = ref({ ...FALLBACK_RATES })

  /**
   * 加载/刷新汇率
   */
  async function loadRates() {
    loading.value = true
    try {
      const data = await fetchRates()
      rates.value = data
    } catch {
      rates.value = { ...FALLBACK_RATES }
    } finally {
      loading.value = false
    }
  }

  /**
   * 获取单个币种汇率
   */
  function getRate(currency) {
    return rates.value[currency] ?? FALLBACK_RATES[currency] ?? 1.0
  }

  /**
   * 金额转人民币
   */
  function toCNY(amount, currency) {
    return convertToCNY(amount, currency, rates.value)
  }

  return {
    loading,
    rates,
    loadRates,
    getRate,
    toCNY
  }
}

// 导出一个无状态的工具函数版本（用于非 composition 场景）
export const exchangeUtils = {
  fetchRates,
  convertToCNY
}
