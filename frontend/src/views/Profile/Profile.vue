<!--
  Profile/Profile.vue - 个人中心主入口父页面
  职责：① 引入并初始化 useProfile() 与 useBackup() ② 渲染侧边栏 + 10 个子面板 ③ 透传 state / 桥接事件
  原 44KB / 1300+ 行的 Profile.vue 已按 Feature 分层拆为：主入口 + 9 个 Panel 子组件 + ProfileSidebar + BackupPanel
-->
<template>
  <TopHeader />

  <div class="profile-page">
    <ProfileSidebar
      :items="sidebarItems"
      :active-panel="activePanel"
      @select="switchPanel"
    />

    <main class="profile-main">
      <PanelBasic
        :active="activePanel === 'panel-basic'"
        :basic-form="basicForm"
        :nickname-len="nicknameLen"
        :signature-len="signatureLen"
        :bio-len="bioLen"
        :years="years"
        :user-id="userStore.profile?.id || userStore.currentUser?.id || ''"
        @save="saveBasic"
      />

      <PanelAvatar
        :active="activePanel === 'panel-avatar'"
        :avatar-src="avatarSrc"
        @trigger-file-input="triggerAvatarInput"
        @preview="previewAvatar"
        @save="saveAvatar"
      />

      <PanelPrivacy
        :active="activePanel === 'panel-privacy'"
        :privacy-settings="privacySettings"
        :home-visibility-text="homeVisibilityText"
        @show-home-visibility="showHomeVisibility"
        @toggle-privacy="togglePrivacy"
      />

      <PanelPush
        :active="activePanel === 'panel-push'"
        :toggles="toggles"
        @toggle-switch="toggleSwitch"
        @save="saveSettings('push')"
      />

      <PanelSecurity
        :active="activePanel === 'panel-security'"
        :email="userStore.currentUser?.email || ''"
        :username="userStore.currentUser?.username || ''"
      />

      <PanelMinIO
        :active="activePanel === 'panel-minio'"
        :minio-config="minioConfig"
        :minio-status-text="minioStatusText"
        :minio-status-detail="minioStatusDetail"
        :minio-status-class="minioStatusClass"
        :minio-status-icon-color="minioStatusIconColor"
        :testing-connection="testingConnection"
        :resetting-min-i-o="resettingMinIO"
        @test="testMinIOConnection"
        @save="saveMinIOConfig"
        @reset="resetMinIOConfig"
      />

      <PanelTimeout
        :active="activePanel === 'panel-timeout'"
        :timeout-config="timeoutConfig"
        :saving-timeout="savingTimeout"
        @select-timeout="selectTimeout"
        @save="saveTimeoutConfig"
      />

      <BackupPanel :active-panel="activePanel" />

      <PanelDelete
        :active="activePanel === 'panel-delete'"
        @confirm="showDeleteConfirm"
      />
    </main>
  </div>
</template>

<script>
import TopHeader from '../../components/TopHeader.vue'
import ProfileSidebar from './components/ProfileSidebar.vue'
import PanelBasic from './components/PanelBasic.vue'
import PanelAvatar from './components/PanelAvatar.vue'
import PanelPrivacy from './components/PanelPrivacy.vue'
import PanelPush from './components/PanelPush.vue'
import PanelSecurity from './components/PanelSecurity.vue'
import PanelMinIO from './components/PanelMinIO.vue'
import PanelTimeout from './components/PanelTimeout.vue'
import PanelDelete from './components/PanelDelete.vue'
import BackupPanel from './components/BackupPanel.vue'
import { useProfile } from './composables/useProfile'

export default {
  name: 'Profile',
  components: {
    TopHeader,
    ProfileSidebar,
    PanelBasic,
    PanelAvatar,
    PanelPrivacy,
    PanelPush,
    PanelSecurity,
    PanelMinIO,
    PanelTimeout,
    PanelDelete,
    BackupPanel
  },
  setup() {
    const {
      // state
      activePanel,
      basicForm,
      nicknameLen,
      signatureLen,
      bioLen,
      years,
      privacySettings,
      homeVisibilityText,
      toggles,
      avatarSrc,
      minioConfig,
      minioStatusText,
      minioStatusDetail,
      minioStatusClass,
      minioStatusIconColor,
      testingConnection,
      resettingMinIO,
      timeoutConfig,
      savingTimeout,
      // actions
      switchPanel,
      toggleSwitch,
      togglePrivacy,
      showHomeVisibility,
      saveBasic,
      saveSettings,
      triggerAvatarInput,
      previewAvatar,
      saveAvatar,
      testMinIOConnection,
      saveMinIOConfig,
      resetMinIOConfig,
      selectTimeout,
      saveTimeoutConfig,
      showDeleteConfirm,
      // store
      userStore
    } = useProfile()

    // 侧边栏导航配置（10 个面板）
    const sidebarItems = [
      { id: 'panel-basic', label: '基本资料', icon: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/><circle cx="12" cy="7" r="4"/></svg>' },
      { id: 'panel-avatar', label: '头像设置', icon: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="3" width="18" height="18" rx="2"/><circle cx="8.5" cy="8.5" r="1.5"/><path d="M21 15l-5-5L5 21"/></svg>' },
      { id: 'panel-privacy', label: '隐私设置', icon: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="11" width="18" height="11" rx="2"/><path d="M7 11V7a5 5 0 0 1 10 0v4"/></svg>' },
      { id: 'panel-push', label: '推送设置', icon: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M18 8A6 6 0 0 0 6 8c0 7-3 9-3 9h18s-3-2-3-9"/><path d="M13.73 21a2 2 0 0 1-3.46 0"/></svg>' },
      { id: 'panel-security', label: '账号安全', icon: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/></svg>' },
      { id: 'panel-minio', label: 'MinIO 设置', icon: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="3" width="18" height="18" rx="2"/><circle cx="8.5" cy="8.5" r="1.5"/><path d="M21 15l-5-5L5 21"/><path d="M15 12l3-3"/><path d="M9 6l3-3"/></svg>' },
      { id: 'panel-timeout', label: '超时登出', icon: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/></svg>' },
      { id: 'panel-backup', label: '系统备份', icon: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="7 10 12 15 17 10"/><line x1="12" y1="15" x2="12" y2="3"/></svg>' },
      { id: 'panel-delete', label: '账号注销', icon: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="3 6 5 6 21 6"/><path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"/></svg>' }
    ]

    return {
      // state
      activePanel,
      basicForm,
      nicknameLen,
      signatureLen,
      bioLen,
      years,
      privacySettings,
      homeVisibilityText,
      toggles,
      avatarSrc,
      minioConfig,
      minioStatusText,
      minioStatusDetail,
      minioStatusClass,
      minioStatusIconColor,
      testingConnection,
      resettingMinIO,
      timeoutConfig,
      savingTimeout,
      // actions
      switchPanel,
      toggleSwitch,
      togglePrivacy,
      showHomeVisibility,
      saveBasic,
      saveSettings,
      triggerAvatarInput,
      previewAvatar,
      saveAvatar,
      testMinIOConnection,
      saveMinIOConfig,
      resetMinIOConfig,
      selectTimeout,
      saveTimeoutConfig,
      showDeleteConfirm,
      // sidebar config
      sidebarItems,
      // store
      userStore
    }
  }
}
</script>

<style scoped>
/* ===== Page Layout ===== */
.profile-page {
  max-width: 1200px;
  margin: 24px auto;
  padding: 88px 24px 0;
  display: flex;
  gap: 20px;
  align-items: flex-start;
}

/* Main */
.profile-main {
  flex: 1;
  min-width: 0;
}

@media (max-width: 900px) {
  .profile-page { flex-direction: column; }
}
</style>
