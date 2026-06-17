<!--
  SortBar.vue - 排序栏+视图切换组件

  功能说明：
  - 展示排序选项（入库时间、名称、喜爱度、收藏天数）
  - 展示视图切换按钮（网格、列表）
  - 支持点击排序切换升降序

  Props:
  - sortBy: String - 当前排序字段
  - sortOrder: String - 当前排序方向 'asc' | 'desc'
  - viewMode: String - 当前视图模式 'grid' | 'list'
  - count: Number - 藏品数量

  Events:
  - sort: 点击排序选项时触发，参数 { field }
  - switch-view: 切换视图时触发，参数 { mode }
-->
<template>
  <div class="sort-bar">
    <div class="sort-left">
      <span
        v-for="option in sortOptions"
        :key="option.field"
        class="sort-tag"
        :class="{ active: sortBy === option.field }"
        @click="handleSort(option.field)"
      >
        {{ option.label }}
        <span v-if="sortBy === option.field" class="sort-arrow">
          {{ sortOrder === 'asc' ? '↑' : '↓' }}
        </span>
      </span>
    </div>
    <div class="sort-right">
      <div v-if="count > 0" class="view-toggle">
        <button
          v-for="vm in viewModes"
          :key="vm.mode"
          class="view-btn"
          :class="{ active: viewMode === vm.mode }"
          @click="handleSwitchView(vm.mode)"
        >
          {{ vm.label }}
        </button>
      </div>
      <div v-if="count > 0" class="sort-count">
        共 {{ count }} 件藏品
      </div>
    </div>
  </div>
</template>

<script>
import { SORT_OPTIONS, VIEW_MODES } from '../constants/cabinetConfig'

export default {
  name: 'SortBar',

  props: {
    sortBy: {
      type: String,
      required: true
    },
    sortOrder: {
      type: String,
      required: true
    },
    viewMode: {
      type: String,
      required: true
    },
    count: {
      type: Number,
      default: 0
    }
  },

  data() {
    return {
      sortOptions: SORT_OPTIONS,
      viewModes: VIEW_MODES
    }
  },

  methods: {
    /**
     * 处理排序点击
     * @param {string} field - 排序字段
     */
    handleSort(field) {
      this.$emit('sort', { field })
    },

    /**
     * 处理视图切换
     * @param {string} mode - 视图模式
     */
    handleSwitchView(mode) {
      this.$emit('switch-view', { mode })
    }
  }
}
</script>

<style scoped>
.sort-bar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 16px;
}

.sort-left {
  display: flex;
  gap: 8px;
}

.sort-tag {
  padding: 4px 10px;
  border-radius: 14px;
  font-size: 12px;
  border: 1px solid #EBE8E4;
  background: #fff;
  color: #666;
  cursor: pointer;
  transition: all 0.2s;
}

.sort-tag:hover {
  border-color: #C49A6C;
  color: #C49A6C;
}

.sort-tag.active {
  background: #FDF6EE;
  border-color: #C49A6C;
  color: #C49A6C;
  font-weight: 500;
}

.sort-arrow {
  margin-left: 2px;
}

.sort-right {
  display: flex;
  align-items: center;
  gap: 16px;
}

.view-toggle {
  display: flex;
  gap: 6px;
}

.view-btn {
  padding: 5px 12px;
  border: 1px solid #EBE8E4;
  background: #fff;
  border-radius: 6px;
  font-size: 13px;
  color: #666;
  cursor: pointer;
  transition: all 0.2s;
}

.view-btn:hover {
  border-color: #C49A6C;
  color: #C49A6C;
}

.view-btn.active {
  border-color: #C49A6C;
  color: #C49A6C;
  background: #FDF6EE;
}

.sort-count {
  font-size: 13px;
  color: #999;
}
</style>
