<!--
  CabinetDetail.vue - 收藏家模式我的收藏柜详情组件

  功能说明：
  - 展示某个收藏柜分类的详细藏品列表
  - 包含详情头部（图标、标题、描述、统计）、排序栏、藏品网格
  - 每个藏品支持交互式喜爱度评分（点击展开5星，点击选择，自动保存）
  - 无数据时展示"暂无数据"空状态
  - 支持返回上一级（收藏柜概览）

  组件依赖：
  - 接收 cabinet 作为 props，包含该分类的完整数据

  样式参考：
  - cabinet_detail.html 的 detail-view 部分

  维护提示：
  - 藏品网格最多展示 items 数组中的藏品
  - 空状态显示灰色占位卡片 + "暂无数据"文案
-->
<template>
  <div class="cabinet-detail">
    <!-- 返回按钮 -->
    <div class="detail-nav" @click="goBack">
      <span class="back-arrow">←</span>
      <span class="back-text">返回收藏柜</span>
    </div>

    <!-- 详情头部 -->
    <div class="detail-header">
      <div class="detail-header-left">
        <div class="detail-icon" :style="{ background: cabinet.icon_bg }">
          {{ cabinet.icon }}
        </div>
        <div>
          <div class="detail-title">{{ cabinet.name }}</div>
          <div class="detail-sub">{{ getSubtitle(cabinet.key) }}</div>
        </div>
      </div>
      <div class="detail-stats">
        <div class="d-stat">
          <div class="d-stat-num">{{ cabinet.count }}</div>
          <div class="d-stat-label">藏品</div>
        </div>
        <div class="d-stat" v-if="cabinet.key !== 'air' && cabinet.key !== 'wait'">
          <div class="d-stat-num">{{ formatCompanionDays }}</div>
          <div class="d-stat-label">陪伴天数</div>
        </div>
      </div>
    </div>

    <!-- 排序栏 + 视图切换 -->
    <div class="sort-bar">
      <div class="sort-left">
        <span
          class="sort-tag"
          :class="{ active: sortBy === 'transaction_date' }"
          @click="handleSort('transaction_date')"
        >
          入库时间
          <span v-if="sortBy === 'transaction_date'" class="sort-arrow">{{ sortOrder === 'asc' ? '↑' : '↓' }}</span>
        </span>
        <span
          class="sort-tag"
          :class="{ active: sortBy === 'name' }"
          @click="handleSort('name')"
        >
          名称
          <span v-if="sortBy === 'name'" class="sort-arrow">{{ sortOrder === 'asc' ? '↑' : '↓' }}</span>
        </span>
        <span
          class="sort-tag"
          :class="{ active: sortBy === 'rating' }"
          @click="handleSort('rating')"
        >
          喜爱度
          <span v-if="sortBy === 'rating'" class="sort-arrow">{{ sortOrder === 'asc' ? '↑' : '↓' }}</span>
        </span>
        <span
          class="sort-tag"
          :class="{ active: sortBy === 'holding_days' }"
          @click="handleSort('holding_days')"
        >
          收藏天数
          <span v-if="sortBy === 'holding_days'" class="sort-arrow">{{ sortOrder === 'asc' ? '↑' : '↓' }}</span>
        </span>
      </div>
      <div class="sort-right">
        <div class="view-toggle" v-if="cabinet.count > 0">
          <button
            class="view-btn"
            :class="{ active: viewMode === 'grid' }"
            @click="switchView('grid')"
          >
            ⊞ 网格
          </button>
          <button
            class="view-btn"
            :class="{ active: viewMode === 'list' }"
            @click="switchView('list')"
          >
            ☰ 列表
          </button>
        </div>
        <div class="sort-count" v-if="cabinet.count > 0">
          共 {{ cabinet.count }} 件藏品
        </div>
      </div>
    </div>

    <!-- 有数据时：藏品展示 -->
    <template v-if="sortedItems && sortedItems.length > 0">
      <!-- 网格视图 -->
      <div v-if="viewMode === 'grid'" class="figure-grid">
        <div
          v-for="(item, index) in sortedItems"
          :key="item.id || index"
          class="figure-card"
        >
          <div class="figure-img-wrap">
            <div v-if="item.image" class="figure-img-real">
              <img :src="item.image" :alt="item.name" />
            </div>
            <div v-else class="figure-img-placeholder">{{ cabinet.icon }}</div>
            <span class="figure-status" :class="getStatusClass(cabinet.key)">{{ getStatusText(cabinet.key) }}</span>
            <!-- 交互式喜爱度评分 -->
            <div
              class="figure-stars"
              :class="{ 'is-editing': starEditingIndex === index }"
              @click.stop="toggleStarEdit(index)"
            >
              <template v-if="starEditingIndex === index">
                <span
                  v-for="s in 5"
                  :key="s"
                  class="star-btn"
                  :class="{ filled: s <= (starTempValue || starRatings[item.id] || 0) }"
                  @click.stop="setRating(item.id, index, s)"
                >★</span>
              </template>
              <template v-else>
                <span v-for="s in 5" :key="s" class="star-display" :class="{ filled: s <= (starRatings[item.id] || 0) }">★</span>
              </template>
            </div>
          </div>
          <div class="figure-info">
            <div class="figure-name">{{ item.name || '未知手办' }}</div>
            <div class="figure-line">{{ formatFigureInfo(item) }}</div>
            <div class="figure-line-gray">{{ formatDateInfo(item) }}</div>
            <div class="figure-actions">
              <button class="btn-tiny">查看详情</button>
              <button class="btn-tiny btn-tiny-primary">出柜登记</button>
            </div>
          </div>
        </div>
      </div>

      <!-- 列表视图 -->
      <div v-else class="figure-list">
        <div
          v-for="(item, index) in sortedItems"
          :key="item.id || index"
          class="list-item"
        >
          <div class="list-thumb">
            <div v-if="item.image" class="list-thumb-img">
              <img :src="item.image" :alt="item.name" />
            </div>
            <div v-else class="list-thumb-placeholder">{{ cabinet.icon }}</div>
          </div>
          <div class="list-body">
            <div class="list-title">{{ item.name || '未知手办' }}</div>
            <div class="list-meta">{{ formatFigureInfo(item) }} · {{ formatDateInfo(item) }}</div>
            <div class="list-tags">
              <span class="list-status-tag" :class="getStatusClass(cabinet.key)">{{ getStatusText(cabinet.key) }}</span>
              <!-- 列表模式喜爱度评分 -->
              <span class="list-star-tag">
                <span v-for="s in 5" :key="s" class="star-mini" :class="{ filled: s <= (starRatings[item.id] || 0) }">★</span>
              </span>
            </div>
          </div>
          <div class="list-actions">
            <button class="btn-tiny">查看详情</button>
          </div>
        </div>
      </div>
    </template>

    <!-- 无数据时：空状态 -->
    <div v-else class="empty-state">
      <div class="empty-icon">{{ cabinet.icon }}</div>
      <div class="empty-title">暂无数据</div>
      <div class="empty-desc">该分类下暂无藏品记录</div>
    </div>
  </div>
</template>

<script>
import axios from '../../../../axios'
import { ElMessage } from 'element-plus'

export default {
  name: 'CabinetDetail',
  props: {
    cabinet: {
      type: Object,
      required: true,
      default: () => ({
        key: '',
        name: '',
        description: '',
        icon: '📦',
        icon_bg: '#F5F5F5',
        count: 0,
        companion_days: 0,
        meta: '',
        items: []
      })
    }
  },
  data() {
    return {
      starRatings: {},        // { figureId: rating }
      starEditingIndex: null, // 当前正在编辑的卡片索引
      starTempValue: 0,       // 编辑中的临时值
      viewMode: 'grid',       // 视图模式: 'grid' 网格 / 'list' 列表
      sortBy: 'name',         // 排序字段: 'transaction_date' / 'name' / 'rating' / 'holding_days'
      sortOrder: 'asc'        // 排序方向: 'asc' 升序 / 'desc' 降序
    }
  },
  computed: {
    formatCompanionDays() {
      const days = this.cabinet.companion_days
      if (!days || days === 0) return '-'
      return days.toLocaleString()
    },
    // 排序后的藏品列表
    sortedItems() {
      if (!this.cabinet.items || this.cabinet.items.length === 0) return []
      const items = [...this.cabinet.items]
      const sortBy = this.sortBy
      const sortOrder = this.sortOrder

      items.sort((a, b) => {
        let valA, valB

        switch (sortBy) {
          case 'name':
            valA = (a.name || '').toLowerCase()
            valB = (b.name || '').toLowerCase()
            break
          case 'transaction_date':
            valA = a.transaction_date || ''
            valB = b.transaction_date || ''
            break
          case 'rating':
            valA = this.starRatings[a.id] || 0
            valB = this.starRatings[b.id] || 0
            break
          case 'holding_days':
            valA = a.holding_days || 0
            valB = b.holding_days || 0
            break
          default:
            valA = (a.name || '').toLowerCase()
            valB = (b.name || '').toLowerCase()
        }

        if (valA < valB) return sortOrder === 'asc' ? -1 : 1
        if (valA > valB) return sortOrder === 'asc' ? 1 : -1
        return 0
      })

      return items
    }
  },
  mounted() {
    this.fetchRatings()
  },
  methods: {
    // 获取当前收藏柜中所有手办的评分
    async fetchRatings() {
      if (!this.cabinet.items || this.cabinet.items.length === 0) return
      const figureIds = this.cabinet.items.map(it => it.id).filter(Boolean).join(',')
      if (!figureIds) return
      try {
        const res = await axios.get('/collector/ratings', {
          params: {
            cabinet_type: this.cabinet.key,
            figure_ids: figureIds
          }
        })
        const ratings = res.ratings || []
        const map = {}
        ratings.forEach(r => { map[r.figure_id] = r.rating })
        this.starRatings = map
      } catch (e) {
        // 静默失败，显示无评分
      }
    },
    // 切换编辑状态
    toggleStarEdit(index) {
      if (this.starEditingIndex === index) {
        // 再次点击同一张卡 → 关闭编辑
        this.starEditingIndex = null
        this.starTempValue = 0
      } else {
        // 点击其他卡 → 打开编辑
        const item = this.cabinet.items[index]
        this.starEditingIndex = index
        this.starTempValue = this.starRatings[item.id] || 0
      }
    },
    // 设置评分并自动保存
    async setRating(figureId, index, rating) {
      this.starTempValue = rating
      this.starRatings = { ...this.starRatings, [figureId]: rating }

      // 0.5 秒后自动保存
      setTimeout(async () => {
        try {
          await axios.post('/collector/ratings', {
            figure_id: figureId,
            cabinet_type: this.cabinet.key,
            rating: rating
          })
          ElMessage.success('已更新')
        } catch (e) {
          ElMessage.error('评分保存失败')
        }
      }, 500)

      // 关闭编辑状态
      this.starEditingIndex = null
      this.starTempValue = 0
    },
    goBack() {
      this.$emit('back')
    },
    getSubtitle(key) {
      const map = {
        star: '你最珍视的藏品，陪伴最久的塑料小人',
        new: '30天内加入收藏室的新成员',
        fix: '正在补件、补色或返厂中的病号',
        out: '已经找到新主人的藏品，感谢陪伴',
        air: '空气谷 — 已下单但尚未入库的藏品',
        dup: '同一手办持有2体以上的复数库存',
        wait: '已付清全款或尾款，等待工厂出荷',
        role: '你最钟爱的角色全收集'
      }
      return map[key] || '我的收藏柜详情'
    },
    getStatusClass(key) {
      const map = {
        star: 'st-in',
        new: 'st-in',
        fix: 'st-fix',
        out: 'st-out',
        air: 'st-air',
        dup: 'st-in',
        wait: 'st-air',
        role: 'st-in'
      }
      return map[key] || 'st-in'
    },
    getStatusText(key) {
      const map = {
        star: '在柜',
        new: '在柜',
        fix: '修复中',
        out: '已出',
        air: '预定中',
        dup: '复数',
        wait: '待出荷',
        role: '本命'
      }
      return map[key] || '在柜'
    },
    // 切换视图模式
    switchView(mode) {
      this.viewMode = mode
    },
    // 处理排序点击
    handleSort(field) {
      if (this.sortBy === field) {
        // 同一字段再次点击，切换排序方向
        this.sortOrder = this.sortOrder === 'asc' ? 'desc' : 'asc'
      } else {
        // 切换排序字段，默认升序
        this.sortBy = field
        this.sortOrder = 'asc'
      }
    },
    // 格式化作品·比例·制造商
    formatFigureInfo(item) {
      const work = item.work || '未知'
      const scale = item.scale || '未知'
      const manufacturer = item.manufacturer || '未知'
      return `${work} · ${scale} · ${manufacturer}`
    },
    // 格式化入柜时间·陪伴时间
    formatDateInfo(item) {
      const date = item.transaction_date || '未知'
      const days = item.holding_days
      if (days && days > 0) {
        return `入柜 ${date} · 陪伴 ${days} 天`
      }
      return `入柜 ${date}`
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
  box-shadow: 0 2px 8px rgba(0,0,0,0.04);
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

/* 详情头部 */
.detail-header {
  background: #fff;
  border-radius: 12px;
  padding: 20px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.04);
  margin-bottom: 20px;
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.detail-header-left {
  display: flex;
  align-items: center;
  gap: 16px;
}

.detail-icon {
  width: 48px;
  height: 48px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24px;
  flex-shrink: 0;
}

.detail-title {
  font-size: 18px;
  font-weight: 600;
  color: #1F1F1F;
}

.detail-sub {
  font-size: 13px;
  color: #999;
  margin-top: 2px;
}

.detail-stats {
  display: flex;
  gap: 16px;
}

.d-stat {
  text-align: center;
}

.d-stat-num {
  font-size: 20px;
  font-weight: 700;
  color: #1F1F1F;
}

.d-stat-label {
  font-size: 12px;
  color: #999;
}

/* 排序栏 */
.sort-bar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 16px;
}

.sort-left {
  display: flex;
  gap: 8px;
}

.sort-tag {
  padding: 4px 10px;
  border-radius: 14px;
  font-size: 12px;
  border: 1px solid #EBE8E4;
  background: #fff;
  color: #666;
  cursor: pointer;
}

.sort-tag.active {
  background: #FDF6EE;
  border-color: #C49A6C;
  color: #C49A6C;
  font-weight: 500;
}

.sort-count {
  font-size: 13px;
  color: #999;
}

.sort-right {
  display: flex;
  align-items: center;
  gap: 16px;
}

/* 视图切换按钮 */
.view-toggle {
  display: flex;
  gap: 6px;
}

.view-btn {
  padding: 5px 12px;
  border: 1px solid #EBE8E4;
  background: #fff;
  border-radius: 6px;
  font-size: 13px;
  color: #666;
  cursor: pointer;
  transition: all 0.2s;
}

.view-btn:hover {
  border-color: #C49A6C;
  color: #C49A6C;
}

.view-btn.active {
  border-color: #C49A6C;
  color: #C49A6C;
  background: #FDF6EE;
}

/* 藏品网格 */
.figure-grid {
  display: grid;
  grid-template-columns: repeat(5, 1fr);
  gap: 14px;
}

.figure-card {
  background: #fff;
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 2px 8px rgba(0,0,0,0.04);
  transition: transform 0.2s, box-shadow 0.2s;
}

.figure-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 16px rgba(0,0,0,0.08);
}

.figure-img-wrap {
  height: 180px;
  background: #F0EEEB;
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
}

.figure-img-placeholder {
  width: 100px;
  height: 100px;
  background: #E0DCD7;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 40px;
  color: #B0ABA5;
}

.figure-img-real {
  width: 100%;
  height: 100%;
}

.figure-img-real img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.figure-status {
  position: absolute;
  top: 10px;
  left: 10px;
  padding: 3px 8px;
  border-radius: 10px;
  font-size: 11px;
  font-weight: 600;
  color: #fff;
}

.st-in { background: #7EB8A2; }
.st-air { background: #9B7ED8; }
.st-fix { background: #E6A23C; }
.st-out { background: #999; }

/* 喜爱度星星 - 交互式 */
.figure-stars {
  position: absolute;
  bottom: 10px;
  right: 10px;
  background: rgba(255,255,255,0.9);
  padding: 3px 8px;
  border-radius: 10px;
  font-size: 13px;
  color: #E6A23C;
  cursor: pointer;
  transition: all 0.2s;
  user-select: none;
  letter-spacing: 1px;
}

.figure-stars:hover {
  background: rgba(255,255,255,1);
  box-shadow: 0 2px 8px rgba(0,0,0,0.12);
}

.figure-stars.is-editing {
  background: #fff;
  box-shadow: 0 2px 12px rgba(0,0,0,0.15);
  padding: 4px 10px;
}

.star-display,
.star-btn {
  display: inline-block;
  transition: transform 0.15s, color 0.15s;
  color: #ddd;
}

.star-display.filled,
.star-btn.filled {
  color: #E6A23C;
}

.star-btn {
  cursor: pointer;
  font-size: 15px;
}

.star-btn:hover {
  transform: scale(1.3);
  color: #E6A23C;
}

.figure-info {
  padding: 14px;
}

.figure-name {
  font-size: 15px;
  font-weight: 600;
  margin-bottom: 4px;
  color: #1F1F1F;
}

.figure-line {
  font-size: 12px;
  color: #666;
  margin-bottom: 2px;
}

.figure-line-gray {
  font-size: 12px;
  color: #999;
  margin-bottom: 2px;
}

.figure-actions {
  display: flex;
  gap: 8px;
  margin-top: 10px;
}

.btn-tiny {
  flex: 1;
  padding: 6px 0;
  text-align: center;
  border: 1px solid #EBE8E4;
  background: #fff;
  border-radius: 6px;
  font-size: 12px;
  color: #666;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-tiny:hover {
  border-color: #C49A6C;
  color: #C49A6C;
}

.btn-tiny-primary {
  background: #FDF6EE;
  border-color: #C49A6C;
  color: #C49A6C;
  font-weight: 500;
}

/* 列表视图 */
.figure-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.list-item {
  background: #fff;
  border-radius: 12px;
  padding: 14px 16px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.04);
  display: flex;
  align-items: center;
  gap: 14px;
  transition: transform 0.2s, box-shadow 0.2s;
}

.list-item:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 16px rgba(0,0,0,0.08);
}

.list-thumb {
  width: 56px;
  height: 56px;
  background: #F0EEEB;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  overflow: hidden;
}

.list-thumb-img {
  width: 100%;
  height: 100%;
}

.list-thumb-img img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.list-thumb-placeholder {
  font-size: 24px;
  color: #B0ABA5;
}

.list-body {
  flex: 1;
  min-width: 0;
}

.list-title {
  font-size: 15px;
  font-weight: 600;
  color: #1F1F1F;
  margin-bottom: 4px;
}

.list-meta {
  font-size: 12px;
  color: #666;
  margin-bottom: 6px;
}

.list-tags {
  display: flex;
  align-items: center;
  gap: 8px;
}

.list-status-tag {
  display: inline-block;
  padding: 2px 8px;
  border-radius: 10px;
  font-size: 11px;
  font-weight: 600;
  color: #fff;
}

.list-star-tag {
  font-size: 11px;
  color: #E6A23C;
  letter-spacing: 1px;
}

.star-mini {
  color: #ddd;
}

.star-mini.filled {
  color: #E6A23C;
}

.list-actions {
  flex-shrink: 0;
}

/* 空状态 */
.empty-state {
  background: #fff;
  border-radius: 12px;
  padding: 60px 20px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.04);
  text-align: center;
}

.empty-icon {
  font-size: 56px;
  margin-bottom: 16px;
}

.empty-title {
  font-size: 18px;
  font-weight: 600;
  color: #1F1F1F;
  margin-bottom: 8px;
}

.empty-desc {
  font-size: 14px;
  color: #999;
}

@media (max-width: 768px) {
  .figure-grid {
    grid-template-columns: repeat(2, 1fr);
  }
  .detail-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 16px;
  }
}
</style>
