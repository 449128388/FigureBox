<!--
  SectorRanking.vue - 板块涨幅排行组件

  功能说明：
  - 展示用户持仓按指定维度（作品/制造商/材质/原画作者）聚合的板块涨跌幅排行
  - 支持维度切换 Tab，可在四个维度间自由查看
  - 支持板块行的二级展开（手风琴）：点击板块行展开该板块下所有手办明细
  - 二级展示包括：手办表（缩略图/名称/meta/买入价/现价/涨跌幅/状态）+ 汇总栏
  - 涨跌配色遵循国人习惯（红涨绿跌）

  组件依赖：
  - useSectorRanking.js 提供数据获取、维度切换、二级展开、状态管理
  - 数据优先来自 props.marketData.sectors，切换维度/展开时回源接口
-->

<template>
  <div class="sector-ranking">
    <div class="sector-header">
      <span class="sector-title">板块涨幅排行</span>
      <span v-if="hasData || totalSectors > 0" class="sector-count-inline">共 {{ totalSectors }} 个板块</span>
    </div>

    <!-- 维度切换 -->
    <div class="dimension-tabs">
      <button
        v-for="dim in dimensions"
        :key="dim.code"
        :class="['dimension-tab', { active: activeDimension === dim.code }]"
        @click="setDimension(dim.code)"
      >{{ dim.name }}</button>
    </div>

    <div v-if="loading" class="sector-loading">加载中...</div>

    <div v-else-if="!hasData" class="sector-empty">
      <div class="empty-icon">🗂️</div>
      <div class="empty-text">暂无板块数据，添加更多手办后即可查看</div>
    </div>

    <!-- 板块手风琴列表 -->
    <div v-else class="block-accordion">
      <div
        v-for="(sector, index) in sectors"
        :key="sector.name"
        class="block-item"
      >
        <!-- 板块行（可点击） -->
        <div
          :class="['block-header', { expanded: isExpanded(sector) }]"
          @click="toggleSector(sector)"
        >
          <div :class="['block-rank', { top3: index < 3 }]">{{ index + 1 }}</div>
          <div class="block-info">
            <div class="block-name">
              {{ sector.name }}
              <span v-if="sector.body_count" class="block-count">{{ sector.body_count }}体</span>
            </div>
            <div class="block-sub">{{ sector.stocks || '暂无代表手办' }}</div>
          </div>
          <div :class="['block-pct', sector.change >= 0 ? 'up' : 'down']">
            {{ sector.change >= 0 ? '+' : '' }}{{ sector.change }}%
          </div>
          <svg
            :class="['block-arrow', { expanded: isExpanded(sector) }]"
            viewBox="0 0 24 24" fill="none" stroke="currentColor"
            stroke-width="2" stroke-linecap="round" stroke-linejoin="round"
          >
            <polyline points="6 9 12 15 18 9"></polyline>
          </svg>
        </div>

        <!-- 板块详情（手办表 + 汇总栏） -->
        <div :class="['block-detail', { expanded: isExpanded(sector) }]">
          <div v-if="detailLoading && isExpanded(sector) && !getSectorDetail(sector)" class="detail-loading">
            加载手办明细中...
          </div>

          <template v-else-if="getSectorDetail(sector)">
            <table class="detail-table">
              <thead>
                <tr>
                  <th>手办名称</th>
                  <th>买入价</th>
                  <th>卖出价</th>
                  <th>现价</th>
                  <th>涨跌幅</th>
                  <th>状态</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="fig in getSectorDetail(sector).figures" :key="fig.figure_id">
                  <td>
                    <div class="detail-figure">
                      <div class="detail-thumb">
                        <img v-if="fig.thumb" :src="fig.thumb" :alt="fig.name" @error="onImgError($event)" />
                        <span v-else>🧸</span>
                      </div>
                      <div class="detail-fig-info">
                        <div class="detail-name">{{ fig.name }}</div>
                        <div v-if="fig.meta" class="detail-meta">{{ fig.meta }}</div>
                      </div>
                    </div>
                  </td>
                  <td>¥{{ formatCurrency(fig.buy_price) }}</td>
                  <td :class="['detail-sell', { 'detail-sell-empty': fig.sell_price === null || fig.sell_price === undefined }]">
                    <template v-if="fig.sell_price !== null && fig.sell_price !== undefined">
                      ¥{{ formatCurrency(fig.sell_price) }}
                    </template>
                    <template v-else>-</template>
                  </td>
                  <td>¥{{ formatCurrency(fig.current_price) }}</td>
                  <td :class="['detail-pct', fig.change_pct >= 0 ? 'up' : 'down']">
                    {{ fig.change_pct >= 0 ? '+' : '' }}{{ fig.change_pct }}%
                  </td>
                  <td>
                    <span :class="['detail-tag', fig.status === 'holding' ? 'tag-holding' : 'tag-sold']">
                      ● {{ fig.status === 'holding' ? '在柜' : '已出' }}
                    </span>
                  </td>
                </tr>
              </tbody>
            </table>

            <div class="block-summary">
              <div class="summary-item">
                <strong>¥{{ formatCurrency(getSectorDetail(sector).summary.total_buy) }}</strong>总投入
              </div>
              <div class="summary-item">
                <strong>¥{{ formatCurrency(getSectorDetail(sector).summary.total_current) }}</strong>总市值
              </div>
              <div class="summary-item">
                <strong :style="{ color: getSectorDetail(sector).summary.change_pct >= 0 ? '#F5222D' : '#52C41A' }">
                  {{ getSectorDetail(sector).summary.change_pct >= 0 ? '+' : '' }}{{ getSectorDetail(sector).summary.change_pct }}%
                </strong>板块收益
              </div>
              <div class="summary-item">
                <strong>{{ getSectorDetail(sector).summary.holding_count }}</strong>在柜 /
                <strong>{{ getSectorDetail(sector).summary.sold_count }}</strong>已出
              </div>
            </div>
          </template>

          <div v-else class="detail-loading">暂无手办数据</div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { useSectorRanking } from '../../../composables/useSectorRanking.js'

export default {
  name: 'SectorRanking',
  props: {
    marketData: {
      type: Object,
      default: () => ({})
    }
  },
  setup(props) {
    const {
      sectors,
      totalSectors,
      loading,
      hasData,
      activeDimension,
      setDimension,
      dimensions,
      fetchDimensions,
      ensureSectors,
      expandedSector,
      detailLoading,
      toggleSector,
      isExpanded,
      getSectorDetail
    } = useSectorRanking(props)

    // 拉取维度列表 + 兜底拉取首屏数据
    fetchDimensions()
    ensureSectors(10)

    // 图片加载失败兜底
    const onImgError = (e) => {
      if (e && e.target) {
        e.target.style.display = 'none'
      }
    }

    // 金额格式化（保留整数）
    const formatCurrency = (v) => {
      if (v === null || v === undefined) return '0'
      return Number(v).toLocaleString('zh-CN', { minimumFractionDigits: 0, maximumFractionDigits: 0 })
    }

    return {
      sectors,
      totalSectors,
      loading,
      hasData,
      activeDimension,
      setDimension,
      dimensions,
      expandedSector,
      detailLoading,
      toggleSector,
      isExpanded,
      getSectorDetail,
      onImgError,
      formatCurrency
    }
  }
}
</script>

<style scoped>
.sector-ranking { margin-top: 24px; }

.sector-header {
  display: flex; align-items: center;
  margin-bottom: 12px;
}
.sector-title {
  font-size: 14px; font-weight: 600; color: #666;
  display: inline-flex; align-items: center; gap: 6px;
}
.sector-title::before {
  content: ""; display: inline-block; width: 3px; height: 14px;
  background: #4A90E2; border-radius: 2px;
}
.sector-count-inline {
  margin-left: 10px;
  font-size: 12px; color: #999;
}

/* 维度切换 Tab */
.dimension-tabs {
  display: flex; gap: 8px; margin-bottom: 12px; flex-wrap: wrap;
}
.dimension-tab {
  padding: 5px 14px; border-radius: 6px; font-size: 13px;
  border: 1px solid #D9D9D9; background: #fff; color: #666;
  cursor: pointer; transition: all 0.2s;
}
.dimension-tab:hover { border-color: #4A90E2; color: #4A90E2; }
.dimension-tab.active {
  background: #4A90E2; border-color: #4A90E2; color: #fff;
}

/* 加载/空状态 */
.sector-loading {
  text-align: center; padding: 32px 0; color: #999; font-size: 13px;
}
.sector-empty {
  display: flex; flex-direction: column; align-items: center;
  padding: 32px 20px; background: #FAFAFA; border-radius: 8px;
  border: 1px dashed #E8E8E8;
}
.sector-empty .empty-icon { font-size: 36px; opacity: 0.65; margin-bottom: 8px; }
.sector-empty .empty-text { font-size: 13px; color: #999; }

/* 板块手风琴 */
.block-accordion { background: #fff; }
.block-item { border-bottom: 1px solid #EBE8E4; }
.block-item:last-child { border-bottom: none; }

.block-header {
  display: flex; align-items: center; padding: 14px 16px;
  cursor: pointer; transition: background 0.2s;
}
.block-header:hover { background: #FAFAFA; }
.block-header.expanded { background: #EBF3FC; }

.block-rank {
  width: 28px; flex-shrink: 0;
  font-size: 14px; font-weight: 600; color: #999; text-align: center;
}
.block-rank.top3 { color: #4A90E2; }

.block-info { flex: 1; min-width: 0; margin-left: 12px; }
.block-name {
  font-size: 15px; font-weight: 600; color: #333;
  display: flex; align-items: center; gap: 8px;
}
.block-count {
  font-size: 11px; font-weight: 500; color: #999;
  background: #F5F5F5; padding: 1px 6px; border-radius: 4px;
}
.block-sub {
  font-size: 12px; color: #999; margin-top: 3px;
  overflow: hidden; text-overflow: ellipsis; white-space: nowrap;
}

.block-pct {
  font-size: 15px; font-weight: 700; margin-right: 12px;
  text-align: right; min-width: 70px;
}
/* 国人习惯：红涨绿跌 */
.block-pct.up { color: #F5222D; }
.block-pct.down { color: #52C41A; }

.block-arrow {
  width: 16px; height: 16px; color: #999;
  transition: transform 0.3s; flex-shrink: 0;
}
.block-arrow.expanded { transform: rotate(180deg); color: #4A90E2; }

.block-detail {
  max-height: 0; overflow: hidden;
  transition: max-height 0.3s ease, padding 0.3s ease;
  background: #FAFAFA;
}
.block-detail.expanded {
  max-height: 800px; padding: 12px 16px 16px 56px;
}

.detail-loading {
  padding: 20px 0; text-align: center; color: #999; font-size: 13px;
}

/* 手办明细表 */
.detail-table { width: 100%; border-collapse: collapse; }
.detail-table th {
  text-align: left; padding: 8px 12px; font-size: 12px;
  font-weight: 600; color: #999;
  border-bottom: 1px solid #EBE8E4;
}
.detail-table td {
  padding: 10px 12px; font-size: 13px;
  border-bottom: 1px solid #EEE;
}
.detail-table tr:last-child td { border-bottom: none; }
.detail-table tr:hover td { background: rgba(74, 144, 226, 0.04); }

.detail-figure { display: flex; align-items: center; gap: 10px; }
.detail-thumb {
  width: 32px; height: 32px; border-radius: 6px;
  background: #F0EEEB; display: flex; align-items: center;
  justify-content: center; font-size: 16px; flex-shrink: 0; overflow: hidden;
}
.detail-thumb img { width: 100%; height: 100%; object-fit: cover; display: block; }
.detail-fig-info { min-width: 0; }
.detail-name { font-weight: 500; color: #333; }
.detail-meta { font-size: 11px; color: #999; margin-top: 1px; }

.detail-pct { font-weight: 600; font-size: 13px; }
.detail-pct.up { color: #F5222D; }
.detail-pct.down { color: #52C41A; }

.detail-sell { font-weight: 500; }
.detail-sell-empty { color: #BBB; }

.detail-tag {
  display: inline-flex; align-items: center; gap: 3px;
  font-size: 11px; padding: 1px 6px; border-radius: 4px;
}
.tag-holding { background: #F6FFED; color: #52C41A; }
.tag-sold { background: #F5F5F5; color: #999; }

/* 汇总栏 */
.block-summary {
  display: flex; gap: 16px; margin-top: 12px; padding-top: 12px;
  border-top: 1px dashed #EBE8E4; flex-wrap: wrap;
}
.summary-item {
  font-size: 12px; color: #666;
}
.summary-item strong {
  color: #333; font-size: 14px; margin-right: 4px;
}
</style>
