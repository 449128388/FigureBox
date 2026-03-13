<template>
  <div class="figure-detail-container">
    <div class="header">
      <h1>{{ figure.name }}</h1>
      <button class="btn btn-back" @click="goBack">返回列表</button>
    </div>
    
    <div class="figure-content">
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
      
      <div class="figure-info">
        <div class="info-section">
          <h2>基本信息</h2>
          <div class="info-item">
            <span class="label">名称:</span>
            <span class="value">{{ figure.name }}</span>
          </div>
          <div class="info-item">
            <span class="label">制造商:</span>
            <span class="value">{{ figure.manufacturer || '未设置' }}</span>
          </div>
          <div class="info-item">
            <span class="label">定价:</span>
            <span class="value">{{ figure.price || '未设置' }} {{ getCurrencySymbol(figure.currency) }}</span>
          </div>
          <div class="info-item">
            <span class="label">出货日:</span>
            <span class="value">{{ figure.release_date || '未设置' }}</span>
          </div>
          <div class="info-item">
            <span class="label">入手价格:</span>
            <span class="value">{{ figure.purchase_price || '未设置' }} {{ getCurrencySymbol(figure.purchase_currency) }}</span>
          </div>
          <div class="info-item">
            <span class="label">入手时间:</span>
            <span class="value">{{ figure.purchase_date || '未设置' }}</span>
          </div>
          <div class="info-item">
            <span class="label">入手途径:</span>
            <span class="value">{{ figure.purchase_method || '未设置' }}</span>
          </div>
          <div class="info-item">
            <span class="label">入手形式:</span>
            <span class="value">{{ figure.purchase_type || '未设置' }}</span>
          </div>
        </div>
        
        <div class="info-section">
          <h2>作者信息</h2>
          <div class="info-item">
            <span class="label">原型:</span>
            <span class="value">{{ figure.prototype || '未设置' }}</span>
          </div>
          <div class="info-item">
            <span class="label">涂装:</span>
            <span class="value">{{ figure.painting || '未设置' }}</span>
          </div>
          <div class="info-item">
            <span class="label">原画:</span>
            <span class="value">{{ figure.original_art || '未设置' }}</span>
          </div>
          <div class="info-item">
            <span class="label">作品:</span>
            <span class="value">{{ figure.work || '未设置' }}</span>
          </div>
        </div>
        
        <div class="info-section">
          <h2>规格信息</h2>
          <div class="info-item">
            <span class="label">比例:</span>
            <span class="value">{{ figure.scale || '未设置' }}</span>
          </div>
          <div class="info-item">
            <span class="label">材质:</span>
            <span class="value">{{ figure.material || '未设置' }}</span>
          </div>
          <div class="info-item">
            <span class="label">尺寸:</span>
            <span class="value">{{ figure.size || '未设置' }}</span>
          </div>
        </div>
        
        <div class="info-section" v-if="figure.tags">
          <h2>标签</h2>
          <div class="tags-container">
            <el-tag
              v-for="tag in parseTags(figure.tags)"
              :key="tag"
              size="small"
              effect="light"
              style="margin-right: 8px; margin-bottom: 8px;"
            >
              {{ tag }}
            </el-tag>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { useFigureStore } from '../store'

export default {
  name: 'FigureDetail',
  data() {
    return {
      figure: {},
      activeImageIndex: 0,
      showImagePreview: false,
      currentPreviewImage: ''
    }
  },
  computed: {
    figureStore() {
      return useFigureStore()
    }
  },
  mounted() {
    this.fetchFigureDetail()
  },
  methods: {
    async fetchFigureDetail() {
      const figureId = this.$route.params.id
      try {
        // 从store中获取手办详情
        const figure = this.figureStore.figures.find(f => f.id == figureId)
        if (figure) {
          this.figure = figure
        } else {
          // 如果store中没有，可能需要从API获取
          console.error('手办不存在')
        }
      } catch (error) {
        console.error('获取手办详情失败:', error)
      }
    },
    goBack() {
      this.$router.push('/figures')
    },
    getCurrencySymbol(currency) {
      switch(currency) {
        case 'CNY': return '元'
        case 'JPY': return '日元'
        case 'USD': return '美元'
        case 'EUR': return '欧元'
        default: return '元'
      }
    },
    parseTags(tagStr) {
      if (!tagStr) return []
      return tagStr.split(',').filter(tag => tag.trim())
    },
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
.figure-detail-container {
  margin-top: 20px;
  width: 100%;
  max-width: 1200px;
  margin-left: auto;
  margin-right: auto;
  padding: 20px;
  background-color: #f9f9f9;
  border-radius: 8px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 30px;
  padding-bottom: 20px;
  border-bottom: 2px solid #e0e0e0;
}

.header h1 {
  margin: 0;
  color: #333;
  font-size: 28px;
  font-weight: 600;
}

.btn-back {
  padding: 10px 20px;
  background-color: #2196F3;
  color: white;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-size: 14px;
  font-weight: 500;
  transition: all 0.3s ease;
}

.btn-back:hover {
  background-color: #0b7dda;
  transform: translateY(-2px);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
}

.figure-content {
  display: flex;
  gap: 40px;
}

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

.figure-info {
  flex: 1;
  min-width: 0;
}

.info-section {
  background-color: white;
  padding: 20px;
  border-radius: 8px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
  margin-bottom: 20px;
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

.info-item {
  display: flex;
  margin-bottom: 12px;
}

.label {
  flex: 0 0 100px;
  font-weight: 500;
  color: #666;
}

.value {
  flex: 1;
  color: #333;
}

.tags-container {
  display: flex;
  flex-wrap: wrap;
}

@media (max-width: 768px) {
  .figure-content {
    flex-direction: column;
  }
  
  .figure-images {
    flex: 1;
  }
  
  .main-image {
    height: 300px;
  }
}
</style>