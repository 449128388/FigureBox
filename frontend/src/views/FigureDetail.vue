<template>
  <div class="figure-detail-container">
    <!-- 加载状态 -->
    <div v-if="loading" class="loading-container">
      <div class="loading-spinner"></div>
      <p>加载中...</p>
    </div>
    
    <!-- 内容区域 -->
    <template v-else>
      <div class="header">
        <h1>中文名称：{{ figure.name }}</h1>
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
          <div v-if="figure.japanese_name" class="info-item">
            <span class="label">日文名:</span>
            <span class="value">{{ figure.japanese_name }}</span>
          </div>
          <div class="info-item" v-if="figure.manufacturer">
            <span class="label">制造商:</span>
            <span class="value">{{ figure.manufacturer }}</span>
          </div>
          <div class="info-item" v-if="figure.price !== null && figure.price !== undefined">
            <span class="label">定价:</span>
            <span class="value">{{ figure.price }} {{ getCurrencySymbol(figure.currency) }}</span>
          </div>
          <div class="info-item" v-if="figure.release_date">
            <span class="label">出货日:</span>
            <span class="value">{{ figure.release_date }}</span>
          </div>
          <div class="info-item" v-if="figure.purchase_price !== null && figure.purchase_price !== undefined">
            <span class="label">入手价格:</span>
            <span class="value">{{ figure.purchase_price }} {{ getCurrencySymbol(figure.purchase_currency) }}</span>
          </div>
          <div class="info-item" v-if="figure.purchase_date">
            <span class="label">入手时间:</span>
            <span class="value">{{ figure.purchase_date }}</span>
          </div>
          <div class="info-item" v-if="figure.purchase_method">
            <span class="label">入手途径:</span>
            <span class="value">{{ figure.purchase_method }}</span>
          </div>
          <div class="info-item" v-if="figure.purchase_type">
            <span class="label">入手形式:</span>
            <span class="value">{{ figure.purchase_type }}</span>
          </div>
          <div class="info-item" v-if="figure.quantity !== null && figure.quantity !== undefined">
            <span class="label">数量:</span>
            <span class="value">{{ figure.quantity }}</span>
          </div>
        </div>

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

        <!-- 尾款信息模块 -->
        <div class="info-section" v-if="relatedOrders.length > 0">
          <h2>尾款信息</h2>
          
          <!-- 订单切换标签 -->
          <div class="order-tabs" v-if="relatedOrders.length > 1">
            <div 
              v-for="(order, index) in relatedOrders" 
              :key="order.id"
              class="order-tab"
              :class="{ active: activeOrderIndex === index }"
              @click="activeOrderIndex = index"
            >
              订单 {{ index + 1 }} ({{ order.status }})
            </div>
          </div>
          
          <div class="info-item" v-if="selectedOrder.deposit !== null && selectedOrder.deposit !== undefined">
            <span class="label">定金:</span>
            <span class="value">¥{{ selectedOrder.deposit }}</span>
          </div>
          <div class="info-item" v-if="selectedOrder.balance !== null && selectedOrder.balance !== undefined">
            <span class="label">尾款:</span>
            <span class="value">¥{{ selectedOrder.balance }}</span>
          </div>
          <div class="info-item" v-if="selectedOrder.due_date">
            <span class="label">出荷日期:</span>
            <span class="value">{{ selectedOrder.due_date }}</span>
          </div>
          <div class="info-item" v-if="selectedOrder.status">
            <span class="label">尾款状态:</span>
            <span class="value" :class="getStatusClass(selectedOrder.status)">{{ selectedOrder.status }}</span>
          </div>
          <div class="info-item" v-if="selectedOrder.shop_name">
            <span class="label">购买店铺:</span>
            <span class="value">{{ selectedOrder.shop_name }}</span>
          </div>
          <div class="info-item" v-if="selectedOrder.shop_contact">
            <span class="label">联系方式:</span>
            <span class="value">{{ selectedOrder.shop_contact }}</span>
          </div>
          <div class="info-item" v-if="selectedOrder.tracking_number">
            <span class="label">物流订单:</span>
            <a class="value tracking-link" :href="`https://www.baidu.com/s?wd=${encodeURIComponent(selectedOrder.tracking_number)}`" target="_blank" rel="noopener noreferrer">{{ selectedOrder.tracking_number }}</a>
          </div>
        </div>        

        <!-- 作者信息模块 -->  
        <div class="info-section" v-if="figure.painting || figure.original_art || figure.work">
          <h2>作者信息</h2>
          <div class="info-item" v-if="figure.painting">
            <span class="label">涂装:</span>
            <span class="value">{{ figure.painting }}</span>
          </div>
          <div class="info-item" v-if="figure.original_art">
            <span class="label">原画:</span>
            <span class="value">{{ figure.original_art }}</span>
          </div>
          <div class="info-item" v-if="figure.work">
            <span class="label">作品:</span>
            <span class="value">{{ figure.work }}</span>
          </div>
        </div>

        <!-- 规格信息模块 -->        
        <div class="info-section" v-if="figure.scale || figure.material || figure.size">
          <h2>规格信息</h2>
          <div class="info-item" v-if="figure.scale">
            <span class="label">比例:</span>
            <span class="value">{{ figure.scale }}</span>
          </div>
          <div class="info-item" v-if="figure.material">
            <span class="label">材质:</span>
            <span class="value">{{ figure.material }}</span>
          </div>
          <div class="info-item" v-if="figure.size">
            <span class="label">尺寸:</span>
            <span class="value">{{ figure.size }}</span>
          </div>
        </div>
        
      </div>
    </div>
    </template>
  </div>
</template>

<script>
import { useFigureStore, useOrderStore } from '../store'
import axios from '../axios'

export default {
  name: 'FigureDetail',
  data() {
    return {
      figure: {},
      activeImageIndex: 0,
      activeOrderIndex: 0,
      showImagePreview: false,
      currentPreviewImage: '',
      loading: true
    }
  },
  computed: {
    figureStore() {
      return useFigureStore()
    },
    orderStore() {
      return useOrderStore()
    },
    // 获取与当前手办关联的所有订单
    relatedOrders() {
      const figureId = parseInt(this.$route.params.id)
      return this.orderStore.orders.filter(order => order.figure_id === figureId)
    },
    // 当前选中的订单
    selectedOrder() {
      return this.relatedOrders.length > 0 ? this.relatedOrders[this.activeOrderIndex] : null
    }
  },
  mounted() {
    this.fetchFigureDetail()
    this.orderStore.fetchOrders() // 获取订单数据
  },
  methods: {
    async fetchFigureDetail() {
      this.loading = true
      const figureId = this.$route.params.id
      try {
        // 调用API获取手办详情（包含完整的标签数据）
        // axios拦截器已处理response.data，直接返回数据
        const data = await axios.get(`/figures/${figureId}`)
        this.figure = data
      } catch (error) {
        console.error('获取手办详情失败:', error)
        // 如果API调用失败，尝试从store中获取
        const figure = this.figureStore.figures.find(f => f.id == figureId)
        if (figure) {
          this.figure = figure
        }
      } finally {
        this.loading = false
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
    openImagePreview() {
      if (this.figure.images && this.figure.images.length > 0) {
        this.currentPreviewImage = this.figure.images[this.activeImageIndex]
        this.showImagePreview = true
      }
    },
    closeImagePreview() {
      this.showImagePreview = false
      this.currentPreviewImage = ''
    },
    // 获取状态样式类
    getStatusClass(status) {
      switch(status) {
        case '未支付': return 'status-unpaid'
        case '已支付': return 'status-paid'
        case '已完成': return 'status-paid'
        case '已取消': return 'status-cancelled'
        default: return ''
      }
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
  min-height: 400px;
}

/* 加载状态样式 */
.loading-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 400px;
}

.loading-spinner {
  width: 50px;
  height: 50px;
  border: 4px solid #f3f3f3;
  border-top: 4px solid #409eff;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

.loading-container p {
  margin-top: 16px;
  color: #666;
  font-size: 14px;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
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
  padding: 2px 0;
  min-height: 20px;
  line-height: 1.5;
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

/* 尾款状态样式 */
.status-unpaid {
  color: #f44336;
  font-weight: 600;
}

.status-paid {
  color: #4CAF50;
  font-weight: 600;
}

.status-cancelled {
  color: #9e9e9e;
  font-weight: 600;
}

/* 物流订单链接样式 */
.tracking-link {
  color: #2196F3;
  cursor: pointer;
  text-decoration: none;
}

.tracking-link:hover {
  color: #1976D2;
}

/* 订单切换标签样式 */
.order-tabs {
  display: flex;
  gap: 10px;
  margin-bottom: 20px;
  flex-wrap: wrap;
}

.order-tab {
  padding: 8px 16px;
  background-color: #f5f5f5;
  border-radius: 20px;
  cursor: pointer;
  font-size: 14px;
  font-weight: 500;
  color: #666;
  transition: all 0.3s ease;
  border: 2px solid transparent;
}

.order-tab:hover {
  background-color: #e8e8e8;
  color: #333;
  transform: translateY(-1px);
}

.order-tab.active {
  background-color: #2196F3;
  color: white;
  border-color: #1976D2;
  box-shadow: 0 2px 8px rgba(33, 150, 243, 0.3);
}

.order-tab.active:hover {
  background-color: #1976D2;
  color: white;
}
</style>