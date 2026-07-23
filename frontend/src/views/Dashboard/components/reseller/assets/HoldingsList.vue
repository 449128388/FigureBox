<!--
  HoldingsList.vue - 持仓列表组件

  功能说明：
  - 展示手办持仓列表，按盈亏排序
  - 支持手办名字模糊搜索和手办状态筛选
  - 提供手办卡片展示，包含基本信息、收益情况
  - 支持点击手办名字跳转到详情页
  - 支持修改市场价功能

  组件依赖：
  - 接收 dashboardData 作为 props
  - 触发 edit-price 事件给父组件

  维护提示：
  - 风险状态通过 statusTable 提供帮助信息
  - 筛选功能通过 showFilter 控制显示
  - 手办卡片点击事件通过 $router.push 跳转
-->
<template>
  <div class="holdings-section">
    <div class="section-header">
      <div class="section-title">
        📊 持仓列表 (按盈亏排序)
        <el-tooltip
          placement="top"
          :show-after="200"
          effect="light"
        >
          <template #content>
            <div v-html="statusTable"></div>
          </template>
          <el-button size="small" type="info" class="status-help-button">
            ?
          </el-button>
        </el-tooltip>
      </div>
      <el-button @click="showFilter = !showFilter">
        筛选 ▼
      </el-button>
    </div>

    <!-- 筛选条件 -->
    <div v-if="showFilter" class="filter-section">
      <!-- 手办名字搜索和状态筛选同一行 -->
      <div class="filter-row combined-filter-row">
        <el-input
          v-model="searchKeyword"
          placeholder="搜索手办名字"
          prefix-icon="Search"
          class="search-input"
          clearable
          @keyup.enter="handleSearch"
        />
        <div class="status-filter-buttons">
          <el-button
            v-for="filter in statusFilters"
            :key="filter.value"
            :type="selectedStatusFilter === filter.value ? 'primary' : 'default'"
            size="small"
            @click="selectedStatusFilter = filter.value"
          >
            {{ filter.label }}
          </el-button>
        </div>
      </div>
      <!-- 查询和重置按钮 -->
      <div class="filter-row action-row">
        <el-button type="primary" @click="handleSearch" :loading="loading">
          <el-icon><Search /></el-icon>
          查询
        </el-button>
        <el-button @click="handleReset">
          <el-icon><RefreshRight /></el-icon>
          重置
        </el-button>
      </div>
    </div>

    <!-- 持仓卡片 -->
    <div class="holdings-cards">
      <!-- 空数据提示 -->
      <div v-if="paginatedData.length === 0" class="empty-holdings">
        <el-empty :description="emptyDescription" />
      </div>
      <div
        v-for="(item, index) in paginatedData"
        :key="item.figure_id"
        class="holding-card"
        :class="getStatusClass(item.status)"
        @long-press="handleLongPress(item)"
      >
        <div class="card-image" v-if="item.image">
          <img :src="item.image" :alt="item.figure_name" />
        </div>
        <div class="card-content">
          <div class="card-header">
            <div class="card-title">
              <router-link :to="`/figures/${item.figure_id}`" class="figure-name-link">
                {{ item.figure_name }}
              </router-link>
            </div>
            <el-dropdown>
              <span class="el-dropdown-link">
                操作 ▼
              </span>
              <template #dropdown>
                <el-dropdown-menu>
                  <el-dropdown-item @click="$emit('sell-asset', item)">卖出</el-dropdown-item>
                  <el-dropdown-item @click="$emit('add-position', item)">补仓</el-dropdown-item>
                  <el-dropdown-item @click="$emit('edit-price', item)">修改市场价</el-dropdown-item>
                </el-dropdown-menu>
              </template>
            </el-dropdown>
          </div>
          <div class="card-body">
            <div class="card-info">
              <div class="info-item">
                <span class="label">库存:</span>
                <span class="value">{{ item.stock || 1 }}体</span>
              </div>
              <div class="info-item">
                <span class="label">状态:</span>
                <span class="value">{{ item.status || '收藏中' }}</span>
              </div>
            </div>
            <div class="card-divider"></div>
            <div class="card-prices">
              <div class="price-item">
                <span class="label">成本:</span>
                <span class="value">¥{{ formatNumber(item.cost_price) }}</span>
              </div>
              <div class="price-item">
                <span class="label">市场价:</span>
                <span class="value">¥{{ formatNumber(item.current_price) }}</span>
              </div>
              <div class="price-item">
                <span class="label">盈亏:</span>
                <span class="value" :class="{ positive: item.profit >= 0, negative: item.profit < 0 }">
                  {{ item.profit >= 0 ? '+' : '' }}¥{{ formatNumber(Math.abs(item.profit)) }} ({{ item.profit_percentage >= 0 ? '+' : '' }}{{ item.profit_percentage.toFixed(0) }}%)
                </span>
              </div>
            </div>
            <div class="card-footer">
              <div class="footer-item" v-if="item.purchase_date">
                <span class="label">入手时间:</span>
                <span class="value">{{ item.purchase_date }}</span>
              </div>
              <div class="footer-item" v-if="item.holding_days">
                <span class="label">持有:</span>
                <span class="value">{{ item.holding_days }}天</span>
              </div>
              <div class="footer-item" v-if="item.market_share">
                <span class="label">市值占比:</span>
                <span class="value">{{ item.market_share }}%</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 分页组件 -->
    <div class="pagination-wrapper" v-if="total > 0">
      <span class="pagination-info">{{ rangeText }}</span>
      <el-pagination
        v-model:current-page="page"
        v-model:page-size="pageSize"
        :page-sizes="pageSizeOptions"
        :total="total"
        layout="sizes, prev, pager, next, jumper"
        background
        @size-change="handleSizeChange"
        @current-change="handlePageChange"
      />
    </div>
  </div>
</template>

<script>
import { ref, computed, watch } from 'vue'
import { Search, RefreshRight } from '@element-plus/icons-vue'
import axios from '../../../../../axios'
import { useHoldingsPagination } from '../../../composables/useHoldingsPagination'

export default {
  name: 'HoldingsList',
  components: {
    Search,
    RefreshRight
  },
  props: {
    dashboardData: {
      type: Object,
      default: () => ({})
    }
  },
  emits: ['sell-asset', 'add-position', 'edit-price'],
  setup(props) {
    const showFilter = ref(false)
    const searchKeyword = ref('')
    const selectedStatusFilter = ref('all')
    const loading = ref(false)
    const filteredHoldingsData = ref([])
    const hasSearched = ref(false)

    // 筛选后的持仓列表（总数据源）
    const holdingsSource = computed(() => {
      if (hasSearched.value) {
        return filteredHoldingsData.value
      }
      return props.dashboardData?.holdings || []
    })

    // 使用分页业务逻辑
    const {
      page,
      pageSize,
      pageSizeOptions,
      total,
      totalPages,
      paginatedData,
      rangeText,
      handlePageChange,
      handleSizeChange,
      resetPage
    } = useHoldingsPagination(holdingsSource)

    // 手办状态筛选选项 - 使用实际风险状态
    const statusFilters = [
      { label: '全部', value: 'all' },
      { label: '🚀 暴涨', value: '🚀 暴涨' },
      { label: '📈 上涨', value: '📈 上涨' },
      { label: '➖ 横盘', value: '➖ 横盘' },
      { label: '📉 告警', value: '📉 告警' },
      { label: '🟢 破位', value: '🟢 破位' },
      { label: '💀 退市', value: '💀 退市' }
    ]

    const statusTable = ref(`
<table style="border-collapse: collapse; width: 100%; font-size: 12px;">
  <tr style="background-color: #f5f7fa; font-weight: bold;">
    <th style="border: 1px solid #dcdfe6; padding: 4px 8px; text-align: left;">状态标签</th>
    <th style="border: 1px solid #dcdfe6; padding: 4px 8px; text-align: left;">触发条件</th>
    <th style="border: 1px solid #dcdfe6; padding: 4px 8px; text-align: left;">颜色</th>
    <th style="border: 1px solid #dcdfe6; padding: 4px 8px; text-align: left;">操作建议</th>
  </tr>
  <tr>
    <td style="border: 1px solid #dcdfe6; padding: 4px 8px;">🚀 暴涨</td>
    <td style="border: 1px solid #dcdfe6; padding: 4px 8px;">单月涨幅 ≥ +15%</td>
    <td style="border: 1px solid #dcdfe6; padding: 4px 8px; color: #F44336;">红色</td>
    <td style="border: 1px solid #dcdfe6; padding: 4px 8px;">考虑止盈或分批减仓</td>
  </tr>
  <tr>
    <td style="border: 1px solid #dcdfe6; padding: 4px 8px;">📈 上涨</td>
    <td style="border: 1px solid #dcdfe6; padding: 4px 8px;">涨幅 +5% ~ +15%</td>
    <td style="border: 1px solid #dcdfe6; padding: 4px 8px; color: #FF6B6B;">浅红</td>
    <td style="border: 1px solid #dcdfe6; padding: 4px 8px;">持有，设置+20%止盈点</td>
  </tr>
  <tr>
    <td style="border: 1px solid #dcdfe6; padding: 4px 8px;">➖ 横盘</td>
    <td style="border: 1px solid #dcdfe6; padding: 4px 8px;">波动 -5% ~ +5%</td>
    <td style="border: 1px solid #dcdfe6; padding: 4px 8px; color: #909399;">灰色</td>
    <td style="border: 1px solid #dcdfe6; padding: 4px 8px;">观望，适合建仓或定投</td>
  </tr>
  <tr>
    <td style="border: 1px solid #dcdfe6; padding: 4px 8px;">📉 告警</td>
    <td style="border: 1px solid #dcdfe6; padding: 4px 8px;">跌幅 -10% ~ -20%</td>
    <td style="border: 1px solid #dcdfe6; padding: 4px 8px; color: #E6A23C;">黄色</td>
    <td style="border: 1px solid #dcdfe6; padding: 4px 8px;">警惕，准备止损预案</td>
  </tr>
  <tr>
    <td style="border: 1px solid #dcdfe6; padding: 4px 8px;">🟢 破位</td>
    <td style="border: 1px solid #dcdfe6; padding: 4px 8px;">跌幅 ≥ -20% 或 破发</td>
    <td style="border: 1px solid #dcdfe6; padding: 4px 8px; color: #4CAF50;">绿色</td>
    <td style="border: 1px solid #dcdfe6; padding: 4px 8px; font-weight: bold;">强制止损，避免深套</td>
  </tr>
  <tr>
    <td style="border: 1px solid #dcdfe6; padding: 4px 8px;">💀 退市</td>
    <td style="border: 1px solid #dcdfe6; padding: 4px 8px;">跌幅 ≥ -50% 或 绝版无市</td>
    <td style="border: 1px solid #dcdfe6; padding: 4px 8px; color: #2E7D32;">深绿</td>
    <td style="border: 1px solid #dcdfe6; padding: 4px 8px;">流动性归零，账面资产作废</td>
  </tr>
</table>
    `)

    const formatNumber = (num) => {
      return num?.toLocaleString() || '0'
    }

    const getStatusClass = (status) => {
      if (!status) return ''
      if (status.includes('暴涨')) return 'status-surge'
      if (status.includes('上涨')) return 'status-rise'
      if (status.includes('横盘')) return 'status-flat'
      if (status.includes('告警')) return 'status-warning'
      if (status.includes('破位') || status.includes('破发')) return 'status-break'
      if (status.includes('退市')) return 'status-delisted'
      return ''
    }

    const handleLongPress = (item) => {

    }

    // 查询持仓列表
    const handleSearch = async () => {
      loading.value = true
      try {
        const params = {}
        if (searchKeyword.value && searchKeyword.value.trim()) {
          params.keyword = searchKeyword.value.trim()
        }
        if (selectedStatusFilter.value && selectedStatusFilter.value !== 'all') {
          params.status = selectedStatusFilter.value
        }
        params.page = page.value
        params.page_size = pageSize.value

        const data = await axios.get('/assets/holdings/filter', { params })
        if (data && data.holdings) {
          filteredHoldingsData.value = data.holdings
          hasSearched.value = true
        }
      } catch (error) {
        console.error('查询持仓列表失败:', error)
      } finally {
        loading.value = false
      }
    }

    // 重置筛选条件
    const handleReset = () => {
      searchKeyword.value = ''
      selectedStatusFilter.value = 'all'
      filteredHoldingsData.value = []
      hasSearched.value = false
      resetPage()
    }

    // 空数据提示文本
    const emptyDescription = computed(() => {
      if (hasSearched.value) {
        return '没有找到匹配的手办'
      }
      return '暂无数据'
    })

    return {
      showFilter,
      searchKeyword,
      selectedStatusFilter,
      statusFilters,
      statusTable,
      formatNumber,
      getStatusClass,
      handleLongPress,
      paginatedData,
      emptyDescription,
      loading,
      handleSearch,
      handleReset,
      // 分页相关
      page,
      pageSize,
      pageSizeOptions,
      total,
      rangeText,
      handlePageChange,
      handleSizeChange
    }
  }
}
</script>

<style scoped>
.holdings-section {
  background-color: white;
  padding: 20px;
  border-radius: 8px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

/* 标题样式 - 确保问号和标题在同一行 */
.section-title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 18px;
  font-weight: bold;
}

/* 状态帮助按钮样式 */
.status-help-button {
  width: 24px;
  height: 24px;
  min-width: 24px;
  padding: 0;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 14px;
  font-weight: bold;
}

/* 筛选条件 */
.filter-section {
  margin-bottom: 20px;
  padding: 15px;
  background-color: #f5f5f5;
  border-radius: 6px;
}

.filter-row {
  display: flex;
  gap: 10px;
  align-items: center;
  flex-wrap: wrap;
}

/* 联合筛选行样式 - 搜索和状态筛选在同一行 */
.combined-filter-row {
  display: flex;
  gap: 15px;
  align-items: center;
  flex-wrap: wrap;
}

.combined-filter-row .search-input {
  width: 200px;
  flex-shrink: 0;
}

.status-filter-buttons {
  display: flex;
  gap: 8px;
  align-items: center;
  flex-wrap: wrap;
}

.status-filter-buttons .el-button {
  font-size: 14px;
}

/* 操作按钮行样式 */
.action-row {
  margin-top: 15px;
  padding-top: 15px;
  border-top: 1px dashed #dcdfe6;
  justify-content: flex-end;
}

/* 持仓卡片 */
.holdings-cards {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(400px, 1fr));
  gap: 20px;
}

.empty-holdings {
  width: 100%;
  padding: 40px 0;
  display: flex;
  justify-content: center;
  align-items: center;
  grid-column: 1 / -1;
  min-height: 200px;
}

.holding-card {
  background-color: #f9f9f9;
  border: 1px solid #e8e8e8;
  border-radius: 8px;
  padding: 15px;
  transition: all 0.3s ease;
  display: flex;
  flex-direction: row;
  align-items: flex-start;
}

.holding-card:hover {
  box-shadow: 0 4px 16px 0 rgba(0, 0, 0, 0.1);
  transform: translateY(-2px);
}

/* 持仓状态样式 */
.holding-card.status-surge {
  border-left: 4px solid #F5222D;
  background-color: #FFF1F0;
}

.holding-card.status-rise {
  border-left: 4px solid #FF7875;
  background-color: #FFF2F2;
}

.holding-card.status-flat {
  border-left: 4px solid #8c8c8c;
  background-color: #f5f5f5;
}

.holding-card.status-warning {
  border-left: 4px solid #faad14;
  background-color: #fffbe6;
}

.holding-card.status-break {
  border-left: 4px solid #52C41A;
  background-color: #F6FFED;
}

.holding-card.status-delisted {
  border-left: 4px solid #000000;
  background-color: #f0f0f0;
}

/* 卡片内容 */
.card-image {
  width: 80px;
  height: 80px;
  margin-right: 15px;
  border-radius: 4px;
  overflow: hidden;
  flex-shrink: 0;
}

.card-image img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.card-content {
  flex: 1;
  min-width: 0;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
}

.card-title {
  font-size: 16px;
  font-weight: bold;
  color: #333;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  flex: 1;
  margin-right: 10px;
}

.figure-name-link {
  color: #333;
  text-decoration: none;
  transition: color 0.3s ease;
}

.figure-name-link:hover {
  color: #409eff;
}

.card-body {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.card-info {
  display: flex;
  gap: 20px;
  font-size: 14px;
}

.info-item {
  display: flex;
  align-items: center;
  gap: 5px;
}

.info-item .label {
  color: #666;
}

.info-item .value {
  font-weight: bold;
  color: #333;
}

.card-divider {
  height: 1px;
  background-color: #e0e0e0;
  margin: 5px 0;
}

.card-prices {
  display: flex;
  flex-direction: column;
  gap: 5px;
}

.price-item {
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 14px;
}

.price-item .label {
  color: #666;
  min-width: 40px;
}

.price-item .value {
  font-weight: bold;
  color: #333;
}

.price-item .value.positive {
  color: #f5222d;  /* 红色 - 盈利（中国股市规范：红涨绿跌） */
}

.price-item .value.negative {
  color: #52c41a;  /* 绿色 - 亏损（中国股市规范：红涨绿跌） */
}

.card-footer {
  display: flex;
  gap: 20px;
  font-size: 12px;
  color: #999;
  margin-top: 5px;
}

.footer-item {
  display: flex;
  align-items: center;
  gap: 5px;
}

.footer-item .label {
  color: #999;
}

.footer-item .value {
  font-weight: bold;
  color: #666;
}

/* 操作下拉按钮样式 - 移除hover时的黑框 */
.el-dropdown-link {
  cursor: pointer;
  color: #409EFF;
  padding: 4px 8px;
  border-radius: 4px;
  transition: none;
  background-color: transparent;
}

.el-dropdown-link:hover {
  background-color: transparent;
  color: #66b1ff;
}

/* 深度选择器覆盖Element Plus默认样式 */
:deep(.el-dropdown-link:hover) {
  background-color: transparent !important;
  color: #66b1ff !important;
}

:deep(.el-dropdown-link:focus) {
  background-color: transparent !important;
  outline: none !important;
}

/* 分页组件样式 */
.pagination-wrapper {
  display: flex;
  justify-content: flex-end;
  align-items: center;
  margin-top: 24px;
  padding-top: 16px;
  border-top: 1px solid #e4e7ed;
  flex-wrap: wrap;
  gap: 12px;
}

.pagination-info {
  font-size: 14px;
  color: #606266;
  white-space: nowrap;
  margin-right: 0;
}
</style>