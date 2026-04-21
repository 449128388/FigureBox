<!--
  FiguresList.vue - 手办列表组件

  功能说明：
  - 展示手办列表
  - 处理空状态显示（暂无数据）
  - 遍历渲染 FigureItem 组件
  - 传递事件给父组件
  - 【新增】支持批量选择模式，传递选中状态给子组件

  组件依赖：
  - FigureItem.vue - 手办卡片组件

  维护提示：
  - 接收 figures 数组作为 props
  - 接收 searchTagIds 作为 props 传递给 FigureItem
  - 接收 isBatchMode、selectedIds、disabledIds 作为批量选择相关 props
  - 编辑、删除、筛选标签、切换选择等事件通过 $emit 传递给父组件
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
      :is-batch-mode="isBatchMode"
      :is-selected="isSelected(figure.id)"
      :is-disabled="isDisabled(figure.id)"
      :disabled-tooltip="getDisabledTooltip(figure)"
      @edit="$emit('edit', $event)"
      @delete="$emit('delete', $event)"
      @filter-by-tag="$emit('filter-by-tag', $event)"
      @toggle-selection="handleToggleSelection"
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
    },
    // 【新增】批量选择相关 props
    isBatchMode: {
      type: Boolean,
      default: false
    },
    selectedIds: {
      type: Set,
      default: () => new Set()
    },
    disabledIds: {
      type: Set,
      default: () => new Set()
    }
  },
  emits: ['edit', 'delete', 'filter-by-tag', 'toggle-selection'],
  setup(props, { emit }) {
    // 【新增】检查手办是否被选中
    const isSelected = (figureId) => {
      return props.selectedIds.has(figureId)
    }

    // 【新增】检查手办是否被禁用
    const isDisabled = (figureId) => {
      return props.disabledIds.has(figureId)
    }

    // 【新增】获取禁用提示信息
    const getDisabledTooltip = (figure) => {
      // 如果有未完成订单的标记
      if (figure.has_incomplete_orders) {
        return '该手办存在未完成订单'
      }
      return '该手办存在未完成订单'
    }

    // 【新增】处理切换选择事件
    const handleToggleSelection = (figureId, selected) => {
      emit('toggle-selection', figureId, selected)
    }

    return {
      isSelected,
      isDisabled,
      getDisabledTooltip,
      handleToggleSelection
    }
  }
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
