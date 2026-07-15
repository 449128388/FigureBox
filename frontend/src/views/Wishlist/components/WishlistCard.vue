<template>
  <div class="wish-card" :data-id="item.id">
    <div class="card-image-wrapper">
      <img v-if="item.cover" :src="item.cover" :alt="item.name" class="card-image" @error="onImgError" />
      <div v-else class="card-image-placeholder">
        <i class="ri-image-2-line"></i>
        <span>暂无图片</span>
      </div>
      <span :class="['status-badge', badgeClass]">{{ item.status_label }}</span>
      <span class="source-tag">
        <i :class="['ri', sourceIcon]"></i>
        {{ item.source.label }}
      </span>
    </div>
    <div class="card-body-inner">
      <div class="card-title-row">
        <input
          type="checkbox"
          class="card-checkbox"
          :checked="selected"
          @change="$emit('toggle-select', item.id)"
        />
        <router-link :to="'/figures/' + item.id" class="card-title-link">{{ item.name }}</router-link>
      </div>
      <div class="card-meta">
        <div class="meta-row">
          <span class="meta-label">官方定价</span>
          <span class="meta-value price">¥{{ formatPrice(item.price, item.currency) }}</span>
        </div>
        <div v-if="item.release_date" class="meta-row">
          <span class="meta-label">预计发售</span>
          <span class="meta-value date">{{ item.release_date }}</span>
        </div>
        <div v-if="item.manufacturer" class="meta-row">
          <span class="meta-label">厂商</span>
          <span class="meta-value">{{ item.manufacturer }}</span>
        </div>
        <div v-if="item.scale" class="meta-row">
          <span class="meta-label">比例</span>
          <span class="meta-value">{{ item.scale }}</span>
        </div>
        <div v-if="item.market_price" class="meta-row">
          <span class="meta-label">市场价</span>
          <span class="meta-value">¥{{ formatPrice(item.market_price, item.market_currency) }}</span>
        </div>
      </div>
      <div v-if="item.tags && item.tags.length" class="card-tags">
        <span v-for="t in item.tags" :key="t.id" class="tag">{{ t.name }}</span>
      </div>
      <div v-if="item.note" class="card-note">{{ item.note }}</div>
      <div class="card-actions">
        <button v-if="item.status !== 'cancelled'" class="card-btn card-btn-buy" @click="$emit('move-to-library', item)">
          <i class="ri-shopping-bag-3-line"></i> 转入手办库
        </button>
        <button class="card-btn card-btn-edit" @click="$emit('edit', item)">
          <i class="ri-edit-line"></i> 编辑
        </button>
        <button class="card-btn card-btn-del" @click="$emit('delete', item)">
          <i class="ri-delete-bin-line"></i>
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  item: { type: Object, required: true },
  selected: { type: Boolean, default: false }
})
defineEmits(['toggle-select', 'edit', 'delete', 'move-to-library'])

const badgeClass = computed(() => {
  return {
    wish: 'badge-wish',
    released: 'badge-released',
    purchased: 'badge-purchased',
    cancelled: 'badge-cancelled'
  }[props.item.status] || 'badge-wish'
})

const sourceIcon = computed(() => {
  const icon = props.item.source?.icon || 'link'
  return `ri-${icon}`
})

const formatPrice = (value, currency) => {
  const n = Number(value) || 0
  if (currency && currency !== 'CNY') {
    return `${n.toLocaleString('zh-CN', { maximumFractionDigits: 2 })} ${currency}`
  }
  return n.toLocaleString('zh-CN', { minimumFractionDigits: 0, maximumFractionDigits: 2 })
}

const onImgError = (e) => {
  e.target.style.display = 'none'
}
</script>

<style scoped>
.wish-card {
  background: #fff;
  border-radius: 10px;
  overflow: hidden;
  box-shadow: 0 2px 12px rgba(0,0,0,0.08);
  transition: all 0.3s;
  position: relative;
  display: flex;
  flex-direction: column;
}
.wish-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 24px rgba(0,0,0,0.12);
}
.card-image-wrapper {
  position: relative;
  height: 220px;
  overflow: hidden;
  background: #f5f5f5;
}
.card-image {
  width: 100%;
  height: 100%;
  object-fit: contain;
  transition: transform 0.5s;
}
.wish-card:hover .card-image { transform: scale(1.05); }
.card-image-placeholder {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #bbb;
  font-size: 16px;
  flex-direction: column;
  gap: 8px;
}
.card-image-placeholder i { font-size: 48px; color: #ddd; }
.status-badge {
  position: absolute;
  top: 12px;
  right: 12px;
  padding: 4px 12px;
  border-radius: 20px;
  font-size: 12px;
  font-weight: 600;
  color: #fff;
  backdrop-filter: blur(10px);
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
  z-index: 1;
}
.badge-wish { background: rgba(24,144,255,0.9); }
.badge-released { background: rgba(250,140,22,0.9); }
.badge-purchased { background: rgba(82,196,26,0.9); }
.badge-cancelled { background: rgba(153,153,153,0.9); }
.source-tag {
  position: absolute;
  top: 12px;
  left: 12px;
  background: rgba(0,0,0,0.6);
  color: #fff;
  padding: 3px 10px;
  border-radius: 4px;
  font-size: 11px;
  display: flex;
  align-items: center;
  gap: 4px;
  backdrop-filter: blur(4px);
  z-index: 1;
}
.card-body-inner {
  padding: 16px;
  flex: 1;
  display: flex;
  flex-direction: column;
}
.card-title-row {
  display: flex;
  align-items: flex-start;
  gap: 8px;
  margin-bottom: 8px;
}
.card-checkbox {
  margin-top: 4px;
  flex-shrink: 0;
}
.card-title-link {
  font-size: 16px;
  font-weight: 600;
  color: #1890ff;
  margin-bottom: 0;
  line-height: 1.4;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
  flex: 1;
  /* 固定高度为 2 行，避免因标题换行导致下方内容（备注）水平错位 */
  height: 2.8em;
  text-decoration: none;
}
.card-meta {
  display: flex;
  flex-direction: column;
  gap: 8px;
  margin-bottom: 12px;
}
.meta-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 13px;
}
.meta-label { color: #999; }
.meta-value { color: #333; font-weight: 500; }
.meta-value.price { color: #ff4d4f; font-size: 15px; font-weight: 600; }
.meta-value.date { color: #fa8c16; }
.card-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  margin-bottom: 12px;
}
.tag {
  padding: 2px 8px;
  background: #f0f5ff;
  color: #1890ff;
  border-radius: 4px;
  font-size: 12px;
  border: 1px solid #d6e4ff;
}
.card-note {
  background: #fafafa;
  padding: 8px 12px;
  border-radius: 6px;
  font-size: 12px;
  color: #666;
  margin-bottom: 12px;
  border-left: 3px solid #1890ff;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
  min-height: 36px;
}
.card-actions {
  display: flex;
  gap: 8px;
  margin-top: auto;
}
.card-btn {
  flex: 1;
  padding: 6px 0;
  border-radius: 6px;
  border: none;
  cursor: pointer;
  font-size: 13px;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 4px;
  transition: all 0.3s;
  font-weight: 500;
}
.card-btn-buy {
  background: #fff2e8;
  color: #fa8c16;
  border: 1px solid #ffd8bf;
}
.card-btn-buy:hover { background: #fa8c16; color: #fff; }
.card-btn-edit {
  background: #e6f4ff;
  color: #1890ff;
  flex: 1;
  border: 1px solid #bae0ff;
}
.card-btn-edit:hover { background: #1890ff; color: #fff; }
.card-btn-del {
  background: #fff1f0;
  color: #ff4d4f;
  border: 1px solid #ffa39e;
  width: 36px;
  flex: none;
}
.card-btn-del:hover { background: #ff4d4f; color: #fff; }
</style>
