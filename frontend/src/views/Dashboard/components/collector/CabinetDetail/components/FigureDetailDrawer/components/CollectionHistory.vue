<!--
  CollectionHistory.vue - 收藏历程子组件

  Props:
  - historyList: Array - 收藏历程列表
    支持两种格式：
    1. API 格式：[{ date, type_label, quantity, price, balance }]
    2. 旧格式：[{ date, text }] （兼容回退）

  说明：
  - text 支持 HTML 标签（如 <strong>）
-->
<template>
  <div class="section" v-if="historyList && historyList.length > 0">
    <div class="section-title">收藏历程</div>
    <div class="timeline-mini">
      <div v-for="(item, index) in historyList" :key="index" class="tl-item">
        <div class="tl-dot" :class="item.type === 'sell' ? 'dot-sell' : item.type === 'adjust' ? 'dot-adjust' : 'dot-buy'"></div>
        <div class="tl-date">{{ item.date }}</div>
        <!-- API 格式 -->
        <template v-if="item.type_label">
          <div class="tl-text">
            <span class="tl-tag" :class="item.type === 'sell' ? 'tag-sell' : item.type === 'adjust' ? 'tag-adjust' : item.type_label === '补仓' ? 'tag-replenish' : 'tag-buy'">
              {{ item.type_label }}
            </span>
            <strong>{{ item.quantity }}</strong> 体
            <span v-if="item.price"> · {{ item.type === 'sell' ? '卖出价' : '成本价' }} ¥{{ formatPrice(item.price) }}</span>
            <span v-if="item.quantity > 0" class="tl-balance"> · 库存 {{ item.balance }} 体</span>
          </div>
        </template>
        <!-- 旧格式兼容 -->
        <div v-else class="tl-text" v-html="item.text"></div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'CollectionHistory',

  props: {
    historyList: {
      type: Array,
      default: () => []
    }
  },

  methods: {
    formatPrice(val) {
      if (val === undefined || val === null) return '0'
      return Number(val).toLocaleString('zh-CN', { minimumFractionDigits: 2, maximumFractionDigits: 2 })
    }
  }
}
</script>

<style scoped>
.section {
  margin-bottom: 24px;
}

.section-title {
  font-size: 14px;
  font-weight: 600;
  color: #1F1F1F;
  margin-bottom: 12px;
  display: flex;
  align-items: center;
  gap: 6px;
}

.section-title::before {
  content: "";
  display: inline-block;
  width: 3px;
  height: 14px;
  background: #C49A6C;
  border-radius: 2px;
}

.timeline-mini {
  position: relative;
  padding-left: 20px;
}

.timeline-mini::before {
  content: "";
  position: absolute;
  left: 5px;
  top: 0;
  bottom: 0;
  width: 2px;
  background: #EBE8E4;
}

.tl-item {
  position: relative;
  margin-bottom: 14px;
}

.tl-item:last-child {
  margin-bottom: 0;
}

.tl-dot {
  position: absolute;
  left: -20px;
  top: 4px;
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: #C49A6C;
  border: 2px solid #fff;
}

.dot-buy {
  background: #7EB8A2;
}

.dot-adjust {
  background: #78909C;
}

.dot-sell {
  background: #D66A6A;
}

.tl-date {
  font-size: 12px;
  color: #999;
  margin-bottom: 2px;
}

.tl-text {
  font-size: 13px;
  color: #1F1F1F;
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 2px;
}

.tl-tag {
  display: inline-block;
  padding: 1px 6px;
  border-radius: 4px;
  font-size: 11px;
  font-weight: 600;
  margin-right: 4px;
}

.tag-buy {
  background: #E8F5E9;
  color: #2E7D32;
}

.tag-replenish {
  background: #FFF3E0;
  color: #E65100;
}

.tag-adjust {
  background: #ECEFF1;
  color: #546E7A;
}

.tag-sell {
  background: #FFEBEE;
  color: #C62828;
}

.tl-balance {
  font-size: 12px;
  color: #666;
}
</style>
