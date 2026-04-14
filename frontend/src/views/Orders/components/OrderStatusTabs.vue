<!--
  OrderStatusTabs.vue - 订单状态标签组件

  功能说明：
  - 提供订单状态筛选标签
  - 包含全部、未支付、已支付、已取消等状态
  - 显示各状态的订单数量
  - 支持点击切换状态

  组件依赖：
  - 接收 currentStatus 作为 props，显示当前选中状态
  - 接收 statusCounts 作为 props，显示各状态的订单数量

  维护提示：
  - 状态切换通过 changeStatus 事件向父组件传递
  - 激活状态通过 active 类名控制
-->
<template>
  <div class="status-tabs">
    <div 
      class="status-tab" 
      :class="{ active: currentStatus === 'all' }"
      @click="$emit('changeStatus', 'all')"
    >
      全部 ({{ statusCounts.all }})
    </div>
    <div 
      class="status-tab" 
      :class="{ active: currentStatus === '未支付' }"
      @click="$emit('changeStatus', '未支付')"
    >
      未支付 ({{ statusCounts['未支付'] }})
    </div>
    <div 
      class="status-tab" 
      :class="{ active: currentStatus === '已支付' }"
      @click="$emit('changeStatus', '已支付')"
    >
      已支付 ({{ statusCounts['已支付'] }})
    </div>
    <div 
      class="status-tab" 
      :class="{ active: currentStatus === '已取消' }"
      @click="$emit('changeStatus', '已取消')"
    >
      已取消 ({{ statusCounts['已取消'] }})
    </div>
    <div 
      class="status-tab" 
      :class="{ active: currentStatus === '已完成' }"
      @click="$emit('changeStatus', '已完成')"
    >
      已完成 ({{ statusCounts['已完成'] }})
    </div>
    <div class="status-tab balance-tab">
      待补款: ¥{{ totalUnpaidBalance.toFixed(2) }}
    </div>
  </div>
</template>

<script>
export default {
  name: 'OrderStatusTabs',
  props: {
    currentStatus: {
      type: String,
      default: '未支付'
    },
    statusCounts: {
      type: Object,
      required: true
    },
    totalUnpaidBalance: {
      type: Number,
      default: 0
    }
  },
  emits: ['changeStatus']
}
</script>

<style scoped>
.status-tabs {
  display: flex;
  gap: 10px;
  margin-bottom: 20px;
  padding: 10px;
  background-color: white;
  border-radius: 8px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.status-tab {
  padding: 10px 20px;
  border-radius: 6px;
  cursor: pointer;
  font-size: 14px;
  font-weight: 500;
  color: #666;
  background-color: #f5f5f5;
  transition: all 0.3s ease;
  border: 2px solid transparent;
}

.status-tab:hover {
  background-color: #e8e8e8;
  transform: translateY(-1px);
}

.status-tab.active {
  background-color: #2196F3;
  color: white;
  border-color: #1976D2;
  box-shadow: 0 2px 8px rgba(33, 150, 243, 0.3);
}

.status-tab.active:hover {
  background-color: #1976D2;
}

/* 待补款统计项样式 */
.status-tab.balance-tab {
  margin-left: auto;
  background-color: #FF9800;
  color: white;
  border-color: #F57C00;
  font-weight: 600;
}

.status-tab.balance-tab:hover {
  background-color: #F57C00;
  transform: translateY(-1px);
  box-shadow: 0 2px 8px rgba(255, 152, 0, 0.3);
}
</style>