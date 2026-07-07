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
    <!-- HPI 头部：指数值 + 累计收益 -->
    <div class="hpi-header">
      <div class="hpi-main">
        <span class="hpi-value">{{ formatNumber(indexData?.index_value) }}</span>
        <span :class="['hpi-change', returnClass]">
          <span class="hpi-arrow">{{ changeArrow }}</span>
          <span class="hpi-change-points">+{{ formatNumber(Math.abs(indexData?.index_value - 1000)) }}</span>
          <span class="hpi-change-pct">({{ formatPct(indexData?.avg_return) }})</span>
        </span>
      </div>
    </div>

    <!-- 基准信息 + 生涯累计收益（同行） -->
    <div class="hpi-base-info" v-if="indexData?.first_buy_date">
      基准: <span>1,000</span> (首次买入日: {{ formatDate(indexData?.first_buy_date) }}) &nbsp;|&nbsp;
      生涯累计收益率: <strong :class="returnClass">{{ formatPct(indexData?.avg_return) }}</strong>
    </div>

    <!-- 统计卡片 -->
    <div class="hpi-stats">
      <div class="stat-card">
        <div class="stat-label">累计交易</div>
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
    </div>

      <!-- 投资复盘 -->
      <InvestmentReview :market-data="marketData" />

      <!-- 板块涨幅排行 -->
      <SectorRanking :market-data="marketData" />
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted, watch, nextTick } from 'vue'
import axios from '../../../../../axios'
import * as echarts from 'echarts'

import InvestmentReview from './InvestmentReview.vue'
import SectorRanking from './SectorRanking.vue'

export default {
  name: 'HPIDetail',
  components: { InvestmentReview, SectorRanking },
  props: {
    marketData: { type: Object, default: () => ({}) }
  },
  setup(props) {
    const chartRef = ref(null)
    const selectedRange = ref(30)
    const historyData = ref([])
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

    const changeArrow = computed(() => {
      const v = indexData.value?.avg_return || 0
      if (v > 0) return '↑'
      if (v < 0) return '↓'
      return '—'
    })

    const fetchHistory = async (days) => {
      try {
        const res = await axios.get(`/market/hpi-history?days=${days}`)
        historyData.value = res.history || []
        renderChart()
      } catch { /* ignore */ }
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
        // 本地日期工具（避免 toISOString 的 UTC 偏移）
        const fmtLocal = (d) => {
          const y = d.getFullYear()
          const m = String(d.getMonth() + 1).padStart(2, '0')
          const day = String(d.getDate()).padStart(2, '0')
          return `${y}-${m}-${day}`
        }
        const parseLocal = (s) => {
          const [y, m, d] = s.split('-').map(Number)
          return new Date(y, m - 1, d)
        }
        const data = historyData.value

        // 按时间控件（selectedRange）补齐中间缺失的日期，保证 X 轴连续显示
        const dates = []
        const inCabinet = []
        const sold = []
        const dataMap = {}
        for (const d of data) {
          dataMap[d.date] = d
        }
        const range = selectedRange.value
        const today = new Date()
        today.setHours(0, 0, 0, 0)
        let startDate, endDate
        if (range >= 9999) {
          // 全部：起始 = data 最小日期，结束 = today（始终包含今天）
          endDate = today
          let earliest = today
          for (const key in dataMap) {
            const dt = parseLocal(key)
            if (dt < earliest) earliest = dt
          }
          startDate = earliest
        } else {
          // 近7/30/365：起始 = endDate - (N-1)，结束 = today（也始终包含今天）
          endDate = today
          startDate = new Date(today)
          startDate.setDate(startDate.getDate() - (range - 1))
        }
        // 遍历 startDate -> endDate 之间的所有日期（用本地日期格式化）
        const totalDays = Math.floor((endDate - startDate) / 86400000) + 1
        for (let i = 0; i < totalDays; i++) {
          const d = new Date(startDate)
          d.setDate(d.getDate() + i)
          const ds = fmtLocal(d)
          dates.push(ds)
          const hit = dataMap[ds]
          inCabinet.push(hit ? (hit.in_cabinet_value || 0) : 0)
          sold.push(hit ? (hit.sold_value || 0) : 0)
        }

        chartInstance.setOption({
          tooltip: {
            trigger: 'axis',
            formatter: (params) => {
              const idx = params[0].dataIndex
              const date = dates[idx]
              const ic = Math.round(inCabinet[idx] || 0)
              const sl = Math.round(sold[idx] || 0)
              return `<div>
                <div>${date}</div>
                <div><span style="display:inline-block;width:8px;height:8px;background:#52c41a;border-radius:50%;margin-right:4px;"></span>在柜指数 <strong>${ic}</strong></div>
                <div><span style="display:inline-block;width:8px;height:8px;background:#bfbfbf;border-radius:50%;margin-right:4px;"></span>已出指数 <strong>${sl}</strong></div>
              </div>`
            }
          },
          legend: {
            bottom: 0,
            data: [
              { name: '在柜指数', icon: 'circle', itemStyle: { color: '#52c41a' } },
              { name: '已出指数', icon: 'circle', itemStyle: { color: '#bfbfbf' } }
            ],
            textStyle: { fontSize: 12, color: '#666' }
          },
          grid: { left: 60, right: 50, top: 20, bottom: 60, containLabel: true },
          xAxis: {
            type: 'category',
            data: dates,
            boundaryGap: false,
            axisLabel: {
              fontSize: 10,
              rotate: 45,
              margin: 14,
              interval: dates.length > 60 ? Math.floor(dates.length / 30) : 0
            }
          },
          yAxis: {
            type: 'value',
            min: 0,
            splitLine: { lineStyle: { type: 'dashed', color: '#eee' } }
          },
          series: [
            {
              name: '在柜指数',
              type: 'line',
              data: inCabinet,
              smooth: true,
              symbol: 'none',
              lineStyle: { color: '#52c41a', width: 2 }
            },
            {
              name: '已出指数',
              type: 'line',
              data: sold,
              smooth: true,
              symbol: 'none',
              lineStyle: { color: '#bfbfbf', width: 2, type: 'dashed' }
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
    const formatDate = (v) => {
      if (!v) return ''
      // 处理 "2023-12-25" 或 ISO 格式日期
      const d = new Date(v)
      if (isNaN(d.getTime())) return String(v).substring(0, 10)
      return d.toISOString().substring(0, 10)
    }

    onMounted(() => {
      fetchHistory(selectedRange.value)
    })

    watch(() => props.marketData, () => {
      if (!historyData.value.length) fetchHistory(selectedRange.value)
    })

    return {
      chartRef, selectedRange, timeRanges, historyData,
      indexData, returnClass, changeArrow, switchRange, formatNumber, formatPct, formatCurrency, formatDate
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

.hpi-header { margin-bottom: 12px; }
.hpi-main { display: flex; align-items: baseline; gap: 16px; }
.hpi-value { font-size: 48px; font-weight: 700; color: #333; line-height: 1; }
.hpi-change { font-size: 16px; font-weight: 600; display: inline-flex; align-items: baseline; gap: 4px; }
.hpi-change.up { color: #f5222d; }
.hpi-change.down { color: #52c41a; }
.hpi-arrow { font-size: 18px; }
.hpi-change-points { font-size: 18px; font-weight: 700; }
.hpi-change-pct { font-size: 14px; font-weight: 500; opacity: 0.85; }

.hpi-base-info { font-size: 13px; color: #999; margin-bottom: 16px; }
.hpi-base-info span { color: #666; }
.hpi-base-info strong { font-weight: 600; }
.hpi-base-info strong.up { color: #f5222d; }
.hpi-base-info strong.down { color: #52c41a; }

.hpi-stats { display: flex; gap: 10px; margin-bottom: 16px; flex-wrap: wrap; }
.stat-card {
  flex: 1; min-width: 80px; background: #fafafa; border-radius: 8px; padding: 12px; text-align: center; border: 1px solid #f0f0f0;
}
.stat-label { font-size: 12px; color: #999; margin-bottom: 4px; }
.stat-value { font-size: 20px; font-weight: 700; color: #333; }
.stat-value.sold-track { color: #faad14; }
.stat-value.fly { color: #52c41a; }
.stat-value.right { color: #f5222d; }

/* 涨平跌药丸样式 */
.hpi-stats-pills { display: flex; gap: 10px; }
.stat-pill {
  padding: 8px 14px; border-radius: 8px; text-align: center;
  border: 1px solid #f0f0f0; min-width: 60px;
}
.stat-pill.up { background: #fff2f0; border-color: #ffccc7; }
.stat-pill.flat { background: #fafafa; border-color: #f0f0f0; }
.stat-pill.down { background: #f6ffed; border-color: #b7eb8f; }
.pill-label { font-size: 11px; color: #999; margin-bottom: 2px; }
.pill-num { font-size: 18px; font-weight: 700; }
.stat-pill.up .pill-num { color: #f5222d; }
.stat-pill.flat .pill-num { color: #8c8c8c; }
.stat-pill.down .pill-num { color: #52c41a; }

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

</style>
