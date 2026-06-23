<!--
  Dashboard.vue - 资产看板主页面
  
  功能说明：
  - 提供双模式切换：倒狗模式（投资视角）和收藏家模式（收藏视角）
  - 倒狗模式包含资产、行情、交易三大模块，支持塑料小人指数(HPI)追踪、盈亏分析等
  - 收藏家模式展示收藏统计、价值藏品、标签云等收藏维度数据
  - 集成年度消费上限设置、资产刷新等快捷操作
  
  组件依赖：
  - AssetView.vue - 资产模块（资产概览、持仓列表、收益曲线等）
  - MarketView.vue - 行情模块（K线图、板块排行、投研观点等）
  - TradeView.vue - 交易模块（交易统计、流水记录等）
  - CollectorOverview.vue - 收藏家概览
  
  维护提示：
  - 模式切换通过 currentMode 控制，数据独立维护
  - 子组件通过 Props 接收数据，通过 Events 触发父组件刷新
-->
<template>
  <div class="orders-container">
    <div class="header">
      <div class="header-left">
        <h2>资产看板</h2>
        <div class="mode-toggle">
          <button 
            class="mode-btn" 
            :class="{ active: currentMode === 'collector' }"
            @click="setMode('collector')"
          >
            🏛️ 收藏家模式
          </button>
          <button 
            class="mode-btn" 
            :class="{ active: currentMode === 'reseller' }"
            @click="setMode('reseller')"
          >
            📈 倒狗模式
          </button>
        </div>
      </div>
      <div class="header-actions">
        <div class="user-info">
          <span v-if="userStore.isAuthenticated">当前用户: </span>
          <span v-if="userStore.isAuthenticated" class="username" @click="$router.push('/profile')" style="cursor: pointer; color: #666;">{{ userStore.currentUser?.username }}</span>
          <button v-if="userStore.isAuthenticated" class="btn btn-logout" @click="logout">退出</button>
        </div>
      </div>
    </div>

    <!-- 倒狗模式内容 -->
    <div v-if="currentMode === 'reseller'">
      <!-- 倒狗模式操作栏 -->
      <div class="reseller-actions">
        <div class="view-tabs">
          <el-button 
            v-for="tab in viewTabs" 
            :key="tab.value"
            :class="{ active: activeView === tab.value }"
            @click="activeView = tab.value"
          >
            {{ tab.label }}
          </el-button>
        </div>
        <div class="action-buttons">
          <!-- 资产版块按钮 -->
          <template v-if="activeView === 'asset'">
            <el-button type="info" @click="showAnnualLimitDialog">
              <el-icon><Money /></el-icon> 年度手办消费上限
            </el-button>
            <el-button type="primary" @click="refreshData">
              <el-icon><Refresh /></el-icon> 刷新资产
            </el-button>
          </template>
          <!-- 行情版块按钮 -->
          <template v-if="activeView === 'market'">
            <el-button type="primary" @click="refreshData">
              <el-icon><Refresh /></el-icon> 刷新行情
            </el-button>
            <el-button @click="openAlertSettings">
              <el-icon><Bell /></el-icon> 设置预警
            </el-button>
          </template>
          <!-- 交易版块按钮 -->
          <template v-if="activeView === 'trade'">
            <el-button type="primary" @click="openBillExportDialog">
              <el-icon><Download /></el-icon> 账单导出
            </el-button>
            <el-button type="primary" @click="refreshTradeData">
              <el-icon><Refresh /></el-icon> 刷新交易
            </el-button>
          </template>
        </div>
      </div>

      <!-- 资产视图 -->
      <AssetView 
        v-if="activeView === 'asset'" 
        :dashboard-data="dashboardData"
        @sell-asset="sellAsset"
        @add-position="addPosition"
        @cut-loss="cutLoss"
        @edit-price="editPrice"
        @refresh-data="fetchDashboardData"
      />

      <!-- 行情视图 -->
      <MarketView 
        v-else-if="activeView === 'market'" 
        :market-data="marketData"
        @add-watchlist="addToWatchlist"
      />

      <!-- 交易视图 -->
      <TradeView
        v-else-if="activeView === 'trade'"
        :trade-data="tradeData"
        :selected-month="selectedMonth"
        @open-buy-dialog="openBuyDialog"
        @open-sell-dialog="openSellDialog"
        @open-payment-dialog="openPaymentDialog"
        @open-cancel-dialog="openCancelDialog"
        @view-record="viewRecord"
        @delete-record="deleteRecord"
        @month-change="handleMonthChange"
        @filter-change="handleTradeFilterChange"
      />
    </div>

    <!-- 收藏家模式内容 -->
    <div v-else class="collector-mode">
      <!-- 本命厂商列表/详情视图 -->
      <template v-if="showManufacturerView">
        <ManufacturerListView
          v-if="manufacturerView === 'list'"
          :manufacturers="manufacturers"
          :manufacturer-count="manufacturerCount"
          :loading="manufacturerLoading"
          @add="handleManufacturerAdd"
          @select="handleManufacturerSelect"
          @edit="handleManufacturerEdit"
          @delete="handleManufacturerDelete"
          @back="handleManufacturerBackToCabinets"
        />
        <ManufacturerDetailView
          v-else-if="manufacturerView === 'detail'"
          :manufacturer="currentManufacturer"
          :loading="manufacturerDetailLoading"
          @back="handleManufacturerBackFromDetail"
          @edit="handleManufacturerEdit"
          @view-figure="handleManufacturerViewFigure"
          @sell="handleManufacturerSellFigure"
        />
        <MakerFormDialog
          :visible="manufacturerDialogVisible"
          :is-editing="manufacturerIsEditing"
          :form-data="manufacturerFormData"
          @close="handleManufacturerDialogClose"
          @save="handleManufacturerSave"
        />
        <!-- 本命厂商 - 藏品详情抽屉 -->
        <FigureDetailDrawer
          :visible="manufacturerDetailDrawerVisible"
          :figure="manufacturerSelectedFigure"
          cabinet-key="role"
          cabinet-name="本命厂商"
          cabinet-icon="🏭"
          :rating="0"
          @close="manufacturerDetailDrawerVisible = false"
          @sell="handleManufacturerDetailSell"
        />
        <!-- 本命厂商 - 出柜登记抽屉 -->
        <FigureOutDrawer
          :visible="manufacturerOutDrawerVisible"
          :figure="manufacturerSelectedFigure"
          cabinet-key="role"
          cabinet-name="本命厂商"
          cabinet-icon="🏭"
          @close="manufacturerOutDrawerVisible = false"
          @confirm="handleManufacturerOutConfirm"
        />
      </template>
      <!-- 收藏柜详情视图 -->
      <CabinetDetail
        v-else-if="selectedCabinet"
        :cabinet="selectedCabinet"
        @back="handleCabinetBack"
        @refresh="handleCabinetRefresh"
      />
      <!-- 收藏柜概览视图 -->
      <template v-else>
        <CollectorHeader
          @share-poster="sharePoster"
          @privacy-settings="privacySettings"
        />
        
        <CollectorOverview :collector-data="collectorData" />
        
        <CollectionCabinets
          :collector-data="collectorData"
          @cabinet-click="handleCabinetClick"
        />
        
        <TagCloud
          :collector-data="collectorData"
          @filter-by-tag="filterByTag"
        />
        
        <!-- 标签筛选结果 -->
        <div v-if="tagFilterResults" class="tag-filter-results">
          <div class="filter-result-header">
            <div class="filter-result-title">
              标签筛选：<span class="filter-result-tag">#{{ tagFilterName }}</span>
              <span class="filter-result-count">{{ tagFilterResults.length }} 个结果</span>
            </div>
            <button class="btn-clear-filter" @click="clearTagFilter">✕ 清除筛选</button>
          </div>
          <div v-if="tagFilterResults.length > 0" class="filter-results-grid">
            <div
              v-for="fig in tagFilterResults"
              :key="fig.id"
              class="figure-card"
              @click="goToFigureDetail(fig.id)"
            >
              <div class="figure-img-wrap">
                <div v-if="fig.image" class="figure-img-real">
                  <img :src="fig.image" :alt="fig.name" />
                </div>
                <div v-else class="figure-img-placeholder">📦</div>
              </div>
              <div class="figure-info">
                <div class="figure-name">{{ fig.name || '未知' }}</div>
                <div class="figure-line">{{ fig.work }} · {{ fig.scale }} · {{ fig.manufacturer }}</div>
                <div class="figure-line-gray" v-if="fig.transaction_date">入柜 {{ fig.transaction_date }}</div>
              </div>
            </div>
          </div>
          <div v-else class="filter-empty">
            未找到匹配该标签的手办
          </div>
        </div>
        
        <ActivityFeed
          :collector-data="collectorData"
          @activity-action="handleActivityAction"
        />
      </template>
    </div>

    <!-- 预警设置对话框 -->
    <el-dialog
      v-model="alertDialogVisible"
      title="设置预警"
      width="500px"
    >
      <el-form :model="alertForm" label-width="80px">
        <el-form-item label="手办">
          <el-select v-model="alertForm.figure_id" placeholder="选择手办">
            <el-option 
              v-for="figure in figures" 
              :key="figure.id" 
              :label="figure.name" 
              :value="figure.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="预警类型">
          <el-select v-model="alertForm.alert_type" placeholder="选择预警类型">
            <el-option value="price_drop" label="价格下跌" />
            <el-option value="price_rise" label="价格上涨" />
          </el-select>
        </el-form-item>
        <el-form-item label="阈值">
          <el-input v-model.number="alertForm.threshold" placeholder="输入预警阈值(%)" />
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="alertDialogVisible = false">取消</el-button>
          <el-button type="primary" @click="createAlert">确定</el-button>
        </span>
      </template>
    </el-dialog>

    <!-- 年度手办消费上限设置对话框 -->
    <el-dialog
      v-model="annualLimitDialogVisible"
      title="年度手办消费上限设置"
      width="500px"
    >
      <el-form :model="annualLimitForm" label-width="120px">
        <el-form-item label="年度消费上限">
          <el-input-number 
            v-model="annualLimitForm.limit" 
            :min="0" 
            :precision="2"
            :step="1000"
            style="width: 200px"
          />
          <span style="margin-left: 10px; color: #909399;">元</span>
        </el-form-item>
        <el-form-item>
          <div style="color: #909399; font-size: 12px; line-height: 1.5;">
            <p>提示：</p>
            <p>1. 设置年度手办消费上限后，系统将在您接近或超出上限时提醒您</p>
            <p>2. 设置为0表示不限制年度消费</p>
            <p>3. 该设置仅作为参考，不会阻止您继续购买手办</p>
          </div>
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="annualLimitDialogVisible = false">取消</el-button>
          <el-button type="primary" @click="saveAnnualLimit" :loading="annualLimitLoading">
            保存设置
          </el-button>
        </span>
      </template>
    </el-dialog>

    <!-- 账单导出弹窗 -->
    <BillExportDialog
      v-model="billExportDialogVisible"
      :current-month="selectedMonth"
      :loading="billExportLoading"
      @export="handleBillExport"
    />

    <!-- 创建买入订单抽屉 -->
    <CreateBuyOrderDrawer
      v-model:visible="createBuyOrderDrawerVisible"
      @success="fetchDashboardData"
    />

    <!-- 创建卖出订单抽屉 -->
    <CreateSellOrderDrawer
      v-model:visible="createSellOrderDrawerVisible"
      @success="fetchDashboardData"
    />

    <!-- 补款订单列表弹窗 -->
    <PayBalanceOrderListDialog
      v-model="payBalanceOrderListVisible"
      @select-order="selectPayBalanceOrder"
    />

    <!-- 补款确认抽屉 -->
    <PayBalanceConfirmDrawer
      v-model="payBalanceConfirmVisible"
      :order="selectedPayBalanceOrder"
      @success="handlePayBalanceSuccess"
    />
  </div>
</template>

<script>
import { ref, onMounted, onUnmounted, nextTick, watch } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '../store'
import axios from '../axios'
import { Refresh, Bell, Download, Plus, Money, Close } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'

// 导入收藏家模式组件
import CollectorHeader from './Dashboard/components/collector/CollectorHeader.vue'
import CollectorOverview from './Dashboard/components/collector/CollectorOverview.vue'
import CollectionCabinets from './Dashboard/components/collector/CollectionCabinets.vue'
import CabinetDetail from './Dashboard/components/collector/CabinetDetail/CabinetDetail.vue'
import TagCloud from './Dashboard/components/collector/TagCloud.vue'
import ActivityFeed from './Dashboard/components/collector/ActivityFeed.vue'

// 导入本命厂商组件
import ManufacturerListView from './Dashboard/components/collector/ManufacturerList/ManufacturerList.vue'
import ManufacturerDetailView from './Dashboard/components/collector/ManufacturerList/ManufacturerDetail.vue'
import MakerFormDialog from './Dashboard/components/collector/ManufacturerList/MakerFormDialog.vue'

// 导入藏品详情抽屉组件
import FigureDetailDrawer from './Dashboard/components/collector/CabinetDetail/components/FigureDetailDrawer/FigureDetailDrawer.vue'
import FigureOutDrawer from './Dashboard/components/collector/CabinetDetail/components/FigureOutDrawer/index.vue'

// 导入倒狗模式组件
import AssetView from './Dashboard/components/reseller/AssetView.vue'
import MarketView from './Dashboard/components/reseller/MarketView.vue'
import TradeView from './Dashboard/components/reseller/TradeView.vue'
import BillExportDialog from './Dashboard/components/reseller/trade/BillExportDialog.vue'
import CreateBuyOrderDrawer from './Dashboard/components/reseller/trade/CreateBuyOrderDrawer.vue'
import CreateSellOrderDrawer from './Dashboard/components/reseller/trade/CreateSellOrderDrawer.vue'
import PayBalanceOrderListDialog from './Dashboard/components/reseller/trade/PayBalanceOrderListDialog.vue'
import PayBalanceConfirmDrawer from './Dashboard/components/reseller/trade/PayBalanceConfirmDrawer.vue'

// 导入收藏家模式 composable
import { useCollectorData } from './Dashboard/composables/useCollectorData'
// 导入本命厂商 composable
import { useManufacturer } from './Dashboard/components/collector/ManufacturerList/composables/useManufacturer'
// 导入账单导出 composable
import { useBillExport } from './Dashboard/composables/useBillExport'
// 导入创建买入订单 composable
import { useCreateBuyOrder } from './Dashboard/composables/useCreateBuyOrder'
// 导入创建卖出订单 composable
import { useCreateSellOrder } from './Dashboard/composables/useCreateSellOrder'
// 导入补款 composable
import { usePayBalance } from './Dashboard/composables/usePayBalance'

export default {
  name: 'Dashboard',
  components: {
    Refresh,
    Bell,
    Download,
    Plus,
    Money,
    Close,
    // 收藏家模式组件
      CollectorHeader,
      CollectorOverview,
      CollectionCabinets,
      CabinetDetail,
      TagCloud,
      ActivityFeed,
      // 本命厂商组件
      ManufacturerListView,
      ManufacturerDetailView,
      MakerFormDialog,
      // 藏品详情抽屉组件
      FigureDetailDrawer,
      FigureOutDrawer,
      // 倒狗模式组件
      AssetView,
      MarketView,
      TradeView,
      BillExportDialog,
      CreateBuyOrderDrawer,
      CreateSellOrderDrawer,
      PayBalanceOrderListDialog,
      PayBalanceConfirmDrawer,
    },
  setup() {
    const router = useRouter()
    const userStore = useUserStore()
    const dashboardData = ref(null)
    const loading = ref(true)

    // 使用收藏家模式 composable
    const { collectorData, loading: collectorLoading, fetchCollectorData, sharePoster, privacySettings, filterByTag, clearTagFilter, tagFilterResults, tagFilterName, handleActivityAction } = useCollectorData()

    // 使用本命厂商 composable
    const {
      manufacturers,
      manufacturerCount,
      loading: manufacturerLoading,
      currentManufacturer,
      detailLoading: manufacturerDetailLoading,
      formDialogVisible: manufacturerDialogVisible,
      isEditing: manufacturerIsEditing,
      formData: manufacturerFormData,
      currentView: manufacturerView,
      fetchManufacturers,
      fetchManufacturerDetail,
      openAddDialog: handleManufacturerAdd,
      openEditDialog: handleManufacturerEdit,
      saveManufacturer,
      removeManufacturer: handleManufacturerDelete,
      backToList: handleManufacturerBackToList
    } = useManufacturer()

    const showManufacturerView = ref(false)

    // 本命厂商 - 藏品详情/出柜登记抽屉状态
    const manufacturerDetailDrawerVisible = ref(false)
    const manufacturerOutDrawerVisible = ref(false)
    const manufacturerSelectedFigure = ref(null)

    // 使用账单导出 composable
    const { dialogVisible: billExportDialogVisible, loading: billExportLoading, openDialog: openBillExportDialog, exportBill: handleBillExport } = useBillExport()

    // 使用创建买入订单 composable
    const { drawerVisible: createBuyOrderDrawerVisible, openDrawer: openCreateBuyOrderDrawer } = useCreateBuyOrder()

    // 使用创建卖出订单 composable
    const { drawerVisible: createSellOrderDrawerVisible, openDrawer: openCreateSellOrderDrawer } = useCreateSellOrder({
      onSuccess: () => {
        // 刷新资产和交易数据
        fetchDashboardData()
      }
    })

    // 使用补款 composable
    const {
      payBalanceOrderListVisible,
      payBalanceConfirmVisible,
      selectedPayBalanceOrder,
      openPayBalanceOrderList,
      selectPayBalanceOrder,
      handlePayBalanceSuccess
    } = usePayBalance({
      onSuccess: () => {
        // 刷新资产和交易数据
        fetchDashboardData()
        fetchTradeData()
      }
    })

    const activeView = ref('asset')
    const alertDialogVisible = ref(false)
    const figures = ref([])
    const currentMode = ref('reseller')
    const selectedCabinet = ref(null)
    const tradeData = ref(null)
    const marketData = ref(null)
    
    // 年度消费上限设置
    const annualLimitDialogVisible = ref(false)
    const annualLimitForm = ref({ limit: 0 })
    const annualLimitLoading = ref(false)
    
    const alertForm = ref({
      figure_id: '',
      alert_type: 'price_drop',
      threshold: 10
    })
    
    const viewTabs = [
      { label: '资产', value: 'asset' },
      { label: '行情', value: 'market' },
      { label: '交易', value: 'trade' }
    ]
    
    // 格式化数字
    const formatNumber = (num) => {
      return num?.toLocaleString() || '0'
    }
    
    // 退出登录
    const logout = () => {
      userStore.logout()
      router.push('/login')
    }
    
    // 获取资产数据
    const fetchDashboardData = async () => {
      loading.value = true
      try {
        const res = await axios.get('/assets/dashboard')
        dashboardData.value = res
      } catch (error) {
        ElMessage.error('获取数据失败')
      } finally {
        loading.value = false
      }
    }
    
    // 当前选中的年月
    const selectedMonth = ref({
      year: new Date().getFullYear(),
      month: new Date().getMonth() + 1
    })

    // 当前筛选参数
    const tradeFilterParams = ref({
      filterType: 'all',
      timeType: 'last30days',
      dateRange: [],
      figureIds: [],
      platforms: [],
      statusList: [],
      minAmount: null,
      maxAmount: null,
      keyword: ''
    })

    // 获取交易数据（并行请求三个独立接口）
    const fetchTradeData = async () => {
      try {
        const { year, month } = selectedMonth.value
        const baseParams = { year, month }
        const filterParams = {
          filter_type: tradeFilterParams.value.filterType,
          time_type: tradeFilterParams.value.timeType,
          date_start: tradeFilterParams.value.dateRange?.[0] || null,
          date_end: tradeFilterParams.value.dateRange?.[1] || null,
          figure_ids: tradeFilterParams.value.figureIds?.join(',') || null,
          platforms: tradeFilterParams.value.platforms?.join(',') || null,
          status_list: tradeFilterParams.value.statusList?.join(',') || null,
          min_amount: tradeFilterParams.value.minAmount,
          max_amount: tradeFilterParams.value.maxAmount,
          keyword: tradeFilterParams.value.keyword || null
        }

        // 并行请求三个独立接口
        const [monthlyStatsRes, transactionsRes, profitAnalysisRes] = await Promise.all([
          axios.get('/trade_records/monthly-stats', { params: baseParams }),
          axios.get('/trade_records/transactions', { params: { ...baseParams, ...filterParams } }),
          axios.get('/trade_records/profit-analysis', { params: baseParams })
        ])

        // 拼装页面数据
        tradeData.value = {
          monthly_stats: monthlyStatsRes.monthly_stats,
          transactions: transactionsRes.transactions,
          profit_analysis: profitAnalysisRes.profit_analysis,
          query_month: monthlyStatsRes.query_month,
          filter: transactionsRes.filter
        }
      } catch (error) {
        ElMessage.error('获取交易数据失败')
      }
    }

    // 处理月份切换（仅更新月度统计，不触发交易流水和利润分析接口）
    const handleMonthChange = async (newMonth) => {
      selectedMonth.value = newMonth
      // 只获取月度统计数据
      try {
        const res = await axios.get('/trade_records/monthly-stats', {
          params: { year: newMonth.year, month: newMonth.month }
        })
        // 只更新月度统计数据，保持其他数据不变
        tradeData.value = {
          ...tradeData.value,
          monthly_stats: res.monthly_stats,
          query_month: res.query_month
        }
      } catch (error) {
        ElMessage.error('获取月度统计失败')
      }
    }

    // 处理交易筛选变更（仅触发交易流水接口，不触发月度统计和利润分析接口）
    const handleTradeFilterChange = async (filterParams) => {
      tradeFilterParams.value = { ...filterParams }
      // 只获取交易流水数据
      try {
        const { year, month } = selectedMonth.value
        const params = {
          year,
          month,
          filter_type: filterParams.filterType,
          time_type: filterParams.timeType,
          date_start: filterParams.dateRange?.[0] || null,
          date_end: filterParams.dateRange?.[1] || null,
          figure_ids: filterParams.figureIds?.join(',') || null,
          platforms: filterParams.platforms?.join(',') || null,
          status_list: filterParams.statusList?.join(',') || null,
          min_amount: filterParams.minAmount,
          max_amount: filterParams.maxAmount,
          keyword: filterParams.keyword || null
        }
        const res = await axios.get('/trade_records/transactions', { params })
        // 只更新交易流水数据，保持其他数据不变
        tradeData.value = {
          ...tradeData.value,
          transactions: res.transactions,
          filter: res.filter
        }
      } catch (error) {
        ElMessage.error('获取交易流水失败')
      }
    }
    
    // 获取行情数据
    const fetchMarketData = async () => {
      try {
        const res = await axios.get('/market/dashboard')
        marketData.value = res
      } catch (error) {
        ElMessage.error('获取行情数据失败')
      }
    }
    
    // 刷新数据
    const refreshData = async () => {
      if (activeView.value === 'asset') {
        await fetchDashboardData()
        // 如果日涨跌数据不存在，自动初始化基准数据
        if (dashboardData.value?.summary?.has_daily_change === false) {
          try {
            await axios.post('/assets/dashboard/init-daily-change')
            ElMessage.success('日涨跌基准数据已创建，明天开始正常计算')
            // 重新获取数据以更新显示
            await fetchDashboardData()
          } catch (error) {
            console.error('初始化日涨跌基准数据失败:', error)
          }
        }
      } else if (activeView.value === 'market') {
        await fetchMarketData()
      }
    }
    
    // 刷新交易数据
    const refreshTradeData = async () => {
      await fetchTradeData()
    }
    
    // 设置模式
    const setMode = (mode) => {
      currentMode.value = mode
      selectedCabinet.value = null  // 切换模式时关闭详情
      if (mode === 'collector') {
        fetchCollectorData()
      } else if (mode === 'reseller') {
        fetchDashboardData()
      }
    }
    
    // 收藏柜点击：进入详情
    const handleCabinetClick = (cabinet) => {
      if (cabinet.key === 'role') {
        // 本命厂商走独立视图
        showManufacturerView.value = true
        selectedCabinet.value = null
        fetchManufacturers()
      } else {
        selectedCabinet.value = cabinet
        showManufacturerView.value = false
      }
    }
    
    // 本命厂商详情
    const handleManufacturerSelect = (id) => {
      fetchManufacturerDetail(id)
    }

    // 本命厂商详情返回列表（含刷新）
    const handleManufacturerBackFromDetail = () => {
      handleManufacturerBackToList()
      fetchManufacturers()
    }

    // 本命厂商列表返回收藏柜概览
    const handleManufacturerBackToCabinets = () => {
      showManufacturerView.value = false
      fetchCollectorData()
    }

    // 本命厂商 - 查看手办详情
    const handleManufacturerViewFigure = (fig) => {
      manufacturerSelectedFigure.value = fig
      manufacturerDetailDrawerVisible.value = true
    }

    // 本命厂商 - 手办出柜登记
    const handleManufacturerSellFigure = (fig) => {
      manufacturerSelectedFigure.value = fig
      manufacturerOutDrawerVisible.value = true
    }

    // 本命厂商 - 详情抽屉中的出柜登记
    const handleManufacturerDetailSell = ({ figure }) => {
      manufacturerDetailDrawerVisible.value = false
      setTimeout(() => {
        manufacturerSelectedFigure.value = figure || manufacturerSelectedFigure.value
        manufacturerOutDrawerVisible.value = true
      }, 300)
    }

    // 本命厂商 - 出柜登记确认
    const handleManufacturerOutConfirm = async (payload) => {
      try {
        // 本命厂商分类标识映射: role → maker
        const cabinetType = payload.cabinetKey === 'role' ? 'maker' : (payload.cabinetKey || 'maker')
        await axios.post(`/collector/cabinets/figures/${payload.figureId}/exclude`, {
          cabinet_type: cabinetType
        })
        ElMessage.success('出柜成功')
        manufacturerOutDrawerVisible.value = false
        fetchManufacturers()
      } catch (e) {
        ElMessage.error('出柜失败: ' + (e.response?.data?.detail || e.message))
      }
    }

    // 跳转到手办详情页
    const goToFigureDetail = (figureId) => {
      router.push({ name: 'FigureDetail', params: { id: figureId } })
    }

    // 本命厂商弹窗关闭
    const handleManufacturerDialogClose = () => {
      manufacturerDialogVisible.value = false
    }

    // 本命厂商保存
    const handleManufacturerSave = async (formDataFromDialog) => {
      // 将弹窗表单数据同步到 composable 的 formData
      if (formDataFromDialog) {
        Object.assign(manufacturerFormData, formDataFromDialog)
      }
      const success = await saveManufacturer()
      if (success) {
        manufacturerDialogVisible.value = false
      }
    }

    // 收藏柜详情返回
    const handleCabinetBack = () => {
      selectedCabinet.value = null
      fetchCollectorData()
    }

    // 收藏柜刷新（出柜登记后刷新数据）
    const handleCabinetRefresh = async () => {
      await fetchCollectorData()
      // 刷新后用最新数据更新当前选中的收藏柜
      const freshCabinet = collectorData.value?.cabinets?.find(
        c => c.key === selectedCabinet.value?.key
      )
      if (freshCabinet) {
        selectedCabinet.value = freshCabinet
      }
    }
    
    // 显示年度消费上限对话框
    const showAnnualLimitDialog = async () => {
      try {
        const response = await axios.get('/assets/settings/annual-limit')
        if (response && response.annual_spending_limit !== undefined) {
          annualLimitForm.value.limit = Number(response.annual_spending_limit) || 0
        } else {
          annualLimitForm.value.limit = 0
        }
      } catch (error) {
        annualLimitForm.value.limit = 0
      }
      annualLimitDialogVisible.value = true
    }
    
    // 保存年度消费上限
    const saveAnnualLimit = async () => {
      annualLimitLoading.value = true
      try {
        await axios.post('/assets/settings/annual-limit', {
          limit: annualLimitForm.value.limit
        })
        ElMessage.success('年度消费上限设置成功')
        annualLimitDialogVisible.value = false
        // 刷新当前页面
        window.location.reload()
      } catch (error) {
        ElMessage.error('设置失败')
      } finally {
        annualLimitLoading.value = false
      }
    }
    
    // 打开预警设置
    const openAlertSettings = () => {
      alertDialogVisible.value = true
    }
    
    // 创建预警
    const createAlert = async () => {
      try {
        await axios.post('/assets/alerts', alertForm.value)
        ElMessage.success('预警设置成功')
        alertDialogVisible.value = false
      } catch (error) {
        ElMessage.error('设置失败')
      }
    }
    
    // 导出账单
    const exportBill = () => {
      ElMessage.info('账单导出功能开发中')
    }
    
    // 资产操作
    const sellAsset = (item) => {
      // 卖出功能已通过 QuickSellDialog 组件实现
      // 此函数保留用于兼容性，实际逻辑在 AssetView.vue 中处理
    }
    
    const addPosition = (item) => {
      // 补仓功能已通过 AddPositionDialog 组件实现
      // 此函数保留用于兼容性
    }
    
    const cutLoss = (item) => {
      ElMessage.info(`斩仓 ${item.figure_name} 功能开发中`)
    }
    
    const editPrice = (item) => {
      // 价格修改功能已在 PriceUpdateDialog 组件中实现
      // 此函数保留用于兼容性，实际逻辑在 AssetView.vue 中处理
    }
    
    // 添加到自选股
    const addToWatchlist = () => {
      ElMessage.info('添加自选股功能开发中')
    }
    
    // 交易操作
    const openBuyDialog = () => {
      openCreateBuyOrderDrawer()
    }

    const openSellDialog = () => {
      openCreateSellOrderDrawer()
    }

    const openPaymentDialog = () => {
      openPayBalanceOrderList()
    }
    
    const openCancelDialog = () => {
      ElMessage.info('功能正在开发中')
    }
    
    const viewRecord = (record) => {
      ElMessage.info(`查看记录 ${record.id}`)
    }
    
    const deleteRecord = (record) => {
      ElMessageBox.confirm('确定删除该记录吗？', '提示', {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }).then(() => {
        ElMessage.success('删除成功')
      }).catch(() => {})
    }
    
    // 监听活跃视图变化
    watch(activeView, async (newView) => {
      if (newView === 'asset') {
        await fetchDashboardData()
      } else if (newView === 'trade') {
        await fetchTradeData()
      } else if (newView === 'market') {
        await fetchMarketData()
      }
    })
    
    // 组件挂载时
    onMounted(() => {
      fetchDashboardData()
      if (localStorage.getItem('token') && !userStore.currentUser) {
        userStore.fetchUser()
      }
    })
    
    return {
      dashboardData,
      collectorData,
      tradeData,
      marketData,
      loading,
      collectorLoading,
      activeView,
      viewTabs,
      alertDialogVisible,
      alertForm,
      figures,
      userStore,
      currentMode,
      selectedCabinet,
      annualLimitDialogVisible,
      annualLimitForm,
      annualLimitLoading,
      formatNumber,
      refreshData,
      refreshTradeData,
      openAlertSettings,
      createAlert,
      setMode,
      handleCabinetClick,
      handleCabinetBack,
      handleCabinetRefresh,
      showAnnualLimitDialog,
      saveAnnualLimit,
      exportBill,
      fetchCollectorData,
      sharePoster,
      privacySettings,
      filterByTag,
      clearTagFilter,
      tagFilterResults,
      tagFilterName,
      handleActivityAction,
      sellAsset,
      addPosition,
      cutLoss,
      editPrice,
      addToWatchlist,
      openBuyDialog,
      openSellDialog,
      openPaymentDialog,
      openCancelDialog,
      viewRecord,
      deleteRecord,
      logout,
      fetchDashboardData,
      handleMonthChange,
      handleTradeFilterChange,
      billExportDialogVisible,
      billExportLoading,
      openBillExportDialog,
      handleBillExport,
      createBuyOrderDrawerVisible,
      createSellOrderDrawerVisible,
      payBalanceOrderListVisible,
      payBalanceConfirmVisible,
      selectedPayBalanceOrder,
      selectPayBalanceOrder,
      handlePayBalanceSuccess,
      // 本命厂商
      showManufacturerView,
      manufacturers,
      manufacturerCount,
      manufacturerLoading,
      currentManufacturer,
      manufacturerDetailLoading,
      manufacturerDialogVisible,
      manufacturerIsEditing,
      manufacturerFormData,
      manufacturerView,
      handleManufacturerAdd,
      handleManufacturerEdit,
      handleManufacturerDelete,
      handleManufacturerBackToList,
      handleManufacturerBackFromDetail,
      handleManufacturerBackToCabinets,
      handleManufacturerSelect,
      handleManufacturerDialogClose,
      handleManufacturerSave,
      // 本命厂商 - 藏品详情/出柜登记
      manufacturerDetailDrawerVisible,
      manufacturerOutDrawerVisible,
      manufacturerSelectedFigure,
      handleManufacturerViewFigure,
      handleManufacturerSellFigure,
      handleManufacturerDetailSell,
      handleManufacturerOutConfirm,
      goToFigureDetail,
    }
  }
}</script>

<style scoped>
.orders-container {
  margin-top: 20px;
  width: 1610px;
  margin-left: 50px;
  margin-right: 50px;
  padding: 20px;
  background-color: #f9f9f9;
  border-radius: 8px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  padding-bottom: 15px;
  border-bottom: 2px solid #e0e0e0;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 16px;
}

.header h2 {
  margin: 0;
  color: #333;
  font-size: 24px;
  font-weight: 600;
}

/* 模式切换按钮 */
.mode-toggle {
  display: inline-flex;
  background: #f5f5f5;
  border-radius: 20px;
  padding: 3px;
  border: 1px solid #e0e0e0;
}

.mode-btn {
  padding: 5px 14px;
  border-radius: 17px;
  font-size: 13px;
  cursor: pointer;
  border: none;
  background: transparent;
  color: #666;
  transition: all 0.2s;
  display: flex;
  align-items: center;
  gap: 4px;
}

.mode-btn.active {
  background: #C49A6C;
  color: #fff;
  font-weight: 500;
  box-shadow: 0 1px 3px rgba(196, 154, 108, 0.3);
}

.header-actions {
  display: flex;
  align-items: center;
  gap: 20px;
}

.view-tabs {
  display: flex;
  gap: 10px;
}

.view-tabs .el-button.active {
  background-color: #1976D2;
  color: white;
}

.action-buttons {
  display: flex;
  align-items: center;
  gap: 10px;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 12px;
  font-size: 13px;
  color: #999;
}

.username {
  font-size: 14px;
  font-weight: 500;
  color: #555;
}

.btn {
  padding: 10px 20px;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-size: 14px;
  font-weight: 500;
  transition: all 0.3s ease;
}

.btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
}

.btn-logout {
  background-color: #fff;
  color: #666;
  padding: 5px 14px;
  font-size: 13px;
  border: 1px solid #e0e0e0;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-logout:hover {
  border-color: #f44336;
  color: #f44336;
}

/* 倒狗模式操作栏 */
.reseller-actions {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  padding: 15px 20px;
  background-color: white;
  border-radius: 8px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
}

.reseller-actions .view-tabs {
  display: flex;
  gap: 10px;
}

.reseller-actions .action-buttons {
  display: flex;
  gap: 10px;
}

/* 收藏家模式容器 */
.collector-mode {
  padding: 20px;
}

/* 标签筛选结果中的手办卡片 */
.filter-results-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 14px;
}

.filter-results-grid .figure-card {
  background: #fff;
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
  transition: transform 0.2s, box-shadow 0.2s;
  cursor: pointer;
}

.filter-results-grid .figure-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.08);
}

.filter-results-grid .figure-img-wrap {
  height: 160px;
  background: #F0EEEB;
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
}

.filter-results-grid .figure-img-placeholder {
  width: 60px;
  height: 60px;
  background: #E0DCD7;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 28px;
  color: #B0ABA5;
}

.filter-results-grid .figure-img-real {
  width: 100%;
  height: 100%;
}

.filter-results-grid .figure-img-real img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.filter-results-grid .figure-info {
  padding: 12px;
}

.filter-results-grid .figure-name {
  font-size: 14px;
  font-weight: 600;
  margin-bottom: 4px;
  color: #1F1F1F;
}

.filter-results-grid .figure-line {
  font-size: 12px;
  color: #666;
  margin-bottom: 2px;
}

.filter-results-grid .figure-line-gray {
  font-size: 12px;
  color: #999;
}

/* 标签筛选结果 */
.tag-filter-results {
  background: #fff;
  border-radius: 12px;
  padding: 20px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
  margin-bottom: 30px;
}

.filter-result-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 16px;
}

.filter-result-title {
  font-size: 16px;
  font-weight: 600;
  color: #333;
  display: flex;
  align-items: center;
  gap: 8px;
}

.filter-result-tag {
  display: inline-flex;
  align-items: center;
  padding: 2px 10px;
  border-radius: 14px;
  font-size: 14px;
  background: #FDF6EE;
  color: #C49A6C;
  border: 1px solid #E8D5C0;
}

.filter-result-count {
  font-size: 13px;
  color: #999;
}

.btn-clear-filter {
  padding: 5px 12px;
  border: 1px solid #EBE8E4;
  background: #fff;
  border-radius: 6px;
  font-size: 13px;
  color: #666;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-clear-filter:hover {
  border-color: #D66A6A;
  color: #D66A6A;
}

.filter-empty {
  text-align: center;
  color: #999;
  font-size: 14px;
  padding: 30px 0;
}

.filter-results-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 14px;
}

@media (max-width: 768px) {
  .orders-container {
    margin-left: 10px;
    margin-right: 10px;
    padding: 10px;
  }
  
  .header {
    flex-direction: column;
    gap: 15px;
    align-items: flex-start;
  }
  
  .header-actions {
    flex-direction: column;
    width: 100%;
    gap: 10px;
  }
  
  .reseller-actions {
    flex-direction: column;
    gap: 15px;
    align-items: flex-start;
  }
  
  .reseller-actions .action-buttons {
    width: 100%;
    flex-wrap: wrap;
  }
}
</style>