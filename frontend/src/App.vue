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
  height: 911px;
  margin-top: -20px;
}

/* 默认宽度设置（适用于1920*1080分辨率，视口约1920px） */
#app {
  max-width: 1800px;
  height: 911px;
  margin-left: 50px;
  margin-right: 50px;
  padding: 20px;
  width: 100%;
  margin-top: -20px;
}

/* 2560*1600分辨率（考虑150%缩放后视口约1707px）使用1600px宽度 */
/* 1700px-1800px范围是2560×1600分辨率150%缩放后的视口宽度 */
@media (min-width: 1700px) and (max-width: 1800px) {
  #app {
    max-width: 1600px;
    height: 858px;
  }
}

/* 确保figures-container和orders-container继续居中展示 */
.figures-container,
.orders-container {
  margin: 0 auto;
  width: 100%;
  max-width: 100%;
}

/* 响应式设计 */
@media (min-width: 1700px) and (max-width: 1800px) {
  .main-wrapper {
    margin-left: 0 !important;
    margin-top: -20px;
    height: 858px;
  }
}
</style>
