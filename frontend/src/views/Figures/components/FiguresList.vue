<template>
  <div class="figures-list">
    <div v-if="figures.length === 0" class="empty-state">
      <p>暂无数据</p>
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
