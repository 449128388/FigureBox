<!--
  CollectorHeader.vue - 收藏家模式头部组件

  功能说明：
  - 展示收藏家头像和标题
  - 提供分享海报和隐私设置按钮
  - 通过事件向父组件传递操作

  组件依赖：
  - 无外部组件依赖

  维护提示：
  - 点击事件通过 $emit 传递给父组件
  - 使用 Element Plus 图标组件
-->
<template>
  <div class="profile-hero">
    <div class="profile-left">
      <div class="avatar">🧸</div>
      <div class="profile-info">
        <div class="profile-title">我的塑料资产</div>
        <div class="profile-sub">藏品陈列室 · 以热爱为尺，不以涨跌为度</div>
      </div>
    </div>
    <div class="profile-actions">
      <button class="btn-ghost" @click="sharePoster">
        <span class="btn-icon">📤</span> 分享海报
      </button>
      <button class="btn-ghost" @click="privacySettings">
        <span class="btn-icon">🔒</span> 隐私设置
      </button>
    </div>
  </div>
</template>

<script>
export default {
  name: 'CollectorHeader',
  emits: ['share-poster', 'privacy-settings'],
  methods: {
    sharePoster() {
      this.$emit('share-poster')
    },
    privacySettings() {
      this.$emit('privacy-settings')
    }
  }
}
</script>

<style scoped>
.profile-hero {
  background: var(--card-bg, #FFFFFF);
  border-radius: var(--radius, 12px);
  padding: 24px;
  margin-bottom: 20px;
  box-shadow: var(--shadow, 0 2px 8px rgba(0,0,0,0.04));
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.profile-left {
  display: flex;
  align-items: center;
  gap: 16px;
}

.avatar {
  width: 56px;
  height: 56px;
  border-radius: 50%;
  background: linear-gradient(135deg, #E8D5C0, #C49A6C);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24px;
  color: #fff;
  flex-shrink: 0;
}

.profile-info {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.profile-title {
  font-size: 20px;
  font-weight: 600;
  color: var(--text-primary, #1F1F1F);
}

.profile-sub {
  font-size: 13px;
  color: var(--text-tertiary, #999999);
}

.profile-actions {
  display: flex;
  gap: 10px;
}

.btn-ghost {
  padding: 6px 14px;
  border: 1px solid var(--border, #EBE8E4);
  background: #fff;
  border-radius: 6px;
  font-size: 13px;
  color: var(--text-secondary, #666666);
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 6px;
  transition: all 0.2s;
}

.btn-ghost:hover {
  border-color: var(--accent, #C49A6C);
  color: var(--accent, #C49A6C);
}

.btn-icon {
  font-size: 14px;
}

@media (max-width: 768px) {
  .profile-hero {
    flex-direction: column;
    gap: 15px;
    text-align: center;
  }

  .profile-left {
    flex-direction: column;
  }

  .profile-actions {
    width: 100%;
    justify-content: center;
  }
}
</style>
