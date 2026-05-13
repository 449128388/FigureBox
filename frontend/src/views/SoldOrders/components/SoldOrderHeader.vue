<template>
  <div class="header">
    <h2>已出售订单</h2>
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
      <div class="user-info">
        <span v-if="userStore.isAuthenticated">当前用户：</span>
        <span v-if="userStore.isAuthenticated" class="username" @click="$emit('navigateToProfile')" style="cursor: pointer; color: #2196F3; text-decoration: underline;">{{ userStore.currentUser?.username }}</span>
        <button v-if="userStore.isAuthenticated" class="btn btn-logout" @click="$emit('logout')">退出</button>
      </div>
    </div>
  </div>
</template>

<script>
import { useUserStore } from '../../../store'

export default {
  name: 'SoldOrderHeader',
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
  emits: ['openAddForm', 'navigateToProfile', 'logout', 'toggle-batch-mode'],
  computed: {
    userStore() {
      return useUserStore()
    }
  }
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

.btn-add {
  background-color: #4CAF50;
  color: white;
  padding: 12px 24px;
  font-size: 16px;
}

.btn-add:hover {
  background-color: #45a049;
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