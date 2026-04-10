<template>
  <div class="form-grid">
    <div class="form-group">
      <label>标签</label>
      <el-select
        v-model="localFigure.tag_ids"
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
          v-for="item in tagStore.tags"
          :key="item.id"
          :label="item.name"
          :value="item.id"
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
