<!--
  ImageUpload.vue - 图片上传组件

  功能说明：
  - 提供手办图片的上传和管理功能
  - 支持多图上传（最多10张）
  - 支持图片预览和删除
  - 支持拖拽调整图片顺序
  - 限制单张图片大小不超过20MB

  组件依赖：
  - 无外部组件依赖

  维护提示：
  - 接收 images 作为 props，显示已上传的图片
  - 图片操作通过 view-image、remove-image、file-upload、reorder-images 事件向父组件传递
  - 使用隐藏的 input[type="file"] 处理文件选择
  - 拖拽排序使用 HTML5 Drag & Drop API，不依赖第三方库
-->
<template>
  <div class="form-group full-width">
    <label>图片上传 (最多10张，每张不超过20MB)</label>
    <div class="image-upload-container">
      <div class="image-upload-list">
        <div
          v-for="(image, index) in images"
          :key="index"
          class="image-upload-item"
          :class="{ 'drag-over': dragOverIndex === index }"
          draggable="true"
          @dragstart="handleDragStart($event, index)"
          @dragover="handleDragOver($event, index)"
          @dragenter="handleDragEnter($event, index)"
          @dragleave="handleDragLeave"
          @drop="handleDrop($event, index)"
          @dragend="handleDragEnd"
        >
          <img :src="image" :alt="`图片 ${index + 1}`">
          <div class="image-actions">
            <button type="button" class="icon-btn view-btn" @click="$emit('view-image', image)">
              <i class="fa-solid fa-eye"></i>
            </button>
            <button type="button" class="icon-btn delete-btn" @click="$emit('remove-image', index)">
              <i class="fa-solid fa-trash"></i>
            </button>
          </div>
          <div class="drag-handle">
            <i class="fa-solid fa-grip-vertical"></i>
          </div>
        </div>
        <div v-if="images.length < 10" class="image-upload-placeholder" @click="triggerFileInput">
          <span>+</span>
          <p>添加图片</p>
        </div>
      </div>
      <input type="file" ref="fileInput" multiple accept="image/*" style="display: none" @change="$emit('file-upload', $event)">
    </div>
  </div>
</template>

<script>
export default {
  name: 'ImageUpload',
  props: {
    images: {
      type: Array,
      default: () => []
    }
  },
  emits: ['view-image', 'remove-image', 'file-upload', 'reorder-images'],
  data() {
    return {
      dragIndex: null,
      dragOverIndex: null
    }
  },
  methods: {
    triggerFileInput() {
      this.$refs.fileInput.click()
    },
    handleDragStart(event, index) {
      this.dragIndex = index
      event.dataTransfer.effectAllowed = 'move'
      event.dataTransfer.setData('text/plain', String(index))
    },
    handleDragOver(event, index) {
      event.preventDefault()
      event.dataTransfer.dropEffect = 'move'
      this.dragOverIndex = index
    },
    handleDragEnter(event, index) {
      event.preventDefault()
      this.dragOverIndex = index
    },
    handleDragLeave() {
      this.dragOverIndex = null
    },
    handleDrop(event, index) {
      event.preventDefault()
      const fromIndex = this.dragIndex
      if (fromIndex === null || fromIndex === index) {
        this.dragOverIndex = null
        return
      }
      const newImages = [...this.images]
      const [moved] = newImages.splice(fromIndex, 1)
      newImages.splice(index, 0, moved)
      this.$emit('reorder-images', newImages)
      this.dragIndex = null
      this.dragOverIndex = null
    },
    handleDragEnd() {
      this.dragIndex = null
      this.dragOverIndex = null
    }
  }
}
</script>

<style scoped>
.form-group.full-width {
  grid-column: 1 / -1;
  margin-top: 20px;
}

.form-group label {
  display: block;
  margin-bottom: 8px;
  color: #333;
  font-weight: 500;
  font-size: 16px;
}

.image-upload-container {
  margin-top: 10px;
}

.image-upload-list {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}

.image-upload-item {
  position: relative;
  width: 100px;
  height: 100px;
  border: 2px solid #ddd;
  border-radius: 4px;
  overflow: hidden;
  cursor: grab;
  transition: border-color 0.2s, opacity 0.2s;
}

.image-upload-item:active {
  cursor: grabbing;
}

.image-upload-item.drag-over {
  border-color: #2196F3;
  opacity: 0.7;
}

.image-upload-item img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: all 0.3s ease;
  pointer-events: none;
}

.image-actions {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
  opacity: 0;
  transition: all 0.3s ease;
  z-index: 1;
}

.image-upload-item:hover .image-actions {
  opacity: 1;
}

.image-upload-item:hover img {
  transform: scale(1.05);
}

/* 拖拽把手 - 左上角 */
.drag-handle {
  position: absolute;
  top: 2px;
  left: 2px;
  width: 20px;
  height: 20px;
  background: rgba(0, 0, 0, 0.4);
  border-radius: 3px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
  font-size: 12px;
  z-index: 2;
  opacity: 0;
  transition: opacity 0.2s;
  cursor: grab;
}

.image-upload-item:hover .drag-handle {
  opacity: 1;
}

.icon-btn {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  border: none;
  font-size: 14px;
  transition: all 0.2s ease;
}

.view-btn {
  background: #f5f5f5;
  color: #666;
}
.view-btn:hover {
  background: #e6f7ff;
  color: #1890ff;
}

.delete-btn {
  background: #f5f5f5;
  color: #666;
}
.delete-btn:hover {
  background: #fff2f0;
  color: #ff4d4f;
}

.image-upload-placeholder {
  width: 100px;
  height: 100px;
  border: 2px dashed #ddd;
  border-radius: 4px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.3s ease;
}

.image-upload-placeholder:hover {
  border-color: #2196F3;
  background-color: rgba(33, 150, 243, 0.05);
}

.image-upload-placeholder span {
  font-size: 32px;
  color: #999;
  margin-bottom: 8px;
}

.image-upload-placeholder p {
  font-size: 14px;
  color: #999;
  margin: 0;
}

@media (max-width: 768px) {
  .image-upload-item,
  .image-upload-placeholder {
    width: 80px;
    height: 80px;
  }
}
</style>
