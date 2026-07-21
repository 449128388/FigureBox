<!--
  FigureDetail.vue - 手办详情页（容器组件）

  功能说明：
  - 顶部 TopHeader 全站统一导航
  - 布局：1400px 宽白底容器 + 24px 内边距
  - 顶部 page-header
  - 主体双栏：左 420px sticky 图片区 | 右 1fr 信息区
  - 信息区为 info-card 堆叠

  组件依赖：
  - TopHeader - 顶部导航栏
  - FigureHeader（页头）
  - FigureImages（左侧图片区）
  - FigureBasicInfo / FigureTags / FigureOrders / FigureAuthorInfo / FigureSpecInfo（右侧信息卡片）
  - useFigureDetail composable（数据拉取与业务函数）
-->
<template>
  <TopHeader />
  <div class="main-container">
    <!-- 加载状态 -->
    <div v-if="loading" class="loading-state">
      <div class="loading-spinner"></div>
      <p>加载中...</p>
    </div>

    <template v-else-if="figure && figure.id">
      <FigureHeader :figure="figure" />

      <div class="detail-layout">
        <FigureImages :figure="figure" />

        <div class="info-section">
          <FigureBasicInfo :figure="figure" />
          <FigureTags :figure="figure" />
          <FigureOrders :related-orders="relatedOrders" />
          <FigureAuthorInfo :figure="figure" />
          <FigureSpecInfo :figure="figure" />
        </div>
      </div>
    </template>

    <div v-else class="empty-state">
      <div class="empty-state-icon">📦</div>
      <p>未找到该手办</p>
    </div>
  </div>
</template>

<script>
import TopHeader from '../components/TopHeader.vue'
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
    TopHeader,
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

        const figureId = this.$route.params.id
        const [figureData, orders] = await Promise.all([
          fetchFigureDetail(figureId),
          fetchOrders()
        ])

        this.figure = figureData || {}
        this.relatedOrders = getRelatedOrders(figureId, orders)
      } catch (error) {
        this.figure = {}
        this.relatedOrders = []
      } finally {
        this.loading = false
      }
    }
  }
}
</script>

<style scoped>
.main-container {
  max-width: 1400px;
  margin: 84px auto 0;
  padding: 24px;
}

/* 双栏布局 */
.detail-layout {
  display: grid;
  grid-template-columns: 420px 1fr;
  gap: 24px;
}
.info-section {
  display: flex;
  flex-direction: column;
  gap: 20px;
  min-width: 0;
}

/* 加载 / 空状态 */
.loading-state,
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 100px 0;
  color: #999;
}
.loading-spinner {
  width: 40px;
  height: 40px;
  border: 4px solid #f3f3f3;
  border-top: 4px solid #1890ff;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-bottom: 16px;
}
.empty-state-icon {
  font-size: 64px;
  margin-bottom: 12px;
  opacity: 0.3;
}
@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

/* 响应式 */
@media (max-width: 1100px) {
  .detail-layout { grid-template-columns: 340px 1fr; }
}
@media (max-width: 900px) {
  .detail-layout { grid-template-columns: 1fr; }
  .info-section { gap: 16px; }
}
@media (max-width: 600px) {
  .main-container { padding: 16px; }
}
</style>
