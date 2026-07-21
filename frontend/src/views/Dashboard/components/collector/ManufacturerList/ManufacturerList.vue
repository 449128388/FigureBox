<!--
  ManufacturerList.vue - 本命厂商列表页组件

  功能说明：
  - 展示所有已添加的本命厂商卡片
  - 支持按关键词搜索、按状态筛选
  - 支持新增、编辑、删除操作
  - 点击卡片进入厂商详情页

  交互流程：
  收藏柜首页 → 点击「本命厂商」 → 厂商列表页（含搜索框 / 筛选）
                                     ↓
                               点击「+ 添加本命厂商」
                                     ↓
                               填写信息 → 保存 → 列表自动刷新
                                     ↓
                               点击卡片 → 厂商详情页
-->
<template>
  <div class="manufacturer-list">
    <!-- 返回按钮 -->
    <div class="detail-nav" @click="$emit('back')">
      <span class="back-arrow">←</span>
      <span class="back-text">返回收藏柜</span>
    </div>

    <!-- 列表头部 -->
    <div class="maker-list-header">
      <div>
        <span class="maker-list-title">本命厂商</span>
        <span class="maker-list-count">共 {{ manufacturerCount }} 家</span>
      </div>
      <button class="btn-header btn-header-primary" @click="$emit('add')">
        <span>+</span> 添加本命厂商
      </button>
    </div>

    <!-- ===== 搜索栏 ===== -->
    <div class="search-section">
      <div class="search-bar">
        <div class="search-input-wrapper">
          <span class="search-icon">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor"
                 stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <circle cx="11" cy="11" r="8"></circle>
              <line x1="21" y1="21" x2="16.65" y2="16.65"></line>
            </svg>
          </span>
          <input
            v-model="localKeyword"
            type="text"
            class="search-input"
            placeholder="搜索厂商名称、关键词..."
            @keyup.enter="handleSearchClick"
          />
        </div>
        <button class="search-btn" @click="handleSearchClick">
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor"
               stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <circle cx="11" cy="11" r="8"></circle>
            <line x1="21" y1="21" x2="16.65" y2="16.65"></line>
          </svg>
          搜索
        </button>
        <button class="reset-btn" @click="handleResetClick">重置</button>
      </div>
      <div class="filter-tags">
        <span class="filter-label">筛选：</span>
        <span
          class="filter-tag"
          :class="{ active: localFilter === '' }"
          @click="handleFilterTagClick('')"
        >全部 <span class="count">{{ totalAll }}</span></span>
        <span
          class="filter-tag"
          :class="{ active: localFilter === 'in' }"
          @click="handleFilterTagClick('in')"
        >有在柜 <span class="count">{{ totalIn }}</span></span>
        <span
          class="filter-tag"
          :class="{ active: localFilter === 'out' }"
          @click="handleFilterTagClick('out')"
        >无在柜 <span class="count">{{ totalOut }}</span></span>
      </div>
    </div>

    <!-- 统计栏 -->
    <div class="stats-bar">
      <div class="stats-text">
        共找到 <strong>{{ manufacturerCount }}</strong> 家厂商
        <template v-if="localKeyword || localFilter">
          <span class="stats-hint">（已应用筛选条件）</span>
        </template>
      </div>
    </div>

    <!-- 空状态（区分：无数据 / 无匹配结果） -->
    <div
      v-if="!loading && manufacturers.length === 0"
      class="empty-state"
    >
      <div class="empty-state-icon">{{ localKeyword || localFilter ? '🔍' : '🏭' }}</div>
      <div class="empty-state-title">
        {{ localKeyword || localFilter ? '没有匹配的厂商' : '暂无本命厂商' }}
      </div>
      <div class="empty-state-desc">
        <template v-if="localKeyword || localFilter">
          请尝试更换关键词或调整筛选条件
        </template>
        <template v-else>
          点击右上角「添加本命厂商」开始追厂之旅
        </template>
      </div>
      <button
        v-if="localKeyword || localFilter"
        class="btn-reset-empty"
        @click="handleResetClick"
      >重置筛选</button>
    </div>

    <!-- 厂商卡片网格 -->
    <div v-else class="maker-grid">
      <div
        v-for="maker in manufacturers"
        :key="maker.id"
        class="maker-card"
        @click="$emit('select', maker.id)"
      >
        <div class="maker-card-header">
          <div class="maker-logo">
            <template v-if="maker.logo_url">
              <img :src="maker.logo_url" :alt="maker.name">
            </template>
            <template v-else>
              🏭
            </template>
          </div>
          <div class="maker-info">
            <div class="maker-tag">厂商</div>
            <div class="maker-name">{{ maker.name }}</div>
            <div class="maker-desc">{{ maker.description || '暂无描述' }}</div>
          </div>
        </div>
        <div class="maker-card-body">
          <div class="maker-stats">
            <div class="maker-stat">
              <div class="maker-stat-num">{{ maker.total_count }}</div>
              <div class="maker-stat-label">总藏品</div>
            </div>
            <div class="maker-stat">
              <div class="maker-stat-num">{{ maker.in_count }}</div>
              <div class="maker-stat-label">在柜</div>
            </div>
          </div>
          <div class="maker-actions" @click.stop>
            <button class="maker-btn maker-btn-edit" @click="$emit('edit', maker)">编辑</button>
            <button class="maker-btn" @click="$emit('delete', maker.id)">删除</button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'ManufacturerList',
  props: {
    manufacturers: {
      type: Array,
      default: () => []
    },
    manufacturerCount: {
      type: Number,
      default: 0
    },
    // 全局统计（独立于 filter_type），用于渲染筛选标签计数
    manufacturerStats: {
      type: Object,
      default: () => ({ all: 0, in: 0, out: 0 })
    },
    loading: {
      type: Boolean,
      default: false
    },
    // 当前生效的搜索关键词（由父组件传入）
    keyword: {
      type: String,
      default: ''
    },
    // 当前生效的筛选类型（由父组件传入）
    filterType: {
      type: String,
      default: ''
    }
  },
  emits: ['add', 'select', 'edit', 'delete', 'back', 'search', 'filter-change', 'reset'],
  data() {
    return {
      localKeyword: '',
      localFilter: ''
    }
  },
  computed: {
    /**
     * 筛选标签计数：使用后端返回的全局统计（仅受 keyword 影响，与当前 filter 无关）
     * 这样无论选中「全部 / 有在柜 / 无在柜」，三个标签的数字始终保持稳定
     */
    totalAll() {
      return this.manufacturerStats?.all ?? 0
    },
    totalIn() {
      return this.manufacturerStats?.in ?? 0
    },
    totalOut() {
      return this.manufacturerStats?.out ?? 0
    }
  },
  watch: {
    // 同步父组件的 keyword 到本地（用于重置/初次加载）
    keyword: {
      immediate: true,
      handler(val) {
        this.localKeyword = val || ''
      }
    },
    filterType: {
      immediate: true,
      handler(val) {
        this.localFilter = val || ''
      }
    }
  },
  methods: {
    handleSearchClick() {
      this.$emit('search', this.localKeyword)
    },
    handleFilterTagClick(type) {
      this.localFilter = type
      this.$emit('filter-change', type)
    },
    handleResetClick() {
      this.localKeyword = ''
      this.localFilter = ''
      this.$emit('reset')
    }
  }
}
</script>

<style scoped>
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

.maker-list-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 20px;
}

.maker-list-title {
  font-size: 18px;
  font-weight: 600;
}

.maker-list-count {
  font-size: 13px;
  color: #999;
  margin-left: 8px;
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

.btn-header-primary {
  background: #00BCD4;
  border-color: #00BCD4;
  color: #fff;
}

.btn-header-primary:hover {
  background: #00ACC1;
  border-color: #00ACC1;
  color: #fff;
}

/* ===== 搜索栏区域 ===== */
.search-section {
  background: #fff;
  border-radius: 8px;
  padding: 16px 20px;
  margin-bottom: 20px;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.04);
}

.search-bar {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 12px;
}

.search-input-wrapper {
  flex: 1;
  position: relative;
  min-width: 200px;
}

.search-input {
  width: 100%;
  height: 40px;
  padding: 0 16px 0 40px;
  border: 1px solid #d9d9d9;
  border-radius: 8px;
  font-size: 14px;
  color: #333;
  outline: none;
  transition: all 0.2s;
  background: #fafafa;
}

.search-input:focus {
  border-color: #00BCD4;
  box-shadow: 0 0 0 3px rgba(0, 188, 212, 0.1);
  background: #fff;
}

.search-input::placeholder {
  color: #bfbfbf;
}

.search-icon {
  position: absolute;
  left: 14px;
  top: 50%;
  transform: translateY(-50%);
  color: #bfbfbf;
  pointer-events: none;
  display: flex;
  align-items: center;
  justify-content: center;
}

.search-btn {
  height: 40px;
  padding: 0 20px;
  border-radius: 8px;
  border: none;
  background: #00BCD4;
  color: #fff;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
  display: flex;
  align-items: center;
  gap: 6px;
}

.search-btn:hover {
  background: #00ACC1;
}

.reset-btn {
  height: 40px;
  padding: 0 16px;
  border-radius: 8px;
  border: 1px solid #d9d9d9;
  background: #fff;
  color: #666;
  font-size: 14px;
  cursor: pointer;
  transition: all 0.2s;
}

.reset-btn:hover {
  border-color: #00BCD4;
  color: #00BCD4;
}

/* 筛选标签 */
.filter-tags {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-wrap: wrap;
}

.filter-label {
  font-size: 13px;
  color: #999;
  margin-right: 4px;
}

.filter-tag {
  padding: 4px 12px;
  border-radius: 4px;
  font-size: 13px;
  cursor: pointer;
  transition: all 0.2s;
  border: 1px solid #d9d9d9;
  background: #fff;
  color: #666;
}

.filter-tag:hover {
  border-color: #00BCD4;
  color: #00BCD4;
}

.filter-tag.active {
  background: #E0F7FA;
  border-color: #00BCD4;
  color: #00BCD4;
  font-weight: 500;
}

.filter-tag .count {
  font-size: 11px;
  color: #999;
  margin-left: 4px;
}

.filter-tag.active .count {
  color: #00BCD4;
}

/* 统计栏 */
.stats-bar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 16px;
}

.stats-text {
  font-size: 14px;
  color: #666;
}

.stats-text strong {
  color: #1F1F1F;
  font-weight: 600;
}

.stats-hint {
  font-size: 12px;
  color: #999;
  margin-left: 6px;
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

.btn-reset-empty {
  padding: 6px 18px;
  border-radius: 6px;
  border: 1px solid #d9d9d9;
  background: #fff;
  color: #666;
  font-size: 13px;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-reset-empty:hover {
  border-color: #00BCD4;
  color: #00BCD4;
}

/* Maker Grid */
.maker-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 16px;
}

.maker-card {
  background: #fff;
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 2px 8px rgba(0,0,0,0.04);
  transition: transform 0.2s, box-shadow 0.2s;
  cursor: pointer;
  border: 1px solid transparent;
  display: flex;
  flex-direction: column;
}

.maker-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 16px rgba(0,0,0,0.08);
  border-color: #B2EBF2;
}

.maker-card-header {
  display: flex;
  align-items: center;
  gap: 14px;
  padding: 16px;
  border-bottom: 1px solid #EBE8E4;
}

.maker-logo {
  width: 64px;
  height: 64px;
  background: #F0EEEB;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 28px;
  color: #B0ABA5;
  flex-shrink: 0;
  overflow: hidden;
}

.maker-logo img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.maker-info {
  flex: 1;
  min-width: 0;
}

.maker-tag {
  display: inline-block;
  font-size: 11px;
  padding: 1px 8px;
  border-radius: 4px;
  background: #E0F7FA;
  color: #00BCD4;
  border: 1px solid #B2EBF2;
  margin-bottom: 4px;
}

.maker-name {
  font-size: 16px;
  font-weight: 600;
  margin-bottom: 2px;
}

.maker-desc {
  font-size: 12px;
  color: #999;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.maker-card-body {
  padding: 12px 16px;
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.maker-stats {
  display: flex;
  gap: 16px;
}

.maker-stat {
  text-align: center;
}

.maker-stat-num {
  font-size: 18px;
  font-weight: 700;
  color: #1F1F1F;
}

.maker-stat-label {
  font-size: 11px;
  color: #999;
}

.maker-actions {
  display: flex;
  gap: 6px;
}

.maker-btn {
  padding: 4px 10px;
  border: 1px solid #EBE8E4;
  background: #fff;
  border-radius: 6px;
  font-size: 12px;
  color: #666;
  cursor: pointer;
  transition: all 0.2s;
}

.maker-btn:hover {
  border-color: #D66A6A;
  color: #D66A6A;
}

.maker-btn-edit:hover {
  border-color: #00BCD4;
  color: #00BCD4;
}

@media (max-width: 768px) {
  .maker-grid {
    grid-template-columns: 1fr;
  }
  .search-bar {
    flex-wrap: wrap;
  }
}
</style>
