<template>
  <div class="collector-overview">
    <div class="overview-card">
      <div class="card-icon">💸</div>
      <div class="card-label">总投入</div>
      <div class="card-value">¥{{ formatNumber(collectorData?.summary?.total_investment || 0) }}</div>
    </div>
    <div class="overview-card">
      <div class="card-icon">💎</div>
      <div class="card-label">现估值</div>
      <div class="card-value">¥{{ formatNumber(collectorData?.summary?.total_valuation || 0) }}</div>
    </div>
    <div class="overview-card">
      <div class="card-icon">💰</div>
      <div class="card-label">回血额</div>
      <div class="card-value">¥{{ formatNumber(collectorData?.summary?.blood_money || 0) }}</div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'CollectorOverview',
  props: {
    collectorData: {
      type: Object,
      default: () => ({})
    }
  },
  methods: {
    formatNumber(num) {
      return num.toLocaleString()
    }
  }
}
</script>

<style scoped>
.collector-overview {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 20px;
  margin-bottom: 30px;
}

.overview-card {
  background-color: white;
  padding: 25px;
  border-radius: 8px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
  text-align: center;
  transition: transform 0.3s ease;
}

.overview-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.15);
}

.card-icon {
  font-size: 32px;
  margin-bottom: 10px;
}

.card-label {
  font-size: 14px;
  color: #666;
  margin-bottom: 5px;
}

.card-value {
  font-size: 24px;
  font-weight: bold;
  color: #333;
}

@media (max-width: 768px) {
  .collector-overview {
    grid-template-columns: 1fr;
  }
}
</style>
