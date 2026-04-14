<!--
  FigureDetail.vue - 手办详情页面
  
  功能说明：
  - 展示单个手办的完整详细信息
  - 包含基本信息、图片展示、标签、关联订单、作者信息、规格参数等模块
  - 支持从手办列表点击跳转进入
  
  组件依赖：
  - FigureHeader.vue - 手办标题和返回按钮
  - FigureImages.vue - 图片轮播展示
  - FigureBasicInfo.vue - 基础信息（价格、发售日期等）
  - FigureTags.vue - 标签展示
  - FigureOrders.vue - 关联订单列表
  - FigureAuthorInfo.vue - 作者/涂装/原画信息
  - FigureSpecInfo.vue - 规格参数（比例、材质、尺寸等）
  
  维护提示：
  - 通过路由参数 figureId 获取手办ID
  - 使用 useFigureDetail composable 管理数据获取逻辑
  - 加载状态单独处理，避免空白页面
-->
<template>
  <div class="figure-detail-container">
    <!-- 加载状态 -->
    <div v-if="loading" class="loading-container">
      <div class="loading-spinner"></div>
      <p>加载中...</p>
    </div>
    
    <!-- 内容区域 -->
    <template v-else>
      <FigureHeader :figure="figure" />
    
      <div class="figure-content">
        <FigureImages :figure="figure" />
        
        <div class="figure-info">
          <FigureBasicInfo :figure="figure" />
          <FigureTags :figure="figure" />
          <FigureOrders :relatedOrders="relatedOrders" />
          <FigureAuthorInfo :figure="figure" />
          <FigureSpecInfo :figure="figure" />
        </div>
      </div>
    </template>
  </div>
</template>

<script>
import FigureHeader from './FigureDetail/components/FigureHeader.vue'
import FigureImages from './FigureDetail/components/FigureImages.vue'
import FigureBasicInfo from './FigureDetail/components/FigureBasicInfo.vue'
import FigureTags from './FigureDetail/components/FigureTags.vue'
import FigureOrders from './FigureDetail/components/FigureOrders.vue'
import FigureAuthorInfo from './FigureDetail/components/FigureAuthorInfo.vue'
import FigureSpecInfo from './FigureDetail/components/FigureSpecInfo.vue'
import { useFigureDetail } from './FigureDetail/composables/useFigureDetail'

export default {
  name: 'FigureDetail',
  components: {
    FigureHeader,
    FigureImages,
    FigureBasicInfo,
    FigureTags,
    FigureOrders,
    FigureAuthorInfo,
    FigureSpecInfo
  },
  data() {
    return {
      loading: true,
      figure: {},
      relatedOrders: []
    }
  },
  async mounted() {
    await this.fetchFigureDetail()
  },
  methods: {
    async fetchFigureDetail() {
      try {
        this.loading = true
        const { fetchFigureDetail, fetchOrders, getRelatedOrders } = useFigureDetail()
        
        // 并行获取手办详情和订单数据
        const [figureData, orders] = await Promise.all([
          fetchFigureDetail(this.$route.params.id),
          fetchOrders()
        ])
        
        this.figure = figureData
        this.relatedOrders = getRelatedOrders(this.$route.params.id, orders)
      } catch (error) {
      } finally {
        this.loading = false
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
  margin-left: 50px;
  margin-right: 50px;
  padding: 20px;
  background-color: #f9f9f9;
  border-radius: 8px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
}

.loading-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 100px 0;
}

.loading-spinner {
  width: 40px;
  height: 40px;
  border: 4px solid #f3f3f3;
  border-top: 4px solid #3498db;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-bottom: 10px;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.figure-content {
  display: flex;
  gap: 20px;
  margin-top: 20px;
}

.figure-info {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 20px;
}

@media (max-width: 768px) {
  .figure-content {
    flex-direction: column;
  }
  
  .figure-detail-container {
    margin-left: 20px;
    margin-right: 20px;
  }
}
</style>