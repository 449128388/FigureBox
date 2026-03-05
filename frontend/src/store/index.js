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
    figures: []
  }),
  actions: {
    async fetchFigures() {
      const response = await axios.get('/figures/')
      this.figures = response
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

export const useOrderStore = defineStore('order', {
  state: () => ({
    orders: []
  }),
  actions: {
    async fetchOrders() {
      const response = await axios.get('/orders')
      this.orders = response
    },
    async createOrder(order) {
      const response = await axios.post('/orders', order)
      this.orders.push(response)
    },
    async updateOrder(id, order) {
      const response = await axios.put(`/orders/${id}`, order)
      const index = this.orders.findIndex(o => o.id === id)
      if (index !== -1) {
        this.orders[index] = response
      }
    },
    async deleteOrder(id) {
      await axios.delete(`/orders/${id}`)
      this.orders = this.orders.filter(o => o.id !== id)
    }
  }
})