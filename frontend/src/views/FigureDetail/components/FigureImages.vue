<!--
  FigureImages.vue - 手办图片展示组件

  功能说明：
  - 左侧 sticky 主图区：3:4 比例大图 + 缩略图列表
  - 点击缩略图切换主图
  - 点击主图打开原图预览
  - 无图片时显示占位图标

  组件依赖：
  - 接收 figure 作为 props
-->
<template>
  <div class="image-section">
    <div class="main-image" @click="openImagePreview">
      <img
        v-if="figure.images && figure.images.length > 0"
        :src="figure.images[activeImageIndex]"
        :alt="figure.name"
      >
      <span v-else class="image-placeholder">📷</span>
    </div>
    <div v-if="figure.images && figure.images.length > 1" class="thumbnail-list">
      <div
        v-for="(image, index) in figure.images"
        :key="index"
        class="thumbnail"
        :class="{ active: activeImageIndex === index }"
        @click.stop="activeImageIndex = index"
      >
        <img :src="image" :alt="`${figure.name} 图 ${index + 1}`">
      </div>
    </div>

    <!-- 图片预览模态框 -->
    <div v-if="showImagePreview" class="image-preview-overlay" @click="closeImagePreview">
      <div class="image-preview-container" @click.stop>
        <button class="close-btn" @click="closeImagePreview">×</button>
        <img class="preview-image" :src="currentPreviewImage" :alt="figure.name">
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'FigureImages',
  props: {
    figure: {
      type: Object,
      required: true
    }
  },
  data() {
    return {
      activeImageIndex: 0,
      showImagePreview: false,
      currentPreviewImage: ''
    }
  },
  watch: {
    'figure.id'() {
      // 切换手办时复位主图索引
      this.activeImageIndex = 0
    }
  },
  methods: {
    openImagePreview() {
      if (this.figure.images && this.figure.images.length > 0) {
        this.currentPreviewImage = this.figure.images[this.activeImageIndex]
        this.showImagePreview = true
      }
    },
    closeImagePreview() {
      this.showImagePreview = false
      this.currentPreviewImage = ''
    }
  }
}
</script>

<style scoped>
.image-section {
  position: sticky;
  top: 80px;
  height: fit-content;
}

.main-image {
  width: 100%;
  aspect-ratio: 3 / 4;
  background: #e8e8e8;
  border-radius: 12px;
  overflow: hidden;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 16px;
  border: 1px solid #e8e8e8;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
  cursor: pointer;
  position: relative;
  transition: all 0.3s ease;
}
.main-image:hover {
  transform: scale(1.01);
  box-shadow: 0 6px 16px rgba(0, 0, 0, 0.12);
}
.main-image img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}
.image-placeholder {
  font-size: 64px;
  color: #d9d9d9;
}

.thumbnail-list {
  display: flex;
  gap: 10px;
  justify-content: center;
  flex-wrap: wrap;
}
.thumbnail {
  width: 64px;
  height: 64px;
  border-radius: 8px;
  overflow: hidden;
  border: 2px solid transparent;
  cursor: pointer;
  transition: all 0.2s;
  background: #e8e8e8;
}
.thumbnail:hover { border-color: #40a9ff; transform: translateY(-2px); }
.thumbnail.active { border-color: #1890ff; box-shadow: 0 2px 8px rgba(24, 144, 255, 0.2); }
.thumbnail img { width: 100%; height: 100%; object-fit: cover; }

/* 图片预览 */
.image-preview-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.9);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 2000;
}
.image-preview-container {
  position: relative;
  max-width: 90vw;
  max-height: 90vh;
}
.preview-image {
  max-width: 90vw;
  max-height: 90vh;
  object-fit: contain;
}
.close-btn {
  position: absolute;
  top: -40px;
  right: 0;
  background: none;
  border: none;
  color: white;
  font-size: 30px;
  cursor: pointer;
  width: 30px;
  height: 30px;
  line-height: 1;
}
</style>
