<!--
  AssetAnalysis.vue - 资产分析组件

  功能说明：
  - 显示手办的平均成本分析
  - 显示盈亏分析（已实现盈亏、未实现盈亏）
  - 支持股票式补仓的成本计算展示
  - 显示投资回报率等关键指标

  组件依赖：
  - Element Plus 的 el-card、el-statistic 组件
  - 接收 averageCost 和 profitAnalysis 作为 props

  维护提示：
  - 盈亏为正显示绿色，为负显示红色
  - 数据为空时显示占位符
-->
<template>
  <div class="asset-analysis">
    <h3 class="section-title">资产分析</h3>

    <!-- 平均成本卡片 -->
    <el-card class="analysis-card" v-if="averageCost">
      <template #header>
        <div class="card-header">
          <span>成本分析</span>
        </div>
      </template>
      <div class="stats-grid">
        <div class="stat-item">
          <div class="stat-label">平均成本</div>
          <div class="stat-value">¥{{ formatPrice(averageCost.average_cost) }}</div>
        </div>
        <div class="stat-item">
          <div class="stat-label">总投入</div>
          <div class="stat-value">¥{{ formatPrice(averageCost.total_cost) }}</div>
        </div>
        <div class="stat-item">
          <div class="stat-label">总数量</div>
          <div class="stat-value">{{ averageCost.total_quantity }} 个</div>
        </div>
        <div class="stat-item">
          <div class="stat-label">当前持仓</div>
          <div class="stat-value">{{ averageCost.total_remaining }} 个</div>
        </div>
      </div>
    </el-card>

    <!-- 盈亏分析卡片 -->
    <el-card class="analysis-card" v-if="profitAnalysis">
      <template #header>
        <div class="card-header">
          <span>盈亏分析</span>
        </div>
      </template>
      <div class="stats-grid">
        <div class="stat-item">
          <div class="stat-label">已实现盈亏</div>
          <div class="stat-value" :class="getProfitClass(profitAnalysis.realized_profit)">
            {{ formatProfit(profitAnalysis.realized_profit) }}
          </div>
        </div>
        <div class="stat-item" v-if="profitAnalysis.unrealized_profit !== undefined">
          <div class="stat-label">未实现盈亏</div>
          <div class="stat-value" :class="getProfitClass(profitAnalysis.unrealized_profit)">
            {{ formatProfit(profitAnalysis.unrealized_profit) }}
          </div>
        </div>
        <div class="stat-item" v-if="profitAnalysis.total_profit !== undefined">
          <div class="stat-label">总盈亏</div>
          <div class="stat-value" :class="getProfitClass(profitAnalysis.total_profit)">
            {{ formatProfit(profitAnalysis.total_profit) }}
          </div>
        </div>
        <div class="stat-item">
          <div class="stat-label">卖出收入</div>
          <div class="stat-value">¥{{ formatPrice(profitAnalysis.total_sell_revenue) }}</div>
        </div>
      </div>

      <!-- 当前市场价格 -->
      <div class="market-price-section" v-if="profitAnalysis.current_market_price">
        <div class="market-price-label">当前市场价格</div>
        <div class="market-price-value">¥{{ formatPrice(profitAnalysis.current_market_price) }}</div>
      </div>
    </el-card>

    <!-- 空状态 -->
    <el-empty v-if="!averageCost && !profitAnalysis" description="暂无资产分析数据" />
  </div>
</template>

<script>
export default {
  name: 'AssetAnalysis',
  props: {
    averageCost: {
      type: Object,
      default: null
    },
    profitAnalysis: {
      type: Object,
      default: null
    }
  },
  setup() {
    // 格式化价格
    const formatPrice = (price) => {
      if (price === null || price === undefined) return '0.00'
      return Number(price).toFixed(2)
    }

    // 格式化盈亏（带正负号）
    const formatProfit = (profit) => {
      if (profit === null || profit === undefined) return '¥0.00'
      const sign = profit >= 0 ? '+' : ''
      return `${sign}¥${Number(profit).toFixed(2)}`
    }

    // 获取盈亏样式类
    const getProfitClass = (profit) => {
      if (profit === null || profit === undefined) return ''
      return profit >= 0 ? 'profit-positive' : 'profit-negative'
    }

    return {
      formatPrice,
      formatProfit,
      getProfitClass
    }
  }
}
</script>

<style scoped>
.asset-analysis {
  margin-top: 20px;
}

.section-title {
  margin: 0 0 15px 0;
  font-size: 16px;
  font-weight: 600;
  color: #333;
}

.analysis-card {
  margin-bottom: 15px;
}

.card-header {
  font-weight: 600;
  color: #303133;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
  gap: 20px;
}

.stat-item {
  text-align: center;
  padding: 15px;
  background-color: #f5f7fa;
  border-radius: 4px;
}

.stat-label {
  font-size: 12px;
  color: #909399;
  margin-bottom: 8px;
}

.stat-value {
  font-size: 18px;
  font-weight: 600;
  color: #303133;
}

.stat-value.profit-positive {
  color: #67c23a;
}

.stat-value.profit-negative {
  color: #f56c6c;
}

.market-price-section {
  margin-top: 20px;
  padding-top: 20px;
  border-top: 1px solid #ebeef5;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.market-price-label {
  font-size: 14px;
  color: #606266;
}

.market-price-value {
  font-size: 20px;
  font-weight: 600;
  color: #409eff;
}
</style>
