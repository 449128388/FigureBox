<!--
  Profile/Profile.vue - 个人中心主入口父页面
  职责：① 引入并初始化 useProfile() / useSecurity() / useEmailConfig() ② 渲染侧边栏 + 10 个子面板 ③ 透传 state / 桥接事件
  原 44KB / 1300+ 行的 Profile.vue 已按 Feature 分层拆为：主入口 + 10 个 Panel 子组件 + ProfileSidebar + BackupPanel
-->
<template>
  <TopHeader />

  <div class="profile-page">
    <ProfileSidebar
      :items="sidebarItems"
      :active-panel="activePanel"
      @select="handleSwitchPanel"
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
        @open-change-password="openDialog"
      />

      <!-- 修改登录密码弹窗（账号安全） -->
      <ChangePasswordDialog
        :visible="dialogVisible"
        :form="pwdForm"
        :errors="errors"
        :password-visible="pwdPasswordVisible"
        :strength-segments="strengthSegments"
        :strength-label="strengthLabel"
        :strength-color="strengthColor"
        :strength-shown="strengthShown"
        :submitting="submitting"
        @close="closeDialog"
        @submit="submitChangePassword"
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

      <PanelEmail
        :active="activePanel === 'panel-email'"
        :email-config="emailConfig"
        :password-visible="emailPasswordVisible"
        v-model:test-recipient="testRecipient"
        :saving-config="emailSavingConfig"
        :testing-connection="emailTestingConnection"
        :sending-test-email="sendingTestEmail"
        :email-status-text="emailStatusText"
        :email-status-detail="emailStatusDetail"
        :email-status-class="emailStatusClass"
        :email-status-icon-color="emailStatusIconColor"
        @save="saveEmailConfig"
        @test="testEmailConnection"
        @send-test="sendTestEmail"
        @toggle-pwd="togglePasswordVisible"
      />

      <PanelLicense
        :active="activePanel === 'panel-license'"
        :license-status="licenseStatus"
        :history="history"
        v-model:online-key="onlineKey"
        :offline-filename="offlineFilename"
        :activating="activating"
        :importing="importing"
        :revoking="revoking"
        :deleting="deleting"
        :exporting-req="exportingReq"
        :status-card-text="statusCardText"
        :status-card-class="statusCardClass"
        :status-card-icon-color="statusCardIconColor"
        :status-card-detail="statusCardDetail"
        @activate="activateOnline"
        @file-change="importOffline"
        @revoke="revokeLicense"
        @delete-history="deleteLicense"
        @export-req="exportReqFile"
        @export-lic="exportLicenseFile"
        @save="onLicenseSave"
      />

      <PanelDelete
        :active="activePanel === 'panel-delete'"
        @confirm="showDeleteConfirm"
      />
    </main>
  </div>
</template>

<script>
import { onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import TopHeader from '../../components/TopHeader.vue'
import ProfileSidebar from './components/ProfileSidebar.vue'
import PanelBasic from './components/PanelBasic.vue'
import PanelAvatar from './components/PanelAvatar.vue'
import PanelPrivacy from './components/PanelPrivacy.vue'
import PanelPush from './components/PanelPush.vue'
import PanelSecurity from './components/PanelSecurity.vue'
import ChangePasswordDialog from './components/ChangePasswordDialog.vue'
import PanelMinIO from './components/PanelMinIO.vue'
import PanelTimeout from './components/PanelTimeout.vue'
import PanelEmail from './components/PanelEmail.vue'
import PanelLicense from './components/PanelLicense.vue'
import PanelDelete from './components/PanelDelete.vue'
import BackupPanel from './components/BackupPanel.vue'
import { useProfile } from './composables/useProfile'
import { useSecurity } from './composables/useSecurity'
import { useEmailConfig } from './composables/useEmailConfig'
import { useLicense } from './composables/useLicense'

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
    ChangePasswordDialog,
    PanelMinIO,
    PanelTimeout,
    PanelEmail,
    PanelLicense,
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
      // 2026-08-05 新增：按需加载（点击模块才请求）
      loadProfile,
      loadPrivacySettings,
      loadMinIOConfig,
      loadTimeoutConfig,
      // store
      userStore
    } = useProfile()

    // 修改登录密码（账号安全）业务逻辑
    const {
      dialogVisible,
      openDialog,
      closeDialog,
      pwdForm,
      errors,
      passwordVisible: pwdPasswordVisible,
      submitting,
      strengthSegments,
      strengthLabel,
      strengthColor,
      strengthShown,
      submitChangePassword
    } = useSecurity()

    // 邮箱设置（SMTP 发件配置）业务逻辑
    const {
      emailConfig,
      passwordVisible: emailPasswordVisible,
      testRecipient,
      savingConfig: emailSavingConfig,
      testingConnection: emailTestingConnection,
      sendingTestEmail,
      emailStatusText,
      emailStatusDetail,
      emailStatusClass,
      emailStatusIconColor,
      loadEmailConfig,
      saveEmailConfig,
      testEmailConnection,
      sendTestEmail,
      togglePasswordVisible
    } = useEmailConfig()

    // 许可管理（2026-08-07 新增）业务逻辑
    const {
      licenseStatus,
      history,
      onlineKey,
      offlineFilename,
      activating,
      importing,
      revoking,
      deleting,
      exportingReq,
      statusCardText,
      statusCardClass,
      statusCardIconColor,
      statusCardDetail,
      loadLicenseStatus,
      loadHistory,
      activateOnline,
      importOffline,
      revokeLicense,
      deleteLicense,
      exportReqFile,
      exportLicenseFile
    } = useLicense()

    // 许可面板"保存设置"占位（保留与 HTML 原版 1:1 的按钮，不产生实际写操作）
    const onLicenseSave = () => {
      ElMessage.success('许可设置已保存')
    }

    // ========== 面板按需加载（2026-08-05 新增） ==========
    // 进入个人中心不再全量请求所有模块，改为「点击哪个模块才加载哪个模块」：
    // 每个面板首次激活时拉取一次对应数据，切回时不重复请求（状态保留在 composable）
    const loadedPanels = new Set()
    const panelLoaders = {
      'panel-basic': loadProfile,
      'panel-privacy': loadPrivacySettings,
      'panel-minio': loadMinIOConfig,
      'panel-timeout': loadTimeoutConfig,
      'panel-email': loadEmailConfig,
      'panel-license': () => Promise.all([loadLicenseStatus(), loadHistory()])
    }
    const handleSwitchPanel = (panelId) => {
      switchPanel(panelId)
      if (!loadedPanels.has(panelId) && panelLoaders[panelId]) {
        loadedPanels.add(panelId)
        panelLoaders[panelId]()
      }
    }

    // 挂载时默认激活「基本资料」面板 → 只加载该面板数据（其余面板点击时才请求）
    onMounted(() => {
      handleSwitchPanel('panel-basic')
    })

    // 侧边栏导航配置（11 个面板）
    const sidebarItems = [
      { id: 'panel-basic', label: '基本资料', icon: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/><circle cx="12" cy="7" r="4"/></svg>' },
      { id: 'panel-avatar', label: '头像设置', icon: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="3" width="18" height="18" rx="2"/><circle cx="8.5" cy="8.5" r="1.5"/><path d="M21 15l-5-5L5 21"/></svg>' },
      { id: 'panel-privacy', label: '隐私设置', icon: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="11" width="18" height="11" rx="2"/><path d="M7 11V7a5 5 0 0 1 10 0v4"/></svg>' },
      { id: 'panel-push', label: '推送设置', icon: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M18 8A6 6 0 0 0 6 8c0 7-3 9-3 9h18s-3-2-3-9"/><path d="M13.73 21a2 2 0 0 1-3.46 0"/></svg>' },
      { id: 'panel-security', label: '账号安全', icon: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/></svg>' },
      { id: 'panel-minio', label: 'MinIO 设置', icon: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="3" width="18" height="18" rx="2"/><circle cx="8.5" cy="8.5" r="1.5"/><path d="M21 15l-5-5L5 21"/><path d="M15 12l3-3"/><path d="M9 6l3-3"/></svg>' },
      { id: 'panel-timeout', label: '超时登出', icon: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/></svg>' },
      { id: 'panel-backup', label: '系统备份', icon: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="7 10 12 15 17 10"/><line x1="12" y1="15" x2="12" y2="3"/></svg>' },
      { id: 'panel-email', label: '邮箱设置', icon: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M4 4h16c1.1 0 2 .9 2 2v12c0 1.1-.9 2-2 2H4c-1.1 0-2-.9-2-2V6c0-1.1.9-2 2-2z"/><polyline points="22,6 12,13 2,6"/></svg>' },
      { id: 'panel-license', label: '许可管理', icon: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="3" width="18" height="18" rx="2" ry="2"/><path d="M9 12l2 2 4-4"/><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/></svg>' },
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
      // 2026-08-05 新增：按需加载
      handleSwitchPanel,
      // 修改登录密码（账号安全）
      dialogVisible,
      openDialog,
      closeDialog,
      pwdForm,
      errors,
      passwordVisible: pwdPasswordVisible,
      submitting,
      strengthSegments,
      strengthLabel,
      strengthColor,
      strengthShown,
      submitChangePassword,
      // 邮箱设置（SMTP 发件配置）
      emailConfig,
      emailPasswordVisible,
      testRecipient,
      emailSavingConfig,
      emailTestingConnection,
      sendingTestEmail,
      emailStatusText,
      emailStatusDetail,
      emailStatusClass,
      emailStatusIconColor,
      loadEmailConfig,
      saveEmailConfig,
      testEmailConnection,
      sendTestEmail,
      togglePasswordVisible,
      // 许可管理
      licenseStatus,
      history,
      onlineKey,
      offlineFilename,
      activating,
      importing,
      revoking,
      deleting,
      exportingReq,
      statusCardText,
      statusCardClass,
      statusCardIconColor,
      statusCardDetail,
      loadLicenseStatus,
      loadHistory,
      activateOnline,
      importOffline,
      revokeLicense,
      deleteLicense,
      exportReqFile,
      exportLicenseFile,
      onLicenseSave,
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
