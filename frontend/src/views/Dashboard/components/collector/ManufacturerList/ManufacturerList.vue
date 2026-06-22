<!--
  ManufacturerList.vue - 本命厂商列表页组件

  功能说明：
  - 展示所有已添加的本命厂商卡片
  - 支持新增、编辑、删除操作
  - 点击卡片进入厂商详情页

  交互流程：
  收藏柜首页 → 点击「本命厂商」 → 厂商列表页
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

    <!-- 空状态 -->
    <div v-if="!loading && manufacturers.length === 0" class="empty-state">
      <div class="empty-state-icon">🏭</div>
      <div class="empty-state-title">暂无本命厂商</div>
      <div class="empty-state-desc">点击右上角「添加本命厂商」开始追厂之旅</div>
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
    loading: {
      type: Boolean,
      default: false
    }
  },
  emits: ['add', 'select', 'edit', 'delete', 'back']
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
}
</style>
