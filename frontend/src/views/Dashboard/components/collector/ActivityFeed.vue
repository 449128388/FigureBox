<!--
  ActivityFeed.vue - 收藏家模式动态流组件

  功能说明：
  - 展示用户与藏品/订单的所有交互事件
  - 按日期分组渲染时间轴
  - 支持事件类型筛选
  - 支持点击查看事件详情
  - 支持分页加载更多

  组件依赖：
  - 使用 useActivityFeed composable 管理业务逻辑
  - 使用 activityApi.js 进行 API 调用

  Events:
  - activity-action: 操作按钮点击事件
-->

<template>
  <div class="feed-card">
    <div class="feed-header">
      <el-icon><ChatDotRound /></el-icon> 动态流
    </div>

    <!-- 筛选器 -->
    <div class="filter-bar">
      <button
        v-for="opt in filterOptions"
        :key="opt.value"
        class="filter-btn"
        :class="{ active: currentFilter === opt.value }"
        @click="switchFilter(opt.value)"
      >
        <span class="filter-dot" :style="{ background: opt.color }"></span>
        {{ opt.label }}
      </button>
    </div>

    <!-- 加载中 -->
    <div v-if="loading && activityGroups.length === 0" class="loading-state">
      <div class="loading-spinner"></div>
      <div class="loading-text">加载中...</div>
    </div>

    <!-- 动态流内容 -->
    <div v-else-if="activityGroups.length > 0" class="feed-content">
      <div v-for="group in activityGroups" :key="group.date" class="feed-group">
        <div class="feed-date">
          <span class="date-icon">🗓️</span>
          <span>{{ group.date }}</span>
          <span v-if="group.label" class="date-label">· {{ group.label }}</span>
        </div>
        <div class="feed-timeline">
          <div v-for="(item, index) in group.items" :key="item.id" class="feed-item">
            <div class="feed-dot" :class="getEventDotClass(item.event_type)"></div>
            <div class="feed-content">
              <div class="feed-title" v-html="formatEventTitle(item)"></div>
              <div class="feed-meta">
                <button class="feed-detail-btn" @click="showDetail(item.id)">查看详情</button>
                <span class="feed-time">{{ formatTime(item.created_at) }}</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 空状态 -->
    <div v-else class="empty-state">
      <div class="empty-state-icon">🎉</div>
      <div class="empty-state-title">开始你的收藏之旅吧！</div>
      <div class="empty-state-desc">去添加第一体手办</div>
    </div>

    <!-- 加载更多 / 没有更多 -->
    <div class="load-more">
      <button v-if="hasMore" class="load-more-btn" @click="loadMore" :disabled="loading">
        {{ loading ? '加载中...' : '加载更多' }}
      </button>
      <span v-else-if="activityGroups.length > 0" class="load-more-text">没有更多动态了</span>
    </div>
  </div>

  <!-- ===== 详情弹窗 (Bottom Sheet) ===== -->
  <div v-if="detailVisible" class="sheet-overlay" @click="closeDetail">
    <div class="sheet" @click.stop>
      <div class="sheet-header">
        <div class="sheet-title">{{ detailSheetTitle }}</div>
        <div class="sheet-close" @click="closeDetail">×</div>
      </div>
      <div class="sheet-body" v-if="eventDetail">
        <!-- 手办卡片 -->
        <div class="detail-figure-card" v-if="showFigureCard">
          <div class="detail-figure-img">
            <img v-if="figureImageUrl" :src="figureImageUrl" :alt="detailData.figure_name" class="figure-real-img" />
            <span v-else>🧸</span>
          </div>
          <div class="detail-figure-info">
            <div class="detail-figure-name">{{ detailData.figure_name }}</div>
            <div class="detail-figure-line">{{ figureWork }} · {{ figureScale }} · {{ figureManufacturer }}</div>
          </div>
        </div>

        <!-- BUY 事件 -->
        <template v-if="eventDetail.event_type === 'buy'">
          <div class="detail-section">
            <div class="detail-section-title">订单信息</div>
            <div class="detail-row"><span class="detail-row-label">订单编号</span><span class="detail-row-value buy-detail-value">{{ detailData.order_no }}</span></div>
            <div class="detail-row"><span class="detail-row-label">下单时间</span><span class="detail-row-value buy-detail-value">{{ eventDetail.created_at?.replace('T', ' ') }}</span></div>
            <div class="detail-row"><span class="detail-row-label">支付类型</span><span class="detail-row-value buy-detail-value">{{ detailData.paid_type }}</span></div>
            <div class="detail-row"><span class="detail-row-label">已付定金</span><span class="detail-row-value buy-detail-value">{{ currencySymbol }}{{ detailData.amount }}</span></div>
            <div class="detail-row"><span class="detail-row-label">待补尾款</span><span class="detail-row-value buy-detail-value">{{ balanceCurrencySymbol }}{{ detailData.balance || 0 }}</span></div>
            <div class="detail-row"><span class="detail-row-label">当前状态</span><span class="detail-row-value status status-wait">🟡 {{ detailData.status }}</span></div>
          </div>
          <div v-if="detailData.status === '等待补款'" class="detail-actions">
            <button class="detail-btn" @click="navigateToOrders">查看订单详情</button>
            <button class="detail-btn detail-btn-primary" @click="navigateToOrdersAndEdit(detailData.order_id)">去补款</button>
          </div>
        </template>

        <!-- SELL 事件 -->
        <template v-if="eventDetail.event_type === 'sell'">
          <div class="profit-card" :class="{ profit: (detailData.profit || 0) >= 0 }">
            <div class="profit-label">实现盈亏</div>
            <div class="profit-value">{{ (detailData.profit || 0) >= 0 ? '+' : '' }}¥{{ detailData.profit }}</div>
            <div class="profit-sub">收益率 {{ detailData.profit_rate || '0.00' }}% · 持有 {{ detailData.hold_days || 0 }} 天</div>
          </div>
          <div class="detail-section">
            <div class="detail-section-title">交易信息</div>
            <div class="detail-row"><span class="detail-row-label">订单号</span><span class="detail-row-value buy-detail-value">{{ detailData.order_no || '-' }}</span></div>
            <div class="detail-row"><span class="detail-row-label">卖出价格</span><span class="detail-row-value accent">¥{{ detailData.sell_price }}</span></div>
            <div class="detail-row"><span class="detail-row-label">成本价格</span><span class="detail-row-value">¥{{ detailData.cost_price }}</span></div>
            <div class="detail-row"><span class="detail-row-label">净利润</span><span :class="['detail-row-value', (detailData.profit || 0) >= 0 ? 'red' : 'green']">{{ (detailData.profit || 0) >= 0 ? '+' : '' }}¥{{ detailData.profit }}</span></div>
            <div class="detail-row"><span class="detail-row-label">卖出日期</span><span class="detail-row-value buy-detail-value">{{ detailData.out_date }}</span></div>
            <div class="detail-row"><span class="detail-row-label">买家</span><span class="detail-row-value buy-detail-value">{{ detailData.buyer || '-' }}</span></div>
            <div class="detail-row"><span class="detail-row-label">持有天数</span><span class="detail-row-value buy-detail-value">{{ detailData.hold_days }} 天</span></div>
            <div class="detail-row" v-if="detailData.tracking_number"><span class="detail-row-label">快递单号</span><span class="detail-row-value buy-detail-value">{{ detailData.tracking_number }}</span></div>
            <div class="detail-row" v-if="detailData.logistics_company"><span class="detail-row-label">物流公司</span><span class="detail-row-value buy-detail-value">{{ detailData.logistics_company }}</span></div>
          </div>
          <div class="detail-actions">
            <button class="detail-btn" @click="navigateToSoldOrders">查看资金流水</button>
            <button class="detail-btn detail-btn-primary" @click="navigateToFigureDetail(detailData.figure_id)">查看手办详情</button>
          </div>
        </template>

        <!-- FULL_PAY 事件 -->
        <template v-if="eventDetail.event_type === 'full_pay'">
          <div class="detail-section">
            <div class="detail-section-title">付款信息（补款后）</div>
            <div class="detail-row"><span class="detail-row-label">订单编号</span><span class="detail-row-value buy-detail-value">{{ detailData.order_no }}</span></div>
            <div class="detail-row"><span class="detail-row-label">定金金额</span><span class="detail-row-value buy-detail-value">{{ currencySymbol }}{{ detailData.deposit_paid || 0 }}</span></div>
            <div class="detail-row"><span class="detail-row-label">本次尾款</span><span class="detail-row-value buy-detail-value">{{ currencySymbol }}{{ detailData.paid_amount }}</span></div>
            <div class="detail-row"><span class="detail-row-label">累计支付</span><span class="detail-row-value buy-detail-value">{{ currencySymbol }}{{ detailData.total_paid }}</span></div>
            <div class="detail-row"><span class="detail-row-label">支付时间</span><span class="detail-row-value buy-detail-value">{{ detailData.pay_date }}</span></div>
            <div class="detail-row"><span class="detail-row-label">当前状态</span><span class="detail-row-value status status-done">🟢 {{ detailData.status }}</span></div>
          </div>
          <div class="detail-section">
            <div class="detail-section-title">订单进度追踪</div>
            <div class="status-timeline">
              <div class="status-timeline-item">
                <div class="status-timeline-dot active"></div>
                <div class="status-timeline-text active">定金已付</div>
                <div class="status-timeline-time">{{ eventDetail.created_at?.replace('T', ' ') }}</div>
              </div>
              <div class="status-timeline-item">
                <div class="status-timeline-dot current"></div>
                <div class="status-timeline-text current">尾款已付清</div>
                <div class="status-timeline-time">{{ detailData.pay_date }}</div>
              </div>
              <div class="status-timeline-item">
                <div class="status-timeline-dot"></div>
                <div class="status-timeline-text">工厂出荷</div>
                <div class="status-timeline-time">{{ detailData.due_date ? '预计 ' + detailData.due_date : '待确认' }}</div>
              </div>
              <div class="status-timeline-item">
                <div class="status-timeline-dot"></div>
                <div class="status-timeline-text">入库</div>
                <div class="status-timeline-time">待确认</div>
              </div>
            </div>
          </div>
          <div class="detail-actions">
            <button class="detail-btn" @click="navigateToOrders">查看订单详情</button>
          </div>
        </template>

        <!-- IN_STOCK 事件 -->
        <template v-if="eventDetail.event_type === 'in_stock'">
          <div class="detail-section">
            <div class="detail-section-title">入库信息</div>
            <div class="detail-row"><span class="detail-row-label">入库日期</span><span class="detail-row-value buy-detail-value">{{ detailData.in_date }}</span></div>
            <div class="detail-row"><span class="detail-row-label">订单编号</span><span class="detail-row-value buy-detail-value">{{ detailData.order_no }}</span></div>
            <div class="detail-row"><span class="detail-row-label">入库成本</span><span class="detail-row-value buy-detail-value">{{ currencySymbol }}{{ detailData.cost }}</span></div>
            <div class="detail-row"><span class="detail-row-label">入柜位置</span><span class="detail-row-value buy-detail-value">{{ figureCabinets || detailData.cabinet || '未分类' }}</span></div>
            <div class="detail-row"><span class="detail-row-label">当前状态</span><span class="detail-row-value status status-done">🟢 {{ detailData.status }}</span></div>
          </div>
          <div class="detail-actions">
            <button class="detail-btn" @click="navigateToFigureDetail(detailData.figure_id)">查看手办详情</button>
          </div>
        </template>

        <!-- OUT 事件 -->
        <template v-if="eventDetail.event_type === 'out'">
          <div class="detail-section">
            <div class="detail-section-title">移出信息</div>
            <div class="detail-row"><span class="detail-row-label">移出分类</span><span class="detail-row-value">{{ detailData.from_cabinet }}</span></div>
            <div class="detail-row"><span class="detail-row-label">移出原因</span><span class="detail-row-value">{{ detailData.reason || '未填写' }}</span></div>
          </div>
          <div class="out-notice">
            ⚠️ 出柜登记仅影响展示柜分类，不会删除藏品信息，也不会产生交易流水。该藏品仍可在资产列表中查看。
          </div>
        </template>

        <!-- TAG_ADD 事件 -->
        <template v-if="eventDetail.event_type === 'tag_add'">
          <div class="detail-section">
            <div class="detail-section-title">标签信息</div>
            <div class="detail-row"><span class="detail-row-label">标签名称</span><span class="detail-row-value tags-row"><span class="tag-badge" v-for="t in detailData.tags" :key="t.tag_id" :style="{ background: (t.tag_color || '#C49A6C') + '20', color: t.tag_color || '#C49A6C' }">#{{ t.tag_name }}</span></span></div>
            <div class="detail-row"><span class="detail-row-label">添加时间</span><span class="detail-row-value">{{ detailData.add_date }}</span></div>
          </div>
        </template>

        <!-- ORDER_CANCEL 事件 -->
        <template v-if="eventDetail.event_type === 'order_cancel'">
          <div class="detail-section">
            <div class="detail-section-title">订单信息</div>
            <div class="detail-row"><span class="detail-row-label">订单编号</span><span class="detail-row-value buy-detail-value">{{ detailData.order_no }}</span></div>
            <div class="detail-row"><span class="detail-row-label">取消时间</span><span class="detail-row-value buy-detail-value">{{ eventDetail.created_at?.replace('T', ' ') }}</span></div>
            <div class="detail-row"><span class="detail-row-label">取消原因</span><span class="detail-row-value buy-detail-value">{{ detailData.cancel_reason || '未填写' }}</span></div>
            <div class="detail-row"><span class="detail-row-label">退款金额</span><span class="detail-row-value buy-detail-value">¥{{ detailData.refund_amount || 0 }}</span></div>
            <div class="detail-row"><span class="detail-row-label">当前状态</span><span class="detail-row-value status status-cancel">⚪ {{ detailData.status || '已取消' }}</span></div>
          </div>
          <div class="detail-actions">
            <button class="detail-btn" @click="navigateToFigureDetail(detailData.figure_id)">查看手办详情</button>
          </div>
        </template>

        <!-- PRICE_UPDATE 事件 -->
        <template v-if="eventDetail.event_type === 'price_update'">
          <div class="detail-section">
            <div class="detail-section-title">价格变动</div>
            <div class="detail-row"><span class="detail-row-label">更新日期</span><span class="detail-row-value buy-detail-value">{{ detailData.update_date }}</span></div>
            <div class="detail-row"><span class="detail-row-label">原市场价</span><span class="detail-row-value buy-detail-value">{{ getCurrencySymbol(detailData.old_currency) }}{{ detailData.old_price }}</span></div>
            <div class="detail-row"><span class="detail-row-label">新市场价</span><span class="detail-row-value buy-detail-value">{{ getCurrencySymbol(detailData.new_currency) }}{{ detailData.new_price }}</span></div>
            <div class="detail-row"><span class="detail-row-label">变动金额</span><span :class="['detail-row-value', (detailData.change || 0) >= 0 ? 'red' : 'green']">{{ (detailData.change || 0) >= 0 ? '+' : '' }}¥{{ detailData.change }}</span></div>
            <div class="detail-row"><span class="detail-row-label">变动幅度</span><span :class="['detail-row-value', (detailData.change || 0) >= 0 ? 'red' : 'green']">{{ (detailData.change || 0) >= 0 ? '📈' : '📉' }} {{ detailData.change_rate }}</span></div>
          </div>
          <div class="detail-actions">
            <button class="detail-btn" @click="navigateToFigureDetail(detailData.figure_id)">查看手办详情</button>
          </div>
        </template>

        <!-- 回退：未知事件类型显示原始 detail_data -->
        <template v-if="!['buy','sell','full_pay','in_stock','out','tag_add','order_cancel','price_update'].includes(eventDetail.event_type)">
          <div class="detail-section">
            <div class="detail-section-title">事件数据</div>
            <pre style="font-size:12px;white-space:pre-wrap;word-break:break-all;">{{ JSON.stringify(detailData, null, 2) }}</pre>
          </div>
        </template>
      </div>
    </div>
  </div>
</template>

<script>
import { computed } from 'vue'
import { useRouter } from 'vue-router'
import { ChatDotRound } from '@element-plus/icons-vue'
import { useActivityFeed } from './ActivityFeed/composables/useActivityFeed.js'

export default {
  name: 'ActivityFeed',

  components: { ChatDotRound },

  props: {
    collectorData: {
      type: Object,
      default: () => ({})
    }
  },

  emits: ['activity-action'],

  setup(props, { emit }) {
    const router = useRouter()
    const feed = useActivityFeed()

    const filterOptions = [
      { value: 'all', label: '全部动态', color: '#C49A6C' },
      { value: 'buy', label: '买入', color: '#4A90E2' },
      { value: 'full_pay', label: '尾款付清', color: '#4A90E2' },
      { value: 'in_stock', label: '入库', color: '#C49A6C' },
      { value: 'sell', label: '卖出', color: '#D66A6A' },
      { value: 'out', label: '出柜', color: '#999' },
      { value: 'order', label: '订单', color: '#00BCD4' },
      { value: 'order_cancel', label: '取消', color: '#999' },
      { value: 'tag', label: '标签', color: '#9B7ED8' },
      { value: 'price', label: '价格', color: '#7EB8A2' }
    ]

    // 加载初始数据
    feed.loadActivities('all')

    // 计算属性
    const detailSheetTitle = computed(() => {
      return '动态流详情'
    })
    const showFigureCard = computed(() => {
      const type = feed.eventDetail.value?.event_type
      return ['buy', 'sell', 'full_pay', 'in_stock', 'out', 'tag_add', 'order_cancel', 'price_update'].includes(type)
    })
    const detailData = computed(() => {
      return feed.eventDetail.value?.detail_data || {}
    })
    const figureImageUrl = computed(() => {
      // 优先使用后端返回的 figure_image（从 Figure.images[0] 获取）
      if (feed.eventDetail.value?.figure_image) {
        return feed.eventDetail.value.figure_image
      }
      // 降级使用 detail_data 中的 cover_image（BUY 事件）
      if (detailData.value?.cover_image) {
        return detailData.value.cover_image
      }
      return ''
    })
    const figureWork = computed(() => {
      return feed.eventDetail.value?.figure_work || detailData.value?.work || '未知'
    })
    const figureScale = computed(() => {
      return feed.eventDetail.value?.figure_scale || detailData.value?.scale || '未知'
    })
    const figureManufacturer = computed(() => {
      return feed.eventDetail.value?.figure_manufacturer || detailData.value?.manufacturer || '未知'
    })
    const currencySymbol = computed(() => {
      const map = { 'CNY': '¥', 'JPY': 'JP ¥', 'USD': '$', 'EUR': '€', 'GBP': '£', 'HKD': 'HK$', 'TWD': 'NT$', 'KRW': '₩' }
      return map[detailData.value?.currency] || '¥'
    })
    const balanceCurrencySymbol = computed(() => {
      const map = { 'CNY': '¥', 'JPY': 'JP ¥', 'USD': '$', 'EUR': '€', 'GBP': '£', 'HKD': 'HK$', 'TWD': 'NT$', 'KRW': '₩' }
      return map[detailData.value?.balance_currency] || '¥'
    })

    // IN_STOCK 事件：实时计算手办所在藏品柜（来自后端接口）
    const figureCabinets = computed(() => {
      const cabs = feed.eventDetail.value?.figure_cabinets
      if (cabs && Array.isArray(cabs) && cabs.length > 0) {
        return cabs.join(' / ')
      }
      return ''
    })

    // 获取货币符号
    function getCurrencySymbol(currency) {
      const map = { 'CNY': '¥', 'JPY': 'JP ¥', 'USD': '$', 'EUR': '€', 'GBP': '£', 'HKD': 'HK$', 'TWD': 'NT$', 'KRW': '₩' }
      return map[currency] || currency || '¥'
    }

    // 导航方法
    function navigateToSoldOrders() {
      router.push('/sell')
    }

    function navigateToFigureDetail(figureId) {
      if (figureId) {
        router.push(`/figures/${figureId}`)
      }
    }

    function navigateToOrders() {
      router.push('/orders')
    }

    function navigateToOrdersAndEdit(orderId) {
      if (orderId) {
        router.push(`/orders?editOrderId=${orderId}`)
      }
    }

    return {
      ...feed,
      filterOptions,
      detailSheetTitle,
      showFigureCard,
      detailData,
      figureImageUrl,
      figureWork,
      figureScale,
      figureManufacturer,
      currencySymbol,
      balanceCurrencySymbol,
      figureCabinets,
      getCurrencySymbol,
      navigateToSoldOrders,
      navigateToFigureDetail,
      navigateToOrders,
      navigateToOrdersAndEdit
    }
  }
}
</script>

<style scoped>
.feed-card {
  margin-bottom: 30px;
  background: #fff;
  border-radius: 12px;
  padding: 20px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
}

.feed-header {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 18px;
  font-weight: 600;
  color: #333;
  margin-bottom: 16px;
}

/* ===== Filter Bar ===== */
.filter-bar {
  display: flex;
  gap: 8px;
  margin-bottom: 20px;
  flex-wrap: wrap;
}

.filter-btn {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  padding: 5px 12px;
  border: 1px solid #EBE8E4;
  background: #fff;
  border-radius: 6px;
  font-size: 13px;
  color: #666;
  cursor: pointer;
  transition: all 0.2s;
}

.filter-btn:hover {
  border-color: #E8D5C0;
  color: #C49A6C;
  background: #FDF6EE;
}

.filter-btn.active {
  background: #FDF6EE;
  border-color: #C49A6C;
  color: #C49A6C;
  font-weight: 500;
}

.filter-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
}

/* ===== Date Group ===== */
.feed-group {
  margin-bottom: 20px;
}

.feed-group:last-child {
  margin-bottom: 0;
}

.feed-date {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 13px;
  color: #999;
  margin-bottom: 12px;
  padding-left: 4px;
}

.date-icon {
  font-size: 14px;
}

.date-label {
  color: #666;
  font-weight: 500;
}

/* ===== Timeline ===== */
.feed-timeline {
  position: relative;
  padding-left: 28px;
}

.feed-timeline::before {
  content: "";
  position: absolute;
  left: 8px;
  top: 4px;
  bottom: 0;
  width: 2px;
  background: linear-gradient(180deg, #E8D5C0 0%, transparent 100%);
  border-radius: 1px;
}

/* ===== Feed Item ===== */
.feed-item {
  position: relative;
  padding-bottom: 16px;
}

.feed-item:last-child {
  padding-bottom: 0;
}

.feed-dot {
  position: absolute;
  left: -24px;
  top: 4px;
  width: 12px;
  height: 12px;
  border-radius: 50%;
  border: 2px solid #fff;
  box-shadow: 0 0 0 2px #E8D5C0;
  z-index: 1;
}

.feed-dot.buy { background: #4A90E2; box-shadow: 0 0 0 2px #BBDEFB; }
.feed-dot.full_pay { background: #7EB8A2; box-shadow: 0 0 0 2px #C8E6D5; }
.feed-dot.in_stock { background: #C49A6C; box-shadow: 0 0 0 2px #E8D5C0; }
.feed-dot.sell { background: #D66A6A; box-shadow: 0 0 0 2px #FFCDD2; }
.feed-dot.out { background: #999; box-shadow: 0 0 0 2px #E0E0E0; }
.feed-dot.tag_add { background: #9B7ED8; box-shadow: 0 0 0 2px #E1BEE7; }
.feed-dot.fix { background: #E6A23C; box-shadow: 0 0 0 2px #FFE082; }
.feed-dot.order_create { background: #00BCD4; box-shadow: 0 0 0 2px #B2EBF2; }
.feed-dot.order_cancel { background: #BDBDBD; box-shadow: 0 0 0 2px #E0E0E0; }
.feed-dot.price_update { background: #7EB8A2; box-shadow: 0 0 0 2px #C8E6D5; }

.feed-content {
  background: #FAFAFA;
  border-radius: 10px;
  padding: 12px 14px;
  border: 1px solid #EBE8E4;
  transition: all 0.2s;
}

.feed-content:hover {
  border-color: #E8D5C0;
  background: #FDFBF9;
}

.feed-title {
  font-size: 14px;
  color: #333;
  line-height: 1.6;
}

.feed-title :deep(.highlight) {
  color: #C49A6C;
  font-weight: 600;
}

.feed-title :deep(.price) {
  color: #D66A6A;
  font-weight: 600;
}

.feed-title :deep(.profit) {
  color: #D66A6A;
  font-weight: 600;
}

.feed-title :deep(.loss) {
  color: #7EB8A2;
  font-weight: 600;
}

.feed-title :deep(.tag-badge) {
  display: inline-block;
  font-size: 14px;
  padding: 1px 6px;
  border-radius: 6px;
  margin-left: 4px;
  vertical-align: middle;
}

.feed-meta {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-top: 8px;
}

.feed-detail-btn {
  padding: 4px 12px;
  border: 1px solid #EBE8E4;
  background: #fff;
  border-radius: 6px;
  font-size: 12px;
  color: #666;
  cursor: pointer;
  transition: all 0.2s;
}

.feed-detail-btn:hover {
  border-color: #C49A6C;
  color: #C49A6C;
  background: #FDF6EE;
}

.feed-time {
  font-size: 12px;
  color: #999;
}

/* ===== Load More ===== */
.load-more {
  text-align: center;
  padding: 20px 0 0;
}

.load-more-btn {
  padding: 8px 24px;
  border: 1px solid #EBE8E4;
  background: #fff;
  border-radius: 20px;
  font-size: 13px;
  color: #666;
  cursor: pointer;
  transition: all 0.2s;
}

.load-more-btn:hover {
  border-color: #C49A6C;
  color: #C49A6C;
}

.load-more-btn:disabled {
  cursor: default;
  opacity: 0.6;
}

.load-more-text {
  font-size: 13px;
  color: #999;
}

/* ===== Empty State ===== */
.empty-state {
  text-align: center;
  padding: 40px 20px;
  color: #999;
}

.empty-state-icon {
  font-size: 48px;
  margin-bottom: 12px;
  opacity: 0.6;
}

.empty-state-title {
  font-size: 16px;
  font-weight: 600;
  color: #333;
  margin-bottom: 6px;
}

.empty-state-desc {
  font-size: 14px;
}

/* ===== Loading State ===== */
.loading-state {
  text-align: center;
  padding: 40px 20px;
}

.loading-spinner {
  display: inline-block;
  width: 24px;
  height: 24px;
  border: 3px solid #EBE8E4;
  border-top-color: #C49A6C;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
  margin-bottom: 8px;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.loading-text {
  font-size: 14px;
  color: #999;
}

/* ===== Center Detail Modal ===== */
.sheet-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.4);
  z-index: 200;
  display: flex;
  align-items: center;
  justify-content: center;
  backdrop-filter: blur(4px);
}

.sheet {
  background: #fff;
  border-radius: 16px;
  width: 92%;
  max-width: 600px;
  max-height: 90vh;
  overflow-y: auto;
  box-shadow: 0 12px 40px rgba(0, 0, 0, 0.2);
  animation: modalIn 0.25s ease;
}

@keyframes modalIn {
  from { opacity: 0; transform: scale(0.92); }
  to { opacity: 1; transform: scale(1); }
}

.sheet-header {
  padding: 16px 20px;
  border-bottom: 1px solid #EBE8E4;
  display: flex;
  align-items: center;
  justify-content: space-between;
  position: sticky;
  top: 0;
  background: #fff;
  z-index: 1;
  border-radius: 16px 16px 0 0;
}

.sheet-title {
  font-size: 16px;
  font-weight: 600;
}

.sheet-close {
  width: 28px;
  height: 28px;
  border-radius: 50%;
  border: 1px solid #EBE8E4;
  background: #fff;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  font-size: 16px;
  color: #999;
  transition: all 0.2s;
}

.sheet-close:hover {
  border-color: #D66A6A;
  color: #D66A6A;
}

.sheet-body {
  padding: 20px;
}

/* Detail Figure Card */
.detail-figure-card {
  display: flex;
  gap: 14px;
  padding: 14px;
  background: #FAFAFA;
  border-radius: 10px;
  border: 1px solid #EBE8E4;
  margin-bottom: 20px;
}

.detail-figure-img {
  width: 72px;
  height: 72px;
  background: #F0EEEB;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 32px;
  color: #B0ABA5;
  flex-shrink: 0;
  overflow: hidden;
}

.figure-real-img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  border-radius: 8px;
}

.detail-figure-info {
  flex: 1;
}

.detail-figure-name {
  font-size: 16px;
  font-weight: 600;
  margin-bottom: 4px;
  color: #1F1F1F;
}

.detail-figure-line {
  font-size: 13px;
  color: #666;
  margin-bottom: 2px;
}

/* Detail Sections */
.detail-section {
  margin-bottom: 20px;
}

.detail-section-title {
  font-size: 14px;
  font-weight: 600;
  color: #666;
  margin-bottom: 10px;
  display: flex;
  align-items: center;
  gap: 6px;
}

.detail-section-title::before {
  content: "";
  display: inline-block;
  width: 3px;
  height: 14px;
  background: #C49A6C;
  border-radius: 2px;
}

.detail-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px 0;
  border-bottom: 1px solid #EBE8E4;
  font-size: 14px;
}

.detail-row:last-child {
  border-bottom: none;
}

.detail-row-label {
  color: #666;
}

.detail-row-value {
  color: #333;
  font-weight: 500;
}

.detail-row-value.buy-detail-value {
  color: rgb(31, 31, 31);
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
  line-height: 21px;
  height: 21px;
}

.detail-row-value.accent {
  color: #C49A6C;
}

.detail-row-value.green {
  color: #7EB8A2;
}

.detail-row-value.red {
  color: #D66A6A;
}

.detail-row-value.status {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  padding: 2px 8px;
  border-radius: 10px;
  font-size: 12px;
}

.status-wait {
  background: #FFF8E1;
  color: #E6A23C;
}

.status-done {
  background: #E8F5E9;
  color: #7EB8A2;
}

.status-cancel {
  background: #F5F5F5;
  color: #999;
}

/* Status Timeline */
.status-timeline {
  position: relative;
  padding-left: 24px;
}

.status-timeline::before {
  content: "";
  position: absolute;
  left: 5px;
  top: 0;
  bottom: 0;
  width: 2px;
  background: #EBE8E4;
  border-radius: 1px;
}

.status-timeline-item {
  position: relative;
  padding-bottom: 16px;
}

.status-timeline-item:last-child {
  padding-bottom: 0;
}

.status-timeline-dot {
  position: absolute;
  left: -22px;
  top: 2px;
  width: 10px;
  height: 10px;
  border-radius: 50%;
  background: #EBE8E4;
  border: 2px solid #fff;
}

.status-timeline-dot.active {
  background: #C49A6C;
}

.status-timeline-dot.current {
  background: #7EB8A2;
  box-shadow: 0 0 0 2px #C8E6D5;
}

.status-timeline-text {
  font-size: 13px;
  color: #666;
}

.status-timeline-text.active {
  color: #1F1F1F;
  font-weight: 500;
}

.status-timeline-text.current {
  color: #7EB8A2;
  font-weight: 600;
}

.status-timeline-time {
  font-size: 11px;
  color: #999;
  margin-top: 2px;
}

/* Profit Card */
.profit-card {
  background: linear-gradient(135deg, #FFEBEE 0%, #fff 100%);
  border-radius: 12px;
  padding: 16px;
  border: 1px solid #FFCDD2;
  margin-bottom: 20px;
  text-align: center;
}

.profit-card.loss {
  background: linear-gradient(135deg, #E8F5E9 0%, #fff 100%);
  border-color: #C8E6D5;
}

.profit-label {
  font-size: 13px;
  color: #666;
  margin-bottom: 4px;
}

.profit-value {
  font-size: 28px;
  font-weight: 700;
  color: #D66A6A;
}

.profit-card.loss .profit-value {
  color: #7EB8A2;
}

.profit-sub {
  font-size: 12px;
  color: #999;
  margin-top: 4px;
}

/* Out Notice */
.out-notice {
  background: #FFF8E1;
  border: 1px solid #FFE082;
  border-radius: 8px;
  padding: 12px;
  margin-bottom: 20px;
  font-size: 13px;
  color: #E6A23C;
  line-height: 1.6;
}

/* Tag Badge */
.tag-badge {
  display: inline-block;
  font-size: 12px;
  padding: 2px 8px;
  border-radius: 6px;
  border: 1px solid;
}

.tags-row {
  display: flex;
  flex-wrap: wrap;
  gap: 4px;
}

/* Detail Actions */
.detail-actions {
  display: flex;
  gap: 10px;
  padding-top: 10px;
}

.detail-btn {
  flex: 1;
  padding: 10px 0;
  text-align: center;
  border: 1px solid #EBE8E4;
  background: #fff;
  border-radius: 8px;
  font-size: 14px;
  color: #666;
  cursor: pointer;
  transition: all 0.2s;
}

.detail-btn:hover {
  border-color: #C49A6C;
  color: #C49A6C;
  background: #FDF6EE;
}

.detail-btn-primary {
  background: #C49A6C;
  border-color: #C49A6C;
  color: #fff;
}

.detail-btn-primary:hover {
  background: #B08A5C;
  border-color: #B08A5C;
}
</style>
