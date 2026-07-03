<template>
  <header class="top-header">
    <router-link to="/home" class="logo-area">
      <img src="/imgs/logo.png" alt="FigureBox">
      FigureBox
    </router-link>
    <nav class="header-nav">
      <router-link to="/figures">手办库</router-link>
      <router-link to="/orders">尾款管理</router-link>
      <router-link to="/sell">已出订单</router-link>
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

    onMounted(() => {
      document.addEventListener('click', handleClickOutside)
    })

    onUnmounted(() => {
      document.removeEventListener('click', handleClickOutside)
    })

    return {
      userStore,
      isDropdownOpen,
      showLogoutModal,
      showToast,
      toastMessage,
      toastType,
      toggleDropdown,
      closeDropdown,
      openLogoutModal,
      closeLogoutModal,
      handleLogoutClick,
      handleLogout
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
</style>