<!--
  FormTagsTab.vue - 手办表单标签管理标签页组件

  功能说明：
  - 提供手办标签的选择和管理功能
  - 支持多选、搜索、创建新标签
  - 显示现有标签列表

  组件依赖：
  - 使用 Element Plus 的 el-select 组件
  - 接收 tagStore 作为 props，用于获取标签数据

  维护提示：
  - 接收 figure 作为 props，双向绑定 tag_names
  - 标签变更通过 tag-change 事件向父组件传递
  - 支持动态创建新标签（allow-create）
-->
<template>
  <div class="form-grid">
    <div class="form-group">
      <label>标签</label>
      <el-select
        v-model="localFigure.tag_names"
        multiple
        filterable
        allow-create
        default-first-option
        placeholder="请选择或输入标签"
        empty-text="暂无数据"
        style="width: 334px"
        @change="$emit('tag-change', $event)"
      >
        <el-option
          v-for="name in tagOptions"
          :key="name"
          :label="name"
          :value="name"
        />
      </el-select>
    </div>
  </div>
</template>

<script>
export default {
  name: 'FormTagsTab',
  props: {
    figure: {
      type: Object,
      required: true
    },
    tagStore: {
      type: Object,
      required: true
    }
  },
  emits: ['update:figure', 'tag-change'],
  computed: {
    localFigure: {
      get() {
        return this.figure
      },
      set(value) {
        this.$emit('update:figure', value)
      }
    },
    // 2026-07-29 重构：标签改为 figure.tags JSON 字段，下拉候选取自 tagStore 标签名去重
    tagOptions() {
      const names = (this.tagStore.tags || []).map(t => t && t.name).filter(Boolean)
      const current = Array.isArray(this.figure.tag_names) ? this.figure.tag_names : []
      return Array.from(new Set([...names, ...current]))
    }
  }
}
</script>

<style scoped>
.form-grid {
  display: grid;
  grid-template-columns: 1fr;
  gap: 15px;
  margin-bottom: 20px;
}

.form-group {
  margin-bottom: 0;
}

.form-group label {
  display: block;
  margin-bottom: 8px;
  color: #333;
  font-weight: 500;
  font-size: 16px;
}
</style>
