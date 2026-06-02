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
      <!-- 饼图空数据提示 -->
      <div v-if="!hasPieData" class="empty-chart">
        <el-empty description="暂无数据" />
      </div>
      <div v-else ref="pieChart" class="pie-chart"></div>
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
      <!-- 收益曲线空数据提示 -->
      <div v-if="!hasProfitData" class="empty-chart">
        <el-empty description="暂无数据" />
      </div>
      <div v-else ref="profitChart" class="profit-chart"></div>
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

    // 判断饼图是否有数据
    const hasPieData = computed(() => {
      if (currentPieChart.value === 'risk') {
        return (props.dashboardData?.risk_distribution || []).length > 0
      } else if (currentPieChart.value === 'manufacturer') {
        return (props.dashboardData?.manufacturer_distribution || []).length > 0
      } else if (currentPieChart.value === 'holding_period') {
        return (props.dashboardData?.holding_period_distribution || []).length > 0
      } else {
        return (props.dashboardData?.tier_distribution || []).length > 0
      }
    })

    // 判断收益曲线是否有数据
    const hasProfitData = computed(() => {
      return (props.dashboardData?.kline_data || []).length > 0
    })
    
    const formatNumber = (num) => {
      return num?.toLocaleString() || '0'
    }
    
    const initPieChart = () => {
      // 如果DOM元素不存在，延迟重试
      if (!pieChart.value) {
        setTimeout(() => initPieChart(), 100)
        return
      }
      
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
      // 如果DOM元素不存在，延迟重试
      if (!profitChart.value) {
        setTimeout(() => initProfitChart(), 100)
        return
      }

      if (profitChartInstance.value) {
        profitChartInstance.value.dispose()
      }

      profitChartInstance.value = echarts.init(profitChart.value)

      // 使用后端返回的收益曲线数据（每日收益 = 当日总市值 - 当日总成本）
      const klineData = props.dashboardData?.kline_data || []

      // 边界情况处理：全新用户/空仓 - 显示y=0直线
      if (klineData.length === 0) {
        const today = new Date().toISOString().split('T')[0]
        const emptyData = [
          { date: today, profit: 0 }
        ]
        renderProfitChart(emptyData, true)
        return
      }

      renderProfitChart(klineData, false)
    }

    // 渲染收益曲线图表
    const renderProfitChart = (data, isEmptyData) => {
      const xAxisData = data.map(item => item.date)
      const seriesData = data.map(item => item.profit || item.value || 0)

      // 计算数据范围，用于确定视觉映射
      const minProfit = Math.min(...seriesData)
      const maxProfit = Math.max(...seriesData)

      // 判断是否有正负混合数据
      const hasPositive = maxProfit > 0
      const hasNegative = minProfit < 0

      const option = {
        tooltip: {
          trigger: 'item',
          formatter: function(params) {
            const value = params.value
            const color = value >= 0 ? '#FF4D4F' : '#52C41A'
            return `${params.name}<br/>收益: <span style="color:${color}">¥${formatNumber(value)}</span>`
          }
        },
        grid: {
          left: '3%',
          right: '8%',
          bottom: '3%',
          top: '10%',
          containLabel: true
        },
        xAxis: {
          type: 'category',
          data: xAxisData,
          boundaryGap: false,
          axisLine: { lineStyle: { color: '#ccc' } },
          axisLabel: {
            color: '#666',
            interval: 'auto',
            rotate: 0,
            formatter: function(value) {
              // 确保日期格式正确显示
              return value
            }
          }
        },
        yAxis: {
          type: 'value',
          axisLabel: {
            formatter: '¥{value}',
            color: '#666'
          },
          splitLine: {
            lineStyle: {
              color: '#f0f0f0'
            }
          }
        },
        series: [
          {
            name: '收益',
            data: seriesData,
            type: 'line',
            smooth: true,
            // 零轴参考线 - 使用 markLine 强制显示在 Y=0 位置
            markLine: {
              symbol: 'none',
              silent: true,
              animation: false,
              data: [
                {
                  yAxis: 0,
                  lineStyle: {
                    color: '#999',
                    type: 'dashed',
                    width: 1
                  },
                  label: {
                    show: false
                  }
                }
              ]
            },
            // 使用 itemStyle 实现根据数据点正负值显示不同颜色
            itemStyle: {
              color: function(params) {
                return params.value >= 0 ? '#FF4D4F' : '#52C41A'
              }
            },
            lineStyle: {
              width: 2,
              // 使用渐变色实现线条根据正负值显示不同颜色
              color: {
                type: 'linear',
                x: 0,
                y: 0,
                x2: 0,
                y2: 1,
                colorStops: [
                  { offset: 0, color: '#FF4D4F' },  // 正值区域：红色
                  { offset: 0.5, color: '#FF4D4F' }, // 中间过渡
                  { offset: 0.5, color: '#52C41A' }, // 零轴位置切换颜色
                  { offset: 1, color: '#52C41A' }    // 负值区域：绿色
                ]
              }
            },
            // 区域填充：根据正负值显示不同颜色
            areaStyle: {
              color: {
                type: 'linear',
                x: 0,
                y: 0,
                x2: 0,
                y2: 1,
                colorStops: [
                  { offset: 0, color: '#FFE6E6' },      // 正值区域：浅红色
                  { offset: 0.5, color: 'rgba(255, 230, 230, 0.1)' },
                  { offset: 0.5, color: 'rgba(230, 247, 230, 0.1)' },
                  { offset: 1, color: '#E6F7E6' }       // 负值区域：浅绿色
                ]
              }
            },
            symbol: 'circle',
            symbolSize: 4
          }
        ]
      }

      // 如果是空数据（全新用户），显示y=0直线
      if (isEmptyData) {
        option.visualMap = null
        option.series[0].lineStyle = {
          color: '#999',
          width: 1,
          type: 'dashed'
        }
        option.series[0].areaStyle = null
        option.title = {
          text: '暂无收益数据',
          left: 'center',
          top: 'center',
          textStyle: { color: '#909399', fontSize: 14 }
        }
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
      switchPieChart,
      hasPieData,
      hasProfitData
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

/* 空数据图表样式 */
.empty-chart {
  height: 300px;
  display: flex;
  align-items: center;
  justify-content: center;
}
</style>