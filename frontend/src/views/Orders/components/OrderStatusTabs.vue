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