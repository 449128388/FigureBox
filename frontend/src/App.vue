<template>
  <div>
    <!-- 只在非首页、登录页、注册页显示侧边栏 -->
    <Sidebar v-if="!isSpecialPage" @toggle="handleSidebarToggle" />
    <div class="main-wrapper" :style="{ marginLeft: getMarginLeft() }">
      <div id="app">
        <router-view />
      </div>
    </div>
  </div>
</template>

<script>
import Sidebar from './components/Sidebar.vue'

export default {
  name: 'App',
  components: {
    Sidebar
  },
  data() {
    return {
      isSidebarCollapsed: false
    }
  },
  computed: {
    isSpecialPage() {
      const currentPath = this.$route.path
      return ['/', '/home', '/login', '/register', '/profile'].includes(currentPath)
    }
  },
  methods: {
    handleSidebarToggle(collapsed) {
      this.isSidebarCollapsed = collapsed
    },
    getMarginLeft() {
      if (this.isSpecialPage) {
        return '0px'
      }
      return this.isSidebarCollapsed ? '0px' : '20px'
    }
  }
}
</script>

<style>
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  font-family: Arial, sans-serif;
  background-color: #f5f5f5;
}

.main-wrapper {
  transition: margin-left 0.3s ease;
  display: flex;
  justify-content: center;
  align-items: flex-start;
  min-height: 100vh;
  padding: 20px;
  width: 100%;
}

#app {
  max-width: 1600px;
  margin-left: 50px;
  margin-right: 50px;
  padding: 20px;
  width: 100%;
}

/* 确保figures-container和orders-container继续居中展示 */
.figures-container,
.orders-container {
  margin: 0 auto;
  width: 100%;
  max-width: 100%;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .main-wrapper {
    margin-left: 0 !important;
  }
}
</style>