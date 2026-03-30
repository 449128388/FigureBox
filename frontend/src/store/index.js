import { defineStore } from 'pinia'
import axios from '../axios'

export const useUserStore = defineStore('user', {
  state: () => ({
    user: null,
    token: localStorage.getItem('token') || null
  }),
  getters: {
    isAuthenticated: (state) => !!state.token,
    currentUser: (state) => state.user
  },
  actions: {
    async login(email, password) {
      const response = await axios.post('/auth/login', { email, password })
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
        console.error('Failed to fetch user:', error)
      }
    },
    logout() {
      this.token = null
      this.user = null
      localStorage.removeItem('token')
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
      if (params.tag_id) {
        queryParams.append('tag_id', params.tag_id)
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
      this.figures = response
      
      // 设置总数（用于分页）
      // 注意：这里使用返回数据的长度作为当前页数据量
      // 实际总数量需要通过其他方式获取（如后端返回的 total 字段）
      this.totalCount = response.length
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
    }
  }
})

export const useTagStore = defineStore('tag', {
  state: () => ({
    tags: []
  }),
  actions: {
    async fetchTags() {
      const response = await axios.get('/figures/tags/')
      this.tags = response
      return response
    },
    async createTag(tag) {
      const response = await axios.post('/figures/tags/', tag)
      this.tags.push(response)
      return response
    },
    async updateTag(id, tag) {
      const response = await axios.put(`/figures/tags/${id}/`, tag)
      const index = this.tags.findIndex(t => t.id === id)
      if (index !== -1) {
        this.tags[index] = response
      }
      return response
    },
    async deleteTag(id) {
      await axios.delete(`/figures/tags/${id}/`)
      this.tags = this.tags.filter(t => t.id !== id)
    }
  }
})

export const useOrderStore = defineStore('order', {
  state: () => ({
    orders: []
  }),
  actions: {
    async fetchOrders() {
      const response = await axios.get('/orders/')
      this.orders = response
    },
    async createOrder(order) {
      const response = await axios.post('/orders/', order)
      this.orders.push(response)
    },
    async updateOrder(id, order) {
      const response = await axios.put(`/orders/${id}/`, order)
      const index = this.orders.findIndex(o => o.id === id)
      if (index !== -1) {
        this.orders[index] = response
      }
    },
    async deleteOrder(id) {
      await axios.delete(`/orders/${id}/`)
      this.orders = this.orders.filter(o => o.id !== id)
    }
  }
})