<template>
  <header class="top-header">
    <router-link to="/home" class="logo-area">
      <img src="/imgs/logo.png" alt="FigureBox">
      FigureBox
    </router-link>
    <nav class="header-nav">
      <router-link to="/home">首页</router-link>
      <router-link to="/figures">手办库</router-link>
      <router-link to="/orders">尾款管理</router-link>
      <router-link to="/sell">已出订单</router-link>
      <router-link to="/wishlist">愿望清单</router-link>
      <router-link to="/dashboard">资产看板</router-link>
      <router-link to="/profile">个人中心</router-link>
    </nav>
    <div class="header-user">
      <div class="user-dropdown-trigger" :class="{ open: isDropdownOpen }" @click.stop="toggleDropdown">
        <span>{{ userStore.currentUser?.username || userStore.profile?.username || '' }}</span>
        <img class="header-avatar" :src="userStore.currentUser?.avatar_url || userStore.profile?.avatar_url || '/imgs/none.jpg'" />
        <svg class="dropdown-arrow" viewBox="0 0 10 6" fill="none" stroke="currentColor" stroke-width="1.5">
          <path d="M1 1l4 4 4-4"/>
        </svg>
      </div>
      <div class="user-dropdown-menu" :class="{ show: isDropdownOpen }">
        <router-link to="/profile" class="dropdown-item" @click="closeDropdown">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/>
            <circle cx="12" cy="7" r="4"/>
          </svg>
          个人资料
        </router-link>
        <div class="dropdown-divider"></div>
        <div class="dropdown-item" @click="openAboutModal">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <circle cx="12" cy="12" r="10"/>
            <line x1="12" y1="16" x2="12" y2="12"/>
            <line x1="12" y1="8" x2="12.01" y2="8"/>
          </svg>
          关于
        </div>
        <div class="dropdown-divider"></div>
        <div class="dropdown-item logout" @click="handleLogoutClick">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4"/>
            <polyline points="16 17 21 12 16 7"/>
            <line x1="21" y1="12" x2="9" y2="12"/>
          </svg>
          退出登录
        </div>
      </div>
    </div>

    <div class="modal-overlay" :class="{ show: showLogoutModal }" @click="closeLogoutModal">
      <div class="modal-box" @click.stop>
        <div class="modal-title">确认退出</div>
        <div class="modal-body">确定要退出登录吗？退出后将清除登录状态，需要重新登录才能继续使用。</div>
        <div class="modal-actions">
          <button class="btn btn-cancel" @click="closeLogoutModal">取消</button>
          <button class="btn btn-danger" @click="handleLogout">确认退出</button>
        </div>
      </div>
    </div>

    <!-- 关于弹窗 -->
    <div class="modal-overlay about-overlay" :class="{ show: showAboutModal }" @click="closeAboutModal">
      <div class="about-modal" @click.stop>
        <div class="about-header">
          <button class="about-close" @click="closeAboutModal">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <line x1="18" y1="6" x2="6" y2="18"/>
              <line x1="6" y1="6" x2="18" y2="18"/>
            </svg>
          </button>
          <div class="about-logo">
            <img src="/imgs/logo.png" alt="FigureBox" class="about-logo-img">
          </div>
          <div class="about-title">FigureBox</div>
          <div class="about-version">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="12" height="12">
              <circle cx="12" cy="12" r="4"/>
              <line x1="1.05" y1="12" x2="7" y2="12"/>
              <line x1="17.01" y1="12" x2="22.96" y2="12"/>
            </svg>
            v1.1.14 (Build 20260723)
          </div>
          <div class="about-slogan">为二次元手办爱好者打造的资产管理工具</div>
        </div>

        <div class="about-body">
          <div class="about-section">
            <div class="about-section-title">产品信息</div>
            <div class="about-info-row">
              <span class="about-info-label">产品名称</span>
              <span class="about-info-value">FigureBox 手办管理系统</span>
            </div>
            <div class="about-info-row">
              <span class="about-info-label">当前版本</span>
              <span class="about-info-value">v2.1.0</span>
            </div>
            <div class="about-info-row">
              <span class="about-info-label">更新日期</span>
              <span class="about-info-value">2026-07-10</span>
            </div>
            <div class="about-info-row">
              <span class="about-info-label">运行环境</span>
              <span class="about-info-value">Web / Docker / MySQL 8.0 / minio </span>
            </div>
          </div>

          <div class="about-section">
            <div class="about-section-title">开发团队</div>
            <div class="about-desc" style="margin-bottom: 10px;">
              FigureBox 由热爱二次元手办的开发者打造，致力于用专业的资产管理思维管理你的塑料小人。
            </div>
            <div class="about-team">
              <span class="team-tag">产品经理</span>
              <span class="team-tag">前端开发</span>
              <span class="team-tag">后端开发</span>
              <span class="team-tag">UI 设计</span>
            </div>
          </div>

          <div class="about-section">
            <div class="about-section-title">联系我们</div>
            <div class="about-info-row">
              <span class="about-info-label">官方邮箱</span>
              <span class="about-info-value">
                <a href="mailto:hello@figurebox.app">zw9710631@163.com</a>
              </span>
            </div>
            <div class="about-info-row">
              <span class="about-info-label">GitHub</span>
              <span class="about-info-value">
                <a href="https://github.com/449128388/FigureBox/" target="_blank">https://github.com/449128388/FigureBox/</a>
              </span>
            </div>
            <div class="about-info-row">
              <span class="about-info-label">问题反馈</span>
              <span class="about-info-value">
                <a href="https://github.com/449128388/FigureBox/issues" target="_blank">提交 Issue</a>
              </span>
            </div>
          </div>

          <div class="about-section">
            <div class="about-section-title">开源协议</div>
            <div class="about-desc">
              FigureBox 前端与后端核心代码采用 <strong>MIT License</strong> 开源，欢迎社区贡献。HPI 指数算法与塑料小人估值模型受相关知识产权保护。
            </div>
          </div>

          <div class="about-section">
            <div class="about-section-title">特别致谢</div>
            <div class="about-desc">
              感谢 ECharts、Remix Icon 等开源项目的贡献者。
            </div>
          </div>
        </div>

        <div class="about-footer">
          <div class="about-links">
            <a class="about-link" href="https://github.com/449128388/FigureBox/" target="_blank">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="14" height="14">
                <path d="M9 19c-5 1.5-5-2.5-7-3m14 6v-3.87a3.37 3.37 0 0 0-.94-2.61c3.14-.35 6.44-1.54 6.44-7A5.44 5.44 0 0 0 20 4.77 5.07 5.07 0 0 0 19.91 1S18.73.65 16 2.48a13.38 13.38 0 0 0-7 0C6.27.65 5.09 1 5.09 1A5.07 5.07 0 0 0 5 4.77a5.44 5.44 0 0 0-1.5 3.78c0 5.42 3.3 6.61 6.44 7A3.37 3.37 0 0 0 9 18.13V22"/>
              </svg>
              GitHub
            </a>
            <a class="about-link" href="#" target="_blank">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="14" height="14">
                <line x1="22" y1="2" x2="11" y2="13"/>
                <polygon points="22 2 15 22 11 13 2 9 22 2"/>
              </svg>
              交流群
            </a>
            <a class="about-link" href="https://github.com/449128388/FigureBox/blob/main/README.md" target="_blank">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="14" height="14">
                <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>
                <polyline points="14 2 14 8 20 8"/>
              </svg>
              使用文档
            </a>
          </div>
          <div class="about-copyright">
            © 2024-2026 FigureBox Team. All rights reserved.
          </div>
        </div>
      </div>
    </div>

    <div class="toast" :class="{ show: showToast, type: toastType }">{{ toastMessage }}</div>
  </header>
</template>

<script>
import { ref, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '../store'

export default {
  name: 'TopHeader',
  setup() {
    const router = useRouter()
    const userStore = useUserStore()
    
    const isDropdownOpen = ref(false)
    const showLogoutModal = ref(false)
    const showAboutModal = ref(false)
    const showToast = ref(false)
    const toastMessage = ref('')
    const toastType = ref('success')

    const toggleDropdown = () => {
      isDropdownOpen.value = !isDropdownOpen.value
    }

    const closeDropdown = () => {
      isDropdownOpen.value = false
    }

    const openLogoutModal = () => {
      showLogoutModal.value = true
    }

    const handleLogoutClick = () => {
      closeDropdown()
      openLogoutModal()
    }

    const openAboutModal = () => {
      closeDropdown()
      showAboutModal.value = true
    }

    const closeAboutModal = () => {
      showAboutModal.value = false
    }

    const closeLogoutModal = () => {
      showLogoutModal.value = false
    }

    const handleLogout = async () => {
      closeLogoutModal()
      showToastMessage('已退出登录，正在跳转...', 'success')
      await userStore.logout()
      setTimeout(() => {
        router.push('/login')
      }, 1500)
    }

    const showToastMessage = (message, type = 'success') => {
      toastMessage.value = message
      toastType.value = type
      showToast.value = true
      setTimeout(() => {
        showToast.value = false
      }, 2500)
    }

    const handleClickOutside = (event) => {
      const trigger = event.target.closest('.user-dropdown-trigger')
      const menu = event.target.closest('.user-dropdown-menu')
      if (!trigger && !menu) {
        closeDropdown()
      }
    }

    const handleEsc = (event) => {
      if (event.key === 'Escape' && showAboutModal.value) {
        closeAboutModal()
      }
    }

    onMounted(() => {
      document.addEventListener('click', handleClickOutside)
      document.addEventListener('keydown', handleEsc)
    })

    onUnmounted(() => {
      document.removeEventListener('click', handleClickOutside)
      document.removeEventListener('keydown', handleEsc)
    })

    return {
      userStore,
      isDropdownOpen,
      showLogoutModal,
      showAboutModal,
      showToast,
      toastMessage,
      toastType,
      toggleDropdown,
      closeDropdown,
      openLogoutModal,
      closeLogoutModal,
      handleLogoutClick,
      handleLogout,
      openAboutModal,
      closeAboutModal
    }
  }
}
</script>

<style scoped>
.top-header {
  background: #fff;
  border-bottom: 1px solid #e3e5e7;
  padding: 0 24px;
  height: 64px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  z-index: 100;
  width: 100%;
  box-sizing: border-box;
}
.logo-area {
  display: flex;
  align-items: center;
  gap: 12px;
  font-size: 18px;
  font-weight: 700;
  color: #18191c;
  text-decoration: none;
  cursor: pointer;
}
.logo-area:hover {
  opacity: 0.8;
}
.logo-area img { width: 32px; height: 32px; border-radius: 8px; }
.header-nav {
  display: flex;
  gap: 24px;
  font-size: 14px;
  color: #61666d;
}
.header-nav a,
.header-nav router-link {
  text-decoration: none;
  color: inherit;
  transition: color 0.2s;
  cursor: pointer;
}
.header-nav a:hover, .header-nav a.active,
.header-nav router-link:hover, .header-nav router-link.active,
.header-nav router-link.router-link-active { color: #00a1d6; }
.header-user {
  display: flex;
  align-items: center;
  gap: 12px;
  font-size: 14px;
  color: #61666d;
  position: relative;
}
.user-dropdown-trigger {
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
  padding: 4px 8px 4px 4px;
  border-radius: 20px;
  transition: background 0.2s;
  user-select: none;
}
.user-dropdown-trigger:hover {
  background: #f6f7f8;
}
.header-avatar {
  width: 36px; height: 36px;
  border-radius: 50%;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  display: flex; align-items: center; justify-content: center;
  color: #fff; font-weight: 600; font-size: 14px;
  flex-shrink: 0;
}
.dropdown-arrow {
  width: 10px; height: 6px;
  transition: transform 0.2s;
  color: #9499a0;
}
.user-dropdown-trigger.open .dropdown-arrow {
  transform: rotate(180deg);
}
.user-dropdown-menu {
  position: absolute;
  top: calc(100% + 8px);
  right: 0;
  background: #fff;
  border: 1px solid #e3e5e7;
  border-radius: 8px;
  box-shadow: 0 4px 16px rgba(0,0,0,0.1);
  min-width: 160px;
  padding: 6px 0;
  opacity: 0;
  transform: translateY(-8px);
  pointer-events: none;
  transition: all 0.2s ease;
  z-index: 200;
}
.user-dropdown-menu.show {
  opacity: 1;
  transform: translateY(0);
  pointer-events: auto;
}
.user-dropdown-menu::before {
  content: "";
  position: absolute;
  top: -6px;
  right: 20px;
  width: 10px;
  height: 10px;
  background: #fff;
  border-left: 1px solid #e3e5e7;
  border-top: 1px solid #e3e5e7;
  transform: rotate(45deg);
}
.dropdown-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px 16px;
  font-size: 14px;
  color: #18191c;
  cursor: pointer;
  transition: all 0.15s;
  text-decoration: none;
}
.dropdown-item:hover {
  background: #f0f5ff;
  color: #00a1d6;
}
.dropdown-item svg {
  width: 16px; height: 16px;
  opacity: 0.7;
}
.dropdown-divider {
  height: 1px;
  background: #e3e5e7;
  margin: 6px 12px;
}
.dropdown-item.logout {
  color: #f25d8e;
}
.dropdown-item.logout:hover {
  background: #fff0f3;
}
.dropdown-item.logout svg {
  color: #f25d8e;
}

.modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0,0,0,0.45);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  opacity: 0;
  pointer-events: none;
  transition: opacity 0.3s;
}
.modal-overlay.show {
  opacity: 1;
  pointer-events: auto;
}
.modal-box {
  background: #fff;
  border-radius: 8px;
  box-shadow: 0 4px 24px rgba(0,0,0,0.15);
  width: 420px;
  max-width: 90vw;
  padding: 28px;
  transform: scale(0.95);
  transition: transform 0.3s;
}
.modal-overlay.show .modal-box {
  transform: scale(1);
}
.modal-title {
  font-size: 18px;
  font-weight: 700;
  color: #18191c;
  margin-bottom: 12px;
}
.modal-body {
  font-size: 14px;
  color: #61666d;
  line-height: 1.7;
  margin-bottom: 24px;
}
.modal-actions {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
}
.btn {
  padding: 10px 20px;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-size: 14px;
  font-weight: 500;
  transition: all 0.2s;
}
.btn-cancel {
  background: #fff;
  color: #61666d;
  border: 1px solid #e3e5e7;
}
.btn-cancel:hover {
  background: #f6f7f8;
}
.btn-danger {
  background: #f25d8e;
  color: #fff;
}
.btn-danger:hover {
  background: #e6457a;
}

.toast {
  position: fixed;
  top: 80px;
  left: 50%;
  transform: translateX(-50%) translateY(-20px);
  background: #18191c;
  color: #fff;
  padding: 10px 20px;
  border-radius: 6px;
  font-size: 14px;
  opacity: 0;
  pointer-events: none;
  transition: all 0.3s;
  z-index: 2000;
  box-shadow: 0 4px 12px rgba(0,0,0,0.15);
}
.toast.show {
  opacity: 1;
  transform: translateX(-50%) translateY(0);
}

/* 关于弹窗 */
.about-overlay { z-index: 1100; }
.about-modal {
  background: #fff;
  border-radius: 16px;
  width: 90%;
  max-width: 520px;
  max-height: 85vh;
  overflow: hidden;
  display: flex;
  flex-direction: column;
  transform: scale(0.95) translateY(10px);
  transition: transform 0.3s;
}
.modal-overlay.show .about-modal {
  transform: scale(1) translateY(0);
}
.about-header {
  padding: 24px 24px 0;
  text-align: center;
  position: relative;
}
.about-close {
  position: absolute;
  top: 16px;
  right: 16px;
  width: 32px;
  height: 32px;
  border-radius: 50%;
  border: none;
  background: rgba(0,0,0,0.04);
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #666;
  transition: all 0.2s;
}
.about-close:hover {
  background: rgba(0,0,0,0.08);
  color: #1a1a1a;
}
.about-close svg { width: 16px; height: 16px; }
.about-logo {
  width: 72px;
  height: 72px;
  border-radius: 20px;
  overflow: hidden;
  margin-bottom: 12px;
  box-shadow: 0 4px 12px rgba(24,144,255,0.3);
}
.about-logo-img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  display: block;
}
.about-title {
  font-size: 22px;
  font-weight: 700;
  color: #1a1a1a;
  margin-bottom: 4px;
}
.about-version {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  font-size: 12px;
  color: #999;
  background: #f5f5f5;
  padding: 4px 12px;
  border-radius: 12px;
  margin-bottom: 8px;
}
.about-slogan {
  font-size: 13px;
  color: #999;
  margin-bottom: 16px;
}
.about-body {
  padding: 8px 24px 20px;
  overflow-y: auto;
  max-height: 45vh;
}
.about-section { margin-bottom: 18px; }
.about-section:last-child { margin-bottom: 0; }
.about-section-title {
  font-size: 12px;
  font-weight: 600;
  color: #999;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  margin-bottom: 8px;
}
.about-info-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 6px 0;
  font-size: 14px;
}
.about-info-label { color: #666; }
.about-info-value { color: #1a1a1a; font-weight: 500; }
.about-info-value a {
  color: #1890ff;
  text-decoration: none;
}
.about-info-value a:hover { text-decoration: none; }
.about-desc {
  font-size: 13px;
  color: #666;
  line-height: 1.7;
}
.about-team {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}
.team-tag {
  padding: 4px 12px;
  background: #e6f7ff;
  color: #1890ff;
  border-radius: 6px;
  font-size: 12px;
  font-weight: 500;
}
.about-footer {
  padding: 14px 24px;
  background: #fafafa;
  border-top: 1px solid #f0f0f0;
  text-align: center;
}
.about-links {
  display: flex;
  justify-content: center;
  gap: 16px;
  margin-bottom: 6px;
}
.about-link {
  font-size: 13px;
  color: #1890ff;
  text-decoration: none;
  display: inline-flex;
  align-items: center;
  gap: 4px;
  transition: opacity 0.2s;
}
.about-link:hover { opacity: 0.7; }
.about-copyright {
  font-size: 12px;
  color: #bbb;
}
@media (max-width: 480px) {
  .about-modal { max-width: 95%; }
}
</style>