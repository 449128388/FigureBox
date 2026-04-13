<template>
  <div class="orders-container">
    <div class="header">
      <h2>资产看板</h2>
      <div class="header-actions">
        <div class="action-buttons">
          <el-button 
            :type="currentMode === 'reseller' ? 'success' : 'info'"
            @click="toggleMode"
          >
            {{ currentMode === 'reseller' ? '收藏家模式' : '倒狗模式' }}
          </el-button>
        </div>
        <div class="user-info">
          <span v-if="userStore.isAuthenticated">当前用户：</span>
          <span v-if="userStore.isAuthenticated" class="username" @click="$router.push('/profile')" style="cursor: pointer; color: #2196F3; text-decoration: underline;">{{ userStore.currentUser?.username }}</span>
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
            <el-button type="primary" @click="exportBill">
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
        @open-buy-dialog="openBuyDialog"
        @open-sell-dialog="openSellDialog"
        @open-payment-dialog="openPaymentDialog"
        @open-cancel-dialog="openCancelDialog"
        @view-record="viewRecord"
        @delete-record="deleteRecord"
      />
    </div>

    <!-- 收藏家模式内容 -->
    <div v-else class="collector-mode">
      <CollectorHeader
        @share-poster="sharePoster"
        @privacy-settings="privacySettings"
      />
      
      <CollectorOverview :collector-data="collectorData" />
      
      <ValuableCollections :collector-data="collectorData" />
      
      <TagCloud
        :collector-data="collectorData"
        @filter-by-tag="filterByTag"
      />
      
      <ActivityFeed
        :collector-data="collectorData"
        @activity-action="handleActivityAction"
      />
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
import ValuableCollections from './Dashboard/components/collector/ValuableCollections.vue'
import TagCloud from './Dashboard/components/collector/TagCloud.vue'
import ActivityFeed from './Dashboard/components/collector/ActivityFeed.vue'

// 导入倒狗模式组件
import AssetView from './Dashboard/components/reseller/AssetView.vue'
import MarketView from './Dashboard/components/reseller/MarketView.vue'
import TradeView from './Dashboard/components/reseller/TradeView.vue'

// 导入收藏家模式 composable
import { useCollectorData } from './Dashboard/composables/useCollectorData'

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
    ValuableCollections,
    TagCloud,
    ActivityFeed,
    // 倒狗模式组件
    AssetView,
    MarketView,
    TradeView
  },
  setup() {
    const router = useRouter()
    const userStore = useUserStore()
    const dashboardData = ref(null)
    const loading = ref(true)
    
    // 使用收藏家模式 composable
    const { collectorData, loading: collectorLoading, fetchCollectorData, sharePoster, privacySettings, filterByTag, handleActivityAction } = useCollectorData()
    
    const activeView = ref('asset')
    const alertDialogVisible = ref(false)
    const figures = ref([])
    const currentMode = ref('reseller')
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
      try {
        const res = await axios.get('/assets/dashboard')
        dashboardData.value = res
      } catch (error) {
        console.error('获取资产数据失败:', error)
      }
    }
    
    // 获取交易数据
    const fetchTradeData = async () => {
      try {
        const res = await axios.get('/assets/trade/records')
        tradeData.value = res
      } catch (error) {
        console.error('获取交易数据失败:', error)
      }
    }
    
    // 获取行情数据
    const fetchMarketData = async () => {
      try {
        const res = await axios.get('/assets/market/dashboard')
        marketData.value = res
      } catch (error) {
        console.error('获取行情数据失败:', error)
        // 生成模拟数据
        marketData.value = {
          index: {
            value: 2847.35,
            change: 45.20,
            change_percentage: 1.61,
            volume: 230000000,
            up_count: 1230,
            flat_count: 45,
            down_count: 320,
            limit_up: '初音、蕾姆、狂三',
            limit_down: '无'
          },
          kline: {
            macd: '金叉',
            rsi: 68
          },
          sectors: [
            {
              name: '初音未来概念',
              change: 8.5,
              stocks: '初音韶华、赛车音、雪未来'
            },
            {
              name: 'FGO系列',
              change: 5.2,
              stocks: '摩根、妖兰、提亚马特'
            },
            {
              name: '碧蓝航线',
              change: 3.1,
              stocks: '信浓、柴郡、埃吉尔'
            },
            {
              name: '原神系列',
              change: -2.3,
              stocks: '雷神、神子(高位回调)'
            }
          ],
          watchlist: [
            {
              name: '初音韶华',
              current_price: 2000,
              change: 15,
              target_price: 2500,
              target_distance: '还差25%'
            },
            {
              name: '蕾姆婚纱',
              current_price: 1200,
              change: -5,
              target_price: 1500,
              target_distance: '还需上涨30%'
            },
            {
              name: '(观望中)',
              current_price: 800,
              change: 0,
              target_price: 600,
              target_distance: '等破发入手'
            }
          ],
          research: {
            rating: 'GSC 初音韶华 买入',
            target_price: '¥2,800 (+40%)',
            stop_loss: '¥1,600 (-20%)',
            institution: 'Hpoi研究院',
            date: '2026-04-01',
            reason: '再版停产公告+海景房属性+即将出荷'
          }
        }
      }
    }
    
    // 刷新数据
    const refreshData = async () => {
      if (activeView.value === 'asset') {
        await fetchDashboardData()
      } else if (activeView.value === 'market') {
        await fetchMarketData()
      }
    }
    
    // 刷新交易数据
    const refreshTradeData = async () => {
      await fetchTradeData()
    }
    
    // 切换模式
    const toggleMode = () => {
      currentMode.value = currentMode.value === 'reseller' ? 'collector' : 'reseller'
      if (currentMode.value === 'collector') {
        fetchCollectorData()
      }
    }
    
    // 显示年度消费上限对话框
    const showAnnualLimitDialog = () => {
      annualLimitDialogVisible.value = true
    }
    
    // 保存年度消费上限
    const saveAnnualLimit = async () => {
      annualLimitLoading.value = true
      try {
        await axios.post('/assets/annual-limit', {
          limit: annualLimitForm.value.limit
        })
        ElMessage.success('年度消费上限设置成功')
        annualLimitDialogVisible.value = false
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
      ElMessage.info(`卖出 ${item.figure_name} 功能开发中`)
    }
    
    const addPosition = (item) => {
      ElMessage.info(`补仓 ${item.figure_name} 功能开发中`)
    }
    
    const cutLoss = (item) => {
      ElMessage.info(`斩仓 ${item.figure_name} 功能开发中`)
    }
    
    const editPrice = (item) => {
      ElMessage.info(`修改 ${item.figure_name} 现价功能开发中`)
    }
    
    // 添加到自选股
    const addToWatchlist = () => {
      ElMessage.info('添加自选股功能开发中')
    }
    
    // 交易操作
    const openBuyDialog = () => {
      ElMessage.info('买入功能开发中')
    }
    
    const openSellDialog = () => {
      ElMessage.info('卖出功能开发中')
    }
    
    const openPaymentDialog = () => {
      ElMessage.info('补款功能开发中')
    }
    
    const openCancelDialog = () => {
      ElMessage.info('撤单功能开发中')
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
      annualLimitDialogVisible,
      annualLimitForm,
      annualLimitLoading,
      formatNumber,
      refreshData,
      refreshTradeData,
      openAlertSettings,
      createAlert,
      toggleMode,
      showAnnualLimitDialog,
      saveAnnualLimit,
      exportBill,
      fetchCollectorData,
      sharePoster,
      privacySettings,
      filterByTag,
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
      logout
    }
  }
}
</script>

<style scoped>
.orders-container {
  margin-top: 20px;
  width: 100%;
  max-width: 1650px;
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

.header h2 {
  margin: 0;
  color: #333;
  font-size: 24px;
  font-weight: 600;
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
  gap: 15px;
  padding: 10px 15px;
  background-color: white;
  border-radius: 6px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
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
  background-color: #f44336;
  color: white;
  padding: 8px 16px;
  font-size: 14px;
}

.btn-logout:hover {
  background-color: #da190b;
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