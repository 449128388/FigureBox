<!--
  FigureOrders.vue - 手办订单信息组件

  功能说明：
  - 展示手办关联的订单信息（尾款信息）
  - 支持多个订单的标签切换
  - 订单数量超过4个时支持折叠展开
  - 显示订单的详细信息，包括金额、状态、支付期限等

  组件依赖：
  - 接收 relatedOrders 作为 props，包含订单数组

  维护提示：
  - 活动订单索引通过 activeOrderIndex 控制
  - 订单展开状态通过 isOrdersExpanded 控制
  - 仅在有订单时显示（relatedOrders.length > 0）
-->
<template>
  <div class="info-section" v-if="relatedOrders.length > 0">
    <h2>尾款信息</h2>
    
    <!-- 订单切换标签 -->
    <div class="order-tabs" v-if="relatedOrders.length > 1">
      <!-- 显示前4个订单标签 -->
      <div 
        v-for="(order, index) in displayedOrders" 
        :key="order.id"
        class="order-tab"
        :class="{ active: activeOrderIndex === index }"
        @click="activeOrderIndex = index"
      >
        订单 {{ index + 1 }} ({{ order.status }})
      </div>
      <!-- 折叠展开按钮 -->
      <div 
        v-if="relatedOrders.length > 4"
        class="order-tab expand-tab"
        @click="toggleExpandOrders"
      >
        <span v-if="!isOrdersExpanded">+{{ relatedOrders.length - 4 }}</span>
        <span v-else>收起</span>
      </div>
      <!-- 展开后显示的额外订单标签 -->
      <template v-if="isOrdersExpanded">
        <div 
          v-for="(order, index) in expandedOrders" 
          :key="order.id"
          class="order-tab"
          :class="{ active: activeOrderIndex === index + 4 }"
          @click="activeOrderIndex = index + 4"
        >
          订单 {{ index + 5 }} ({{ order.status }})
        </div>
      </template>
    </div>
    
    <div class="info-item" v-if="selectedOrder.deposit !== null && selectedOrder.deposit !== undefined">
      <span class="label">定金:</span>
      <span class="value">¥{{ selectedOrder.deposit }}</span>
    </div>
    <div class="info-item" v-if="selectedOrder.balance !== null && selectedOrder.balance !== undefined">
      <span class="label">尾款:</span>
      <span class="value">¥{{ selectedOrder.balance }}</span>
    </div>
    <div class="info-item" v-if="selectedOrder.due_date">
      <span class="label">出荷日期:</span>
      <span class="value">{{ selectedOrder.due_date }}</span>
    </div>
    <div class="info-item" v-if="selectedOrder.status">
      <span class="label">尾款状态:</span>
      <span class="value" :class="getStatusClass(selectedOrder.status)">{{ selectedOrder.status }}</span>
    </div>
    <div class="info-item" v-if="selectedOrder.shop_name">
      <span class="label">购买店铺:</span>
      <span class="value">{{ selectedOrder.shop_name }}</span>
    </div>
    <div class="info-item" v-if="selectedOrder.shop_contact">
      <span class="label">联系方式:</span>
      <span class="value">{{ selectedOrder.shop_contact }}</span>
    </div>
    <div class="info-item" v-if="selectedOrder.tracking_number">
      <span class="label">物流订单:</span>
      <a class="value tracking-link" :href="`https://www.baidu.com/s?wd=${encodeURIComponent(selectedOrder.tracking_number)}`" target="_blank" rel="noopener noreferrer">{{ selectedOrder.tracking_number }}</a>
    </div>
  </div>
</template>

<script>
export default {
  name: 'FigureOrders',
  props: {
    relatedOrders: {
      type: Array,
      default: () => []
    }
  },
  data() {
    return {
      activeOrderIndex: 0,
      isOrdersExpanded: false // 订单标签是否展开
    }
  },
  computed: {
    // 当前选中的订单
    selectedOrder() {
      return this.relatedOrders.length > 0 ? this.relatedOrders[this.activeOrderIndex] : null
    },
    // 显示的前4个订单
    displayedOrders() {
      return this.relatedOrders.slice(0, 4)
    },
    // 展开后显示的额外订单（第5个及以后）
    expandedOrders() {
      return this.relatedOrders.slice(4)
    }
  },
  methods: {
    // 获取状态样式类
    getStatusClass(status) {
      switch(status) {
        case '未支付': return 'status-unpaid'
        case '已支付': return 'status-paid'
        case '已完成': return 'status-paid'
        case '已取消': return 'status-cancelled'
        default: return ''
      }
    },
    // 切换订单标签展开/折叠状态
    toggleExpandOrders() {
      this.isOrdersExpanded = !this.isOrdersExpanded
    }
  }
}
</script>

<style scoped>
.info-section {
  background-color: white;
  padding: 20px;
  border-radius: 8px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
}

.info-section h2 {
  margin-top: 0;
  margin-bottom: 20px;
  color: #333;
  font-size: 20px;
  font-weight: 600;
  border-bottom: 1px solid #e0e0e0;
  padding-bottom: 10px;
}

.info-item {
  display: flex;
  margin-bottom: 12px;
}

.label {
  flex: 0 0 100px;
  font-weight: 500;
  color: #666;
}

.value {
  flex: 1;
  color: #333;
  padding: 2px 0;
  min-height: 20px;
  line-height: 1.5;
}

/* 尾款状态样式 */
.status-unpaid {
  color: #f44336;
  font-weight: 600;
}

.status-paid {
  color: #4CAF50;
  font-weight: 600;
}

.status-cancelled {
  color: #9e9e9e;
  font-weight: 600;
}

/* 物流订单链接样式 */
.tracking-link {
  color: #2196F3;
  cursor: pointer;
  text-decoration: none;
}

.tracking-link:hover {
  color: #1976D2;
}

/* 订单切换标签样式 */
.order-tabs {
  display: flex;
  gap: 10px;
  margin-bottom: 20px;
  flex-wrap: wrap;
}

.order-tab {
  padding: 8px 16px;
  background-color: #f5f5f5;
  border-radius: 20px;
  cursor: pointer;
  font-size: 14px;
  font-weight: 500;
  color: #666;
  transition: all 0.3s ease;
  border: 2px solid transparent;
}

.order-tab:hover {
  background-color: #e8e8e8;
  color: #333;
  transform: translateY(-1px);
}

.order-tab.active {
  background-color: #2196F3;
  color: white;
  border-color: #1976D2;
  box-shadow: 0 2px 8px rgba(33, 150, 243, 0.3);
}

.order-tab.active:hover {
  background-color: #1976D2;
  color: white;
}

/* 展开按钮样式 */
.order-tab.expand-tab {
  background-color: #e3f2fd;
  color: #2196F3;
  border: 2px dashed #2196F3;
  font-weight: 600;
}

.order-tab.expand-tab:hover {
  background-color: #2196F3;
  color: white;
  border-style: solid;
}
</style>