<!--
  FigureBasicInfo.vue - 手办基本信息卡片

  功能说明：
  - 卡片式布局：图标标题栏 + 右上角状态徽章
  - info-grid 紧凑两列展示：日文名 / 制造商 / 官方定价 / 市场价 / 出货日 / 平均入手价 / 入手时间 / 入手途径 / 入手形式 / 数量
  - 金额字段红色高亮

  组件依赖：
  - 接收 figure 作为 props
  - 业务逻辑从 useFigureDetail 导入（getFigureStatusBadge / formatPrice / formatDate / formatQuantity / getCurrencySymbol）
-->
<template>
  <div class="info-card" v-if="hasContent">
    <div class="card-header-bar">
      <div class="card-title">
        <svg class="card-title-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <rect x="3" y="3" width="18" height="18" rx="2" ry="2"></rect>
          <line x1="9" y1="9" x2="15" y2="15"></line>
          <line x1="15" y1="9" x2="9" y2="15"></line>
        </svg>
        基本信息
      </div>
      <span class="card-badge" :class="statusBadge.class">{{ statusBadge.text }}</span>
    </div>
    <div class="card-body">
      <div class="info-grid">
        <div class="info-item" v-if="figure.japanese_name">
          <span class="info-label">日文名</span>
          <span class="info-value">{{ figure.japanese_name }}</span>
        </div>
        <div class="info-item" v-if="figure.manufacturer">
          <span class="info-label">制造商</span>
          <span class="info-value">{{ figure.manufacturer }}</span>
        </div>
        <div class="info-item" v-if="figure.price !== null && figure.price !== undefined">
          <span class="info-label">官方定价</span>
          <span class="info-value price">
            {{ formatPrice(figure.price) }}
            <span class="info-value-suffix">{{ getCurrencySymbol(figure.currency) }}</span>
          </span>
        </div>
        <div class="info-item" v-if="figure.market_price !== null && figure.market_price !== undefined">
          <span class="info-label">市场价</span>
          <span class="info-value price">
            {{ formatPrice(figure.market_price) }}
            <span class="info-value-suffix">{{ getCurrencySymbol(figure.market_currency) }}</span>
          </span>
        </div>
        <div class="info-item" v-if="figure.release_date">
          <span class="info-label">出货日</span>
          <span class="info-value">{{ formatDate(figure.release_date) }}</span>
        </div>
        <div class="info-item" v-if="figure.average_purchase_price > 0">
          <span class="info-label">平均入手价</span>
          <span class="info-value price">
            {{ formatPrice(figure.average_purchase_price) }}
            <span class="info-value-suffix">{{ getCurrencySymbol(figure.purchase_currency) }}</span>
          </span>
        </div>
        <div class="info-item" v-if="figure.purchase_date">
          <span class="info-label">入手时间</span>
          <span class="info-value">{{ formatDate(figure.purchase_date) }}</span>
        </div>
        <div class="info-item" v-if="figure.purchase_method">
          <span class="info-label">入手途径</span>
          <span class="info-value">{{ figure.purchase_method }}</span>
        </div>
        <div class="info-item" v-if="figure.purchase_type">
          <span class="info-label">入手形式</span>
          <span class="info-value">{{ figure.purchase_type }}</span>
        </div>
        <div class="info-item" v-if="figure.quantity !== null && figure.quantity !== undefined">
          <span class="info-label">数量</span>
          <span class="info-value">{{ formatQuantity(figure.quantity) }}</span>
        </div>
        <div class="info-item info-item-full" v-if="figure.note">
          <span class="info-label">备注</span>
          <span class="info-value note-value">{{ figure.note }}</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { useFigureDetail } from '../composables/useFigureDetail'

export default {
  name: 'FigureBasicInfo',
  props: {
    figure: {
      type: Object,
      required: true
    }
  },
  computed: {
    hasContent() {
      const f = this.figure
      return !!(f.japanese_name || f.manufacturer
        || f.price || f.market_price || f.release_date
        || f.average_purchase_price || f.purchase_date
        || f.purchase_method || f.purchase_type
        || f.quantity || f.note)
    },
    statusBadge() {
      const { getFigureStatusBadge } = useFigureDetail()
      return getFigureStatusBadge(this.figure)
    }
  },
  methods: {
    formatPrice(v) { return useFigureDetail().formatPrice(v) },
    formatDate(v) { return useFigureDetail().formatDate(v) },
    formatQuantity(v) { return useFigureDetail().formatQuantity(v) },
    getCurrencySymbol(c) { return useFigureDetail().getCurrencySymbol(c) }
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
}
.badge-blue { background: #e6f7ff; color: #1890ff; }
.badge-green { background: #f6ffed; color: #52c41a; }
.badge-orange { background: #fff7e6; color: #d46b08; }
.badge-red { background: #fff1f0; color: #ff4d4f; }
.card-body { padding: 20px 24px; }

.info-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 14px 32px;
}
.info-item {
  display: flex;
  align-items: baseline;
  gap: 10px;
}
.info-label {
  font-size: 13px;
  color: #999;
  flex-shrink: 0;
  min-width: 78px;
}
.info-value {
  font-size: 14px;
  color: #333;
  font-weight: 500;
}
.info-value.price {
  color: #ff4d4f;
  font-weight: 600;
  font-size: 15px;
}
.info-value-suffix {
  font-size: 12px;
  color: #999;
  font-weight: 400;
  margin-left: 4px;
}
.info-item-full {
  grid-column: 1 / -1;
  flex-direction: column;
  align-items: flex-start;
  gap: 6px;
}
.note-value {
  white-space: pre-wrap;
  word-break: break-word;
  line-height: 1.6;
  color: #444;
  font-weight: 400;
}
</style>
