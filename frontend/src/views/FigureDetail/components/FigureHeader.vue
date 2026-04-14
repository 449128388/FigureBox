<!--
  FigureHeader.vue - 手办详情头部组件

  功能说明：
  - 展示手办的中文名称
  - 提供返回列表的按钮
  - 布局采用左右对齐的方式

  组件依赖：
  - 接收 figure 作为 props，包含 name 字段

  维护提示：
  - 返回按钮通过 $router.push('/figures') 跳转
  - 布局使用 flex 实现左右对齐
-->
<template>
  <div class="header">
    <h1>中文名称：{{ figure.name }}</h1>
    <button class="btn btn-back" @click="goBack">返回列表</button>
  </div>
</template>

<script>
export default {
  name: 'FigureHeader',
  props: {
    figure: {
      type: Object,
      required: true
    }
  },
  methods: {
    goBack() {
      this.$router.push('/figures')
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

.header h1 {
  margin: 0;
  color: #333;
  font-size: 28px;
  font-weight: 600;
}

.btn-back {
  padding: 10px 20px;
  background-color: #2196F3;
  color: white;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-size: 14px;
  font-weight: 500;
  transition: all 0.3s ease;
}

.btn-back:hover {
  background-color: #0b7dda;
  transform: translateY(-2px);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
}
</style>