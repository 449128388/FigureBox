<!--
  ImagePreview.vue - 图片预览组件

  功能说明：
  - 提供图片预览功能
  - 显示大图预览
  - 支持点击关闭和点击背景关闭

  组件依赖：
  - 无外部组件依赖

  维护提示：
  - 接收 show 和 image 作为 props
  - 关闭事件通过 close 事件向父组件传递
  - 点击背景区域会触发关闭事件
-->
<template>
  <div v-if="show" class="image-preview-modal" @click.self="$emit('close')">
    <div class="image-preview-content" @click.stop>
      <button class="btn btn-close-preview" @click="$emit('close')">×</button>
      <img :src="image" :alt="'预览图片'">
    </div>
  </div>
</template>

<script>
export default {
  name: 'ImagePreview',
  props: {
    show: {
      type: Boolean,
      required: true
    },
    image: {
      type: String,
      default: ''
    }
  },
  emits: ['close']
}
</script>

<style scoped>
/* 图片预览模态框样式 */
.image-preview-modal {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(0, 0, 0, 0.8);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.image-preview-content {
  position: relative;
  max-width: 90%;
  max-height: 90%;
}

.image-preview-content img {
  max-width: 100%;
  max-height: 80vh;
  object-fit: contain;
  border-radius: 8px;
}

.btn-close-preview {
  position: absolute;
  top: -40px;
  right: 0;
  background-color: rgba(255, 255, 255, 0.2);
  color: white;
  border: none;
  border-radius: 50%;
  width: 30px;
  height: 30px;
  font-size: 18px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
}

.btn-close-preview:hover {
  background-color: rgba(255, 255, 255, 0.3);
}
</style>
