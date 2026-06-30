<!--
  HPIDetail.vue - 塑料小人指数(HPI)详情组件

  功能说明：
  - 展示 HPI 指数值、平均收益率
  - K 线图（在柜/已出双线）
  - 成分股列表（在柜+已出）
  - 卖飞/卖对统计
-->
<template>
  <div class="hpi-detail">
    <!-- 顶部标题行 + 涨平跌药丸（与参考设计一致） -->
    <div class="hpi-title-row">
      <div class="hpi-title-section">
        <h3>塑料小人指数 (HPI)</h3>
        <span class="hpi-subtitle">投资生涯全周期收益指数</span>
      </div>
      <div class="hpi-stats-pills">
        <div class="stat-pill up">
          <div class="pill-label">涨</div>
          <div class="pill-num">{{ indexData?.up_count || 0 }}</div>
        </div>
        <div class="stat-pill flat">
          <div class="pill-label">平</div>
          <div class="pill-num">{{ indexData?.flat_count || 0 }}</div>
        </div>
        <div class="stat-pill down">
          <div class="pill-label">跌</div>
          <div class="pill-num">{{ indexData?.down_count || 0 }}</div>
        </div>
      </div>
    </div>

    <div class="hpi-body">
    <!-- HPI 核心指标 -->
    <div class="hpi-header">
      <div class="hpi-main-value">
        <span class="value">{{ formatNumber(indexData?.index_value) }}</span>
        <span class="unit">点</span>
      </div>
      <div class="hpi-avg-return">
        生涯均价涨幅：<span :class="returnClass">{{ formatPct(indexData?.avg_return) }}</span>
      </div>
    </div>

    <!-- 统计卡片 -->
    <div class="hpi-stats">
      <div class="stat-card">
        <div class="stat-label">生涯手办</div>
        <div class="stat-value">{{ indexData?.total_figures || 0 }}</div>
      </div>
      <div class="stat-card">
        <div class="stat-label">当前在柜</div>
        <div class="stat-value">{{ indexData?.holding_figures || 0 }}</div>
      </div>
      <div class="stat-card">
        <div class="stat-label">已出跟踪</div>
        <div class="stat-value sold-track">{{ indexData?.sold_figures || 0 }}</div>
      </div>
      <div class="stat-card">
        <div class="stat-label">卖飞</div>
        <div class="stat-value fly">{{ indexData?.sold_up_count || 0 }}</div>
      </div>
      <div class="stat-card">
        <div class="stat-label">卖对</div>
        <div class="stat-value right">{{ indexData?.sold_down_count || 0 }}</div>
      </div>
    </div>

    <!-- K 线图 -->
    <div class="hpi-chart-section">
      <div class="chart-header">
        <h4>HPI 走势</h4>
        <div class="time-range">
          <span v-for="r in timeRanges" :key="r.value"
            :class="['range-btn', { active: selectedRange === r.value }]"
            @click="switchRange(r.value)">{{ r.label }}</span>
        </div>
      </div>
      <div ref="chartRef" class="chart-container"></div>
      <div class="chart-legend">
        <span class="legend-item"><span class="line-holding"></span>在柜手办</span>
        <span class="legend-item"><span class="line-sold"></span>已出手办</span>
      </div>
    </div>

    <!-- 成分股列表 -->
    <div class="hpi-components">
      <h4>成分股详情</h4>
      <div v-if="loading" class="loading">加载中...</div>
      <div v-else-if="components.length === 0" class="empty">暂无交易数据</div>
      <div v-else class="component-list">
        <div v-for="comp in components" :key="comp.figure_id" class="component-row">
          <div class="comp-name">{{ comp.figure_name || `手办 #${comp.figure_id}` }}</div>
          <div class="comp-price">买入 ¥{{ formatCurrency(comp.first_buy_price) }}</div>
          <div class="comp-current">现价 ¥{{ formatCurrency(comp.current_price) }}</div>
          <div class="comp-return" :class="{ up: comp.return_pct > 0, down: comp.return_pct < 0 }">
            {{ formatPct(comp.return_pct) }}
          </div>
          <div class="comp-weight">{{ (comp.weight * 100).toFixed(1) }}%</div>
          <div class="comp-status">
            <span v-if="comp.is_sold" class="badge sold">已出</span>
            <span v-else class="badge holding">在柜</span>
          </div>
          <div v-if="comp.is_sold" class="comp-sell-label" :class="{ fly: comp.sell_fly, right: comp.sell_right }">
            {{ comp.sell_fly ? '⚡卖飞' : comp.sell_right ? '✅卖对' : '' }}
          </div>
        </div>
      </div>
    </div>
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted, watch, nextTick } from 'vue'
import axios from '../../../../../axios'
import * as echarts from 'echarts'

export default {
  name: 'HPIDetail',
  props: {
    marketData: { type: Object, default: () => ({}) }
  },
  setup(props) {
    const chartRef = ref(null)
    const selectedRange = ref(30)
    const historyData = ref([])
    const components = ref([])
    const loading = ref(false)
    let chartInstance = null

    const timeRanges = [
      { label: '近7天', value: 7 },
      { label: '近30天', value: 30 },
      { label: '近1年', value: 365 },
      { label: '全部', value: 9999 },
    ]

    const indexData = computed(() => {
      return props.marketData?.index || null
    })

    const returnClass = computed(() => {
      const v = indexData.value?.avg_return || 0
      return v > 0 ? 'up' : v < 0 ? 'down' : ''
    })

    const fetchHistory = async (days) => {
      try {
        const res = await axios.get(`/market/hpi-history?days=${days}`)
        historyData.value = res.history || []
        renderChart()
      } catch { /* ignore */ }
    }

    const fetchComponents = async () => {
      loading.value = true
      try {
        const res = await axios.get('/market/hpi-components')
        components.value = [...(res.holding || []), ...(res.sold || [])]
      } catch { /* ignore */ }
      finally { loading.value = false }
    }

    const switchRange = (days) => {
      selectedRange.value = days
      fetchHistory(days)
    }

    const renderChart = () => {
      if (!chartRef.value) return
      nextTick(() => {
        if (!chartInstance) {
          chartInstance = echarts.init(chartRef.value)
        }
        const data = historyData.value
        if (!data.length) return

        const dates = data.map(d => d.date)
        const values = data.map(d => d.value)
        const holding = data.map(d => d.holding_figures)
        const sold = data.map(d => d.sold_figures)

        chartInstance.setOption({
          tooltip: {
            trigger: 'axis',
            formatter: (params) => {
              const p = params[0]
              const idx = p.dataIndex
              const d = data[idx]
              return `<div>
                <div>日期：${d.date}</div>
                <div>HPI：${d.value?.toFixed(2)}</div>
                <div>收益率：${d.avg_return?.toFixed(2)}%</div>
                <div>在柜：${d.holding_figures} | 已出：${d.sold_figures}</div>
              </div>`
            }
          },
          grid: { left: 50, right: 20, top: 20, bottom: 30 },
          xAxis: {
            type: 'category',
            data: dates,
            axisLabel: { fontSize: 10, rotate: 45 }
          },
          yAxis: {
            type: 'value',
            splitLine: { lineStyle: { type: 'dashed', color: '#eee' } }
          },
          series: [
            {
              name: '在柜',
              type: 'line',
              data: values,
              smooth: true,
              symbol: 'none',
              lineStyle: { color: '#52c41a', width: 2 },
              areaStyle: {
                color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
                  { offset: 0, color: 'rgba(82, 196, 26, 0.3)' },
                  { offset: 1, color: 'rgba(82, 196, 26, 0.02)' }
                ])
              }
            },
            {
              name: '已出',
              type: 'line',
              data: values,
              smooth: true,
              symbol: 'none',
              lineStyle: { color: '#d9d9d9', width: 2, type: 'dashed' }
            }
          ]
        })
      })
    }

    const formatNumber = (v) => {
      if (!v && v !== 0) return '0'
      return Number(v).toLocaleString('zh-CN', { minimumFractionDigits: 2, maximumFractionDigits: 2 })
    }
    const formatPct = (v) => {
      if (!v && v !== 0) return '0%'
      return (v > 0 ? '+' : '') + Number(v).toFixed(2) + '%'
    }
    const formatCurrency = (v) => {
      if (!v && v !== 0) return '0'
      return Number(v).toLocaleString('zh-CN', { minimumFractionDigits: 0, maximumFractionDigits: 0 })
    }

    onMounted(() => {
      fetchHistory(selectedRange.value)
      fetchComponents()
    })

    watch(() => props.marketData, () => {
      if (!historyData.value.length) fetchHistory(selectedRange.value)
    })

    return {
      chartRef, selectedRange, timeRanges, historyData, components, loading,
      indexData, returnClass, switchRange, formatNumber, formatPct, formatCurrency
    }
  }
}
</script>

<style scoped>
/* 卡片容器（与参考设计 card 一致） */
.hpi-detail {
  background: #fff; border-radius: 12px;
  box-shadow: 0 1px 4px rgba(0,0,0,0.06);
  margin-bottom: 16px; overflow: hidden;
}
/* 顶部标题行（与参考设计 card-header 一致） */
.hpi-title-row {
  display: flex; align-items: center; justify-content: space-between;
  padding: 16px 20px;
  border-bottom: 1px solid #f0f0f0;
}
.hpi-title-section h3 { margin: 0; font-size: 15px; font-weight: 600; color: #333; }
.hpi-subtitle { font-size: 12px; color: #999; margin-top: 2px; }

/* 卡片 body（与参考设计 card-body 一致） */
.hpi-body { padding: 20px; }

.hpi-header { margin-bottom: 16px; }
.hpi-main-value { display: flex; align-items: baseline; gap: 4px; margin-bottom: 4px; }
.hpi-main-value .value { font-size: 36px; font-weight: 700; color: #333; }
.hpi-main-value .unit { font-size: 16px; color: #666; }
.hpi-avg-return { font-size: 14px; color: #666; }
.hpi-avg-return span { font-weight: 600; }
.hpi-avg-return .up { color: #f5222d; }
.hpi-avg-return .down { color: #52c41a; }

.hpi-stats { display: flex; gap: 10px; margin-bottom: 16px; flex-wrap: wrap; }
.stat-card {
  flex: 1; min-width: 80px; background: #fafafa; border-radius: 8px; padding: 12px; text-align: center; border: 1px solid #f0f0f0;
}
.stat-label { font-size: 12px; color: #999; margin-bottom: 4px; }
.stat-value { font-size: 20px; font-weight: 700; color: #333; }
.stat-value.sold-track { color: #faad14; }
.stat-value.fly { color: #ff4d4f; }
.stat-value.right { color: #52c41a; }

/* 涨平跌药丸样式 */
.hpi-stats-pills { display: flex; gap: 10px; }
.stat-pill {
  padding: 8px 14px; border-radius: 8px; text-align: center;
  border: 1px solid #f0f0f0; min-width: 60px;
}
.stat-pill.up { background: #f6ffed; border-color: #b7eb8f; }
.stat-pill.flat { background: #fafafa; border-color: #f0f0f0; }
.stat-pill.down { background: #fff2f0; border-color: #ffccc7; }
.pill-label { font-size: 11px; color: #999; margin-bottom: 2px; }
.pill-num { font-size: 18px; font-weight: 700; }
.stat-pill.up .pill-num { color: #52c41a; }
.stat-pill.flat .pill-num { color: #8c8c8c; }
.stat-pill.down .pill-num { color: #ff4d4f; }

.hpi-chart-section { margin-bottom: 24px; }
.chart-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px; }
.chart-header h4 { margin: 0; font-size: 14px; color: #333; }
.time-range { display: flex; gap: 4px; }
.range-btn {
  padding: 4px 12px; font-size: 12px; border: 1px solid #d9d9d9; border-radius: 4px;
  cursor: pointer; color: #666; background: #fff;
}
.range-btn.active { background: #1890ff; color: #fff; border-color: #1890ff; }
.chart-container { width: 100%; height: 300px; }
.chart-legend { display: flex; gap: 20px; margin-top: 8px; font-size: 12px; color: #999; }
.legend-item { display: flex; align-items: center; gap: 6px; }
.line-holding { width: 20px; height: 2px; background: #52c41a; display: inline-block; }
.line-sold { width: 20px; height: 2px; background: #d9d9d9; display: inline-block; border-top: 1px dashed #d9d9d9; }

.hpi-components h4 { font-size: 14px; color: #333; margin-bottom: 12px; }
.loading, .empty { text-align: center; padding: 40px; color: #999; font-size: 14px; }
.component-list { display: flex; flex-direction: column; gap: 8px; }
.component-row {
  display: flex; align-items: center; gap: 12px; padding: 10px 12px;
  background: #fafafa; border-radius: 6px; font-size: 13px; flex-wrap: wrap;
}
.comp-name { flex: 1; min-width: 100px; font-weight: 500; color: #333; }
.comp-price, .comp-current { color: #666; font-size: 12px; }
.comp-return { font-weight: 600; min-width: 60px; }
.comp-return.up { color: #f5222d; }
.comp-return.down { color: #52c41a; }
.comp-weight { color: #999; font-size: 12px; min-width: 50px; }
.badge { font-size: 11px; padding: 2px 8px; border-radius: 10px; }
.badge.sold { background: #fff7e6; color: #d48806; }
.badge.holding { background: #f6ffed; color: #389e0d; }
.comp-sell-label { font-size: 12px; font-weight: 600; }
.comp-sell-label.fly { color: #ff4d4f; }
.comp-sell-label.right { color: #52c41a; }
</style>
