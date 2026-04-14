<!--
  ChartSection.vue - 资产分布和收益曲线组件

  功能说明：
  - 展示饼图和折线图
  - 饼图支持多种维度切换：风险状态分布、IP分布、持仓周期分布、仓位分层分布
  - 折线图展示收益走势
  - 饼图支持自动轮播

  组件依赖：
  - 接收 dashboardData 作为 props
  - 使用 ECharts 库绘制图表

  维护提示：
  - 饼图切换通过 switchPieChart 方法处理
  - 图表初始化和数据更新在 mounted 和 watch 中处理
-->
<template>
  <div class="chart-section">
    <div class="chart-item">
      <div class="section-title">{{ pieChartTitle }}</div>
      <div ref="pieChart" class="pie-chart"></div>
      <!-- 饼图切换指示器 -->
      <div class="pie-chart-dots">
        <span 
          class="dot" 
          :class="{ active: currentPieChart === 'risk' }"
          @click="switchPieChart('risk')"
          title="风险状态分布"
        ></span>
        <span 
          class="dot" 
          :class="{ active: currentPieChart === 'manufacturer' }"
          @click="switchPieChart('manufacturer')"
          title="IP分布"
        ></span>
        <span 
          class="dot" 
          :class="{ active: currentPieChart === 'holding_period' }"
          @click="switchPieChart('holding_period')"
          title="持仓周期分布"
        ></span>
        <span 
          class="dot" 
          :class="{ active: currentPieChart === 'tier' }"
          @click="switchPieChart('tier')"
          title="仓位分层分布"
        ></span>
      </div>
    </div>
    <div class="chart-item">
      <div class="section-title">收益曲线(近1月)</div>
      <div ref="profitChart" class="profit-chart"></div>
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted, onUnmounted, nextTick, watch } from 'vue'
import * as echarts from 'echarts'

export default {
  name: 'ChartSection',
  props: {
    dashboardData: {
      type: Object,
      default: () => ({})
    }
  },
  setup(props) {
    const pieChart = ref(null)
    const pieChartInstance = ref(null)
    const profitChart = ref(null)
    const profitChartInstance = ref(null)
    const currentPieChart = ref('risk')
    const pieChartTimer = ref(null)
    const pieChartTypes = ['risk', 'manufacturer', 'holding_period', 'tier']
    
    const pieChartTitle = computed(() => {
      if (currentPieChart.value === 'risk') {
        return '资产风险状态饼图'
      } else if (currentPieChart.value === 'manufacturer') {
        return '资产厂商分布饼图'
      } else if (currentPieChart.value === 'holding_period') {
        return '资产持仓周期饼图'
      } else {
        return '资产仓位分层饼图'
      }
    })
    
    const formatNumber = (num) => {
      return num?.toLocaleString() || '0'
    }
    
    const initPieChart = () => {
      if (!pieChart.value) return
      
      if (pieChartInstance.value) {
        pieChartInstance.value.dispose()
      }
      
      pieChartInstance.value = echarts.init(pieChart.value)
      
      let chartData = []
      
      if (currentPieChart.value === 'risk') {
        chartData = props.dashboardData?.risk_distribution || []
      } else if (currentPieChart.value === 'manufacturer') {
        chartData = props.dashboardData?.manufacturer_distribution || []
      } else if (currentPieChart.value === 'holding_period') {
        chartData = props.dashboardData?.holding_period_distribution || []
      } else {
        chartData = props.dashboardData?.tier_distribution || []
      }
      
      if (chartData.length === 0) {
        pieChartInstance.value.setOption({
          title: {
            text: '暂无数据',
            left: 'center',
            top: 'center',
            textStyle: { color: '#909399', fontSize: 14 }
          }
        })
        return
      }
      
      const option = {
        tooltip: {
          trigger: 'item',
          formatter: function(params) {
            const data = params.data
            return `${data.name}<br/>市值: ¥${formatNumber(data.value)}<br/>数量: ${data.count}个<br/>占比: ${params.percent}%`
          }
        },
        legend: {
          orient: 'vertical',
          left: '10',
          top: 'middle',
          itemWidth: 25,
          itemHeight: 14,
          textStyle: {
            fontSize: 14
          }
        },
        series: [
          {
            type: 'pie',
            radius: ['40%', '65%'],
            center: ['60%', '50%'],
            avoidLabelOverlap: true,
            itemStyle: {
              borderRadius: 0,
              borderColor: '#fff',
              borderWidth: 2
            },
            label: {
              show: true,
              position: 'outside',
              formatter: '{b}\n{d}%',
              fontSize: 12
            },
            emphasis: {
              label: {
                show: true,
                fontSize: 14,
                fontWeight: 'bold'
              }
            },
            labelLine: {
              show: true,
              length: 15,
              length2: 10
            },
            data: chartData
          }
        ]
      }
      
      pieChartInstance.value.setOption(option)
    }
    
    const initProfitChart = () => {
      if (!profitChart.value) return
      
      if (profitChartInstance.value) {
        profitChartInstance.value.dispose()
      }
      
      profitChartInstance.value = echarts.init(profitChart.value)
      
      const data = []
      for (let i = 0; i < 30; i++) {
        data.push([
          new Date(Date.now() - (30 - i) * 86400000).toISOString().substring(0, 10),
          100000 + i * 1000 + Math.random() * 5000
        ])
      }
      
      const xAxisData = data.map(item => item[0])
      const seriesData = data.map(item => item[1])
      
      const option = {
        tooltip: {
          trigger: 'axis',
          formatter: function(params) {
            return `${params[0].name}<br/>收益: ¥${formatNumber(params[0].value)}`
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
            formatter: '¥{value}'
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
      
      profitChartInstance.value.setOption(option)
    }
    
    const switchPieChart = (type) => {
      currentPieChart.value = type
      initPieChart()
      startPieChartAutoPlay()
    }
    
    const startPieChartAutoPlay = () => {
      if (pieChartTimer.value) {
        clearInterval(pieChartTimer.value)
      }
      pieChartTimer.value = setInterval(() => {
        const currentIndex = pieChartTypes.indexOf(currentPieChart.value)
        const nextIndex = (currentIndex + 1) % pieChartTypes.length
        currentPieChart.value = pieChartTypes[nextIndex]
        initPieChart()
      }, 60000)
    }
    
    const stopPieChartAutoPlay = () => {
      if (pieChartTimer.value) {
        clearInterval(pieChartTimer.value)
        pieChartTimer.value = null
      }
    }
    
    onMounted(() => {
      nextTick(() => {
        initPieChart()
        initProfitChart()
        startPieChartAutoPlay()
      })
    })
    
    onUnmounted(() => {
      stopPieChartAutoPlay()
      pieChartInstance.value?.dispose()
      profitChartInstance.value?.dispose()
    })
    
    watch(() => props.dashboardData, () => {
      nextTick(() => {
        initPieChart()
        initProfitChart()
      })
    }, { deep: true })
    
    return {
      pieChart,
      profitChart,
      currentPieChart,
      pieChartTitle,
      switchPieChart
    }
  }
}
</script>

<style scoped>
.chart-section {
  display: flex;
  gap: 20px;
  margin-bottom: 20px;
}

.chart-item {
  flex: 1;
  background-color: white;
  border-radius: 8px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
  padding: 20px;
}

.section-title {
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 18px;
  font-weight: bold;
  margin-bottom: 15px;
  color: #333;
}

.pie-chart,
.profit-chart {
  height: 300px;
  width: 100%;
}

/* 饼图切换指示器 */
.pie-chart-dots {
  display: flex;
  justify-content: center;
  gap: 8px;
  margin-top: 10px;
}

.pie-chart-dots .dot {
  width: 10px;
  height: 10px;
  border-radius: 50%;
  background-color: #dcdfe6;
  cursor: pointer;
  transition: background-color 0.3s;
}

.pie-chart-dots .dot:hover {
  background-color: #c0c4cc;
}

.pie-chart-dots .dot.active {
  background-color: #409eff;
}
</style>