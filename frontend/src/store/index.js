import { defineStore } from 'pinia'
import axios from '../axios'

export const useUserStore = defineStore('user', {
  state: () => ({
    user: null,
    profile: null,
    token: localStorage.getItem('token') || null
  }),
  getters: {
    isAuthenticated: (state) => !!state.token,
    currentUser: (state) => state.user
  },
  actions: {
    async login(email, password) {
      const response = await axios.post('/auth/login', { email, password })
      // axios 拦截器（src/axios/index.js:38）已经返回 response.data，所以这里是直接的 data
      this.token = response.access_token
      localStorage.setItem('token', response.access_token)
      await this.fetchUser()
    },
    async register(username, email, password) {
      const response = await axios.post('/auth/register', { username, email, password })
      this.token = response.access_token
      localStorage.setItem('token', response.access_token)
      await this.fetchUser()
    },
    async fetchUser() {
      try {
        const response = await axios.get('/users/me')
        this.user = response
      } catch (error) {
        return null
      }
    },
    async fetchProfile() {
      try {
        // axios 拦截器（src/axios/index.js:38）已经返回 response.data，所以这里是直接的 data
        const response = await axios.get('/users/profile')
        this.profile = response
        return response
      } catch (error) {
        return null
      }
    },
    async updateProfile(profileData) {
      const response = await axios.put('/users/profile', profileData)
      this.profile = response
      return response
    },
    async updateSettings(settingsData) {
      const response = await axios.put('/users/settings', settingsData)
      return response
    },
    async updateAvatar(avatarUrl) {
      const response = await axios.put('/users/profile', { avatar_url: avatarUrl })
      if (this.profile) {
        this.profile.avatar_url = avatarUrl
      }
      if (this.currentUser) {
        this.currentUser.avatar_url = avatarUrl
      }
      return response
    },
    logout() {
      this.token = null
      this.user = null
      this.profile = null
      localStorage.removeItem('token')
      return Promise.resolve()
    }
  }
})

export const useFigureStore = defineStore('figure', {
  state: () => ({
    figures: [],
    totalCount: 0
  }),
  actions: {
    async fetchFigures(params = {}) {
      // 构建查询参数
      const queryParams = new URLSearchParams()

      if (params.name) {
        queryParams.append('name', params.name)
      }
      if (params.purchase_type) {
        queryParams.append('purchase_type', params.purchase_type)
      }
      if (params.purchase_date_start) {
        queryParams.append('purchase_date_start', params.purchase_date_start)
      }
      if (params.purchase_date_end) {
        queryParams.append('purchase_date_end', params.purchase_date_end)
      }
      // 2026-07-29 重构：标签已改为 figure.tags JSON 字段，按标签名筛选
      if (params.tag_names && params.tag_names.length > 0) {
        params.tag_names.forEach(tagName => {
          queryParams.append('tag_names', tagName)
        })
      }
      if (params.skip !== undefined) {
        queryParams.append('skip', params.skip)
      }
      if (params.limit !== undefined) {
        queryParams.append('limit', params.limit)
      }
      
      const queryString = queryParams.toString()
      const url = queryString ? `/figures/?${queryString}` : '/figures/'
      
      const response = await axios.get(url)
      // 兼容旧版 list 响应（如未来后端回退到 list）
      if (Array.isArray(response)) {
        this.figures = response
        this.totalCount = response.length
      } else {
        // 新版 { items, total } 响应
        this.figures = response.items || []
        this.totalCount = response.total || 0
      }
    },
    async createFigure(figure) {
      const response = await axios.post('/figures/', figure)
      this.figures.push(response)
    },
    async updateFigure(id, figure) {
      const response = await axios.put(`/figures/${id}`, figure)
      const index = this.figures.findIndex(f => f.id === id)
      if (index !== -1) {
        this.figures[index] = response
      }
    },
    async deleteFigure(id) {
      await axios.delete(`/figures/${id}`)
      this.figures = this.figures.filter(f => f.id !== id)
    },
    async batchDeleteFigures(figureIds) {
      const response = await axios.post('/figures/batch-delete', {
        figure_ids: figureIds
      })
      // 从前端列表中移除已删除的手办
      this.figures = this.figures.filter(f => !figureIds.includes(f.id))
      return response
    },
    async fetchFiguresWithStock(name = null) {
      // 获取有库存的手办列表（用于出售订单选择）
      const queryParams = new URLSearchParams()
      if (name) {
        queryParams.append('name', name)
      }
      const queryString = queryParams.toString()
      const url = queryString ? `/figures/with-stock?${queryString}` : '/figures/with-stock'
      
      const response = await axios.get(url)
      this.figures = response
      this.totalCount = response.length
      return response
    }
  }
})

export const useTagStore = defineStore('tag', {
  state: () => ({
    tags: []
  }),
  actions: {
    async fetchTags() {
      const response = await axios.get('/figures/tags')
      this.tags = response
      return response
    },
    async createTag(tag) {
      const response = await axios.post('/figures/tags', tag)
      this.tags.push(response)
      return response
    },
    async updateTag(id, tag) {
      const response = await axios.put(`/figures/tags/${id}`, tag)
      const index = this.tags.findIndex(t => t.id === id)
      if (index !== -1) {
        this.tags[index] = response
      }
      return response
    },
    async deleteTag(id) {
      await axios.delete(`/figures/tags/${id}`)
      this.tags = this.tags.filter(t => t.id !== id)
    }
  }
})

export const useOrderStore = defineStore('order', {
  state: () => ({
    orders: [],
    totalUnpaidBalance: 0
  }),
  actions: {
    async fetchOrders(params = {}) {
      // 2026-08-06 修复：透传搜索参数（figure_name / due_date_start / due_date_end），
      // 让后端 OrderService.get_orders 按条件过滤，前端搜索按钮才会真正生效
      const response = await axios.get('/orders/', { params })
      this.orders = response
      // 同时获取未支付尾款总额
      await this.fetchUnpaidBalance()
      return response
    },
    async createOrder(order) {
      await axios.post('/orders/', order)
      // 重新获取订单列表，确保数据格式正确
      await this.fetchOrders()
    },
    async updateOrder(id, order) {
      await axios.put(`/orders/${id}/`, order)
      // 重新获取订单列表，确保数据格式正确
      await this.fetchOrders()
    },
    async deleteOrder(id) {
      await axios.delete(`/orders/${id}/`)
      this.orders = this.orders.filter(o => o.id !== id)
      // 重新获取未支付尾款总额
      await this.fetchUnpaidBalance()
    },
    async batchDeleteOrders(orderIds) {
      const response = await axios.post('/orders/batch-delete/', {
        order_ids: orderIds
      })
      // 从前端列表中移除已删除的订单
      this.orders = this.orders.filter(o => !orderIds.includes(o.id))
      // 重新获取未支付尾款总额
      await this.fetchUnpaidBalance()
      return response
    },
    async fetchUnpaidBalance() {
      try {
        const response = await axios.get('/orders/unpaid-balance/')
        this.totalUnpaidBalance = response.total_unpaid_balance
      } catch (error) {
        this.totalUnpaidBalance = 0
        return 0
      }
    }
  }
})

export const useSoldOrderStore = defineStore('soldOrder', {
  state: () => ({
    soldOrders: [],
    totalNetProfit: 0
  }),
  actions: {
    async fetchSoldOrders() {
      const response = await axios.get('/sold-orders/')
      this.soldOrders = response
      await this.fetchSoldOrderStatistics()
      return response
    },
    async createSoldOrder(order) {
      await axios.post('/sold-orders/', order)
      await this.fetchSoldOrders()
    },
    async updateSoldOrder(id, order) {
      await axios.put(`/sold-orders/${id}/`, order)
      await this.fetchSoldOrders()
    },
    async deleteSoldOrder(id) {
      await axios.delete(`/sold-orders/${id}/`)
      this.soldOrders = this.soldOrders.filter(o => o.id !== id)
      await this.fetchSoldOrderStatistics()
    },
    async batchDeleteSoldOrders(orderIds) {
      const response = await axios.post('/sold-orders/batch-delete/', {
        order_ids: orderIds
      })
      this.soldOrders = this.soldOrders.filter(o => !orderIds.includes(o.id))
      await this.fetchSoldOrderStatistics()
      return response
    },
    async fetchSoldOrderStatistics() {
      try {
        const response = await axios.get('/sold-orders/statistics/')
        this.totalNetProfit = response.total_net_profit
      } catch (error) {
        this.totalNetProfit = 0
        return 0
      }
    },
    async fetchXianyuMonthlyStats(excludeOrderId = null) {
      // 获取当月闲鱼订单统计（用于计算平台手续费）
      let url = '/sold-orders/xianyu-monthly-stats/'
      if (excludeOrderId) {
        url += `?exclude_order_id=${excludeOrderId}`
      }
      const response = await axios.get(url)
      return response
    },
    async fetchFigureCostPrice(figureId) {
      // 获取手办的实际成本价（基于库存账计算）
      const response = await axios.get(`/sold-orders/figure-cost-price/${figureId}/`)
      return response
    }
  }
})