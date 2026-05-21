<template>
  <div class="sold-orders-container">
    <!-- 头部组件 -->
    <SoldOrderHeader 
      :is-batch-mode="isBatchMode"
      :selected-count="selectedCount"
      @openAddForm="openAddForm"
      @navigateToProfile="navigateToProfile"
      @logout="handleLogout"
      @toggle-batch-mode="toggleBatchMode"
    />
    
    <!-- 批量选择工具栏 -->
    <div v-if="isBatchMode" class="batch-toolbar">
      <div class="batch-info">
        <span class="batch-count">已选择 {{ selectedCount }} 项</span>
        <el-button
          type="primary"
          size="small"
          :disabled="paginatedOrders.length === 0"
          @click="handleSelectAll"
        >
          {{ isAllSelected ? '取消全选' : '全选本页' }}
        </el-button>
      </div>
      <div class="batch-actions">
        <el-button
          type="danger"
          size="small"
          :disabled="!hasSelection"
          @click="handleBatchDelete"
        >
          批量删除
        </el-button>
        <el-button
          size="small"
          @click="exitBatchMode"
        >
          退出选择
        </el-button>
      </div>
    </div>
    
    <!-- 【新增】搜索筛选组件 -->
    <SoldOrdersSearch
      v-model:searchFigureName="searchFigureName"
      v-model:searchOrderNumber="searchOrderNumber"
      v-model:searchSellPlatform="searchSellPlatform"
      @search="handleSearch"
      @reset="handleReset"
    />

    <!-- 状态筛选 Tab 和统计 -->
    <SoldOrderStatusTabs
      :currentStatus="currentStatus"
      :statusCounts="statusCounts"
      :totalNetProfit="totalNetProfit"
      @changeStatus="handleStatusChange"
    />

    <!-- 订单列表 -->
    <div class="sold-orders-list">
      <div v-if="filteredOrders.length === 0" class="empty-state">
        <el-empty description="暂无数据" />
      </div>
      <SoldOrderItem 
        v-else 
        v-for="order in paginatedOrders" 
        :key="order.id"
        :order="order"
        :is-batch-mode="isBatchMode"
        :is-selected="isSelected(order.id)"
        @editOrder="handleEditOrder"
        @deleteOrder="openDeleteConfirmDialog"
        @toggle-selection="handleToggleSelection"
      />
    </div>
    
    <!-- 分页组件 -->
    <div v-if="totalOrders > 0" class="pagination-container">
      <el-pagination
        v-model:current-page="currentPage"
        v-model:page-size="pageSize"
        :page-sizes="pageSizes"
        layout="total, sizes, prev, pager, next, jumper"
        :total="totalOrders"
        @size-change="handleSizeChange"
        @current-change="handleCurrentChange"
      />
    </div>
    
    <!-- 添加订单表单 -->
    <SoldOrderForm
      :visible="showAddForm"
      :isEditing="isEditing"
      :newOrder="newOrder"
      :availableFigures="availableFigures"
      @saveOrder="handleSaveOrder"
      @cancel="handleCancelForm"
      @calculatePlatformFee="handleCalculatePlatformFee"
    />

    <!-- 删除确认对话框 -->
    <SoldOrderDeleteConfirmDialog
      v-model:show="showDeleteConfirmDialog"
      :order="orderToDelete"
      @confirm="confirmDelete"
      @cancel="cancelDelete"
    />
  </div>
</template>

<script setup>
import { onMounted } from 'vue'
import { useRouter } from 'vue-router'
import SoldOrderHeader from './SoldOrders/components/SoldOrderHeader.vue'
import SoldOrderStatusTabs from './SoldOrders/components/SoldOrderStatusTabs.vue'
import SoldOrderItem from './SoldOrders/components/SoldOrderItem.vue'
import SoldOrderForm from './SoldOrders/components/SoldOrderForm.vue'
import SoldOrderDeleteConfirmDialog from './SoldOrders/components/SoldOrderDeleteConfirmDialog.vue'
import SoldOrdersSearch from './SoldOrders/components/SoldOrdersSearch.vue'
import { useSoldOrderManagement } from './SoldOrders/composables/useSoldOrderManagement'

// 使用订单管理逻辑
const {
  showAddForm,
  isEditing,
  currentPage,
  pageSize,
  pageSizes,
  currentStatus,
  newOrder,
  showDeleteConfirmDialog,
  orderToDelete,
  filteredOrders,
  paginatedOrders,
  totalOrders,
  statusCounts,
  availableFigures,
  totalNetProfit,

  // 批量选择相关
  isBatchMode,
  selectedCount,
  hasSelection,
  isAllSelected,

  resetForm,
  openAddForm,
  handleSaveOrder,
  handleCancelForm,
  handleCalculatePlatformFee,
  openDeleteConfirmDialog,
  cancelDelete,
  confirmDelete,
  handleEditOrder,
  handleSizeChange,
  handleCurrentChange,
  handleStatusChange,
  handleLogout,
  initializeData,

  // 批量选择方法
  toggleBatchMode,
  handleToggleSelection,
  handleSelectAll,
  handleBatchDelete,
  exitBatchMode,
  isSelected,

  // 【新增】搜索相关
  searchFigureName,
  searchOrderNumber,
  searchSellPlatform,
  handleSearch,
  handleReset
} = useSoldOrderManagement()

// 路由
const router = useRouter()

// 导航到个人资料页面
const navigateToProfile = () => {
  router.push('/profile')
}

// 生命周期
onMounted(() => {
  initializeData()
})
</script>

<style scoped>
.sold-orders-container {
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

.sold-orders-list {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 20px;
  margin-bottom: 20px;
  align-items: stretch;
}

.sold-orders-list > * {
  height: 100%;
}

.empty-state {
  grid-column: 1 / -1;
  text-align: center;
  padding: 60px 20px;
  background-color: white;
  border-radius: 8px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
  color: #999;
  font-size: 16px;
}

.pagination-container {
  display: flex;
  justify-content: flex-end;
  margin-top: 30px;
  padding-top: 20px;
  border-top: 2px solid #e0e0e0;
}

/* 批量选择工具栏样式 */
.batch-toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: white;
  padding: 12px 20px;
  margin-bottom: 15px;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  border-left: 4px solid #3B82F6;
}

.batch-info {
  display: flex;
  align-items: center;
  gap: 15px;
}

.batch-count {
  font-size: 14px;
  font-weight: 500;
  color: #333;
}

.batch-actions {
  display: flex;
  gap: 10px;
}

.batch-toolbar .el-button {
  font-size: 14px !important;
}

@media (max-width: 768px) {
  .pagination-container {
    justify-content: center;
  }
}
</style>