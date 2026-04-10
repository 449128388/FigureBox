<template>
  <div class="info-section" v-if="figure.tags && figure.tags.length > 0">
    <h2>标签</h2>
    <div class="tags-container">
      <el-tag
        v-for="tag in figure.tags"
        :key="tag.id"
        effect="light"
        class="figure-tag"
      >
        {{ tag.name }}
      </el-tag>
    </div>
  </div>
</template>

<script>
export default {
  name: 'FigureTags',
  props: {
    figure: {
      type: Object,
      required: true
    }
  }
}
</script>

<style scoped>
.info-section {
  background-color: white;
  padding: 20px;
  border-radius: 8px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
}

.info-section h2 {
  margin-top: 0;
  margin-bottom: 20px;
  color: #333;
  font-size: 20px;
  font-weight: 600;
  border-bottom: 1px solid #e0e0e0;
  padding-bottom: 10px;
}

.tags-container {
  display: flex;
  flex-wrap: wrap;
}

.figure-tag {
  margin-right: 8px;
  margin-bottom: 8px;
  font-size: 16px;
  padding: 6px 12px;
  height: auto;
}
</style>