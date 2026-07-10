<template>
  <div class="date-card">
    <div class="date-day">{{ day }}</div>
    <div class="date-month">{{ year }}年{{ month }}月</div>
    <div class="date-weekday">{{ weekday }}</div>
  </div>
</template>

<script setup>
const now = new Date()
const days = ['星期日', '星期一', '星期二', '星期三', '星期四', '星期五', '星期六']
const day = String(now.getDate()).padStart(2, '0')
const year = now.getFullYear()
const month = now.getMonth() + 1
const weekday = days[now.getDay()]
</script>

<style scoped>
.date-card {
  background: #fff; border-radius: 12px; padding: 16px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.06); text-align: center;
}
.date-day { font-size: 48px; font-weight: 700; color: #1890ff; line-height: 1; }
.date-month { font-size: 14px; color: #999; margin-top: 4px; }
.date-weekday { font-size: 13px; color: #666; margin-top: 2px; }
</style>
