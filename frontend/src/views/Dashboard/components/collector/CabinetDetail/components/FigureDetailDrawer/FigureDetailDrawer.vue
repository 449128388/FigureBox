<!--
  FigureDetailDrawer.vue - 藏品详情抽屉组件（重构版）

  功能说明：
  - 从右侧滑入的抽屉展示藏品详情
  - 采用组件化拆分，每个子组件职责单一
  - 常量、工具函数独立文件管理

  组件架构：
  - DrawerHeader: 头部区
  - FigureHero: Hero区（图片+基础信息）
  - FavoriteRating: 喜爱度评分
  - FigureBasicInfo: 基本信息网格
  - CollectionHistory: 收藏历程时间线
  - DrawerFooter: 底部操作区

  Props:
  - visible: Boolean - 是否显示抽屉
  - figure: Object - 藏品数据
  - cabinetKey: String - 收藏柜类型key
  - cabinetName: String - 收藏柜名称
  - cabinetIcon: String - 收藏柜图标
  - rating: Number - 当前评分值

  Events:
  - close: 关闭抽屉时触发
  - sell: 点击出柜登记时触发，参数 { figure }
  - update-rating: 评分变化时触发，参数 { figureId, rating }
-->
<template>
  <el-drawer
    v-model="drawerVisible"
    :size="680"
    :with-header="false"
    :modal="true"
    :modal-class="'figure-detail-drawer-modal'"
    direction="rtl"
    destroy-on-close
    @close="handleClose"
  >
    <div class="figure-detail-drawer" v-if="figureData">
      <!-- 头部区 -->
      <DrawerHeader title="🧸 藏品详情" @close="handleClose" />

      <!-- 内容区（可滚动） -->
      <div class="drawer-body">
        <!-- Hero 区域 -->
        <FigureHero
          :figure="figureData"
          :cabinet-icon="cabinetIcon"
          :status-text="statusInfo.text"
          :statuses-list="figureStatuses"
          :is-star-figure="isStarFigure"
        />

        <!-- 喜爱度 -->
        <FavoriteRating
          :rating="currentRating"
          @update-rating="handleRatingChange"
        />

        <!-- 基本信息 -->
        <FigureBasicInfo
          :figure="figureData"
          :cabinet-name="cabinetName"
          :status-label="statusInfo.label"
          :status-color="statusInfo.color"
          :statuses-list="figureStatuses"
        />

        <!-- 收藏历程 -->
        <CollectionHistory :history-list="historyList" />
      </div>

      <!-- 底部操作区 -->
      <DrawerFooter
        @close="handleClose"
        @sell="handleSell"
      />
    </div>
  </el-drawer>
</template>

<script>
import DrawerHeader from './components/DrawerHeader.vue'
import FigureHero from './components/FigureHero.vue'
import FavoriteRating from './components/FavoriteRating.vue'
import FigureBasicInfo from './components/FigureBasicInfo.vue'
import CollectionHistory from './components/CollectionHistory.vue'
import DrawerFooter from './components/DrawerFooter.vue'
import { getStatusInfo, getStatusClass, getStatusLabel, generateHistoryList, isStarFigure } from './utils/figureFormatter'
import axios from '@/axios'

export default {
  name: 'FigureDetailDrawer',

  components: {
    DrawerHeader,
    FigureHero,
    FavoriteRating,
    FigureBasicInfo,
    CollectionHistory,
    DrawerFooter
  },

  props: {
    visible: {
      type: Boolean,
      default: false
    },
    figure: {
      type: Object,
      default: () => ({})
    },
    cabinetKey: {
      type: String,
      default: ''
    },
    cabinetName: {
      type: String,
      default: ''
    },
    cabinetIcon: {
      type: String,
      default: '📦'
    },
    rating: {
      type: Number,
      default: 0
    }
  },

  data() {
    return {
      drawerVisible: this.visible,
      currentRating: this.rating,
      transactionHistory: []
    }
  },

  computed: {
    figureData() {
      return this.figure
    },

    statusInfo() {
      return getStatusInfo(this.cabinetKey)
    },

    isStarFigure() {
      return isStarFigure(this.cabinetKey, this.currentRating)
    },

    /**
     * 从 figure.statuses 数组生成多状态标签列表
     * 兼容旧版单 status 字段
     * 当 figure 无 statuses 字段时，从 cabinetKey 推导状态
     */
    figureStatuses() {
      const statuses = this.figureData.statuses || (this.figureData.status ? [this.figureData.status] : [])
      if (statuses.length > 0) {
        const STATUS_MAP = {
          'in': { text: '在柜', cls: 'st-in' },
          'air_unpaid': { text: '空气谷', cls: 'st-air' },
          'air_paid': { text: '待出荷', cls: 'st-air-paid' },
          'out': { text: '已出', cls: 'st-out' }
        }
        return statuses.map(s => STATUS_MAP[s] || { text: s, cls: 'st-in' })
      }
      // 从 cabinetKey 推导状态，使用 figureDetailConfig 中的常量
      return [{
        text: getStatusLabel(this.cabinetKey),
        cls: getStatusClass(this.cabinetKey)
      }]
    },

    historyList() {
      if (this.transactionHistory.length > 0) {
        return this.transactionHistory
      }
      // 无 API 数据时回退到本地生成
      return generateHistoryList(this.figureData)
    }
  },

  watch: {
    visible(val) {
      this.drawerVisible = val
      if (val) {
        this.currentRating = this.rating
        this.fetchTransactionHistory()
      }
    },
    rating(val) {
      this.currentRating = val
    }
  },

  methods: {
    handleClose() {
      this.drawerVisible = false
      this.transactionHistory = []
      this.$emit('close')
    },

    handleSell() {
      this.$emit('sell', { figure: this.figureData })
    },

    handleRatingChange({ rating }) {
      this.currentRating = rating
      this.$emit('update-rating', { figureId: this.figureData.id, rating })
    },

    /**
     * 获取手办收藏历程流水
     */
    async fetchTransactionHistory() {
      if (!this.figureData?.id) return
      try {
        const res = await axios.get(`/collector/figures/${this.figureData.id}/transactions`)
        if (res?.transactions && res.transactions.length > 0) {
          this.transactionHistory = res.transactions
        }
      } catch (e) {
        console.warn('获取收藏历程失败:', e)
      }
    }
  }
}
</script>

<style scoped>
.figure-detail-drawer {
  height: 100%;
  display: flex;
  flex-direction: column;
}

.drawer-body {
  padding: 24px;
  overflow-y: auto;
  flex: 1;
}
</style>
