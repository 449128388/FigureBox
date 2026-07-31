<!--
  ProfileSidebar.vue - 个人中心左侧侧边导航栏
  父级传入 items 数组（id/label/icon），通过 select 事件传出被点击的 id
-->
<template>
  <aside class="profile-sidebar">
    <div
      v-for="item in items"
      :key="item.id"
      class="sidebar-item"
      :class="{ active: activePanel === item.id }"
      @click="$emit('select', item.id)"
    >
      <span class="sidebar-icon" v-html="item.icon"></span>
      <span>{{ item.label }}</span>
    </div>
  </aside>
</template>

<script>
export default {
  name: 'ProfileSidebar',
  props: {
    items: {
      type: Array,
      required: true,
      default: () => []
    },
    activePanel: {
      type: String,
      default: ''
    }
  },
  emits: ['select']
}
</script>

<style scoped>
.profile-sidebar {
  width: 220px;
  background: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.06);
  overflow: hidden;
  flex-shrink: 0;
  position: sticky;
  top: 24px;
}
.sidebar-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 14px 18px;
  font-size: 14px;
  color: #61666d;
  cursor: pointer;
  transition: all 0.2s;
  border-left: 3px solid transparent;
}
.sidebar-item:hover {
  background: #f6f7f8;
  color: #18191c;
}
.sidebar-item.active {
  background: rgba(0, 161, 214, 0.08);
  color: #00a1d6;
  border-left-color: #00a1d6;
  font-weight: 600;
}
.sidebar-icon {
  width: 18px;
  height: 18px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  opacity: 0.8;
}
.sidebar-icon svg {
  width: 18px;
  height: 18px;
}

@media (max-width: 900px) {
  .profile-sidebar {
    width: 100%;
    position: static;
    display: flex;
    overflow-x: auto;
    gap: 4px;
    padding: 8px;
  }
  .sidebar-item {
    white-space: nowrap;
    border-left: none;
    border-bottom: 3px solid transparent;
  }
  .sidebar-item.active {
    border-left-color: transparent;
    border-bottom-color: #00a1d6;
  }
}
</style>
