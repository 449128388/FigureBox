<!--
  CabinetDetail.vue - 收藏家模式我的收藏柜详情组件（重构版）

  功能说明：
  - 展示某个收藏柜分类的详细藏品列表
  - 包含详情头部、排序栏、藏品网格/列表视图切换
  - 每个藏品支持交互式喜爱度评分
  - 无数据时展示"暂无数据"空状态
  - 支持返回上一级（收藏柜概览）

  组件架构：
  - 采用组件化拆分，每个子组件职责单一
  - 业务逻辑抽离到 useCabinetDetail mixin
  - 常量、工具函数独立文件管理

  依赖：
  - 子组件：DetailHeader, SortBar, FigureGrid, FigureList, EmptyState
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
        :items="sortedItems"
        :cabinet-key="cabinet.key"
        :cabinet-icon="cabinet.icon"
        :star-ratings="starRatings"
        :star-editing-index="starEditingIndex"
        @toggle-star="handleToggleStar"
        @set-rating="handleSetRating"
      />

      <!-- 列表视图 -->
      <FigureList
        v-else
        :items="sortedItems"
        :cabinet-key="cabinet.key"
        :cabinet-icon="cabinet.icon"
        :star-ratings="starRatings"
      />
    </template>

    <!-- 无数据时：空状态 -->
    <EmptyState
      v-else
      :icon="cabinet.icon"
      title="暂无数据"
      description="该分类下暂无藏品记录"
    />
  </div>
</template>

<script>
import DetailHeader from './components/DetailHeader.vue'
import SortBar from './components/SortBar.vue'
import FigureGrid from './components/FigureGrid.vue'
import FigureList from './components/FigureList.vue'
import EmptyState from './components/EmptyState.vue'
import useCabinetDetail from './composables/useCabinetDetail'
import { DEFAULT_CABINET } from './constants/cabinetConfig'

export default {
  name: 'CabinetDetail',

  components: {
    DetailHeader,
    SortBar,
    FigureGrid,
    FigureList,
    EmptyState
  },

  mixins: [useCabinetDetail],

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
