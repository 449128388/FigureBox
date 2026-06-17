/**
 * CabinetDetail 业务逻辑组合式函数（Vue2 版本使用 mixin 方式）
 * 包含排序、评分、API请求等核心业务逻辑
 */

import axios from '@/axios'
import { ElMessage } from 'element-plus'

export default {
  data() {
    return {
      // 评分相关状态
      starRatings: {},        // { figureId: rating }
      starEditingIndex: null, // 当前正在编辑的卡片索引
      starTempValue: 0,       // 编辑中的临时值

      // 视图模式
      viewMode: 'grid',       // 视图模式: 'grid' 网格 / 'list' 列表

      // 排序相关状态
      sortBy: 'name',         // 排序字段: 'transaction_date' / 'name' / 'rating' / 'holding_days'
      sortOrder: 'asc',       // 排序方向: 'asc' 升序 / 'desc' 降序

      // FLIP动画相关
      flipEnabled: true,      // 是否启用FLIP动画
      isAnimating: false      // 是否正在执行动画
    }
  },

  computed: {
    /**
     * 排序后的藏品列表
     */
    sortedItems() {
      if (!this.cabinet?.items || this.cabinet.items.length === 0) return []
      const items = [...this.cabinet.items]
      const sortBy = this.sortBy
      const sortOrder = this.sortOrder

      items.sort((a, b) => {
        let valA, valB

        switch (sortBy) {
          case 'name':
            valA = (a.name || '').toLowerCase()
            valB = (b.name || '').toLowerCase()
            break
          case 'transaction_date':
            valA = a.transaction_date || ''
            valB = b.transaction_date || ''
            break
          case 'rating':
            valA = this.starRatings[a.id] || 0
            valB = this.starRatings[b.id] || 0
            break
          case 'holding_days':
            valA = a.holding_days || 0
            valB = b.holding_days || 0
            break
          default:
            valA = (a.name || '').toLowerCase()
            valB = (b.name || '').toLowerCase()
        }

        if (valA < valB) return sortOrder === 'asc' ? -1 : 1
        if (valA > valB) return sortOrder === 'asc' ? 1 : -1
        return 0
      })

      return items
    }
  },

  mounted() {
    this.fetchRatings()
  },

  methods: {
    /**
     * 获取当前收藏柜中所有手办的评分
     */
    async fetchRatings() {
      if (!this.cabinet?.items || this.cabinet.items.length === 0) return
      const figureIds = this.cabinet.items.map(it => it.id).filter(Boolean).join(',')
      if (!figureIds) return

      try {
        const res = await axios.get('/collector/ratings', {
          params: {
            cabinet_type: this.cabinet.key,
            figure_ids: figureIds
          }
        })
        const ratings = res.ratings || []
        const map = {}
        ratings.forEach(r => { map[r.figure_id] = r.rating })
        this.starRatings = map
      } catch (e) {
        // 静默失败，显示无评分
        console.warn('获取评分失败:', e)
      }
    },

    /**
     * 切换评分编辑状态
     * @param {number} index - 卡片索引
     */
    toggleStarEdit(index) {
      if (this.starEditingIndex === index) {
        // 再次点击同一张卡 → 关闭编辑
        this.starEditingIndex = null
        this.starTempValue = 0
      } else {
        // 点击其他卡 → 打开编辑
        const item = this.sortedItems[index]
        this.starEditingIndex = index
        this.starTempValue = this.starRatings[item.id] || 0
      }
    },

    /**
     * 设置评分并自动保存
     * @param {string} figureId - 手办ID
     * @param {number} index - 卡片索引
     * @param {number} rating - 评分值
     */
    async setRating(figureId, index, rating) {
      this.starTempValue = rating
      this.starRatings = { ...this.starRatings, [figureId]: rating }

      // 0.5 秒后自动保存
      setTimeout(async () => {
        try {
          await axios.post('/collector/ratings', {
            figure_id: figureId,
            cabinet_type: this.cabinet.key,
            rating: rating
          })
          ElMessage.success('已更新')
        } catch (e) {
          ElMessage.error('评分保存失败')
        }
      }, 500)

      // 关闭编辑状态
      this.starEditingIndex = null
      this.starTempValue = 0
    },

    /**
     * 切换视图模式
     * @param {string} mode - 视图模式 'grid' | 'list'
     */
    switchView(mode) {
      this.viewMode = mode
    },

    /**
     * 处理排序点击
     * @param {string} field - 排序字段
     */
    doSort(field) {
      if (this.sortBy === field) {
        // 同一字段再次点击，切换排序方向
        this.sortOrder = this.sortOrder === 'asc' ? 'desc' : 'asc'
      } else {
        // 切换排序字段，根据字段类型设置默认排序方向
        this.sortBy = field
        // 收藏天数、入库时间、喜爱度默认降序（多的/新的在前）
        // 名称默认升序（A-Z）
        const defaultDescFields = ['rating', 'holding_days', 'transaction_date']
        this.sortOrder = defaultDescFields.includes(field) ? 'desc' : 'asc'
      }
    },

    /**
     * 根据收藏柜类型获取默认排序配置
     * @param {string} cabinetKey - 收藏柜类型key
     * @returns {Object} { sortBy, sortOrder }
     */
    getDefaultSortByCabinet(cabinetKey) {
      // 海景房专区默认按喜爱度降序
      if (cabinetKey === 'star') {
        return { sortBy: 'rating', sortOrder: 'desc' }
      }
      // 其他默认按名称升序
      return { sortBy: 'name', sortOrder: 'asc' }
    },

    /**
     * 初始化排序状态（根据收藏柜类型）
     * @param {string} cabinetKey - 收藏柜类型key
     */
    initSortByCabinet(cabinetKey) {
      const { sortBy, sortOrder } = this.getDefaultSortByCabinet(cabinetKey)
      this.sortBy = sortBy
      this.sortOrder = sortOrder
    },

    /**
     * 执行FLIP动画
     * @param {HTMLElement} container - 容器元素
     * @param {Function} callback - 状态变更回调
     */
    async performFlip(container, callback) {
      if (!this.flipEnabled || !container) {
        callback()
        return
      }

      this.isAnimating = true

      // 1. First: 记录旧位置
      const items = Array.from(container.children)
      const oldPositions = new Map()
      items.forEach(item => {
        const rect = item.getBoundingClientRect()
        oldPositions.set(item, { left: rect.left, top: rect.top })
      })

      // 2. 执行状态变更（触发重新排序）
      callback()

      // 等待DOM更新
      await this.$nextTick()

      // 3. Last: 记录新位置并计算偏移
      const newItems = Array.from(container.children)
      newItems.forEach(item => {
        const oldPos = oldPositions.get(item)
        if (oldPos) {
          const newRect = item.getBoundingClientRect()
          const deltaX = oldPos.left - newRect.left
          const deltaY = oldPos.top - newRect.top

          // 4. Invert: 应用反向变换
          if (deltaX !== 0 || deltaY !== 0) {
            item.style.transform = `translate(${deltaX}px, ${deltaY}px)`
            item.style.transition = 'none'
          }
        }
      })

      // 5. Play: 触发动画
      requestAnimationFrame(() => {
        newItems.forEach(item => {
          item.style.transform = ''
          item.style.transition = 'transform 300ms ease-out'
        })

        // 动画结束后清理
        setTimeout(() => {
          newItems.forEach(item => {
            item.style.transition = ''
          })
          this.isAnimating = false
        }, 300)
      })
    }
  }
}
