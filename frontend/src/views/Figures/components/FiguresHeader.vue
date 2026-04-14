<template>
  <div class="header">
    <h2>手办管理</h2>
    <div class="header-actions">
      <div class="action-buttons">
        <button class="btn btn-add" @click="$emit('open-add-form')">添加手办</button>
        <button class="btn btn-import" @click="$emit('import-figures')">
          <i class="fa-solid fa-upload"></i> 导入手办
        </button>
        <button class="btn btn-download" @click="$emit('download-figures')">
          <i class="fa-solid fa-download"></i> 下载数据
        </button>
        <button class="btn btn-refresh" @click="$emit('refresh-figures')">
          <i class="fa-solid fa-refresh"></i>
        </button>
      </div>
      <div class="user-info">
        <span v-if="userStore.isAuthenticated">当前用户：</span>
        <span v-if="userStore.isAuthenticated" class="username" @click="$router.push('/profile')" style="cursor: pointer; color: #2196F3; text-decoration: underline;">{{ userStore.currentUser?.username }}</span>
        <button v-if="userStore.isAuthenticated" class="btn btn-logout" @click="$emit('logout')">退出</button>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'FiguresHeader',
  props: {
    userStore: {
      type: Object,
      required: true
    }
  },
  emits: ['open-add-form', 'import-figures', 'download-figures', 'refresh-figures', 'logout']
}
</script>

<style scoped>
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

.btn-add {
  background-color: #4CAF50;
  color: white;
  padding: 12px 24px;
  font-size: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
  height: 44px;
  box-sizing: border-box;
}

.btn-add:hover {
  background-color: #45a049;
}

.btn-download {
  background-color: #ff9800;
  color: white;
  padding: 12px 24px;
  font-size: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  height: 44px;
  box-sizing: border-box;
}

.btn-download:hover {
  background-color: #f57c00;
}

.btn-refresh {
  background-color: #2196F3;
  color: white;
  padding: 10px 12px;
  font-size: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
  width: 40px;
  height: 40px;
}

.btn-refresh:hover {
  background-color: #0b7dda;
}

.btn-import {
  background-color: #9C27B0;
  color: white;
  padding: 12px 24px;
  font-size: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  height: 44px;
  box-sizing: border-box;
}

.btn-import:hover {
  background-color: #7B1FA2;
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
</style>
