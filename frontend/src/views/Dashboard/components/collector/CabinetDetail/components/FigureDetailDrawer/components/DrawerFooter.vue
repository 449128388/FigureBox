<!--
  DrawerFooter.vue - 抽屉底部操作区子组件

  Events:
  - close: 点击关闭按钮时触发
  - sell: 点击出柜登记按钮时触发
-->
<template>
  <div class="drawer-footer">
    <button class="btn btn-default" @click="handleClose">关闭</button>
    <button class="btn btn-default" @click="handleSell">🏷️ 出柜登记</button>
  </div>
</template>

<script>
export default {
  name: 'DrawerFooter',

  methods: {
    handleClose() {
      this.$emit('close')
    },

    handleSell() {
      this.$emit('sell')
    }
  }
}
</script>

<style scoped>
.drawer-footer {
  padding: 16px 24px;
  border-top: 1px solid #EBE8E4;
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  flex-shrink: 0;
}

.btn {
  padding: 9px 20px;
  border-radius: 8px;
  font-size: 14px;
  cursor: pointer;
  border: 1px solid transparent;
  transition: all 0.2s;
}

.btn-default {
  background: #fff;
  border-color: #EBE8E4;
  color: #666;
}

.btn-default:hover {
  border-color: #C49A6C;
  color: #C49A6C;
}

.btn-primary {
  background: #C49A6C;
  border-color: #C49A6C;
  color: #fff;
}

.btn-primary:hover {
  background: #B0855A;
  border-color: #B0855A;
}
</style>
