<!--
  CabinetDetail.vue - 收藏家模式我的收藏柜详情组件（重构版）

  功能说明：
  - 展示某个收藏柜分类的详细藏品列表
  - 包含详情头部、排序栏、藏品网格/列表视图切换
  - 每个藏品支持交互式喜爱度评分
  - 无数据时展示"暂无数据"空状态
  - 支持返回上一级（收藏柜概览）
  - 支持查看详情抽屉和出柜登记抽屉

  组件架构：
  - 采用组件化拆分，每个子组件职责单一
  - 业务逻辑抽离到 useCabinetDetail mixin
  - 常量、工具函数独立文件管理

  依赖：
  - 子组件：DetailHeader, SortBar, FigureGrid, FigureList, EmptyState, FigureDetailDrawer, FigureOutDrawer
  - 逻辑：useCabinetDetail mixin
  - 常量：cabinetConfig
  - 工具：formatters
-->
<template>
  <div class="cabinet-detail">
    <!-- 返回按钮 -->
    <div class="detail-nav" @click="goBack">
      <span class="back-arrow">←</span>
      <span class="back-text">返回收藏柜</span>
    </div>

    <!-- 详情头部 -->
    <DetailHeader :cabinet="cabinet" />

    <!-- 排序栏 + 视图切换 -->
    <SortBar
      :sort-by="sortBy"
      :sort-order="sortOrder"
      :view-mode="viewMode"
      :count="cabinet.count"
      @sort="handleSort"
      @switch-view="handleSwitchView"
    />

    <!-- 有数据时：藏品展示 -->
    <template v-if="sortedItems && sortedItems.length > 0">
      <!-- 网格视图 -->
      <FigureGrid
        v-if="viewMode === 'grid'"
        :items="paginatedItems"
        :cabinet-key="cabinet.key"
        :cabinet-icon="cabinet.icon"
        :star-ratings="starRatings"
        :star-editing-index="starEditingIndex"
        @toggle-star="handleToggleStar"
        @set-rating="handleSetRating"
        @view-detail="handleViewDetail"
        @sell="handleSell"
      />

      <!-- 列表视图 -->
      <FigureList
        v-else
        :items="paginatedItems"
        :cabinet-key="cabinet.key"
        :cabinet-icon="cabinet.icon"
        :star-ratings="starRatings"
        @view-detail="handleViewDetail"
        @sell="handleSell"
      />

      <!-- 2026-08-06 翻页组件：复用 FiguresPagination 通用组件（与手办库同款） -->
      <FiguresPagination
        :current-page="currentPage"
        :page-size="pageSize"
        :page-sizes="pageSizes"
        :total="sortedItems.length"
        @current-change="handleCurrentChange"
        @size-change="handleSizeChange"
      />
    </template>

    <!-- 无数据时：空状态 -->
    <EmptyState
      v-else
      :icon="cabinet.icon"
      title="暂无数据"
      description="该分类下暂无藏品记录"
    />

    <!-- 查看详情抽屉 -->
    <FigureDetailDrawer
      :visible="detailDrawerVisible"
      :figure="selectedFigure"
      :cabinet-key="cabinet.key"
      :cabinet-name="cabinet.name"
      :cabinet-icon="cabinet.icon"
      :rating="starRatings[selectedFigure?.id] || 0"
      @close="detailDrawerVisible = false"
      @sell="handleDetailSell"
      @update-rating="handleUpdateRating"
    />

    <!-- 出柜登记抽屉 -->
    <FigureOutDrawer
      :visible="outDrawerVisible"
      :figure="selectedFigure"
      :cabinet-key="cabinet.key"
      :cabinet-name="cabinet.name"
      :cabinet-icon="cabinet.icon"
      @close="outDrawerVisible = false"
      @confirm="handleOutConfirm"
    />
  </div>
</template>

<script>
import DetailHeader from './components/DetailHeader.vue'
import SortBar from './components/SortBar.vue'
import FigureGrid from './components/FigureGrid.vue'
import FigureList from './components/FigureList.vue'
import EmptyState from './components/EmptyState.vue'
// 2026-08-06 翻页：复用 Figures 域下的 FiguresPagination 通用分页组件（与手办库同款）
import FiguresPagination from '@/views/Figures/components/FiguresPagination.vue'
import FigureDetailDrawer from './components/FigureDetailDrawer/FigureDetailDrawer.vue'
import FigureOutDrawer from './components/FigureOutDrawer/index.vue'
import useCabinetDetail from './composables/useCabinetDetail'
import axios from '@/axios'
import { ElMessage } from 'element-plus'
import { DEFAULT_CABINET } from './constants/cabinetConfig'

export default {
  name: 'CabinetDetail',

  components: {
    DetailHeader,
    SortBar,
    FigureGrid,
    FigureList,
    EmptyState,
    FiguresPagination,
    FigureDetailDrawer,
    FigureOutDrawer
  },

  mixins: [useCabinetDetail],

  data() {
    return {
      detailDrawerVisible: false,
      outDrawerVisible: false,
      selectedFigure: null
    }
  },

  props: {
    cabinet: {
      type: Object,
      required: true,
      default: () => DEFAULT_CABINET
    }
  },

  watch: {
    /**
     * 监听收藏柜变化，初始化排序状态
     */
    cabinet: {
      immediate: true,
      handler(newCabinet) {
        if (newCabinet?.key) {
          this.initSortByCabinet(newCabinet.key)
        }
      }
    }
  },

  methods: {
    /**
     * 返回上一级
     */
    goBack() {
      this.$emit('back')
    },

    /**
     * 处理排序点击（代理到 mixin 方法）
     * @param {Object} payload - { field }
     */
    handleSort({ field }) {
      this.doSort(field)
    },

    /**
     * 处理视图切换（代理到 mixin 方法）
     * @param {Object} payload - { mode }
     */
    handleSwitchView({ mode }) {
      this.switchView(mode)
    },

    /**
     * 处理切换评分编辑（代理到 mixin 方法）
     * @param {Object} payload - { index }
     */
    handleToggleStar({ index }) {
      this.toggleStarEdit(index)
    },

    /**
     * 处理设置评分（代理到 mixin 方法）
     * @param {Object} payload - { figureId, index, rating }
     */
    handleSetRating({ figureId, index, rating }) {
      this.setRating(figureId, index, rating)
    },

    /**
     * 处理查看详情
     * @param {Object} payload - { item }
     */
    handleViewDetail({ item }) {
      this.selectedFigure = item
      this.detailDrawerVisible = true
    },

    /**
     * 处理出柜登记（从卡片点击）
     * @param {Object} payload - { item }
     */
    handleSell({ item }) {
      this.selectedFigure = item
      this.outDrawerVisible = true
    },

    /**
     * 处理详情页出柜登记
     * @param {Object} payload - { figure }
     */
    handleDetailSell({ figure }) {
      this.detailDrawerVisible = false
      setTimeout(() => {
        this.selectedFigure = figure
        this.outDrawerVisible = true
      }, 300)
    },

    /**
     * 处理更新评分（从详情抽屉）
     * @param {Object} payload - { figureId, rating }
     */
    handleUpdateRating({ figureId, rating }) {
      this.starRatings = { ...this.starRatings, [figureId]: rating }
      // 自动保存到后端
      this.saveRating(figureId, rating)
    },

    /**
     * 保存评分到后端
     * @param {string} figureId - 手办ID
     * @param {number} rating - 评分值
     */
    async saveRating(figureId, rating) {
      try {
        await axios.post('/collector/ratings', {
          figure_id: figureId,
          cabinet_type: this.cabinet.key,
          rating: rating
        })
        ElMessage.success('已更新')
      } catch (e) {
        console.warn('评分保存失败:', e)
        ElMessage.error('评分保存失败')
      }
    },

    /**
     * 处理出柜登记确认（软出柜）
     * @param {Object} payload - { figureId, cabinetKey }
     */
    async handleOutConfirm(payload) {
      try {
        await axios.post(`/collector/cabinets/figures/${payload.figureId}/exclude`, {
          cabinet_type: payload.cabinetKey
        })
        ElMessage.success('出柜成功')
        this.outDrawerVisible = false
        // 刷新数据
        this.$emit('refresh')
      } catch (e) {
        ElMessage.error('出柜失败: ' + (e.response?.data?.detail || e.message))
      }
    }
  }
}
</script>

<style scoped>
.cabinet-detail {
  margin-bottom: 30px;
}

/* 返回导航 */
.detail-nav {
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
  margin-bottom: 20px;
  padding: 8px 12px;
  border-radius: 8px;
  transition: background 0.2s;
  background: #fff;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
  width: fit-content;
}

.detail-nav:hover {
  background: #FDF6EE;
}

.back-arrow {
  width: 28px;
  height: 28px;
  border-radius: 50%;
  border: 1px solid #EBE8E4;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 16px;
  color: #666;
}

.back-text {
  font-size: 14px;
  color: #666;
}
</style>
