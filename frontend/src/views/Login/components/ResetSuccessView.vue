<!--
  ResetSuccessView.vue - 重置密码成功视图
  emits: back
-->
<template>
  <div class="view active">
    <div class="success-icon">
      <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="#4caf50" stroke-width="2.5">
        <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/>
        <polyline points="22 4 12 14.01 9 11.01"/>
      </svg>
    </div>
    <div class="success-title">密码重置成功</div>
    <div class="success-desc">
      你的登录密码已更新，请使用新密码重新登录。<br>
      为保障账号安全，建议定期更换密码。
    </div>
    <button class="btn btn-primary" @click="$emit('back')">返回登录</button>
  </div>
</template>

<script>
export default {
  name: 'ResetSuccessView',
  emits: ['back']
}
</script>
