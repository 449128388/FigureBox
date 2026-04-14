<!--
  FiguresPagination.vue - 手办列表分页组件

  功能说明：
  - 提供分页功能
  - 支持页码切换和每页显示数量调整
  - 仅在有数据时显示（total > 0）

  组件依赖：
  - 使用 Element Plus 的 el-pagination 组件

  维护提示：
  - 接收 currentPage、pageSize、pageSizes、total 作为 props
  - 分页事件通过 $emit 传递给父组件
  - 本地状态 localCurrentPage 和 localPageSize 用于双向绑定
-->
<template>
  <div v-if="total > 0" class="pagination-container">
    <el-pagination
      v-model:current-page="localCurrentPage"
      v-model:page-size="localPageSize"
      :page-sizes="pageSizes"
      layout="total, sizes, prev, pager, next, jumper"
      :total="total"
      @size-change="$emit('size-change', $event)"
      @current-change="$emit('current-change', $event)"
    />
  </div>
</template>

<script>
export default {
  name: 'FiguresPagination',
  props: {
    currentPage: {
      type: Number,
      required: true
    },
    pageSize: {
      type: Number,
      required: true
    },
    pageSizes: {
      type: Array,
      required: true
    },
    total: {
      type: Number,
      required: true
    }
  },
  emits: ['update:currentPage', 'update:pageSize', 'size-change', 'current-change'],
  computed: {
    localCurrentPage: {
      get() {
        return this.currentPage
      },
      set(value) {
        this.$emit('update:currentPage', value)
      }
    },
    localPageSize: {
      get() {
        return this.pageSize
      },
      set(value) {
        this.$emit('update:pageSize', value)
      }
    }
  }
}
</script>

<style scoped>
/* 分页组件样式 */
.pagination-container {
  display: flex;
  justify-content: flex-end;
  margin-top: 20px;
  padding-right: 20px;
}
</style>
