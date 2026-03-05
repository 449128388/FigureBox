<template>
  <div class="sidebar" :class="{ 'collapsed': isCollapsed }">
    <div class="sidebar-header">
      <h3 v-if="!isCollapsed">手办管理系统</h3>
      <button class="toggle-btn" @click="toggleSidebar">
        {{ isCollapsed ? '>' : '<' }}
      </button>
    </div>
    <div class="sidebar-menu">
            <router-link to="/home" class="menu-item" active-class="active">
              <span class="menu-icon">🏠</span>
              <span v-if="!isCollapsed" class="menu-text">首页</span>
            </router-link>
            <router-link to="/figures" class="menu-item" active-class="active">
              <span class="menu-icon">🎎</span>
              <span v-if="!isCollapsed" class="menu-text">手办管理</span>
            </router-link>
            <router-link to="/orders" class="menu-item" active-class="active">
              <span class="menu-icon">📋</span>
              <span v-if="!isCollapsed" class="menu-text">订单管理</span>
            </router-link>
          </div>
  </div>
</template>

<script>
export default {
  name: 'Sidebar',
  data() {
    return {
      isCollapsed: true
    }
  },
  methods: {
    toggleSidebar() {
      this.isCollapsed = !this.isCollapsed
      this.$emit('toggle', this.isCollapsed)
    }
  }
}
</script>

<style scoped>
.sidebar {
  width: 200px;
  height: 100vh;
  background-color: #333;
  color: white;
  transition: width 0.3s ease;
  position: fixed;
  left: 0;
  top: 0;
  z-index: 1000;
  box-shadow: 2px 0 5px rgba(0, 0, 0, 0.2);
}

.sidebar.collapsed {
  width: 60px;
}

.sidebar-header {
  padding: 20px;
  border-bottom: 1px solid #444;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.sidebar-header h3 {
  margin: 0;
  font-size: 18px;
  font-weight: 600;
}

.toggle-btn {
  background: none;
  border: none;
  color: white;
  font-size: 20px;
  cursor: pointer;
  padding: 0;
  width: 30px;
  height: 30px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 4px;
  transition: background-color 0.3s ease;
}

.toggle-btn:hover {
  background-color: rgba(255, 255, 255, 0.1);
}

.sidebar-menu {
  padding: 20px 0;
}

.menu-item {
  display: flex;
  align-items: center;
  padding: 12px 20px;
  color: white;
  text-decoration: none;
  transition: all 0.3s ease;
  border-left: 3px solid transparent;
}

.menu-item:hover {
  background-color: rgba(255, 255, 255, 0.1);
}

.menu-item.active {
  background-color: rgba(76, 175, 80, 0.2);
  border-left-color: #4CAF50;
}

.menu-icon {
  font-size: 20px;
  margin-right: 12px;
  width: 24px;
  text-align: center;
}

.menu-text {
  font-size: 14px;
  font-weight: 500;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .sidebar {
    width: 100%;
    height: auto;
    position: relative;
  }
  
  .sidebar.collapsed {
    width: 100%;
  }
  
  .sidebar-menu {
    display: flex;
    justify-content: space-around;
  }
  
  .menu-item {
    flex-direction: column;
    padding: 10px;
    text-align: center;
  }
  
  .menu-icon {
    margin-right: 0;
    margin-bottom: 5px;
  }
  
  .menu-text {
    font-size: 12px;
  }
}
</style>