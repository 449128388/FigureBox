<!--
  InvestmentReview.vue - 投资复盘模块

  功能说明：
  - 展示成分股逐一复盘（在柜/已出）
  - 每只手办显示：名称、状态、买入→现价、收益率、权重、贡献
  - 底部汇总卡片：卖飞/卖对/投资胜率/累计交易金额

  数据来源：
  - 通过 props 接收 marketData，从中提取 components
  - 或直接从 /api/market/hpi-components 接口获取

  展示策略：
  - 默认折叠态：展示 5 条（刚好一屏可读）
  - 展开/全量态：展示全部，超过 20 条启用滚动容器
  - 排序规则：在柜优先 → |收益率|降序 → 权重降序
  - 空状态：占位图 + 引导文案
-->

<template>
  <div class="review-section">
    <div class="review-title">
      <span>💡 投资复盘</span>
      <span v-if="!loading && sortedComponents.length > 0" class="review-count">
        共 {{ sortedComponents.length }} 体
      </span>
    </div>

    <div v-if="loading" class="loading">加载中...</div>

    <!-- 空状态：占位图 + 引导文案 -->
    <div v-else-if="sortedComponents.length === 0" class="empty-state">
      <div class="empty-icon">📦</div>
      <div class="empty-text">暂无交易记录，快去添加第一体手办吧</div>
      <div class="empty-hint">添加你的第一笔买入后，投资复盘将自动开启</div>
    </div>

    <template v-else>
      <!-- 成分股列表（折叠态 5 条，展开态全部；超过 20 条启用滚动容器） -->
      <div :class="['comp-list', { 'is-scrollable': isExpanded && sortedComponents.length > 20 }]">
        <div v-for="comp in displayedComponents" :key="`${comp.figure_id}-${comp.is_sold ? 'sold' : 'holding'}`" class="comp-row">
          <div class="comp-thumb">
            <img v-if="comp.first_image" :src="comp.first_image" :alt="comp.figure_name" class="comp-thumb-img" @error="handleImgError($event)" />
            <span v-else>{{ comp.figure_name?.charAt(0) || '🧸' }}</span>
          </div>
          <div class="comp-info">
            <div class="comp-name">
              {{ comp.figure_name || `手办 #${comp.figure_id}` }}
              <span class="comp-status" :class="comp.is_sold ? 'sold' : 'holding'">
                ● {{ comp.is_sold ? '已出' : '在柜' }}
                <template v-if="comp.quantity && comp.quantity > 1"> · {{ comp.quantity }}体</template>
              </span>
              <span v-if="comp.is_sold" class="comp-sell-tag" :class="comp.sell_right ? 'sell-right' : 'sell-fly'">
                {{ comp.sell_right ? '✓ 卖对了' : comp.sell_fly ? '⚡ 卖飞' : '' }}
              </span>
            </div>
            <div class="comp-meta">
              <template v-if="comp.is_sold">
                <template v-if="comp.quantity && comp.quantity > 1">
                  买入 ¥{{ formatCurrency(comp.first_buy_price) }}/体 → 卖出 ¥{{ formatCurrency(comp.sell_price) }} · 共 {{ comp.quantity }}体
                </template>
                <template v-else>
                  买入 ¥{{ formatCurrency(comp.first_buy_price) }} → 卖出 ¥{{ formatCurrency(comp.sell_price) }}
                </template>
              </template>
              <template v-else>
                <template v-if="comp.quantity && comp.quantity > 1">
                  买入 ¥{{ formatCurrency(comp.first_buy_price) }}/体 → 现价 ¥{{ formatCurrency(comp.current_price) }} · 在柜 {{ comp.quantity }}体
                </template>
                <template v-else>
                  买入 ¥{{ formatCurrency(comp.first_buy_price) }} → 现价 ¥{{ formatCurrency(comp.current_price) }}
                </template>
                <template v-if="comp.first_buy_date"> | 持仓 {{ holdingDays(comp.first_buy_date) }} 天</template>
              </template>
            </div>
          </div>
          <div class="comp-return">
            <div class="comp-return-val" :class="{ up: comp.return_pct > 0, down: comp.return_pct < 0 }">
              {{ comp.return_pct > 0 ? '+' : '' }}{{ comp.return_pct?.toFixed(1) || '0.0' }}%
            </div>
            <div class="comp-return-label">相对首次买入</div>
          </div>
          <div class="comp-weight">
            <div class="comp-weight-val">{{ ((comp.weight || 0) * 100).toFixed(1) }}%</div>
            <div class="comp-weight-label">权重</div>
          </div>
          <div class="comp-contrib">
            <div class="comp-contrib-val" :class="{ up: comp.contribution > 0, down: comp.contribution < 0 }">
              {{ comp.contribution > 0 ? '+' : '' }}{{ comp.contribution?.toFixed(1) || '0.0' }}
            </div>
            <div class="comp-contrib-label">贡献</div>
          </div>
        </div>
      </div>

      <!-- 展开/收起 切换按钮（仅当总数 > 5 时显示） -->
      <div v-if="sortedComponents.length > 5" class="toggle-bar">
        <button class="toggle-btn" @click="isExpanded = !isExpanded">
          {{ isExpanded ? '收起列表' : `展开全部 (${sortedComponents.length})` }}
          <span class="toggle-arrow">{{ isExpanded ? '▲' : '▼' }}</span>
        </button>
      </div>

      <!-- 卖出统计卡片 -->
      <div class="sell-stats-card">
        <div class="sell-stat-item">
          <div class="sell-stat-num green">{{ sellStats.soldUp }}</div>
          <div class="sell-stat-label">卖飞</div>
          <div class="sell-stat-desc">卖出后上涨</div>
        </div>
        <div class="sell-stat-item">
          <div class="sell-stat-num red">{{ sellStats.soldDown }}</div>
          <div class="sell-stat-label">卖对</div>
          <div class="sell-stat-desc">卖出后下跌/持平</div>
        </div>
        <div class="sell-stat-item">
          <div class="sell-stat-num accent">{{ sellStats.winRate }}</div>
          <div class="sell-stat-label">投资胜率</div>
          <div class="sell-stat-desc">{{ sellStats.soldDown }}/{{ sellStats.soldTotal }} 卖出决策正确</div>
        </div>
        <div class="sell-stat-item">
          <div class="sell-stat-num orange">¥{{ formatCurrency(sellStats.totalAmount) }}</div>
          <div class="sell-stat-label">累计交易金额</div>
          <div class="sell-stat-desc">生涯总投入</div>
        </div>
      </div>
    </template>
  </div>
</template>

<script>
import { ref, computed, watch } from 'vue'
import axios from '../../../../../axios'

// 默认折叠态展示条数（一屏可读）
const COLLAPSED_LIMIT = 5

export default {
  name: 'InvestmentReview',
  props: {
    marketData: {
      type: Object,
      default: () => ({})
    }
  },
  setup(props) {
    const loading = ref(false)
    const components = ref([])
    // 展开/折叠态
    const isExpanded = ref(false)

    // 排序后的成分股：在柜优先 → |收益率|降序 → 权重降序
    const sortedComponents = computed(() => {
      return [...components.value].sort((a, b) => {
        // 1. 在柜手办优先（is_sold = 0 在前）
        if (!!a.is_sold !== !!b.is_sold) {
          return a.is_sold ? 1 : -1
        }
        // 2. 按 |收益率| 绝对值降序（涨跌最猛的在前）
        const absA = Math.abs(a.return_pct || 0)
        const absB = Math.abs(b.return_pct || 0)
        if (absA !== absB) {
          return absB - absA
        }
        // 3. 同收益率下，按权重降序
        return (b.weight || 0) - (a.weight || 0)
      })
    })

    // 实际展示的成分股：折叠态前 5 条，展开态全部
    const displayedComponents = computed(() => {
      return isExpanded.value
        ? sortedComponents.value
        : sortedComponents.value.slice(0, COLLAPSED_LIMIT)
    })

    // 计算卖出统计（按「体」计数：quantity=2 的已出行算作 2 体）
    const sellStats = computed(() => {
      const soldItems = sortedComponents.value.filter(c => c.is_sold)
      const soldUp = soldItems.reduce((sum, c) => sum + (c.sell_fly ? (c.quantity || 1) : 0), 0)
      const soldDown = soldItems.reduce((sum, c) => sum + (c.sell_right ? (c.quantity || 1) : 0), 0)
      const soldTotal = soldItems.reduce((sum, c) => sum + (c.quantity || 1), 0)
      const totalAmount = sortedComponents.value.reduce((sum, c) => sum + (c.total_buy_amount || 0), 0)
      return {
        soldUp,
        soldDown,
        soldTotal,
        winRate: soldTotal > 0 ? `${(soldDown / soldTotal * 100).toFixed(1)}%` : '—',
        totalAmount
      }
    })

    // 持仓天数计算
    const holdingDays = (buyDate) => {
      if (!buyDate) return 0
      const start = new Date(buyDate)
      const now = new Date()
      return Math.floor((now - start) / (1000 * 60 * 60 * 24))
    }

    // 格式化货币
    const formatCurrency = (v) => {
      if (!v && v !== 0) return '0'
      return Number(v).toLocaleString('zh-CN', { minimumFractionDigits: 0, maximumFractionDigits: 0 })
    }

    // 图片加载失败时回退到首字
    const handleImgError = (e) => {
      const target = e.target
      if (target) target.style.display = 'none'
    }

    // 从 marketData 或独立接口获取成分股数据
    const fetchComponents = async () => {
      if (props.marketData?.index?.components?.length) {
        components.value = props.marketData.index.components
        return
      }
      loading.value = true
      try {
        const res = await axios.get('/market/hpi-components')
        components.value = [...(res.holding || []), ...(res.sold || [])]
      } catch { /* ignore */ }
      finally { loading.value = false }
    }

    // 监听 marketData 变化
    watch(() => props.marketData, () => {
      if (props.marketData?.index?.components?.length) {
        components.value = props.marketData.index.components
        // 数据更新时重置为折叠态
        isExpanded.value = false
      }
    }, { immediate: false })

    fetchComponents()

    return {
      components, loading, isExpanded,
      sortedComponents, displayedComponents,
      sellStats, holdingDays, formatCurrency, handleImgError
    }
  }
}
</script>

<style scoped>
.review-section { margin-top: 16px; }
.review-title {
  font-size: 14px; font-weight: 600; color: #666;
  margin-bottom: 12px; display: flex; align-items: center; gap: 8px;
}
.review-title::before {
  content: ""; display: inline-block; width: 3px; height: 14px;
  background: #4A90E2; border-radius: 2px;
}
.review-count {
  font-size: 12px; font-weight: 400; color: #999;
  background: #F5F5F5; padding: 2px 8px; border-radius: 10px;
}
.loading { text-align: center; padding: 40px 0; color: #999; font-size: 13px; }

/* 空状态：占位图 + 引导文案 */
.empty-state {
  display: flex; flex-direction: column; align-items: center;
  padding: 48px 20px; background: #FAFAFA; border-radius: 8px;
  border: 1px dashed #E8E8E8; margin: 8px 0 16px;
}
.empty-icon { font-size: 48px; margin-bottom: 12px; opacity: 0.65; }
.empty-text { font-size: 14px; color: #666; font-weight: 500; margin-bottom: 4px; }
.empty-hint { font-size: 12px; color: #999; }

/* Component List */
.comp-list { margin-bottom: 4px; }
.comp-list.is-scrollable {
  max-height: 560px; overflow-y: auto;
  border: 1px solid #F0F0F0; border-radius: 8px;
  scrollbar-width: thin; scrollbar-color: #D9D9D9 transparent;
}
.comp-list.is-scrollable::-webkit-scrollbar { width: 6px; }
.comp-list.is-scrollable::-webkit-scrollbar-thumb { background: #D9D9D9; border-radius: 3px; }
.comp-list.is-scrollable::-webkit-scrollbar-track { background: transparent; }

/* Component Row */
.comp-row {
  display: flex; align-items: center; padding: 14px 16px;
  border-bottom: 1px solid #EBE8E4; transition: background 0.2s;
}
.comp-row:last-child { border-bottom: none; }
.comp-row:hover { background: #FAFAFA; }

.comp-thumb {
  width: 44px; height: 44px; border-radius: 8px; background: #F0EEEB;
  display: flex; align-items: center; justify-content: center; font-size: 22px;
  margin-right: 14px; flex-shrink: 0; overflow: hidden;
}
.comp-thumb-img { width: 100%; height: 100%; object-fit: cover; border-radius: 8px; }
.comp-info { flex: 1; min-width: 0; }
.comp-name { font-size: 14px; font-weight: 600; margin-bottom: 3px; }
.comp-meta { font-size: 12px; color: #999; }

.comp-status {
  display: inline-flex; align-items: center; gap: 4px;
  font-size: 11px; padding: 2px 8px; border-radius: 10px; margin-left: 8px;
}
.comp-status.holding { background: #E8F5E9; color: #52C41A; }
.comp-status.sold { background: #F5F5F5; color: #8C8C8C; }

.comp-sell-tag {
  font-size: 11px; padding: 2px 8px; border-radius: 10px; margin-left: 8px;
}
/* 国人习惯：卖对（决策正确）红色，卖飞（决策失误）绿色 */
.sell-fly { background: #F6FFED; color: #52C41A; }
.sell-right { background: #FFF1F0; color: #F5222D; }

.comp-return { text-align: right; margin-right: 20px; min-width: 80px; }
.comp-return-val { font-size: 15px; font-weight: 700; }
/* 国人习惯：红涨绿跌 */
.comp-return-val.up { color: #F5222D; }
.comp-return-val.down { color: #52C41A; }
.comp-return-label { font-size: 11px; color: #999; }

.comp-weight { text-align: right; margin-right: 20px; min-width: 60px; }
.comp-weight-val { font-size: 14px; font-weight: 600; color: #1F1F1F; }
.comp-weight-label { font-size: 11px; color: #999; }

.comp-contrib { text-align: right; min-width: 70px; }
.comp-contrib-val { font-size: 14px; font-weight: 600; }
/* 国人习惯：红涨绿跌 */
.comp-contrib-val.up { color: #F5222D; }
.comp-contrib-val.down { color: #52C41A; }
.comp-contrib-label { font-size: 11px; color: #999; }

/* Toggle Bar */
.toggle-bar { text-align: center; padding: 8px 0 4px; }
.toggle-btn {
  background: none; border: none; cursor: pointer;
  font-size: 13px; color: #4A90E2; padding: 6px 16px;
  border-radius: 4px; transition: background 0.2s;
  display: inline-flex; align-items: center; gap: 4px;
}
.toggle-btn:hover { background: #F0F7FF; }
.toggle-arrow { font-size: 10px; }

/* Sell Stats Card */
.sell-stats-card {
  background: linear-gradient(135deg, #FAFAFA 0%, #F5F5F5 100%);
  border-radius: 8px; padding: 16px 20px;
  border: 1px solid #EBE8E4; margin-top: 16px;
  display: flex; align-items: center; justify-content: space-between;
}
.sell-stat-item { text-align: center; }
.sell-stat-num { font-size: 24px; font-weight: 700; }
.sell-stat-num.green { color: #52C41A; }
.sell-stat-num.red { color: #D66A6A; }
.sell-stat-num.accent { color: #4A90E2; }
.sell-stat-num.orange { color: #E6A23C; }
.sell-stat-label { font-size: 12px; color: #999; margin-top: 4px; }
.sell-stat-desc { font-size: 11px; color: #666; margin-top: 2px; }
</style>
