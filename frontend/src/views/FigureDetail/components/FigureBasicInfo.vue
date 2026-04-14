<!--
  FigureBasicInfo.vue - 手办基本信息组件

  功能说明：
  - 展示手办的基本信息
  - 包括日文名、制造商、定价、市场价、出货日、入手价格、入手时间等字段
  - 仅在有相关信息时显示对应字段
  - 支持多货币符号显示

  组件依赖：
  - 接收 figure 作为 props，包含各种基本信息字段

  维护提示：
  - 使用 v-if 条件渲染，仅当有相关信息时显示
  - 使用 getCurrencySymbol 方法获取货币符号
-->
<template>
  <div class="info-section">
    <h2>基本信息</h2>
    <div v-if="figure.japanese_name" class="info-item">
      <span class="label">日文名:</span>
      <span class="value">{{ figure.japanese_name }}</span>
    </div>
    <div class="info-item" v-if="figure.manufacturer">
      <span class="label">制造商:</span>
      <span class="value">{{ figure.manufacturer }}</span>
    </div>
    <div class="info-item" v-if="figure.price !== null && figure.price !== undefined">
      <span class="label">定价:</span>
      <span class="value">{{ figure.price }} {{ getCurrencySymbol(figure.currency) }}</span>
    </div>
    <div class="info-item" v-if="figure.market_price !== null && figure.market_price !== undefined">
      <span class="label">市场价:</span>
      <span class="value">{{ figure.market_price }} {{ getCurrencySymbol(figure.market_currency) }}</span>
    </div>
    <div class="info-item" v-if="figure.release_date">
      <span class="label">出货日:</span>
      <span class="value">{{ figure.release_date }}</span>
    </div>
    <div class="info-item" v-if="figure.purchase_price !== null && figure.purchase_price !== undefined">
      <span class="label">入手价格:</span>
      <span class="value">{{ figure.purchase_price }} {{ getCurrencySymbol(figure.purchase_currency) }}</span>
    </div>
    <div class="info-item" v-if="figure.purchase_date">
      <span class="label">入手时间:</span>
      <span class="value">{{ figure.purchase_date }}</span>
    </div>
    <div class="info-item" v-if="figure.purchase_method">
      <span class="label">入手途径:</span>
      <span class="value">{{ figure.purchase_method }}</span>
    </div>
    <div class="info-item" v-if="figure.purchase_type">
      <span class="label">入手形式:</span>
      <span class="value">{{ figure.purchase_type }}</span>
    </div>
    <div class="info-item" v-if="figure.quantity !== null && figure.quantity !== undefined">
      <span class="label">数量:</span>
      <span class="value">{{ figure.quantity }}</span>
    </div>
  </div>
</template>

<script>
export default {
  name: 'FigureBasicInfo',
  props: {
    figure: {
      type: Object,
      required: true
    }
  },
  methods: {
    getCurrencySymbol(currency) {
      switch(currency) {
        case 'CNY': return '元'
        case 'JPY': return '日元'
        case 'USD': return '美元'
        case 'EUR': return '欧元'
        default: return '元'
      }
    }
  }
}
</script>

<style scoped>
.info-section {
  background-color: white;
  padding: 20px;
  border-radius: 8px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
}

.info-section h2 {
  margin-top: 0;
  margin-bottom: 20px;
  color: #333;
  font-size: 20px;
  font-weight: 600;
  border-bottom: 1px solid #e0e0e0;
  padding-bottom: 10px;
}

.info-item {
  display: flex;
  margin-bottom: 12px;
}

.label {
  flex: 0 0 100px;
  font-weight: 500;
  color: #666;
}

.value {
  flex: 1;
  color: #333;
  padding: 2px 0;
  min-height: 20px;
  line-height: 1.5;
}
</style>