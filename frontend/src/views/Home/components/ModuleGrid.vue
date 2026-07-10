<template>
  <div class="module-grid">
    <div class="module-item" v-for="m in modules" :key="m.name" @click="$router.push(m.route)">
      <div :class="['module-icon', m.color]"><i :class="m.icon"></i></div>
      <div class="module-name">{{ m.name }}</div>
      <div class="module-desc">{{ m.desc }}</div>
    </div>
  </div>
</template>

<script setup>
const modules = [
  { name: '手办管理', desc: '管理在柜藏品', icon: 'ri-box-3-line', color: 'blue', route: '/figures' },
  { name: '订单管理', desc: '尾款与预定追踪', icon: 'ri-shopping-bag-3-line', color: 'orange', route: '/orders' },
  { name: '卖出管理', desc: '已出订单与收益', icon: 'ri-exchange-dollar-line', color: 'green', route: '/sell' },
  { name: '愿望清单', desc: '想买的塑料小人', icon: 'ri-heart-3-line', color: 'pink', route: '/wishlist' },
  { name: '资产看板', desc: 'HPI 与投资收益', icon: 'ri-line-chart-line', color: 'purple', route: '/dashboard' },
  { name: '个人资料', desc: '账户与偏好设置', icon: 'ri-user-settings-line', color: 'cyan', route: '/profile' },
]
</script>

<style scoped>
.module-grid {
  display: grid; grid-template-columns: repeat(3, 1fr); gap: 16px;
}
.module-item {
  background: #fff; border-radius: 10px; padding: 24px 20px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.06); text-align: center; cursor: pointer;
  transition: all 0.3s; border: 1px solid transparent;
  position: relative; overflow: hidden;
}
.module-item::before {
  content: ""; position: absolute; top: 0; left: 0; right: 0; height: 3px;
  background: transparent; transition: all 0.3s;
}
.module-item:hover { transform: translateY(-4px); box-shadow: 0 8px 24px rgba(0,0,0,0.12); border-color: #e6f4ff; }
.module-item:hover::before { background: #1890ff; }
.module-icon {
  width: 56px; height: 56px; border-radius: 16px; margin: 0 auto 12px;
  display: flex; align-items: center; justify-content: center; font-size: 28px;
  transition: all 0.3s;
}
.module-item:hover .module-icon { transform: scale(1.1); }
.module-icon.blue { background: #e6f4ff; color: #1890ff; }
.module-icon.green { background: #f6ffed; color: #52c41a; }
.module-icon.orange { background: #fff7e6; color: #fa8c16; }
.module-icon.purple { background: #f9f0ff; color: #722ed1; }
.module-icon.pink { background: #fff0f6; color: #eb2f96; }
.module-icon.cyan { background: #e6fffb; color: #13c2c2; }
.module-name { font-size: 15px; font-weight: 600; color: #1a1a1a; margin-bottom: 4px; }
.module-desc { font-size: 12px; color: #999; }
@media (max-width: 768px) { .module-grid { grid-template-columns: repeat(2, 1fr); } }
</style>
