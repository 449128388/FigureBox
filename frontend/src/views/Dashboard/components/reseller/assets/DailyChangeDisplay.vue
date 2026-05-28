<!--
  DailyChangeDisplay.vue - 日涨跌展示组件

  功能说明：
  - 展示日涨跌金额和百分比
  - 支持四种优先级状态：
    1. 昨天（T-1）：显示 "较昨日 +¥X (+Y%)"
    2. 前天（T-2）：显示 "较5月26日 +¥X (+Y%)"
    3. 最近有数据的日期：显示 "较5月20日 +¥X (+Y%)"（超过30天加提示）
    4. 无历史数据：显示 "-- (--%)"
  - 根据涨跌情况显示不同颜色（涨红跌绿）

  组件依赖：
  - 接收 dailyChangeData 作为 props
  - 使用 Element Plus 的 Tooltip 组件

  维护提示：
  - 无数据时显示占位符和引导提示
  - 历史对比时显示对比日期
  - 超过30天未更新显示警告提示
-->
<template>
  <div class="daily-change-display">
    <el-tooltip
      :content="tooltipContent"
      :disabled="!showTooltip"
      placement="top"
    >
      <span
        class="daily-change-value"
        :class="{
          'stock-up': hasData && dailyChange > 0,
          'stock-down': hasData && dailyChange < 0,
          'stock-flat': hasData && dailyChange === 0,
          'no-data': !hasData,
          'stale-warning': showStaleWarning
        }"
      >
        <template v-if="hasData">
          <!-- 显示对比日期前缀 -->
          <template v-if="comparisonDate">
            较{{ formatComparisonDate(comparisonDate) }}
          </template>
          <!-- 涨跌金额 -->
          {{ dailyChange >= 0 ? '+' : '' }}¥{{ formatNumber(Math.abs(dailyChange)) }}
          <!-- 涨跌百分比 -->
          ({{ dailyChange >= 0 ? '+' : '' }}{{ dailyChangePercentage.toFixed(2) }}%)
        </template>
        <template v-else>
          -- (--%)
        </template>
      </span>
    </el-tooltip>
  </div>
</template>

<script>
import { computed } from 'vue'

export default {
  name: 'DailyChangeDisplay',
  props: {
    dailyChange: {
      type: Number,
      default: 0
    },
    dailyChangePercentage: {
      type: Number,
      default: 0
    },
    hasDailyChange: {
      type: Boolean,
      default: false
    },
    comparisonDate: {
      type: String,
      default: null
    },
    comparisonType: {
      type: String,
      default: null
    },
    daysSinceLastUpdate: {
      type: Number,
      default: null
    },
    showStaleWarning: {
      type: Boolean,
      default: false
    }
  },
  setup(props) {
    const hasData = computed(() => props.hasDailyChange)

    const showTooltip = computed(() => {
      // 无数据时显示提示
      if (!props.hasDailyChange) return true
      // 超过30天未更新时显示提示
      if (props.showStaleWarning) return true
      return false
    })

    const tooltipContent = computed(() => {
      if (!props.hasDailyChange) {
        return '暂无昨日行情数据，点击【刷新资产】后将开始统计日涨跌'
      }
      if (props.showStaleWarning && props.daysSinceLastUpdate) {
        return `已${props.daysSinceLastUpdate}天未更新行情`
      }
      return ''
    })

    const formatNumber = (num) => {
      if (num === undefined || num === null) return '0'
      return num.toLocaleString('zh-CN', { minimumFractionDigits: 0, maximumFractionDigits: 2 })
    }

    const formatComparisonDate = (dateStr) => {
      if (!dateStr) return ''
      const date = new Date(dateStr)
      const month = date.getMonth() + 1
      const day = date.getDate()
      
      // 根据对比类型决定显示格式
      if (props.comparisonType === 'yesterday') {
        return '昨日'
      }
      // T-2或更早日期显示具体日期
      return `${month}月${day}日`
    }

    return {
      hasData,
      showTooltip,
      tooltipContent,
      formatNumber,
      formatComparisonDate
    }
  }
}
</script>

<style scoped>
.daily-change-display {
  display: inline-block;
}

.daily-change-value {
  font-size: 24px;
  font-weight: bold;
  cursor: default;
}

/* 中国股市颜色标准：涨红跌绿 */
.daily-change-value.stock-up {
  color: #F44336; /* 红色 - 上涨 */
}

.daily-change-value.stock-down {
  color: #4CAF50; /* 绿色 - 下跌 */
}

.daily-change-value.stock-flat {
  color: #909399; /* 灰色 - 持平 */
}

.daily-change-value.no-data {
  color: #909399; /* 灰色 - 无数据 */
  cursor: help;
}

/* 过期警告样式 */
.daily-change-value.stale-warning {
  text-decoration: underline;
  text-decoration-style: dashed;
  text-decoration-color: #FF9800;
}
</style>
