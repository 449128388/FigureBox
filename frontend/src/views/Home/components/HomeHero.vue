<template>
  <div class="hero">
    <div class="hero-content">
      <div class="hero-text">
        <h1>欢迎回来，{{ username || '胶佬' }}</h1>
        <p>{{ fallbackGreeting }}</p>
        <div class="hero-stats">
          <div class="hero-stat">
            <div class="hero-stat-num">{{ stats.figure_count || 0 }}</div>
            <div class="hero-stat-label">在柜手办</div>
          </div>
          <div class="hero-stat">
            <div class="hero-stat-num">{{ stats.wishlist_count || 0 }}</div>
            <div class="hero-stat-label">愿望清单</div>
          </div>
          <div class="hero-stat">
            <div class="hero-stat-num">{{ stats.invest_days || 0 }}</div>
            <div class="hero-stat-label">投资天数</div>
          </div>
        </div>
      </div>
      <div class="hero-avatar">
        <i class="ri-user-smile-line"></i>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  username: { type: String, default: '胶佬' },
  stats: { type: Object, default: () => ({}) },
  greeting: { type: String, default: '' }
})

// 前端兜底：后端无欢迎语时按时间段生成
const fallbackGreeting = computed(() => {
  if (props.greeting) return props.greeting
  const hour = new Date().getHours()
  if (hour >= 5 && hour < 11) return '早上好，今天也是买塑料小人的好日子'
  if (hour >= 11 && hour < 14) return '中午好，看看上午的资产波动'
  if (hour >= 14 && hour < 18) return '下午好，记得检查尾款到期日'
  return '晚上好，来看看今天的资产复盘'
})
</script>

<style scoped>
.hero {
  background: linear-gradient(135deg, #1890ff 0%, #36cfc9 100%);
  border-radius: 0 0 40px 40px;
  padding: 48px 32px 64px;
  margin-bottom: -40px;
  position: relative; overflow: hidden;
  /* 突破父容器宽度限制，铺满整个视口（与 home.html 原型一致） */
  width: 100vw;
  margin-left: calc(50% - 50vw);
  margin-right: calc(50% - 50vw);
}
.hero::before {
  content: ""; position: absolute; top: -50%; right: -10%; width: 500px; height: 500px;
  background: rgba(255,255,255,0.08); border-radius: 50%;
}
.hero::after {
  content: ""; position: absolute; bottom: -30%; left: -5%; width: 300px; height: 300px;
  background: rgba(255,255,255,0.05); border-radius: 50%;
}
.hero-content {
  max-width: 1200px; margin: 0 auto; position: relative; z-index: 1;
  display: flex; justify-content: space-between; align-items: center;
}
.hero-text h1 {
  font-size: 36px; font-weight: 700; color: #fff; margin-bottom: 8px;
  text-shadow: 0 2px 4px rgba(0,0,0,0.1);
}
.hero-text p {
  font-size: 16px; color: rgba(255,255,255,0.85); margin-bottom: 24px;
}
.hero-stats { display: flex; gap: 32px; margin-top: 24px; }
.hero-stat { text-align: center; }
.hero-stat-num { font-size: 28px; font-weight: 700; color: #fff; }
.hero-stat-label { font-size: 13px; color: rgba(255,255,255,0.7); margin-top: 4px; }
.hero-avatar {
  width: 80px; height: 80px; border-radius: 50%;
  background: rgba(255,255,255,0.2); border: 3px solid rgba(255,255,255,0.3);
  display: flex; align-items: center; justify-content: center;
  font-size: 32px; color: #fff;
}
@media (max-width: 768px) {
  .hero-content { flex-direction: column; text-align: center; gap: 24px; }
  .hero-stats { justify-content: center; }
  .hero { padding: 32px 16px 64px; }
}
</style>
