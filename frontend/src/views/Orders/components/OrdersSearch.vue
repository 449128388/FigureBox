<!--
  OrdersSearch.vue - 订单搜索筛选组件

  功能说明：
  - 提供订单搜索和筛选功能
  - 支持按手办名称、出荷日期范围搜索
  - 提供搜索和重置按钮

  组件依赖：
  - 使用 Element Plus 的 el-input、el-date-picker、el-button 组件

  维护提示：
  - 本地状态 localSearchFigureName、localSearchDueDateRange 用于双向绑定
  - 搜索和重置事件通过 $emit 传递给父组件
-->
<template>
  <div class="search-section">
    <div class="search-form">
      <span style="margin-right: 5px; font-weight: 500;">手办名称:</span>
      <!-- 2026-08-06 修复：el-input 加 @keyup.enter，搜索输入框按 Enter 触发搜索（与点击搜索按钮等价） -->
      <el-input v-model="localSearchFigureName" placeholder="搜索手办名称" style="width: 200px; margin-right: 10px;" @keyup.enter="$emit('enter-search')"></el-input>
      <span style="margin-right: 5px; font-weight: 500;">出荷日期:</span>
      <el-date-picker v-model="localSearchDueDateRange" type="daterange" range-separator="至" start-placeholder="开始日期" end-placeholder="结束日期" style="width: 500px; min-width: 500px; max-width: 500px; margin-right: 10px;"></el-date-picker>
      <el-button type="primary" @click="handleSearch">搜索</el-button>
      <el-button @click="handleReset">重置</el-button>
    </div>
  </div>
</template>

<script>
export default {
  name: 'OrdersSearch',
  props: {
    searchFigureName: {
      type: String,
      default: ''
    },
    searchDueDateRange: {
      type: Array,
      default: () => []
    }
  },
  emits: ['update:searchFigureName', 'update:searchDueDateRange', 'search', 'reset', 'enter-search'],
  computed: {
    localSearchFigureName: {
      get() {
        return this.searchFigureName
      },
      set(value) {
        this.$emit('update:searchFigureName', value)
      }
    },
    localSearchDueDateRange: {
      get() {
        return this.searchDueDateRange
      },
      set(value) {
        this.$emit('update:searchDueDateRange', value)
      }
    }
  },
  methods: {
    handleSearch() {
      this.$emit('search')
    },
    handleReset() {
      this.$emit('reset')
    }
  }
}
</script>

<style scoped>
.search-section {
  margin-bottom: 30px;
  padding: 20px;
  background-color: white;
  border-radius: 8px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
}

.search-form {
  display: flex;
  align-items: center;
  gap: 15px;
  width: 100%;
  justify-content: flex-start;
}
</style>
