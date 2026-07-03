import { createRouter, createWebHistory } from 'vue-router'
import Login from '../views/Login.vue'
import Register from '../views/Register.vue'
import Home from '../views/Home.vue'
import Figures from '../views/Figures.vue'
import FigureDetail from '../views/FigureDetail.vue'
import Orders from '../views/Orders.vue'
import SoldOrders from '../views/SoldOrders.vue'
import Profile from '../views/Profile.vue'
import Dashboard from '../views/Dashboard.vue'
import ShareProfile from '../views/ShareProfile.vue'
import { useUserStore } from '../store'

const routes = [
  {
    path: '/',
    redirect: '/home'
  },
  {
    path: '/home',
    name: 'Home',
    component: Home
  },
  {
    path: '/login',
    name: 'Login',
    component: Login
  },
  {
    path: '/register',
    name: 'Register',
    component: Register
  },
  {
    path: '/figures',
    name: 'Figures',
    component: Figures,
    meta: { requiresAuth: true }
  },
  {
    path: '/figures/:id',
    name: 'FigureDetail',
    component: FigureDetail,
    meta: { requiresAuth: true }
  },
  {
    path: '/orders',
    name: 'Orders',
    component: Orders,
    meta: { requiresAuth: true }
  },
  {
    path: '/sell',
    name: 'SoldOrders',
    component: SoldOrders,
    meta: { requiresAuth: true }
  },
  {
    path: '/profile',
    name: 'Profile',
    component: Profile,
    meta: { requiresAuth: true }
  },
  {
    path: '/dashboard',
    name: 'Dashboard',
    component: Dashboard,
    meta: { requiresAuth: true }
  },
  {
    path: '/share/:userId',
    name: 'ShareProfile',
    component: ShareProfile,
    meta: { requiresAuth: false }
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// 路由守卫
router.beforeEach(async (to, from, next) => {
  const requiresAuth = to.matched.some(record => record.meta.requiresAuth)
  const token = localStorage.getItem('token')
  
  if (requiresAuth && !token) {
    next('/login')
  } else {
    if (token) {
      const userStore = useUserStore()
      if (!userStore.currentUser) {
        await userStore.fetchUser()
      }
    }
    next()
  }
})

export default router