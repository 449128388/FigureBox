<!--
  PanelSecurity.vue - 账号安全面板
  props: active / email / username
  三个修改按钮目前都是 disabled，未来可接入修改邮箱/密码/用户名流程
-->
<template>
  <div class="panel" :class="{ active: active }">
    <div class="panel-header">账号安全</div>
    <div class="panel-body">
      <div class="security-list">
        <div class="security-item">
          <div class="security-info">
            <div class="security-title">邮箱地址</div>
            <div class="security-desc">{{ email || '未设置' }}</div>
          </div>
          <button class="btn btn-outline btn-sm" disabled>修改邮箱</button>
        </div>
        <div class="security-item">
          <div class="security-info">
            <div class="security-title">登录密码</div>
            <div class="security-desc">已设置密码</div>
          </div>
          <button class="btn btn-outline btn-sm" disabled>修改密码</button>
        </div>
        <div class="security-item">
          <div class="security-info">
            <div class="security-title">用户名</div>
            <div class="security-desc">{{ username || '' }}</div>
          </div>
          <button class="btn btn-outline btn-sm" disabled>修改用户名</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'PanelSecurity',
  props: {
    active: { type: Boolean, default: false },
    email: { type: String, default: '' },
    username: { type: String, default: '' }
  }
}
</script>

<style scoped>
.panel { background: #fff; border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.06); overflow: hidden; display: none; }
.panel.active { display: block; animation: fadeIn 0.3s ease; }
@keyframes fadeIn { from { opacity: 0; transform: translateY(8px); } to { opacity: 1; transform: translateY(0); } }
.panel-header { padding: 20px 24px; border-bottom: 1px solid #e3e5e7; font-size: 18px; font-weight: 700; color: #18191c; }
.panel-body { padding: 24px 32px 32px; }

.security-list { max-width: 640px; }
.security-item {
  display: flex; align-items: center; justify-content: space-between;
  padding: 20px 0; border-bottom: 1px solid #e3e5e7;
}
.security-item:last-child { border-bottom: none; }
.security-info { display: flex; flex-direction: column; gap: 4px; }
.security-title { font-size: 14px; font-weight: 600; color: #18191c; }
.security-desc { font-size: 13px; color: #9499a0; }

.btn {
  display: inline-flex; align-items: center; justify-content: center; gap: 6px;
  border-radius: 6px; font-weight: 500; cursor: pointer;
  border: none; outline: none; transition: all 0.2s;
}
.btn-outline { background: #fff; color: #61666d; border: 1px solid #c9cdd4; padding: 6px 16px; font-size: 13px; }
.btn-outline:hover { border-color: #00a1d6; color: #00a1d6; }
.btn:disabled { opacity: 0.5; cursor: not-allowed; }
</style>
