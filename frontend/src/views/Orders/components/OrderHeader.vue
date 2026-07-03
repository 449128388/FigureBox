<!--
  OrderHeader.vue - 订单管理页面头部组件

  功能说明：
  - 展示页面标题"尾款管理"
  - 提供添加订单按钮
  - 显示当前登录用户信息和退出按钮
  - 【新增】提供批量删除模式的切换按钮

  组件依赖：
  - 使用 useUserStore 获取用户信息
  - 【新增】接收 isBatchMode 作为 props，控制批量删除模式状态
  - 【新增】接收 selectedCount 作为 props，显示已选择数量

  维护提示：
  - 添加订单按钮通过 openAddForm 事件向父组件传递
  - 用户信息显示根据 userStore.isAuthenticated 判断
  - 退出按钮通过 logout 事件向父组件传递
  - 用户名点击通过 navigateToProfile 事件向父组件传递
  - 【新增】批量删除按钮通过 toggle-batch-mode 事件向父组件传递
-->
<template>
  <div class="header">
    <h2>尾款管理</h2>
    <div class="header-actions">
      <div class="action-buttons">
        <button class="btn btn-add" @click="$emit('openAddForm')">添加订单</button>
        <button
          class="btn"
          :class="isBatchMode ? 'btn-batch-active' : 'btn-batch'"
          @click="$emit('toggle-batch-mode')"
        >
          <i class="fa-solid fa-check-square"></i>
          {{ isBatchMode ? '退出选择' : '批量删除' }}
          <span v-if="isBatchMode && selectedCount > 0" class="batch-badge">{{ selectedCount }}</span>
        </button>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'OrderHeader',
  props: {
    isBatchMode: {
      type: Boolean,
      default: false
    },
    selectedCount: {
      type: Number,
      default: 0
    }
  },
  emits: ['openAddForm', 'toggle-batch-mode']
}
</script>

<style scoped>
.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 30px;
  padding-bottom: 20px;
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

.action-buttons {
  display: flex;
  align-items: center;
  gap: 10px;
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

.btn-add {
  background-color: #4CAF50;
  color: white;
  padding: 12px 24px;
  font-size: 16px;
}

.btn-add:hover {
  background-color: #45a049;
}

/* 【新增】批量删除按钮样式 */
.btn-batch {
  background-color: #607d8b;
  color: white;
  padding: 12px 20px;
  font-size: 14px;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
  height: 44px;
  box-sizing: border-box;
  position: relative;
}

.btn-batch:hover {
  background-color: #546e7a;
}

.btn-batch-active {
  background-color: #3B82F6;
  color: white;
  padding: 12px 20px;
  font-size: 14px;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
  height: 44px;
  box-sizing: border-box;
  position: relative;
  box-shadow: 0 0 0 2px rgba(59, 130, 246, 0.3);
}

.btn-batch-active:hover {
  background-color: #2563eb;
}

.batch-badge {
  background-color: #ff4444;
  color: white;
  font-size: 12px;
  font-weight: 600;
  padding: 2px 6px;
  border-radius: 10px;
  margin-left: 4px;
}

.action-buttons {
  display: flex;
  align-items: center;
  gap: 10px;
}
</style>