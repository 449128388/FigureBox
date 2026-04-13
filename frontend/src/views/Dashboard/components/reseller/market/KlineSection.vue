<template>
  <div class="kline-section">
    <div class="kline-header">
      <div class="kline-tabs">
        <el-button 
          v-for="tab in klineTabs" 
          :key="tab.value"
          :class="{ active: selectedKlineTab === tab.value }"
          @click="selectedKlineTab = tab.value"
        >
          {{ tab.label }}
        </el-button>
      </div>
    </div>
    <div class="kline-chart-container">
      <div ref="marketKlineChart" class="kline-chart"></div>
      <div class="kline-indicators">
        <div class="indicator-item">
          <span class="indicator-label">MACD:</span>
          <span class="indicator-value">{{ marketData?.kline?.macd || '金叉' }}</span>
        </div>
        <div class="indicator-item">
          <span class="indicator-label">RSI:</span>
          <span class="indicator-value" :class="{ warning: marketData?.kline?.rsi > 60 }">
            {{ marketData?.kline?.rsi || 68 }}({{ marketData?.kline?.rsi > 70 ? '超买区' : marketData?.kline?.rsi < 30 ? '超卖区' : '正常区' }})
          </span>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, onMounted, onUnmounted, nextTick, watch } from 'vue'
import * as echarts from 'echarts'

export default {
  name: 'KlineSection',
  props: {
    marketData: {
      type: Object,
      default: () => ({})
    }
  },
  setup(props) {
    const marketKlineChart = ref(null)
    const marketChartInstance = ref(null)
    const selectedKlineTab = ref('day')
    
    const klineTabs = [
      { label: '分时', value: 'minute' },
      { label: '日K', value: 'day' },
      { label: '周K', value: 'week' },
      { label: '月K', value: 'month' }
    ]
    
    const initMarketKlineChart = () => {
      if (!marketKlineChart.value) return
      
      if (marketChartInstance.value) {
        marketChartInstance.value.dispose()
      }
      
      marketChartInstance.value = echarts.init(marketKlineChart.value)
      
      const data = []
      for (let i = 0; i < 30; i++) {
        data.push([
          new Date(Date.now() - (30 - i) * 86400000).toISOString().substring(0, 10),
          2800 + i * 5 + Math.random() * 100
        ])
      }
      
      const xAxisData = data.map(item => item[0])
      const seriesData = data.map(item => item[1])
      
      const option = {
        tooltip: {
          trigger: 'axis',
          formatter: function(params) {
            return `${params[0].name}<br/>指数: ${params[0].value}`
          }
        },
        xAxis: {
          type: 'category',
          data: xAxisData,
          boundaryGap: false
        },
        yAxis: {
          type: 'value',
          axisLabel: {
            formatter: '{value}'
          }
        },
        series: [
          {
            data: seriesData,
            type: 'line',
            smooth: true,
            areaStyle: {
              color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
                { offset: 0, color: 'rgba(76, 175, 80, 0.5)' },
                { offset: 1, color: 'rgba(76, 175, 80, 0.1)' }
              ])
            },
            lineStyle: {
              color: '#4CAF50',
              width: 2
            },
            symbol: 'circle',
            symbolSize: 4
          }
        ]
      }
      
      marketChartInstance.value.setOption(option)
      
      const handleResize = () => {
        marketChartInstance.value?.resize()
      }
      
      window.addEventListener('resize', handleResize)
      
      onUnmounted(() => {
        window.removeEventListener('resize', handleResize)
        marketChartInstance.value?.dispose()
      })
    }
    
    onMounted(() => {
      nextTick(() => {
        initMarketKlineChart()
      })
    })
    
    watch(() => props.marketData, () => {
      nextTick(() => {
        initMarketKlineChart()
      })
    }, { deep: true })
    
    return {
      marketKlineChart,
      selectedKlineTab,
      klineTabs
    }
  }
}
</script>

<style scoped>
/* K线图 */
.kline-section {
  margin-bottom: 30px;
}

.kline-header {
  margin-bottom: 15px;
}

.kline-tabs {
  display: flex;
  gap: 10px;
}

.kline-tabs .el-button.active {
  background-color: #4CAF50;
  color: white;
}

.kline-chart-container {
  position: relative;
  background-color: #f5f5f5;
  border-radius: 8px;
  padding: 20px;
}

.kline-chart {
  width: 100%;
  height: 300px;
  margin-bottom: 15px;
  background: linear-gradient(to bottom, #f0f9ff 0%, #ffffff 100%);
  border-radius: 4px;
  overflow: hidden;
}

.kline-indicators {
  display: flex;
  gap: 30px;
  margin-top: 15px;
  padding-top: 15px;
  border-top: 1px solid #e0e0e0;
}

.indicator-item {
  display: flex;
  align-items: center;
  gap: 10px;
}

.indicator-label {
  font-size: 14px;
  color: #666;
}

.indicator-value {
  font-size: 14px;
  font-weight: bold;
  color: #333;
}

.indicator-value.warning {
  color: #E6A23C;
}
</style>