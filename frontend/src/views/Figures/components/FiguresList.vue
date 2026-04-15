<!--
  FiguresList.vue - 手办列表组件

  功能说明：
  - 展示手办列表
  - 处理空状态显示（暂无数据）
  - 遍历渲染 FigureItem 组件
  - 传递事件给父组件

  组件依赖：
  - FigureItem.vue - 手办卡片组件

  维护提示：
  - 接收 figures 数组作为 props
  - 接收 searchTagIds 作为 props 传递给 FigureItem
  - 编辑、删除、筛选标签等事件通过 $emit 传递给父组件
-->
<template>
  <div class="figures-list">
    <div v-if="figures.length === 0" class="empty-state">
      <el-empty description="暂无数据" />
    </div>
    <FigureItem
      v-else
      v-for="figure in figures"
      :key="figure.id"
      :figure="figure"
      :search-tag-ids="searchTagIds"
      @edit="$emit('edit', $event)"
      @delete="$emit('delete', $event)"
      @filter-by-tag="$emit('filter-by-tag', $event)"
    />
  </div>
</template>

<script>
import FigureItem from './FigureItem.vue'

export default {
  name: 'FiguresList',
  components: {
    FigureItem
  },
  props: {
    figures: {
      type: Array,
      required: true
    },
    searchTagIds: {
      type: Array,
      default: () => []
    }
  },
  emits: ['edit', 'delete', 'filter-by-tag']
}
</script>

<style scoped>
.figures-list {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
  gap: 15px;
  margin-bottom: 20px;
}

.empty-state {
  grid-column: 1 / -1;
  text-align: center;
  padding: 60px 20px;
  background-color: white;
  border-radius: 8px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
  color: #999;
  font-size: 16px;
}
</style>
