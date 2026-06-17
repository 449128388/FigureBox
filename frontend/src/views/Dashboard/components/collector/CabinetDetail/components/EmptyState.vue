<!--
  EmptyState.vue - 空状态组件

  功能说明：
  - 当收藏柜中没有藏品时展示
  - 显示图标、标题、描述信息

  Props:
  - icon: String - 展示的图标
  - title: String - 标题文字
  - description: String - 描述文字
-->
<template>
  <div class="empty-state">
    <div class="empty-icon">{{ icon }}</div>
    <div class="empty-title">{{ title }}</div>
    <div class="empty-desc">{{ description }}</div>
  </div>
</template>

<script>
export default {
  name: 'EmptyState',

  props: {
    icon: {
      type: String,
      default: '📦'
    },
    title: {
      type: String,
      default: '暂无数据'
    },
    description: {
      type: String,
      default: '该分类下暂无藏品记录'
    }
  }
}
</script>

<style scoped>
.empty-state {
  background: #fff;
  border-radius: 12px;
  padding: 60px 20px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
  text-align: center;
}

.empty-icon {
  font-size: 56px;
  margin-bottom: 16px;
}

.empty-title {
  font-size: 18px;
  font-weight: 600;
  color: #1F1F1F;
  margin-bottom: 8px;
}

.empty-desc {
  font-size: 14px;
  color: #999;
}
</style>
