<!--
  CollectionCabinets.vue - 收藏家模式我的收藏柜组件

  功能说明：
  - 展示8个固定分类的收藏柜卡片
  - 即使无数据也展示8个空分类
  - 4个分类有真实统计逻辑（海景房专区、最近入柜、修复工坊、已出藏品）
  - 支持点击查看分类详情

  组件依赖：
  - 接收 collectorData 作为 props，包含 cabinets 数组

  维护提示：
  - 8个卡片固定展示，每个卡片有独立的icon和背景色
  - 数据为空时展示"暂无数据"文案
-->
<template>
  <div class="collection-cabinets">
    <div class="section-title">我的收藏柜</div>
    <div class="cabinet-grid">
      <div
        v-for="cabinet in cabinets"
        :key="cabinet.key"
        class="cabinet-card"
        @click="handleCabinetClick(cabinet)"
      >
        <div class="cabinet-img-wrap">
          <div class="cabinet-img" :style="{ background: cabinet.icon_bg }">
            {{ cabinet.icon }}
          </div>
          <span
            class="cabinet-badge"
            :class="getBadgeClass(cabinet.key)"
          >
            {{ cabinet.description }}
          </span>
        </div>
        <div class="cabinet-info">
          <div class="cabinet-name">{{ cabinet.name }}</div>
          <div class="cabinet-meta">{{ cabinet.meta }}</div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'CollectionCabinets',
  props: {
    collectorData: {
      type: Object,
      default: () => ({})
    }
  },
  computed: {
    cabinets() {
      return this.collectorData?.cabinets || this.defaultCabinets
    },
    defaultCabinets() {
      return [
        { key: 'star', name: '海景房专区', description: '镇柜之宝', icon: '🖼️', icon_bg: '#E8F4F8', count: 0, meta: '暂无镇柜藏品', items: [] },
        { key: 'new', name: '最近入柜', description: '新欢', icon: '✨', icon_bg: '#F0F5E8', count: 0, meta: '暂无新入库', items: [] },
        { key: 'fix', name: '修复工坊', description: '待修复', icon: '🔧', icon_bg: '#FDF6EE', count: 0, meta: '暂无待修复藏品', items: [] },
        { key: 'out', name: '已出藏品', description: '已出坑', icon: '📦', icon_bg: '#F5F5F5', count: 0, meta: '暂无已出藏品', items: [] },
        { key: 'air', name: '预定中', description: '空气谷', icon: '☁️', icon_bg: '#F3E8FF', count: 0, meta: '0 体 · 暂无数据', items: [] },
        { key: 'dup', name: '复数专区', description: '复数', icon: '👯', icon_bg: '#FFF2F0', count: 0, meta: '0 体 · 暂无数据', items: [] },
        { key: 'wait', name: '待出荷', description: '待出荷', icon: '📅', icon_bg: '#E6F7FF', count: 0, meta: '0 体 · 暂无数据', items: [] },
        { key: 'role', name: '本命厂商', description: '本命', icon: '🏭', icon_bg: '#E8F4F8', count: 0, meta: '暂无本命厂商', items: [] }
      ]
    }
  },
  methods: {
    getBadgeClass(key) {
      const map = {
        star: 'badge-star',
        new: 'badge-new',
        fix: 'badge-fix',
        out: 'badge-out',
        air: 'badge-air',
        dup: 'badge-dup',
        wait: 'badge-wait',
        role: 'badge-role'
      }
      return map[key] || 'badge-default'
    },
    handleCabinetClick(cabinet) {
      this.$emit('cabinet-click', cabinet)
    }
  }
}
</script>

<style scoped>
.section-title {
  font-size: 15px;
  font-weight: 600;
  color: #1F1F1F;
  margin-bottom: 14px;
  display: flex;
  align-items: center;
  gap: 6px;
}
.section-title::before {
  content: "";
  display: inline-block;
  width: 4px;
  height: 16px;
  background: #C49A6C;
  border-radius: 2px;
}

.cabinet-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 14px;
  margin-bottom: 30px;
}

.cabinet-card {
  background: #FFFFFF;
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 2px 8px rgba(0,0,0,0.04);
  transition: transform 0.2s, box-shadow 0.2s;
  cursor: pointer;
  border: 1px solid transparent;
}

.cabinet-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 16px rgba(0,0,0,0.08);
  border-color: #E8D5C0;
}

.cabinet-img-wrap {
  height: 120px;
  background: #F0EEEB;
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
}

.cabinet-img {
  width: 56px;
  height: 56px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 28px;
  flex-shrink: 0;
}

.cabinet-badge {
  position: absolute;
  top: 8px;
  right: 8px;
  padding: 2px 8px;
  border-radius: 10px;
  font-size: 11px;
  font-weight: 600;
}

.badge-star { background: #E8F4F8; color: #4A90E2; }
.badge-new { background: #F0F5E8; color: #7EB8A2; }
.badge-fix { background: #FDF6EE; color: #E6A23C; }
.badge-out { background: #F5F5F5; color: #999999; }
.badge-air { background: #F3E8FF; color: #9B7ED8; }
.badge-dup { background: #FFF2F0; color: #D66A6A; }
.badge-wait { background: #E6F7FF; color: #1890FF; }
.badge-role { background: #E0F7FA; color: #00BCD4; }
.badge-default { background: #F5F5F5; color: #999999; }

.cabinet-info {
  padding: 12px;
  text-align: center;
}

.cabinet-name {
  font-size: 14px;
  font-weight: 600;
  margin-bottom: 3px;
  color: #1F1F1F;
}

.cabinet-meta {
  font-size: 12px;
  color: #999999;
}

@media (max-width: 768px) {
  .cabinet-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}
</style>
