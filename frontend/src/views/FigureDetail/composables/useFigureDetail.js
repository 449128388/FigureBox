import { useFigureStore, useOrderStore } from '../../../store'
import axios from '../../../axios'

export function useFigureDetail() {
  const figureStore = useFigureStore()
  const orderStore = useOrderStore()

  const fetchFigureDetail = async (figureId) => {
    try {
      // 调用API获取手办详情（包含完整的标签数据）
      // axios拦截器已处理response.data，直接返回数据
      const data = await axios.get(`/figures/${figureId}`)
      return data
    } catch (error) {
      console.error('获取手办详情失败:', error)
      // 如果API调用失败，尝试从store中获取
      const figure = figureStore.figures.find(f => f.id == figureId)
      return figure || {}
    }
  }

  const fetchOrders = async () => {
    return orderStore.fetchOrders()
  }

  const getRelatedOrders = (figureId, orders) => {
    return orders.filter(order => order.figure_id === parseInt(figureId))
  }

  const getCurrencySymbol = (currency) => {
    switch(currency) {
      case 'CNY': return '元'
      case 'JPY': return '日元'
      case 'USD': return '美元'
      case 'EUR': return '欧元'
      default: return '元'
    }
  }

  const getStatusClass = (status) => {
    switch(status) {
      case '未支付': return 'status-unpaid'
      case '已支付': return 'status-paid'
      case '已完成': return 'status-paid'
      case '已取消': return 'status-cancelled'
      default: return ''
    }
  }

  return {
    figureStore,
    orderStore,
    fetchFigureDetail,
    fetchOrders,
    getRelatedOrders,
    getCurrencySymbol,
    getStatusClass
  }
}