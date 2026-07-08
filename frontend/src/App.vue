<template>
  <div>
    <div class="main-wrapper">
      <div id="app">
        <router-view />
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'App'
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
  display: flex;
  justify-content: center;
  align-items: flex-start;
  min-height: 100vh;
  padding: 0 20px 20px;
  width: 100%;
}

/* 默认宽度设置（适用于1920*1080分辨率，视口约1920px） */
#app {
  max-width: 1800px;
  margin-left: 50px;
  margin-right: 50px;
  padding: 0 20px 20px;
  width: 100%;
}

/* 2560*1600分辨率（考虑150%缩放后视口约1707px）使用1600px宽度 */
@media (min-width: 1700px) and (max-width: 1800px) {
  #app {
    max-width: 1600px;
  }
}

/* 确保figures-container和orders-container继续居中展示 */
.figures-container,
.orders-container {
  margin: 0 auto;
  width: 100%;
  max-width: 100%;
}
</style>
