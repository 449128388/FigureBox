<!--
  DrawerHeader.vue - 抽屉头部子组件

  Props:
  - title: String - 标题文本

  Events:
  - close: 点击关闭按钮时触发
-->
<template>
  <div class="drawer-header">
    <div class="header-title">{{ title }}</div>
    <button class="drawer-close" @click="handleClose">✕</button>
  </div>
</template>

<script>
export default {
  name: 'DrawerHeader',

  props: {
    title: {
      type: String,
      required: true
    }
  },

  methods: {
    handleClose() {
      this.$emit('close')
    }
  }
}
</script>

<style scoped>
.drawer-header {
  padding: 20px 24px;
  border-bottom: 1px solid #EBE8E4;
  display: flex;
  align-items: center;
  justify-content: space-between;
  flex-shrink: 0;
}

.header-title {
  font-size: 17px;
  font-weight: 600;
  color: #1F1F1F;
}

.drawer-close {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  border: 1px solid #EBE8E4;
  background: #fff;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  font-size: 18px;
  color: #666;
  transition: all 0.2s;
}

.drawer-close:hover {
  border-color: #D66A6A;
  color: #D66A6A;
}
</style>
