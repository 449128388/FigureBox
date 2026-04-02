import axios from 'axios'

const instance = axios.create({
  baseURL: '/api',
  timeout: 10000,
  // 允许获取自定义响应头
  headers: {
    'Access-Control-Expose-Headers': 'X-Refresh-Token'
  }
})

// 请求拦截器
instance.interceptors.request.use(
  config => {
    const token = localStorage.getItem('token')
    console.log('请求拦截器 - 路径:', config.url, '有token:', !!token)
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
    const newToken = response.headers['x-refresh-token'] || response.headers['X-Refresh-Token']
    console.log('响应拦截器 - 路径:', response.config?.url, '有新token:', !!newToken)
    if (newToken) {
      const oldToken = localStorage.getItem('token')
      // 只有当新token与旧token不同时才更新
      if (oldToken !== newToken) {
        localStorage.setItem('token', newToken)
        console.log('Token 已自动续期')
      }
    }
    return response.data
  },
  error => {
    console.log('请求错误:', error.response?.status, error.config?.url)
    if (error.response && error.response.status === 401) {
      console.log('401错误，清除token并跳转到登录页')
      localStorage.removeItem('token')
      window.location.href = '/login'
    }
    return Promise.reject(error)
  }
)

export default instance