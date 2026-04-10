<template>
  <div class="figure-images">
    <div class="main-image" @click="openImagePreview">
      <img :src="figure.images && figure.images.length > 0 ? figure.images[activeImageIndex] : '/imgs/no_image.png'" :alt="figure.name">
      <div class="image-overlay">
        <span>点击查看原图</span>
      </div>
    </div>
    <div class="thumbnail-list">
      <div 
        v-for="(image, index) in figure.images" 
        :key="index"
        class="thumbnail-item"
        :class="{ active: activeImageIndex === index }"
        @click="activeImageIndex = index"
      >
        <img :src="image" :alt="`${figure.name} 图片 ${index + 1}`">
      </div>
      <div v-if="!figure.images || figure.images.length === 0" class="thumbnail-item no-image">
        <img src="/imgs/no_image.png" alt="无图片">
      </div>
    </div>
    
    <!-- 图片预览模态框 -->
    <div v-if="showImagePreview" class="image-preview-overlay" @click="closeImagePreview">
      <div class="image-preview-container" @click.stop>
        <button class="close-btn" @click="closeImagePreview">×</button>
        <div class="preview-image-wrapper">
          <img :src="currentPreviewImage" :alt="figure.name">
        </div>
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
.figure-images {
  flex: 0 0 500px;
}

.main-image {
  width: 100%;
  height: 500px;
  background-color: white;
  border-radius: 8px;
  overflow: hidden;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
  margin-bottom: 20px;
}

.main-image {
  cursor: pointer;
  position: relative;
  transition: all 0.3s ease;
}

.main-image:hover {
  transform: scale(1.01);
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);
}

.main-image img {
  width: 100%;
  height: 100%;
  object-fit: contain;
  transition: all 0.3s ease;
}

.image-overlay {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  background: rgba(0, 0, 0, 0.6);
  color: white;
  padding: 10px;
  text-align: center;
  font-size: 14px;
  opacity: 0;
  transition: opacity 0.3s ease;
  border-bottom-left-radius: 8px;
  border-bottom-right-radius: 8px;
}

.main-image:hover .image-overlay {
  opacity: 1;
}

/* 图片预览模态框 */
.image-preview-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.9);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.image-preview-container {
  position: relative;
  max-width: 90vw;
  max-height: 90vh;
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
  padding: 0;
  width: 30px;
  height: 30px;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.3s ease;
}

.close-btn:hover {
  transform: scale(1.1);
  color: #2196F3;
}

.preview-image-wrapper {
  display: flex;
  align-items: center;
  justify-content: center;
  max-height: 90vh;
}

.preview-image-wrapper img {
  max-width: 100%;
  max-height: 90vh;
  object-fit: contain;
}

.thumbnail-list {
  display: flex;
  gap: 10px;
  overflow-x: auto;
  padding-bottom: 10px;
}

.thumbnail-item {
  flex: 0 0 80px;
  height: 80px;
  background-color: white;
  border-radius: 4px;
  overflow: hidden;
  cursor: pointer;
  transition: all 0.3s ease;
  border: 2px solid transparent;
}

.thumbnail-item:hover {
  transform: translateY(-2px);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
}

.thumbnail-item.active {
  border-color: #2196F3;
  box-shadow: 0 0 0 2px rgba(33, 150, 243, 0.2);
}

.thumbnail-item img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.thumbnail-item.no-image {
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: #f0f0f0;
}

@media (max-width: 768px) {
  .figure-images {
    flex: 1;
  }
  
  .main-image {
    height: 300px;
  }
}
</style>