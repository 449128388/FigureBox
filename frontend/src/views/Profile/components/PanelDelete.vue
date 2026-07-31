<!--
  PanelDelete.vue - 账号注销危险区
  props: active
  emits: confirm（点击「申请注销账号」按钮时由父级弹 ElMessageBox 二次确认）
-->
<template>
  <div class="panel" :class="{ active: active }">
    <div class="panel-header">账号注销</div>
    <div class="panel-body">
      <div class="danger-zone">
        <div class="danger-zone-title">⚠️ 注销账号</div>
        <div class="danger-zone-desc">
          注销后，你的个人资料、收藏柜数据、交易记录、收益统计等所有信息将被永久删除且无法恢复。<br>
          请确保已备份重要数据，并确认当前账号无未完成的尾款订单或纠纷。
        </div>
        <button class="btn btn-danger" @click="$emit('confirm')">申请注销账号</button>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'PanelDelete',
  props: {
    active: { type: Boolean, default: false }
  },
  emits: ['confirm']
}
</script>

<style scoped>
.panel { background: #fff; border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.06); overflow: hidden; display: none; }
.panel.active { display: block; animation: fadeIn 0.3s ease; }
@keyframes fadeIn { from { opacity: 0; transform: translateY(8px); } to { opacity: 1; transform: translateY(0); } }
.panel-header { padding: 20px 24px; border-bottom: 1px solid #e3e5e7; font-size: 18px; font-weight: 700; color: #18191c; }
.panel-body { padding: 24px 32px 32px; }

.danger-zone {
  margin-top: 32px; padding: 24px; border: 1px solid #ffd6d6;
  border-radius: 8px; background: #fff8f8;
}
.danger-zone-title { font-size: 16px; font-weight: 700; color: #f25d8e; margin-bottom: 8px; }
.danger-zone-desc { font-size: 13px; color: #61666d; margin-bottom: 16px; line-height: 1.6; }

.btn {
  display: inline-flex; align-items: center; justify-content: center; gap: 6px;
  padding: 9px 24px; border-radius: 6px; font-size: 14px; font-weight: 500;
  cursor: pointer; border: none; outline: none; transition: all 0.2s;
}
.btn-danger { background: #f25d8e; color: #fff; }
.btn-danger:hover { background: #d94d7a; }
</style>
