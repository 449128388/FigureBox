<!--
  Orders.vue - 订单管理主页面

  功能说明：
  - 订单CRUD完整功能：添加、编辑、删除订单
  - 状态筛选：按未支付、已支付、已完成、已取消筛选
  - 统计展示：显示各状态订单数量、未支付尾款总额
  - 智能排序：按出荷日期自动排序（即将出荷优先）
  - 快捷操作：确认收货、编辑订单信息
  - 分页展示：支持自定义每页显示数量
  - 【新增】批量删除功能：支持多选订单进行批量删除

  组件依赖：
  - OrderHeader.vue - 页面头部（添加订单按钮、用户信息、批量删除按钮）
  - OrderStatusTabs.vue - 状态筛选标签页
  - OrderItem.vue - 单个订单卡片
  - OrderForm.vue - 订单表单（添加/编辑）
  - OrderDeleteConfirmDialog.vue - 删除确认对话框

  维护提示：
  - 使用 useOrderManagement composable 管理业务逻辑
  - 订单状态变化时自动重新计算统计信息
  - 确认收货操作需要二次确认
  - 删除订单前需要勾选确认复选框才能启用删除按钮
  - 【新增】批量选择模式下，订单卡片显示复选框
-->
<template>
  <TopHeader />
  <div class="orders-container">
    <!-- 头部组件 -->
    <OrderHeader 
      :is-batch-mode="isBatchMode"
      :selected-count="selectedCount"
      @openAddForm="openAddForm"
      @toggle-batch-mode="toggleBatchMode"
    />
    
    <!-- 【新增】批量选择工具栏 -->
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
    <OrdersSearch
      v-model:searchFigureName="searchFigureName"
      v-model:searchDueDateRange="searchDueDateRange"
      @search="handleSearch"
      @reset="handleReset"
      @enter-search="handleEnterSearch"
    />
    
    <!-- 状态筛选 Tab -->
    <OrderStatusTabs 
      :currentStatus="currentStatus"
      :statusCounts="statusCounts"
      :totalUnpaidBalance="totalUnpaidBalance"
      @changeStatus="handleStatusChange"
    />

    <!-- 订单列表 -->
    <div class="orders-list">
      <!-- 2026-08-06 翻页重构：空态判断改用 totalOrders（后端返回，符合当前过滤条件的总数），
           避免在分页过程中 filteredOrders 中途为 0 误触发空态 -->
      <div v-if="totalOrders === 0" class="empty-state">
        <el-empty description="暂无数据" />
      </div>
      <OrderItem 
        v-else 
        v-for="order in paginatedOrders" 
        :key="order.id"
        :order="order"
        :is-batch-mode="isBatchMode"
        :is-selected="isSelected(order.id)"
        @editOrder="handleEditOrder"
        @receiveOrder="handleReceiveOrder"
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
    <OrderForm
      :visible="showAddForm"
      :isEditing="isEditing"
      :newOrder="newOrder"
      :availableFigures="availableFigures"
      :figureError="figureError"
      :dueDateError="dueDateError"
      @saveOrder="handleSaveOrder"
      @cancel="showAddForm = false"
      @validateStep="handleValidateStep"
    />

    <!-- 删除确认对话框 -->
    <OrderDeleteConfirmDialog
      v-model:show="showDeleteConfirmDialog"
      :order="orderToDelete"
      @confirm="confirmDelete"
      @cancel="cancelDelete"
    />
  </div>
</template>

<script setup>
import { onMounted, watch } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import TopHeader from '../components/TopHeader.vue'
import OrderHeader from './Orders/components/OrderHeader.vue'
import OrderStatusTabs from './Orders/components/OrderStatusTabs.vue'
import OrderItem from './Orders/components/OrderItem.vue'
import OrderForm from './Orders/components/OrderForm.vue'
import OrderDeleteConfirmDialog from './Orders/components/OrderDeleteConfirmDialog.vue'
import OrdersSearch from './Orders/components/OrdersSearch.vue'
import { useOrderManagement } from './Orders/composables/useOrderManagement'

// 使用订单管理逻辑
const {
  showAddForm,
  isEditing,
  currentPage,
  pageSize,
  pageSizes,
  currentStatus,
  figureError,
  dueDateError,
  newOrder,
  showDeleteConfirmDialog,
  orderToDelete,
  paginatedOrders,
  totalOrders,
  statusCounts,
  availableFigures,
  totalUnpaidBalance,

  // 【新增】批量选择相关
  isBatchMode,
  selectedCount,
  hasSelection,
  isAllSelected,

  // 【新增】搜索相关
  searchFigureName,
  searchDueDateRange,

  openAddForm,
  validateForm,
  handleSaveOrder,
  openDeleteConfirmDialog,
  cancelDelete,
  confirmDelete,
  handleReceiveOrder,
  handleEditOrder,
  handleSizeChange,
  handleCurrentChange,
  handleStatusChange,
  handleLogout,
  initializeData,

  // 【新增】批量选择方法
  toggleBatchMode,
  handleToggleSelection,
  handleSelectAll,
  handleBatchDelete,
  exitBatchMode,
  isSelected,

  // 【新增】搜索方法
  handleSearch,
  handleEnterSearch,
  handleReset
} = useOrderManagement()

// 路由
const router = useRouter()
const route = useRoute()

// 导航到个人资料页面
const navigateToProfile = () => {
  router.push('/profile')
}

/**
 * 处理 OrderForm 抛出的步骤校验事件
 * OrderForm 在用户点击「下一步」/ 点击未达步骤 / 保存前会 emit 此事件
 * 这里调用 validateForm 来设置 figureError / dueDateError,使步骤 1 的错误提示在表单中显示
 */
const handleValidateStep = (step) => {
  if (step === 1) {
    validateForm()
  }
}

// 生命周期
onMounted(() => {
  initializeData()
})

// 处理从动态流跳转过来的编辑订单请求
// 2026-08-06 翻页重构：监听 paginatedOrders（后端返回的当前页订单），
// filteredOrders 已删除；paginatedOrders 在订单加载完成后会触发 watch
watch(paginatedOrders, (orders) => {
  const editOrderId = route.query.editOrderId
  if (editOrderId && orders.length > 0) {
    const order = orders.find(o => o.id === Number(editOrderId))
    if (order) {
      handleEditOrder(order)
    }
  }
})
</script>

<style scoped>
.orders-container {
  margin-top: 84px;
  width: 100%;
  max-width: 1650px;
  margin-left: 50px;
  margin-right: 50px;
  padding: 20px;
  background-color: #f9f9f9;
  border-radius: 8px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
}

.orders-list {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
  gap: 15px;
  margin-bottom: 20px;
  /* 确保所有卡片高度一致 */
  align-items: stretch;
}

.orders-list > * {
  /* 确保每个订单卡片占据完整的网格高度 */
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

/* 【新增】批量选择工具栏样式 */
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

/* 【新增】批量工具栏按钮样式 - 字体大小14px */
.batch-toolbar .el-button {
  font-size: 14px !important;
}

@media (max-width: 768px) {
  .pagination-container {
    justify-content: center;
  }
}
</style>