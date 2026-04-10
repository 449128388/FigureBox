<template>
  <div class="orders-container">
    <!-- 头部组件 -->
    <OrderHeader 
      @openAddForm="openAddForm"
      @navigateToProfile="navigateToProfile"
      @logout="handleLogout"
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
      <div v-if="filteredOrders.length === 0" class="empty-state">
        <p>暂无数据</p>
      </div>
      <OrderItem 
        v-else 
        v-for="order in paginatedOrders" 
        :key="order.id"
        :order="order"
        @editOrder="handleEditOrder"
        @receiveOrder="handleReceiveOrder"
        @deleteOrder="handleDeleteOrder"
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
      @saveOrder="handleSaveOrder"
      @cancel="showAddForm = false"
    />
  </div>
</template>

<script setup>
import { onMounted } from 'vue'
import { useRouter } from 'vue-router'
import OrderHeader from './Orders/components/OrderHeader.vue'
import OrderStatusTabs from './Orders/components/OrderStatusTabs.vue'
import OrderItem from './Orders/components/OrderItem.vue'
import OrderForm from './Orders/components/OrderForm.vue'
import { useOrderManagement } from './Orders/composables/useOrderManagement'

// 使用订单管理逻辑
const {
  showAddForm,
  isEditing,
  currentPage,
  pageSize,
  pageSizes,
  currentStatus,
  newOrder,
  filteredOrders,
  paginatedOrders,
  totalOrders,
  statusCounts,
  availableFigures,
  totalUnpaidBalance,
  openAddForm,
  handleSaveOrder,
  handleDeleteOrder,
  handleReceiveOrder,
  handleEditOrder,
  handleSizeChange,
  handleCurrentChange,
  handleStatusChange,
  handleLogout,
  initializeData
} = useOrderManagement()

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

.orders-list {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
  gap: 15px;
  margin-bottom: 20px;
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

@media (max-width: 768px) {
  .pagination-container {
    justify-content: center;
  }
}
</style>