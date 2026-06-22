<!--
  ManufacturerDetail.vue - 本命厂商详情页组件

  功能说明：
  - 展示单个本命厂商的详细信息
  - Hero 区域展示厂商 Logo、名称、描述、链接
  - 统计面板展示总藏品、在柜、预定中、已出数量
  - 手办网格展示该厂商下的所有藏品

  布局参考：
  - 原型 cabinet_detail.html 中本命厂商详情页图二风格
-->
<template>
  <div class="manufacturer-detail">
    <!-- 返回按钮 -->
    <div class="detail-nav" @click="$emit('back')">
      <span class="back-arrow">←</span>
      <span class="back-text">返回厂商列表</span>
    </div>

    <!-- 加载中 -->
    <div v-if="loading" class="loading-state">
      <div class="loading-spinner"></div>
      <div class="loading-text">加载中...</div>
    </div>

    <template v-else-if="manufacturer">
      <!-- 厂商信息 Hero（参考图二风格） -->
      <div class="maker-hero">
        <div class="maker-hero-main">
          <div class="maker-hero-logo">
            <template v-if="manufacturer.logo_url">
              <img :src="manufacturer.logo_url" :alt="manufacturer.name">
            </template>
            <template v-else>
              🏭
            </template>
          </div>
          <div class="maker-hero-info">
            <div class="maker-hero-tag">厂商</div>
            <div class="maker-hero-name">{{ manufacturer.name }}</div>
            <div class="maker-hero-desc">{{ manufacturer.description || '暂无描述' }}</div>
            <div class="maker-hero-links">
              <a
                v-if="manufacturer.website_url"
                :href="manufacturer.website_url"
                class="maker-link"
                target="_blank"
              >🔗 官网：点击进入</a>
              <a
                v-if="manufacturer.twitter_url"
                :href="manufacturer.twitter_url"
                class="maker-link"
                target="_blank"
              >🐦 推特：点击进入</a>
            </div>
          </div>
        </div>
        <div class="maker-hero-footer">
          <div class="maker-hero-stat">
            <div class="maker-hero-stat-num">{{ manufacturer.total_count || 0 }}</div>
            <div class="maker-hero-stat-label">总藏品</div>
          </div>
          <div class="maker-hero-stat">
            <div class="maker-hero-stat-num">{{ manufacturer.in_count || 0 }}</div>
            <div class="maker-hero-stat-label">在柜</div>
          </div>
          <div class="maker-hero-stat">
            <div class="maker-hero-stat-num">{{ manufacturer.air_count || 0 }}</div>
            <div class="maker-hero-stat-label">预定中</div>
          </div>
          <div class="maker-hero-stat">
            <div class="maker-hero-stat-num">{{ manufacturer.out_count || 0 }}</div>
            <div class="maker-hero-stat-label">已出</div>
          </div>
        </div>
      </div>

      <!-- 操作栏 -->
      <div class="sort-bar">
        <div class="sort-left">
          <span
            v-for="tab in filterTabs"
            :key="tab.key"
            class="sort-tag"
            :class="{ active: filterStatus === tab.key }"
            @click="filterStatus = tab.key"
          >{{ tab.label }}</span>
        </div>
        <div>
          <button class="btn-header" @click="$emit('edit', manufacturer)">
            ✏️ 编辑厂商
          </button>
        </div>
      </div>

      <!-- 手办网格 -->
      <div v-if="filteredFigures.length > 0" class="figure-grid">
        <div
          v-for="fig in filteredFigures"
          :key="fig.id"
          class="figure-card"
        >
          <div class="figure-img-wrap">
            <img v-if="fig.image" :src="fig.image" :alt="fig.name" class="figure-img">
            <div v-else class="figure-img-placeholder">🧸</div>
            <div class="figure-statuses">
              <span
                v-for="s in (fig.statuses || [fig.status])"
                :key="s"
                class="figure-status"
                :class="statusClass(s)"
              >
                {{ statusText(s) }}
              </span>
            </div>
          </div>
          <div class="figure-info">
            <div class="figure-name">{{ fig.name }}</div>
            <div class="figure-line">{{ fig.work }} · {{ fig.scale }} · {{ fig.manufacturer }}</div>
            <div class="figure-line-gray" v-if="fig.transaction_date">
              入柜 {{ fig.transaction_date }} · 陪伴 {{ fig.companion_days || 0 }} 天
            </div>
            <div class="figure-actions">
              <button class="btn-tiny" @click.stop="$emit('view-figure', fig)">查看详情</button>
              <button
                v-if="figHasStatus(fig, 'in')"
                class="btn-tiny btn-tiny-primary"
                @click.stop="$emit('sell', fig)"
              >出柜登记</button>
            </div>
          </div>
        </div>
      </div>

      <!-- 空手办状态 -->
      <div v-else class="empty-state">
        <div class="empty-state-icon">📦</div>
        <div class="empty-state-title">{{ filterStatus === 'all' ? '暂无藏品' : '无匹配藏品' }}</div>
        <div class="empty-state-desc">{{ filterStatus === 'all' ? '该厂商下暂无手办记录' : '当前筛选条件下无手办记录' }}</div>
      </div>
    </template>
  </div>
</template>

<script>
export default {
  name: 'ManufacturerDetail',
  props: {
    manufacturer: {
      type: Object,
      default: null
    },
    loading: {
      type: Boolean,
      default: false
    }
  },
  emits: ['back', 'edit', 'view-figure', 'sell'],
  data() {
    return {
      filterStatus: 'all',
      filterTabs: [
        { key: 'all', label: '全部' },
        { key: 'in', label: '在柜' },
        { key: 'air', label: '预定中' },
        { key: 'out', label: '已出' }
      ]
    }
  },
  computed: {
    filteredFigures() {
      if (!this.manufacturer || !this.manufacturer.figures) return []
      if (this.filterStatus === 'all') return this.manufacturer.figures
      if (this.filterStatus === 'air') {
        return this.manufacturer.figures.filter(fig => {
          const statuses = fig.statuses || [fig.status]
          return statuses.includes('air_unpaid') || statuses.includes('air_paid')
        })
      }
      if (this.filterStatus === 'in') {
        return this.manufacturer.figures.filter(fig => {
          const statuses = fig.statuses || [fig.status]
          return statuses.includes('in')
        })
      }
      if (this.filterStatus === 'out') {
        return this.manufacturer.figures.filter(fig => {
          const statuses = fig.statuses || [fig.status]
          return statuses.includes('out')
        })
      }
      return this.manufacturer.figures
    }
  },
  methods: {
    statusClass(s) {
      if (s === 'in') return 'st-in'
      if (s === 'air_unpaid') return 'st-air'
      if (s === 'air_paid') return 'st-air-paid'
      return 'st-out'
    },
    statusText(s) {
      if (s === 'in') return '在柜'
      if (s === 'air_unpaid') return '空气谷'
      if (s === 'air_paid') return '待出荷'
      return '已出'
    },
    figHasStatus(fig, s) {
      const statuses = fig.statuses || [fig.status]
      return statuses.includes(s)
    }
  }
}
</script>

<style scoped>
.detail-nav {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 16px;
  cursor: pointer;
  color: #666;
  font-size: 14px;
  padding: 4px 0;
  transition: color 0.2s;
}

.detail-nav:hover {
  color: #C49A6C;
}

.back-arrow {
  font-size: 18px;
  line-height: 1;
}

.back-text {
  font-size: 14px;
}

/* Loading */
.loading-state {
  text-align: center;
  padding: 60px 20px;
  color: #999;
}

.loading-spinner {
  width: 32px;
  height: 32px;
  border: 3px solid #EBE8E4;
  border-top-color: #00BCD4;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
  margin: 0 auto 12px;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.loading-text {
  font-size: 14px;
}

/* Maker Hero */
.maker-hero {
  background: #fff;
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 2px 8px rgba(0,0,0,0.04);
  margin-bottom: 20px;
}

.maker-hero-main {
  display: flex;
  gap: 20px;
  padding: 24px;
}

.maker-hero-logo {
  width: 140px;
  height: 140px;
  background: #F0EEEB;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 48px;
  color: #B0ABA5;
  flex-shrink: 0;
  overflow: hidden;
  border: 1px solid #EBE8E4;
}

.maker-hero-logo img {
  width: 100%;
  height: 100%;
  object-fit: contain;
  padding: 8px;
}

.maker-hero-info {
  flex: 1;
  display: flex;
  flex-direction: column;
  justify-content: center;
}

.maker-hero-tag {
  display: inline-block;
  font-size: 12px;
  padding: 2px 10px;
  border-radius: 4px;
  background: #E0F7FA;
  color: #00BCD4;
  border: 1px solid #B2EBF2;
  margin-bottom: 8px;
  width: fit-content;
}

.maker-hero-name {
  font-size: 22px;
  font-weight: 700;
  margin-bottom: 6px;
}

.maker-hero-desc {
  font-size: 14px;
  color: #666;
  line-height: 1.6;
}

.maker-hero-links {
  display: flex;
  gap: 20px;
  margin-top: 12px;
}

.maker-link {
  font-size: 13px;
  color: #00BCD4;
  text-decoration: none;
  display: flex;
  align-items: center;
  gap: 4px;
  transition: opacity 0.2s;
}

.maker-link:hover {
  opacity: 0.7;
}

.maker-hero-footer {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 1px;
  background: #EBE8E4;
  border-top: 1px solid #EBE8E4;
}

.maker-hero-stat {
  background: #fff;
  padding: 14px;
  text-align: center;
}

.maker-hero-stat-num {
  font-size: 20px;
  font-weight: 700;
  color: #00BCD4;
}

.maker-hero-stat-label {
  font-size: 12px;
  color: #999;
  margin-top: 2px;
}

/* Sort Bar */
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
  transition: all 0.2s;
}

.sort-tag:hover {
  border-color: #B2EBF2;
  color: #00BCD4;
}

.sort-tag.active {
  background: #E0F7FA;
  border-color: #00BCD4;
  color: #00BCD4;
  font-weight: 500;
}

.btn-header {
  padding: 6px 14px;
  border: 1px solid #EBE8E4;
  background: #fff;
  border-radius: 6px;
  font-size: 13px;
  color: #666;
  cursor: pointer;
  transition: all 0.2s;
  display: flex;
  align-items: center;
  gap: 4px;
}

.btn-header:hover {
  border-color: #00BCD4;
  color: #00BCD4;
  background: #E0F7FA;
}

/* Figure Grid */
.figure-grid {
  display: grid;
  grid-template-columns: repeat(5, 1fr);
  gap: 16px;
}

.figure-card {
  background: #fff;
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 2px 8px rgba(0,0,0,0.04);
  transition: transform 0.2s, box-shadow 0.2s;
  cursor: pointer;
  border: 1px solid transparent;
}

.figure-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 16px rgba(0,0,0,0.08);
  border-color: #B2EBF2;
}

.figure-img-wrap {
  height: 180px;
  background: #F0EEEB;
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
  overflow: hidden;
}

.figure-img {
  width: 100%;
  height: 100%;
  object-fit: cover;
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

.figure-statuses {
  position: absolute;
  top: 10px;
  left: 10px;
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.figure-status {
  padding: 3px 8px;
  border-radius: 10px;
  font-size: 11px;
  font-weight: 600;
  color: #fff;
  width: fit-content;
}

.st-in { background: #7EB8A2; }
.st-air { background: #9B7ED8; }
.st-air-paid { background: #4A90D9; }
.st-out { background: #999; }

.figure-info {
  padding: 14px;
}

.figure-name {
  font-size: 15px;
  font-weight: 600;
  margin-bottom: 4px;
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

.btn-tiny-primary:hover {
  background: #C49A6C;
  color: #fff;
}

/* Empty State */
.empty-state {
  text-align: center;
  padding: 80px 20px;
  color: #999;
}

.empty-state-icon {
  font-size: 56px;
  margin-bottom: 16px;
  opacity: 0.4;
}

.empty-state-title {
  font-size: 16px;
  font-weight: 600;
  color: #1F1F1F;
  margin-bottom: 6px;
}

.empty-state-desc {
  font-size: 14px;
  margin-bottom: 20px;
}

@media (max-width: 768px) {
  .figure-grid {
    grid-template-columns: repeat(3, 1fr);
  }

  .maker-hero-main {
    flex-direction: column;
    align-items: center;
    text-align: center;
  }

  .maker-hero-logo {
    width: 100px;
    height: 100px;
  }

  .maker-hero-tag {
    margin: 0 auto 8px;
  }

  .maker-hero-links {
    justify-content: center;
  }

  .maker-hero-footer {
    grid-template-columns: repeat(2, 1fr);
  }
}
</style>
