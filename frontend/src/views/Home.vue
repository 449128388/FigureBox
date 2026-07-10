<template>
  <div class="home-page">
    <TopHeader />
    <HomeHero :username="summary?.username" :stats="summary || {}" :greeting="summary?.greeting" />
    <div class="main-container">
      <QuickStats :stats="summary || {}" />
      <div class="section-grid">
        <div class="card animate-in">
          <div class="card-header">
            <div class="card-title"><i class="ri-apps-line"></i> 功能模块</div>
            <span class="card-title-sub">点击快速进入</span>
          </div>
          <div class="card-body">
            <ModuleGrid />
          </div>
        </div>
        <div style="display: flex; flex-direction: column; gap: 16px;">
          <HpiMini
            :hpi-value="summary?.hpi_index_value"
            :hpi-change="hpiPointsChange"
            :hpi-change-pct="summary?.hpi_return || 0"
          />
          <DateCard />
        </div>
      </div>
      <div class="section-grid-2">
        <ActivityFeed :activities="activities" />
        <TopHoldings :holdings="topHoldings" />
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import TopHeader from '../components/TopHeader.vue'
import HomeHero from './Home/components/HomeHero.vue'
import QuickStats from './Home/components/QuickStats.vue'
import ModuleGrid from './Home/components/ModuleGrid.vue'
import ActivityFeed from './Home/components/ActivityFeed.vue'
import TopHoldings from './Home/components/TopHoldings.vue'
import HpiMini from './Home/components/HPIMini.vue'
import DateCard from './Home/components/DateCard.vue'
import { useHome } from './Home/composables/useHome'

const { summary, activities, topHoldings } = useHome()

const hpiPointsChange = computed(() => {
  const idx = summary.value?.hpi_index_value
  if (!idx) return 0
  return idx - 1000
})
</script>

<style scoped>
.home-page {
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
  color: #1f1f1f;
  font-size: 14px;
  line-height: 1.5;
  min-height: 100vh;
  background: #f5f5f5;
  padding-top: 64px;
}
.main-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 32px 40px;
  position: relative;
  z-index: 2;
}
.section-grid {
  display: grid;
  grid-template-columns: 2fr 1fr;
  gap: 20px;
  margin-bottom: 24px;
}
.section-grid-2 {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 20px;
  margin-bottom: 24px;
}
.card {
  background: #fff;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.06);
  overflow: hidden;
}
.card-header {
  padding: 16px 20px;
  border-bottom: 1px solid #f0f0f0;
  display: flex;
  align-items: center;
  justify-content: space-between;
}
.card-title {
  font-size: 15px;
  font-weight: 600;
  display: flex;
  align-items: center;
  gap: 8px;
}
.card-title i { color: #1890ff; }
.card-title-sub { font-size: 12px; color: #999; }
.card-body { padding: 16px 20px; }
@keyframes fadeInUp {
  from { opacity: 0; transform: translateY(20px); }
  to { opacity: 1; transform: translateY(0); }
}
.animate-in { animation: fadeInUp 0.5s ease-out; }
@media (max-width: 1024px) {
  .section-grid { grid-template-columns: 1fr; }
  .section-grid-2 { grid-template-columns: 1fr; }
}
@media (max-width: 768px) {
  .main-container { padding: 0 16px 40px; }
}
</style>
