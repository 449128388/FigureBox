import axios from 'axios'

const instance = axios.create({
  baseURL: '/api',
  timeout: 10000
})

// 请求拦截器
instance.interceptors.request.use(
  config => {
    const token = localStorage.getItem('token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  error => {
    return Promise.reject(error)
  }
)

// 响应拦截器
instance.interceptors.response.use(
  response => {
    // 检查是否有新的 token，有则更新（实现 token 自动续期）
    const newToken = response.headers['x-refresh-token']
    if (newToken) {
      localStorage.setItem('token', newToken)
    }
    return response.data
  },
  error => {
    if (error.response && error.response.status === 401) {
      localStorage.removeItem('token')
      window.location.href = '/login'
    }
    return Promise.reject(error)
  }
)

export default instance