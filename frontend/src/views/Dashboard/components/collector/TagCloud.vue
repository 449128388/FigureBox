<!--
  TagCloud.vue - 收藏家模式标签云组件

  功能说明：
  - 展示手办标签的分布情况
  - 显示标签名称和对应数量
  - 支持点击标签进行筛选

  组件依赖：
  - 接收 collectorData 作为 props，包含 tags 数组

  维护提示：
  - 点击标签事件通过 filterByTag 方法处理
  - 使用 Element Plus 图标组件
-->
<template>
  <div class="tag-cloud">
    <div class="section-title">
      <el-icon><CollectionTag /></el-icon> 标签云
    </div>
    <div class="tags">
      <span 
        v-for="tag in collectorData?.tags || []" 
        :key="tag.name"
        class="tag"
        @click="filterByTag(tag.name)"
      >
        #{{ tag.name }}({{ tag.count }})
      </span>
    </div>
  </div>
</template>

<script>
import { CollectionTag } from '@element-plus/icons-vue'

export default {
  name: 'TagCloud',
  components: { CollectionTag },
  props: {
    collectorData: {
      type: Object,
      default: () => ({})
    }
  },
  emits: ['filter-by-tag'],
  methods: {
    filterByTag(tagName) {
      this.$emit('filter-by-tag', tagName)
    }
  }
}
</script>

<style scoped>
.tag-cloud {
  margin-bottom: 30px;
  background-color: white;
  padding: 20px;
  border-radius: 8px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
}

.section-title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 18px;
  font-weight: 600;
  color: #333;
  margin-bottom: 20px;
}

.tags {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}

.tag {
  background-color: #f0f0f0;
  padding: 8px 16px;
  border-radius: 20px;
  font-size: 14px;
  color: #333;
  cursor: pointer;
  transition: all 0.3s ease;
}

.tag:hover {
  background-color: #e3f2fd;
  color: #1976D2;
  transform: translateY(-2px);
  box-shadow: 0 2px 8px rgba(25, 118, 210, 0.3);
}

@media (max-width: 768px) {
  .tags {
    justify-content: center;
  }
}
</style>
