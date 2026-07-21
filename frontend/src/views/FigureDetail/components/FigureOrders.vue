<!--
  FigureOrders.vue - 关联订单卡片

  功能说明：
  - 卡片式布局：图标标题栏 + 订单数徽章 + 添加新订单
  - 多订单时支持 tab 切换查看
  - 订单卡片：header（订单号 + 状态徽章）+ body（grid 字段：定金/尾款/出荷/店铺/联系方式/物流/支付方式/支付时间）+ note（备注）

  组件依赖：
  - 接收 relatedOrders 作为 props
  - 业务逻辑从 useFigureDetail 导入
-->
<template>
  <div class="info-card" v-if="relatedOrders.length > 0">
    <div class="card-header-bar">
      <div class="card-title">
        <svg class="card-title-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <rect x="1" y="4" width="22" height="16" rx="2" ry="2"></rect>
          <line x1="1" y1="10" x2="23" y2="10"></line>
        </svg>
        订单记录
        <span class="card-badge badge-blue">{{ relatedOrders.length }} 笔</span>
      </div>
    </div>
    <div class="card-body">
      <!-- 多订单切换器 -->
      <div v-if="relatedOrders.length > 1" class="order-switcher">
        <span class="order-switcher-label">查看订单：</span>
        <div class="order-switcher-tabs">
          <div
            v-for="(order, idx) in relatedOrders"
            :key="order.id"
            class="order-tab"
            :class="{ active: activeOrderIndex === idx }"
            @click="activeOrderIndex = idx"
          >订单 #{{ idx + 1 }}</div>
        </div>
      </div>

      <!-- 选中订单 -->
      <div v-if="activeOrder" class="order-item">
        <div class="order-header">
          <div class="order-id">
            <span>订单</span>
            <span class="order-id-num">{{ activeOrder.display_order_number || activeOrder.order_number || `#${activeOrder.id}` }}</span>
          </div>
          <span class="order-status" :class="statusBadge(activeOrder.status)">{{ activeOrder.status }}</span>
        </div>
        <div class="order-body">
          <div class="order-field">
            <span class="order-field-label">定金</span>
            <span class="order-field-value price">{{ formatPrice(activeOrder.deposit) }}</span>
          </div>
          <div class="order-field">
            <span class="order-field-label">尾款</span>
            <span class="order-field-value price">{{ formatPrice(activeOrder.balance) }}</span>
          </div>
          <div class="order-field">
            <span class="order-field-label">出荷日期</span>
            <span class="order-field-value">{{ formatDate(activeOrder.due_date) }}</span>
          </div>
          <div class="order-field">
            <span class="order-field-label">购买店铺</span>
            <span class="order-field-value">{{ activeOrder.shop_name || '—' }}</span>
          </div>
          <div class="order-field">
            <span class="order-field-label">联系方式</span>
            <span class="order-field-value">{{ activeOrder.shop_contact || '—' }}</span>
          </div>
          <div class="order-field">
            <span class="order-field-label">物流订单</span>
            <span class="order-field-value">
              <a v-if="activeOrder.tracking_number" class="tracking-link" :href="`https://www.baidu.com/s?wd=${encodeURIComponent(activeOrder.tracking_number)}`" target="_blank" rel="noopener noreferrer">{{ activeOrder.tracking_number }}</a>
              <span v-else>—</span>
            </span>
          </div>
          <div class="order-field">
            <span class="order-field-label">支付方式</span>
            <span class="order-field-value">{{ paymentDisplay.method }}</span>
          </div>
          <div class="order-field">
            <span class="order-field-label">支付时间</span>
            <span class="order-field-value">{{ paymentDisplay.time }}</span>
          </div>
        </div>
        <div v-if="activeOrder.remarks" class="order-note">
          <span class="order-note-label">备注：</span>
          <span class="order-note-content">{{ activeOrder.remarks }}</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { useFigureDetail } from '../composables/useFigureDetail'

export default {
  name: 'FigureOrders',
  props: {
    relatedOrders: {
      type: Array,
      default: () => []
    }
  },
  data() {
    return {
      activeOrderIndex: 0
    }
  },
  computed: {
    activeOrder() {
      return this.relatedOrders[this.activeOrderIndex] || null
    },
    paymentDisplay() {
      if (!this.activeOrder) return { method: '—', time: '—' }
      const { getPaymentDisplay } = useFigureDetail()
      return getPaymentDisplay(this.activeOrder)
    }
  },
  watch: {
    relatedOrders: {
      handler() {
        this.activeOrderIndex = 0
      },
      immediate: false
    }
  },
  methods: {
    formatPrice(v) { return useFigureDetail().formatPrice(v) },
    formatDate(v) { return useFigureDetail().formatDate(v) },
    statusBadge(status) {
      const { getOrderStatusBadge } = useFigureDetail()
      return getOrderStatusBadge(status)
    }
  }
}
</script>

<style scoped>
.info-card {
  background: #fff;
  border-radius: 12px;
  border: 1px solid #e8e8e8;
  overflow: hidden;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.04);
}
.card-header-bar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 16px 24px;
  border-bottom: 1px solid #f0f0f0;
}
.card-title {
  font-size: 15px;
  font-weight: 600;
  color: #1f1f1f;
  display: flex;
  align-items: center;
  gap: 10px;
}
.card-title-icon {
  width: 22px;
  height: 22px;
  color: #1890ff;
}
.card-badge {
  padding: 3px 10px;
  border-radius: 20px;
  font-size: 12px;
  font-weight: 500;
  background: #e6f7ff;
  color: #1890ff;
}
.badge-blue { background: #e6f7ff; color: #1890ff; }
.badge-green { background: #f6ffed; color: #52c41a; }
.badge-orange { background: #fff7e6; color: #d46b08; }
.badge-red { background: #fff1f0; color: #ff4d4f; }
.card-toggle {
  font-size: 13px;
  color: #999;
  cursor: pointer;
  transition: color 0.2s;
}
.card-toggle:hover { color: #1890ff; }
.card-body { padding: 20px 24px; }

/* 订单切换器 */
.order-switcher {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 16px;
  flex-wrap: wrap;
}
.order-switcher-label { font-size: 13px; color: #999; }
.order-switcher-tabs { display: flex; gap: 6px; flex-wrap: wrap; }
.order-tab {
  padding: 5px 14px;
  border-radius: 6px;
  font-size: 13px;
  cursor: pointer;
  transition: all 0.2s;
  border: 1px solid #d9d9d9;
  background: #fff;
  color: #666;
}
.order-tab:hover { border-color: #40a9ff; color: #40a9ff; }
.order-tab.active {
  background: #1890ff;
  border-color: #1890ff;
  color: #fff;
}

/* 单订单卡片 */
.order-item {
  border: 1px solid #f0f0f0;
  border-radius: 8px;
  overflow: hidden;
  background: #fafafa;
}
.order-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px 16px;
  background: #fff;
  border-bottom: 1px solid #f0f0f0;
}
.order-id {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 13px;
  color: #666;
}
.order-id-num {
  color: #1f1f1f;
  font-weight: 600;
  font-size: 14px;
}
.order-status {
  padding: 2px 10px;
  border-radius: 20px;
  font-size: 12px;
  font-weight: 500;
}
.order-body {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 12px 24px;
  padding: 16px;
}
.order-field {
  display: flex;
  align-items: baseline;
  gap: 8px;
  min-width: 0;
}
.order-field-label {
  font-size: 12px;
  color: #999;
  flex-shrink: 0;
  min-width: 56px;
}
.order-field-value {
  font-size: 14px;
  color: #333;
  font-weight: 500;
  word-break: break-word;
}
.order-field-value.price {
  color: #ff4d4f;
  font-weight: 600;
}
.tracking-link {
  color: #1890ff;
  text-decoration: none;
}

.order-note {
  background: #fff;
  padding: 12px 16px;
  border-top: 1px dashed #f0f0f0;
  font-size: 13px;
  color: #666;
}
.order-note-label {
  color: #999;
  font-weight: 500;
}
.order-note-content {
  white-space: pre-wrap;
  word-break: break-word;
}
</style>
